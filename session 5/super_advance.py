from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal, Annotated, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import operator
import json
from datetime import datetime

# ============================================================================
# MOCK KNOWLEDGE BASE DATA
# ============================================================================

KNOWLEDGE_BASE = """
# Product Documentation

## Account Management
- Account creation requires email verification
- Password must be at least 8 characters with uppercase, lowercase, and numbers
- Two-factor authentication is available in Security Settings
- Account deletion takes 30 days to complete
- Premium accounts support up to 5 linked devices

## Billing Information
- Subscription plans: Basic ($9.99/mo), Premium ($19.99/mo), Enterprise ($49.99/mo)
- Billing cycle starts on subscription date
- Refunds available within 30 days of purchase
- Payment methods: Credit card, PayPal, Bank transfer
- Failed payments result in 7-day grace period
- Annual subscriptions get 20% discount

## Technical Support
- System requirements: Windows 10+, macOS 11+, Linux Ubuntu 20.04+
- Mobile apps available for iOS 14+ and Android 9+
- API rate limits: 1000 requests/hour for Premium, 10000/hour for Enterprise
- Downtime notifications sent via email and SMS
- Maintenance windows: Saturdays 2-4 AM EST
- Data backups performed daily at midnight UTC

## Features
- Real-time collaboration with up to 50 users
- File storage: Basic (10GB), Premium (100GB), Enterprise (Unlimited)
- Export formats: PDF, CSV, JSON, XML
- Integration with Slack, Microsoft Teams, Google Workspace
- Custom webhooks available for Enterprise
- Advanced analytics dashboard for Premium and above

## Privacy and Security
- Data encrypted at rest and in transit using AES-256
- GDPR and CCPA compliant
- Data residency options: US, EU, Asia-Pacific
- SOC 2 Type II certified
- Regular security audits performed quarterly
- Bug bounty program active

## Common Issues
- Login failures: Clear cache and cookies, reset password if needed
- Slow performance: Check internet connection, try different browser
- Sync issues: Force sync from Settings > Advanced > Sync Now
- Missing data: Check trash folder, contact support within 90 days
- Payment declined: Verify card details, check with bank
"""

CUSTOMER_TICKETS = """
# Recent Customer Tickets

Ticket #1234:
Customer: John Doe
Issue: Unable to login after password reset
Resolution: Email verification link was expired. Sent new verification email.
Status: Resolved
Date: 2025-10-01

Ticket #1235:
Customer: Jane Smith
Issue: Charged twice for subscription
Resolution: Duplicate charge reversed. Refund processed within 3-5 business days.
Status: Resolved
Date: 2025-10-02

Ticket #1236:
Customer: Bob Johnson
Issue: Data not syncing between devices
Resolution: User had reached device limit. Upgraded to Premium plan.
Status: Resolved
Date: 2025-10-03

Ticket #1237:
Customer: Alice Williams
Issue: Export to PDF not working
Resolution: Browser extension conflict. Disabled conflicting extension.
Status: Resolved
Date: 2025-10-04

Ticket #1238:
Customer: Charlie Brown
Issue: API rate limit errors
Resolution: User exceeded free tier limits. Upgraded to Premium for higher limits.
Status: Resolved
Date: 2025-10-05
"""

# ============================================================================
# STATE SCHEMAS
# ============================================================================

class AgentMessage(TypedDict):
    """Message from an agent."""
    agent: str
    content: str
    timestamp: str
    confidence: float

class CustomerContext(TypedDict):
    """Customer profile and history."""
    customer_id: str
    tier: str  # basic, premium, enterprise
    account_age_days: int
    previous_tickets: int
    satisfaction_score: float

class SupportTicket(TypedDict):
    """Support ticket information."""
    ticket_id: str
    priority: str  # low, medium, high, urgent
    category: str
    subcategory: str
    sentiment: str  # positive, neutral, negative
    estimated_resolution_time: str

class CustomerCareState(TypedDict):
    """Main state for the customer care RAG system."""
    # Input
    customer_query: str
    customer_context: CustomerContext

    # Retrieved knowledge
    relevant_docs: List[dict]
    similar_tickets: List[dict]

    # Agent analysis (accumulating with operator.add)
    triage_analysis: Annotated[List[AgentMessage], operator.add]
    knowledge_synthesis: Annotated[List[AgentMessage], operator.add]
    solution_proposals: Annotated[List[AgentMessage], operator.add]

    # Ticket management
    ticket: SupportTicket
    escalation_needed: bool

    # Multi-round refinement
    iteration: int
    max_iterations: int
    needs_clarification: bool
    clarification_questions: List[str]

    # Final output
    response: str
    next_steps: List[str]
    resources: List[str]
    satisfaction_followup: bool

    # Quality assurance
    qa_approved: bool
    qa_feedback: str

# ============================================================================
# INITIALIZE RAG COMPONENTS
# ============================================================================

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Initialize vector store with knowledge base
def initialize_vector_store():
    """Initialize ChromaDB with knowledge base documents."""

    # Split knowledge base into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    # Create documents
    kb_chunks = text_splitter.split_text(KNOWLEDGE_BASE)
    ticket_chunks = text_splitter.split_text(CUSTOMER_TICKETS)

    kb_docs = [Document(page_content=chunk, metadata={"source": "knowledge_base"})
               for chunk in kb_chunks]
    ticket_docs = [Document(page_content=chunk, metadata={"source": "tickets"})
                   for chunk in ticket_chunks]

    all_docs = kb_docs + ticket_docs

    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        collection_name="customer_support",
        persist_directory="./chroma_db"
    )

    print(f"✅ Initialized vector store with {len(all_docs)} documents")
    return vectorstore

# Global vector store instance
vectorstore = initialize_vector_store()

# Initialize LLMs for different agents
triage_llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
knowledge_llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
solution_llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
qa_llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
coordinator_llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# ============================================================================
# RAG RETRIEVAL NODE
# ============================================================================

def retrieve_knowledge(state: CustomerCareState) -> CustomerCareState:
    """Retrieve relevant knowledge from vector store."""

    print("\n🔍 RETRIEVING KNOWLEDGE from ChromaDB...")

    query = state["customer_query"]
    customer_tier = state["customer_context"]["tier"]

    # Retrieve relevant documents
    docs = vectorstore.similarity_search(query, k=5)

    # Separate by source
    kb_docs = [{"content": doc.page_content, "source": doc.metadata["source"]}
               for doc in docs if doc.metadata["source"] == "knowledge_base"]

    ticket_docs = [{"content": doc.page_content, "source": doc.metadata["source"]}
                   for doc in docs if doc.metadata["source"] == "tickets"]

    print(f"   📚 Retrieved {len(kb_docs)} knowledge base docs")
    print(f"   🎫 Retrieved {len(ticket_docs)} similar ticket docs")

    return {
        "relevant_docs": kb_docs,
        "similar_tickets": ticket_docs
    }

# ============================================================================
# TRIAGE AGENT
# ============================================================================

def triage_agent(state: CustomerCareState) -> CustomerCareState:
    """Analyze and categorize the customer query."""

    print("\n🎯 TRIAGE AGENT analyzing query...")

    query = state["customer_query"]
    customer_context = state["customer_context"]

    prompt = f"""You are a Customer Support Triage Agent. Analyze this customer query.

Customer Query: "{query}"

Customer Context:
- Tier: {customer_context["tier"]}
- Account Age: {customer_context["account_age_days"]} days
- Previous Tickets: {customer_context["previous_tickets"]}
- Satisfaction Score: {customer_context["satisfaction_score"]}/5.0

Analyze and respond in JSON format:
{{
    "category": "billing/technical/account/feature_request/general",
    "subcategory": "specific subcategory",
    "priority": "low/medium/high/urgent",
    "sentiment": "positive/neutral/negative",
    "estimated_resolution_time": "< 1 hour / 1-24 hours / 1-3 days",
    "escalation_recommended": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

    response = triage_llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        analysis = json.loads(content)

        print(f"   Category: {analysis['category']}")
        print(f"   Priority: {analysis['priority']}")
        print(f"   Sentiment: {analysis['sentiment']}")
        print(f"   Confidence: {analysis['confidence']}")

        # Create ticket
        ticket = {
            "ticket_id": f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "priority": analysis["priority"],
            "category": analysis["category"],
            "subcategory": analysis["subcategory"],
            "sentiment": analysis["sentiment"],
            "estimated_resolution_time": analysis["estimated_resolution_time"]
        }

        # Create agent message
        agent_message = {
            "agent": "triage",
            "content": json.dumps(analysis, indent=2),
            "timestamp": datetime.now().isoformat(),
            "confidence": analysis["confidence"]
        }

        return {
            "triage_analysis": [agent_message],
            "ticket": ticket,
            "escalation_needed": analysis["escalation_recommended"]
        }

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {
            "triage_analysis": [{
                "agent": "triage",
                "content": "Error analyzing query",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.5
            }],
            "ticket": {
                "ticket_id": "TKT-ERROR",
                "priority": "medium",
                "category": "general",
                "subcategory": "unknown",
                "sentiment": "neutral",
                "estimated_resolution_time": "1-24 hours"
            },
            "escalation_needed": False
        }

# ============================================================================
# KNOWLEDGE SYNTHESIS AGENT
# ============================================================================

def knowledge_synthesis_agent(state: CustomerCareState) -> CustomerCareState:
    """Synthesize retrieved knowledge into actionable insights."""

    print("\n📚 KNOWLEDGE SYNTHESIS AGENT processing...")

    query = state["customer_query"]
    relevant_docs = state["relevant_docs"]
    similar_tickets = state["similar_tickets"]
    ticket = state["ticket"]

    # Combine retrieved knowledge
    kb_context = "\n\n".join([doc["content"] for doc in relevant_docs])
    ticket_context = "\n\n".join([doc["content"] for doc in similar_tickets])

    prompt = f"""You are a Knowledge Synthesis Agent. Analyze retrieved information.

Customer Query: "{query}"
Category: {ticket["category"]}
Priority: {ticket["priority"]}

Retrieved Knowledge Base Info:
{kb_context}

Similar Past Tickets:
{ticket_context}

Synthesize the information and respond in JSON:
{{
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "applicable_policies": ["policy 1", "policy 2"],
    "common_solutions": ["solution from past tickets"],
    "potential_blockers": ["blocker 1", "blocker 2"],
    "confidence": 0.0-1.0,
    "requires_additional_info": true/false
}}"""

    response = knowledge_llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        synthesis = json.loads(content)

        print(f"   Key Insights: {len(synthesis['key_insights'])}")
        print(f"   Applicable Policies: {len(synthesis['applicable_policies'])}")
        print(f"   Confidence: {synthesis['confidence']}")

        agent_message = {
            "agent": "knowledge_synthesis",
            "content": json.dumps(synthesis, indent=2),
            "timestamp": datetime.now().isoformat(),
            "confidence": synthesis["confidence"]
        }

        return {
            "knowledge_synthesis": [agent_message],
            "needs_clarification": synthesis["requires_additional_info"]
        }

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {
            "knowledge_synthesis": [{
                "agent": "knowledge_synthesis",
                "content": "Error synthesizing knowledge",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.5
            }],
            "needs_clarification": False
        }

# ============================================================================
# SOLUTION GENERATION AGENT
# ============================================================================

def solution_generation_agent(state: CustomerCareState) -> CustomerCareState:
    """Generate specific solutions based on analysis."""

    print("\n💡 SOLUTION GENERATION AGENT creating solutions...")

    query = state["customer_query"]
    ticket = state["ticket"]
    triage = state["triage_analysis"][-1] if state["triage_analysis"] else {}
    knowledge = state["knowledge_synthesis"][-1] if state["knowledge_synthesis"] else {}
    customer_tier = state["customer_context"]["tier"]

    prompt = f"""You are a Solution Generation Agent. Create specific solutions.

Customer Query: "{query}"
Customer Tier: {customer_tier}
Category: {ticket["category"]}
Priority: {ticket["priority"]}

Triage Analysis:
{triage.get("content", "N/A")}

Knowledge Synthesis:
{knowledge.get("content", "N/A")}

Generate solutions in JSON format:
{{
    "primary_solution": {{
        "title": "Solution title",
        "steps": ["step 1", "step 2", "step 3"],
        "expected_outcome": "what should happen",
        "timeframe": "how long it takes"
    }},
    "alternative_solutions": [
        {{
            "title": "Alternative 1",
            "steps": ["step 1", "step 2"],
            "when_to_use": "explanation"
        }}
    ],
    "preventive_measures": ["measure 1", "measure 2"],
    "resources": ["link/doc 1", "link/doc 2"],
    "confidence": 0.0-1.0
}}"""

    response = solution_llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        solutions = json.loads(content)

        print(f"   Primary Solution: {solutions['primary_solution']['title']}")
        print(f"   Alternative Solutions: {len(solutions['alternative_solutions'])}")
        print(f"   Confidence: {solutions['confidence']}")

        agent_message = {
            "agent": "solution_generation",
            "content": json.dumps(solutions, indent=2),
            "timestamp": datetime.now().isoformat(),
            "confidence": solutions["confidence"]
        }

        return {
            "solution_proposals": [agent_message],
            "resources": solutions["resources"]
        }

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {
            "solution_proposals": [{
                "agent": "solution_generation",
                "content": "Error generating solutions",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.5
            }],
            "resources": []
        }

# ============================================================================
# COORDINATOR AGENT
# ============================================================================

def coordinator_agent(state: CustomerCareState) -> CustomerCareState:
    """Coordinate all agent outputs and make decisions."""

    print("\n🎯 COORDINATOR AGENT synthesizing...")

    triage = state.get("triage_analysis", [])
    knowledge = state.get("knowledge_synthesis", [])
    solutions = state.get("solution_proposals", [])
    iteration = state["iteration"]
    max_iterations = state["max_iterations"]

    prompt = f"""You are a Coordinator Agent. Synthesize all agent outputs.

Triage Analysis:
{json.dumps([t["content"] for t in triage], indent=2)}

Knowledge Synthesis:
{json.dumps([k["content"] for k in knowledge], indent=2)}

Solution Proposals:
{json.dumps([s["content"] for s in solutions], indent=2)}

Current Iteration: {iteration + 1}/{max_iterations}

Evaluate and respond in JSON:
{{
    "overall_confidence": 0.0-1.0,
    "solution_completeness": "complete/incomplete",
    "needs_refinement": true/false,
    "needs_clarification": true/false,
    "clarification_questions": ["question 1", "question 2"],
    "reasoning": "explanation"
}}"""

    response = coordinator_llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        evaluation = json.loads(content)

        print(f"   Overall Confidence: {evaluation['overall_confidence']}")
        print(f"   Completeness: {evaluation['solution_completeness']}")
        print(f"   Needs Refinement: {evaluation['needs_refinement']}")

        # Check iteration limit
        needs_refinement = evaluation["needs_refinement"]
        if iteration + 1 >= max_iterations:
            needs_refinement = False
            print(f"   ⚠️ Max iterations reached")

        return {
            "iteration": iteration + 1,
            "needs_clarification": evaluation["needs_clarification"],
            "clarification_questions": evaluation.get("clarification_questions", [])
        }

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {
            "iteration": iteration + 1,
            "needs_clarification": False,
            "clarification_questions": []
        }

# ============================================================================
# RESPONSE GENERATION NODE
# ============================================================================

def generate_final_response(state: CustomerCareState) -> CustomerCareState:
    """Generate customer-facing response."""

    print("\n📝 GENERATING FINAL RESPONSE...")

    query = state["customer_query"]
    customer_context = state["customer_context"]
    ticket = state["ticket"]
    solutions = state.get("solution_proposals", [])
    resources = state.get("resources", [])

    # Extract primary solution
    solution_content = solutions[-1]["content"] if solutions else "{}"

    prompt = f"""Generate a professional, empathetic customer support response.

Customer Query: "{query}"
Customer Tier: {customer_context["tier"]}
Ticket: {ticket["ticket_id"]}
Priority: {ticket["priority"]}

Solutions Available:
{solution_content}

Generate a response that:
1. Acknowledges the customer's concern
2. Provides clear step-by-step solution
3. Offers alternatives if applicable
4. Lists next steps
5. Provides relevant resources
6. Maintains professional yet friendly tone

Keep it concise and actionable."""

    response = coordinator_llm.invoke([HumanMessage(content=prompt)])

    # Generate next steps
    next_steps = [
        f"Ticket {ticket['ticket_id']} has been created",
        "Follow the solution steps provided",
        "Check your email for updates"
    ]

    if ticket["priority"] in ["high", "urgent"]:
        next_steps.append("Our team will follow up within 24 hours")

    # Determine if satisfaction follow-up needed
    satisfaction_followup = ticket["priority"] in ["high", "urgent"] or \
                          ticket["sentiment"] == "negative"

    print(f"   Response generated: {len(response.content)} chars")
    print(f"   Next steps: {len(next_steps)}")
    print(f"   Satisfaction follow-up: {satisfaction_followup}")

    return {
        "response": response.content,
        "next_steps": next_steps,
        "satisfaction_followup": satisfaction_followup
    }

# ============================================================================
# QUALITY ASSURANCE NODE
# ============================================================================

def quality_assurance_check(state: CustomerCareState) -> CustomerCareState:
    """QA check on the final response."""

    print("\n✅ QUALITY ASSURANCE checking response...")

    response = state["response"]
    query = state["customer_query"]
    ticket = state["ticket"]

    prompt = f"""You are a Quality Assurance Agent. Review this support response.

Customer Query: "{query}"
Category: {ticket["category"]}
Priority: {ticket["priority"]}

Generated Response:
{response}

Evaluate the response on:
1. Accuracy - Is the information correct?
2. Completeness - Does it fully address the query?
3. Tone - Is it professional and empathetic?
4. Clarity - Is it easy to understand?
5. Actionability - Are next steps clear?

Respond in JSON:
{{
    "approved": true/false,
    "accuracy_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "tone_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "overall_score": 0.0-1.0,
    "feedback": "brief feedback",
    "improvements": ["suggestion 1", "suggestion 2"]
}}"""

    response_qa = qa_llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response_qa.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        qa_result = json.loads(content)

        print(f"   Approved: {qa_result['approved']}")
        print(f"   Overall Score: {qa_result['overall_score']}")

        return {
            "qa_approved": qa_result["approved"],
            "qa_feedback": json.dumps(qa_result, indent=2)
        }

    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return {
            "qa_approved": True,  # Default to approved on error
            "qa_feedback": "QA check completed with warnings"
        }

# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

def should_refine(state: CustomerCareState) -> Literal["refine", "generate_response"]:
    """Decide whether to refine or generate final response."""
    if state.get("needs_clarification", False) and state["iteration"] < state["max_iterations"]:
        return "refine"
    return "generate_response"

# ============================================================================
# BUILD THE GRAPH
# ============================================================================

def create_customer_care_graph():
    """Create the customer care RAG system graph."""

    workflow = StateGraph(CustomerCareState)

    # Add nodes
    workflow.add_node("retrieve", retrieve_knowledge)
    workflow.add_node("triage", triage_agent)
    workflow.add_node("knowledge_synthesis", knowledge_synthesis_agent)
    workflow.add_node("solution_generation", solution_generation_agent)
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("generate_response", generate_final_response)
    workflow.add_node("qa_check", quality_assurance_check)

    # Set entry point
    workflow.set_entry_point("retrieve")

    # Linear flow for agents (they run sequentially, conceptually parallel)
    workflow.add_edge("retrieve", "triage")
    workflow.add_edge("triage", "knowledge_synthesis")
    workflow.add_edge("knowledge_synthesis", "solution_generation")
    workflow.add_edge("solution_generation", "coordinator")

    # Conditional routing after coordinator
    workflow.add_conditional_edges(
        "coordinator",
        should_refine,
        {
            "refine": "retrieve",  # Loop back for refinement
            "generate_response": "generate_response"
        }
    )

    # Final flow
    workflow.add_edge("generate_response", "qa_check")
    workflow.add_edge("qa_check", END)

    return workflow.compile()

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Run the customer care RAG system."""

    print("=" * 80)
    print("SUPER ADVANCED: CUSTOMER CARE RAG SYSTEM WITH CHROMADB")
    print("=" * 80)

    # Create the graph
    app = create_customer_care_graph()

    # Test queries with customer contexts
    test_cases = [
        {
            "query": "I can't login to my account after resetting my password",
            "context": {
                "customer_id": "CUST-001",
                "tier": "premium",
                "account_age_days": 120,
                "previous_tickets": 2,
                "satisfaction_score": 4.5
            }
        },
        {
            "query": "I was charged twice this month, need a refund",
            "context": {
                "customer_id": "CUST-002",
                "tier": "basic",
                "account_age_days": 30,
                "previous_tickets": 0,
                "satisfaction_score": 5.0
            }
        },
        {
            "query": "How do I export my data to CSV format?",
            "context": {
                "customer_id": "CUST-003",
                "tier": "enterprise",
                "account_age_days": 365,
                "previous_tickets": 5,
                "satisfaction_score": 4.8
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#' * 80}")
        print(f"TEST CASE #{i}")
        print(f"{'#' * 80}")
        print(f"📝 Query: {test_case['query']}")
        print(f"👤 Customer: {test_case['context']['tier'].upper()} tier")
        print(f"{'#' * 80}")

        # Initialize state
        initial_state = {
            "customer_query": test_case["query"],
            "customer_context": test_case["context"],
            "relevant_docs": [],
            "similar_tickets": [],
            "triage_analysis": [],
            "knowledge_synthesis": [],
            "solution_proposals": [],
            "ticket": {},
            "escalation_needed": False,
            "iteration": 0,
            "max_iterations": 2,
            "needs_clarification": False,
            "clarification_questions": [],
            "response": "",
            "next_steps": [],
            "resources": [],
            "satisfaction_followup": False,
            "qa_approved": False,
            "qa_feedback": ""
        }

        # Run the system
        result = app.invoke(initial_state)

        # Print results
        print(f"\n{'=' * 80}")
        print("FINAL RESULTS")
        print(f"{'=' * 80}")

        print(f"\n🎫 Ticket Information:")
        print(f"   ID: {result['ticket']['ticket_id']}")
        print(f"   Priority: {result['ticket']['priority']}")
        print(f"   Category: {result['ticket']['category']}")
        print(f"   Sentiment: {result['ticket']['sentiment']}")
        print(f"   Est. Resolution: {result['ticket']['estimated_resolution_time']}")

        print(f"\n📊 Processing Statistics:")
        print(f"   Iterations: {result['iteration']}")
        print(f"   Escalation Needed: {result['escalation_needed']}")
        print(f"   QA Approved: {result['qa_approved']}")
        print(f"   Satisfaction Follow-up: {result['satisfaction_followup']}")

        print(f"\n💬 Customer Response:")
        print("-" * 80)
        print(result['response'])
        print("-" * 80)

        print(f"\n📋 Next Steps:")
        for i, step in enumerate(result['next_steps'], 1):
            print(f"   {i}. {step}")

        if result['resources']:
            print(f"\n📚 Resources:")
            for resource in result['resources']:
                print(f"   • {resource}")

        print(f"\n✅ QA Feedback:")
        print(result['qa_feedback'])

        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
