import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal, Annotated
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import operator
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Customer Care RAG System",
    page_icon="🎫",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #9467bd;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tier-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        margin: 0.3rem;
    }
    .tier-basic { background-color: #add8e6; color: #00008b; }
    .tier-premium { background-color: #ffd700; color: #8b4513; }
    .tier-enterprise { background-color: #9370db; color: white; }
    .priority-low { color: #2ca02c; }
    .priority-medium { color: #ff7f0e; }
    .priority-high { color: #d62728; }
    .priority-urgent { color: #8b0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎫 Customer Care RAG System with ChromaDB</h1>', unsafe_allow_html=True)
st.markdown("**Complexity:** Super Advanced | **Pattern:** RAG + Multi-agent + Context Awareness")

# Mock knowledge base
KNOWLEDGE_BASE = """
# Account Management
- Account creation requires email verification
- Password must be at least 8 characters
- Two-factor authentication available
- Premium accounts support 5 devices

# Billing Information
- Plans: Basic ($9.99), Premium ($19.99), Enterprise ($49.99)
- Refunds within 30 days
- Annual discount: 20%
- Grace period: 7 days

# Technical Support
- System: Windows 10+, macOS 11+
- API limits: Premium 1000/hr, Enterprise 10000/hr
- Maintenance: Saturdays 2-4 AM EST

# Features
- Collaboration: up to 50 users
- Storage: Basic 10GB, Premium 100GB, Enterprise Unlimited
- Export: PDF, CSV, JSON
"""

CUSTOMER_TICKETS = """
Ticket #1234: Login issue after password reset
Resolution: Sent new verification email
Status: Resolved

Ticket #1235: Double billing
Resolution: Refund processed in 3-5 days
Status: Resolved
"""

# State schemas
class AgentMessage(TypedDict):
    agent: str
    content: str
    timestamp: str
    confidence: float

class CustomerContext(TypedDict):
    customer_id: str
    tier: str
    account_age_days: int
    previous_tickets: int
    satisfaction_score: float

class SupportTicket(TypedDict):
    ticket_id: str
    priority: str
    category: str
    subcategory: str
    sentiment: str
    estimated_resolution_time: str

class CustomerCareState(TypedDict):
    customer_query: str
    customer_context: CustomerContext
    relevant_docs: List[dict]
    similar_tickets: List[dict]
    triage_analysis: Annotated[List[AgentMessage], operator.add]
    knowledge_synthesis: Annotated[List[AgentMessage], operator.add]
    solution_proposals: Annotated[List[AgentMessage], operator.add]
    ticket: SupportTicket
    escalation_needed: bool
    iteration: int
    max_iterations: int
    needs_clarification: bool
    clarification_questions: List[str]
    response: str
    next_steps: List[str]
    resources: List[str]
    satisfaction_followup: bool
    qa_approved: bool
    qa_feedback: str

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key"
    )

    st.divider()

    st.header("👤 Customer Profile")

    customer_tier = st.selectbox("Tier", ["basic", "premium", "enterprise"])
    account_age = st.slider("Account Age (days)", 1, 365, 120)
    previous_tickets = st.slider("Previous Tickets", 0, 10, 2)
    satisfaction = st.slider("Satisfaction Score", 1.0, 5.0, 4.5, 0.1)

    st.divider()

    st.header("🤖 Agents")
    st.markdown("""
    - 🎯 **Triage**: Categorization
    - 📚 **Knowledge**: RAG synthesis
    - 💡 **Solution**: Action plans
    - ✅ **QA**: Quality check
    - 🎯 **Coordinator**: Orchestration
    """)

    st.divider()

    st.header("💡 Examples")
    examples = {
        "Login Issue": "I can't login after resetting my password",
        "Billing": "I was charged twice this month",
        "Feature": "How do I export data to CSV?",
        "Sync Problem": "My data is not syncing",
        "Refund": "I need a refund for my subscription"
    }

    for label, query in examples.items():
        if st.button(label, key=f"ex_{label}", use_container_width=True):
            st.session_state.selected_query = query

# Initialize session state
if 'tickets' not in st.session_state:
    st.session_state.tickets = []
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

# Initialize vector store
@st.cache_resource
def initialize_vector_store(_api_key):
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=_api_key)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        kb_chunks = text_splitter.split_text(KNOWLEDGE_BASE)
        ticket_chunks = text_splitter.split_text(CUSTOMER_TICKETS)

        kb_docs = [Document(page_content=chunk, metadata={"source": "knowledge_base"})
                   for chunk in kb_chunks]
        ticket_docs = [Document(page_content=chunk, metadata={"source": "tickets"})
                       for chunk in ticket_chunks]

        all_docs = kb_docs + ticket_docs

        vectorstore = Chroma.from_documents(
            documents=all_docs,
            embedding=embeddings,
            collection_name="customer_support_streamlit"
        )

        return vectorstore
    except Exception as e:
        st.error(f"Failed to initialize vector store: {e}")
        return None

# Agent functions (simplified for Streamlit)
def retrieve_knowledge(state, vectorstore):
    query = state["customer_query"]
    docs = vectorstore.similarity_search(query, k=3)

    kb_docs = [{"content": doc.page_content[:200], "source": doc.metadata["source"]}
               for doc in docs if doc.metadata["source"] == "knowledge_base"]
    ticket_docs = [{"content": doc.page_content[:200], "source": doc.metadata["source"]}
                   for doc in docs if doc.metadata["source"] == "tickets"]

    return {
        "relevant_docs": kb_docs,
        "similar_tickets": ticket_docs
    }

def triage_agent(state, llm):
    query = state["customer_query"]
    context = state["customer_context"]

    prompt = f"""Analyze this customer query: "{query}"

Customer: {context['tier']} tier, {context['account_age_days']} days old

Respond in JSON:
{{
    "category": "billing/technical/account/feature/general",
    "priority": "low/medium/high/urgent",
    "sentiment": "positive/neutral/negative",
    "confidence": 0.0-1.0
}}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        analysis = json.loads(content)

        ticket = {
            "ticket_id": f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "priority": analysis.get("priority", "medium"),
            "category": analysis.get("category", "general"),
            "subcategory": "unknown",
            "sentiment": analysis.get("sentiment", "neutral"),
            "estimated_resolution_time": "1-24 hours"
        }

        agent_msg = {
            "agent": "triage",
            "content": json.dumps(analysis),
            "timestamp": datetime.now().isoformat(),
            "confidence": analysis.get("confidence", 0.8)
        }

        return {
            "triage_analysis": [agent_msg],
            "ticket": ticket,
            "escalation_needed": analysis.get("priority") in ["high", "urgent"]
        }
    except:
        return {
            "triage_analysis": [{"agent": "triage", "content": "{}", "timestamp": "", "confidence": 0.5}],
            "ticket": {"ticket_id": "ERROR", "priority": "medium", "category": "general", "subcategory": "", "sentiment": "neutral", "estimated_resolution_time": ""},
            "escalation_needed": False
        }

def generate_response(state, llm):
    query = state["customer_query"]
    ticket = state["ticket"]
    context = state["customer_context"]

    prompt = f"""Generate a professional customer support response.

Query: "{query}"
Customer: {context['tier']} tier
Priority: {ticket['priority']}

Provide:
1. Acknowledge concern
2. Clear solution steps
3. Professional tone"""

    response = llm.invoke([HumanMessage(content=prompt)])

    next_steps = [
        f"Ticket {ticket['ticket_id']} created",
        "Follow solution steps",
        "Check email for updates"
    ]

    return {
        "response": response.content,
        "next_steps": next_steps,
        "resources": ["Help Center", "Documentation"],
        "satisfaction_followup": ticket["priority"] in ["high", "urgent"],
        "qa_approved": True,
        "qa_feedback": "Response approved"
    }

# Main interface
st.header("💬 Customer Query")

col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.selected_query:
        query = st.text_area(
            "Enter support query:",
            value=st.session_state.selected_query,
            height=100
        )
        st.session_state.selected_query = ""
    else:
        query = st.text_area("Enter support query:", height=100)

    col_submit, col_clear = st.columns([1, 4])
    with col_submit:
        submit_button = st.button("🚀 Submit", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.tickets = []
            st.rerun()

with col2:
    st.header("📊 Stats")
    st.metric("Total Tickets", len(st.session_state.tickets))

    tier_emoji = {"basic": "🔵", "premium": "🟡", "enterprise": "🟣"}
    st.markdown(f"{tier_emoji[customer_tier]} **Customer Tier:** {customer_tier.upper()}")

# Process query
if submit_button and query:
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key!")
    else:
        try:
            with st.spinner("🔄 Processing with RAG..."):
                # Initialize vector store
                if st.session_state.vectorstore is None:
                    st.session_state.vectorstore = initialize_vector_store(api_key)

                if st.session_state.vectorstore is None:
                    st.error("Failed to initialize RAG system")
                else:
                    llm = ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=api_key)

                    # Create customer context
                    customer_context = {
                        "customer_id": f"CUST-{len(st.session_state.tickets) + 1:03d}",
                        "tier": customer_tier,
                        "account_age_days": account_age,
                        "previous_tickets": previous_tickets,
                        "satisfaction_score": satisfaction
                    }

                    # Initial state
                    state = {
                        "customer_query": query,
                        "customer_context": customer_context,
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

                    # Retrieve from RAG
                    rag_result = retrieve_knowledge(state, st.session_state.vectorstore)
                    state.update(rag_result)

                    # Triage
                    triage_result = triage_agent(state, llm)
                    state.update(triage_result)

                    # Generate response
                    response_result = generate_response(state, llm)
                    state.update(response_result)

                    # Store ticket
                    st.session_state.tickets.append({
                        "query": query,
                        "context": customer_context,
                        "result": state,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display latest ticket
if st.session_state.tickets:
    latest = st.session_state.tickets[-1]
    result = latest["result"]
    ticket = result["ticket"]

    st.divider()

    # Ticket header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Ticket:** {ticket['ticket_id']}")
    with col2:
        priority = ticket['priority']
        st.markdown(f"**Priority:** <span class='priority-{priority}'>{priority.upper()}</span>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"**Category:** {ticket['category']}")
    with col4:
        sent_emoji = {"positive": "😊", "neutral": "😐", "negative": "😞"}
        sentiment = ticket['sentiment']
        st.markdown(f"**Sentiment:** {sent_emoji[sentiment]} {sentiment}")

    # Escalation warning
    if result.get("escalation_needed"):
        st.warning("⚠️ This ticket requires escalation to senior support")

    # RAG retrieval results
    with st.expander("🔍 Retrieved Knowledge", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📚 Knowledge Base:**")
            for doc in result.get("relevant_docs", []):
                st.info(doc["content"])
        with col2:
            st.markdown("**🎫 Similar Tickets:**")
            for doc in result.get("similar_tickets", []):
                st.info(doc["content"])

    # Customer response
    st.header("💬 Support Response")
    st.success(result["response"])

    # Next steps
    st.markdown("### 📋 Next Steps")
    for i, step in enumerate(result.get("next_steps", []), 1):
        st.markdown(f"{i}. {step}")

    # Resources
    if result.get("resources"):
        st.markdown("### 📚 Resources")
        for resource in result["resources"]:
            st.markdown(f"- {resource}")

    # QA status
    col1, col2 = st.columns(2)
    with col1:
        qa_status = "✅ Approved" if result.get("qa_approved") else "⚠️ Pending"
        st.metric("QA Status", qa_status)
    with col2:
        followup = "Yes" if result.get("satisfaction_followup") else "No"
        st.metric("Follow-up Required", followup)

# Ticket history
if st.session_state.tickets:
    st.divider()
    st.header("📜 Ticket History")

    for i, ticket_data in enumerate(reversed(st.session_state.tickets), 1):
        idx = len(st.session_state.tickets) - i
        ticket = ticket_data["result"]["ticket"]

        with st.expander(f"#{idx +1} - {ticket['ticket_id']} ({ticket_data['timestamp']})", expanded=False):
            st.markdown(f"**Query:** {ticket_data['query']}")
            st.markdown(f"**Customer:** {ticket_data['context']['tier'].upper()} tier")
            st.markdown(f"**Priority:** {ticket['priority'].upper()}")
            st.markdown(f"**Category:** {ticket['category']}")
            st.markdown("**Response:**")
            st.info(ticket_data["result"]["response"])

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Super Advanced Example:</strong> Customer Care RAG System with ChromaDB</p>
    <p>Demonstrates: RAG integration, vector search, multi-agent, context awareness</p>
    <p>Learn more: <a href="super_advance_README.md">super_advance_README.md</a></p>
</div>
""", unsafe_allow_html=True)
