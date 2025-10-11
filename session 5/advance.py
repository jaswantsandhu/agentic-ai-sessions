from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator
import json

# ============================================================================
# STATE SCHEMAS
# ============================================================================

class AgentFeedback(TypedDict):
    """Feedback from a single agent."""
    agent_name: str
    issues: List[str]
    suggestions: List[str]
    severity: str  # low, medium, high, critical
    confidence: float  # 0-1

class CodeReviewState(TypedDict):
    """Main state for the code review system."""
    code: str                                    # Code to review
    language: str                                # Programming language
    
    # Agent feedback - using Annotated with operator.add to accumulate
    analyzer_feedback: Annotated[List[AgentFeedback], operator.add]
    architect_feedback: Annotated[List[AgentFeedback], operator.add]
    security_feedback: Annotated[List[AgentFeedback], operator.add]
    
    # Reflection and iteration
    iteration: int
    max_iterations: int
    needs_refinement: bool
    
    # Coordinator decisions
    priority_issues: List[dict]
    consensus_reached: bool
    conflicting_opinions: List[dict]
    
    # Final output
    final_report: str
    recommended_changes: List[str]
    approval_status: str  # pending, approved, needs_revision
    
    # Human-in-the-loop
    human_feedback: str

# ============================================================================
# INITIALIZE LLMS FOR EACH AGENT
# ============================================================================

# Each agent gets a specialized system prompt
def create_agent_llm(agent_type: str) -> ChatOpenAI:
    """Create specialized LLM for each agent type."""

    system_prompts = {
        "analyzer": """You are a Code Analyzer Agent. Your expertise:
- Identifying bugs and logical errors
- Code quality and best practices
- Performance issues
- Code smells and anti-patterns
Focus on correctness and efficiency.""",

        "architect": """You are a Software Architect Agent. Your expertise:
- System design and architecture patterns
- Code structure and organization
- Modularity and separation of concerns
- Scalability considerations
- SOLID principles
Focus on design quality and maintainability.""",

        "security": """You are a Security Expert Agent. Your expertise:
- Security vulnerabilities (SQL injection, XSS, etc.)
- Authentication and authorization issues
- Data validation and sanitization
- Cryptographic best practices
- Dependency vulnerabilities
Focus on security risks and compliance.""",

        "coordinator": """You are a Coordinator Agent. Your role:
- Synthesize feedback from all agents
- Identify conflicts and consensus
- Prioritize issues by severity
- Make final recommendations
- Facilitate agent discussions
Focus on holistic decision-making."""
    }

    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2
    )

# Create agent instances
analyzer_llm = create_agent_llm("analyzer")
architect_llm = create_agent_llm("architect")
security_llm = create_agent_llm("security")
coordinator_llm = create_agent_llm("coordinator")

# ============================================================================
# AGENT NODES
# ============================================================================

def analyzer_agent(state: CodeReviewState) -> CodeReviewState:
    """Analyze code for bugs, performance, and quality issues."""
    
    print("\n🔍 ANALYZER AGENT analyzing code...")
    
    code = state["code"]
    language = state["language"]
    iteration = state["iteration"]
    
    prompt = f"""Analyze this {language} code for issues:

```{language}
{code}
```

Identify:
1. Bugs or logical errors
2. Performance bottlenecks
3. Code quality issues
4. Best practice violations

Respond in JSON format:
{{
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["fix 1", "fix 2"],
    "severity": "low/medium/high/critical",
    "confidence": 0.0-1.0
}}"""

    response = analyzer_llm.invoke([HumanMessage(content=prompt)])
    
    try:
        # Parse response
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        feedback = json.loads(content)
        feedback["agent_name"] = "analyzer"
        
        print(f"   Found {len(feedback.get('issues', []))} issues")
        print(f"   Severity: {feedback.get('severity', 'unknown')}")
        
        return {
            "analyzer_feedback": [feedback]
        }
        
    except Exception as e:
        print(f"   ⚠️ Error parsing feedback: {e}")
        return {
            "analyzer_feedback": [{
                "agent_name": "analyzer",
                "issues": ["Error analyzing code"],
                "suggestions": [],
                "severity": "low",
                "confidence": 0.5
            }]
        }

def architect_agent(state: CodeReviewState) -> CodeReviewState:
    """Review code architecture and design patterns."""
    
    print("\n🏗️ ARCHITECT AGENT reviewing design...")
    
    code = state["code"]
    language = state["language"]
    
    prompt = f"""Review the architecture and design of this {language} code:

```{language}
{code}
```

Evaluate:
1. Design patterns and architecture
2. Code structure and organization
3. Modularity and coupling
4. Scalability considerations
5. SOLID principles adherence

Respond in JSON format:
{{
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["improvement 1", "improvement 2"],
    "severity": "low/medium/high/critical",
    "confidence": 0.0-1.0
}}"""

    response = architect_llm.invoke([HumanMessage(content=prompt)])
    
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        feedback = json.loads(content)
        feedback["agent_name"] = "architect"
        
        print(f"   Found {len(feedback.get('issues', []))} design issues")
        print(f"   Severity: {feedback.get('severity', 'unknown')}")
        
        return {
            "architect_feedback": [feedback]
        }
        
    except Exception as e:
        print(f"   ⚠️ Error parsing feedback: {e}")
        return {
            "architect_feedback": [{
                "agent_name": "architect",
                "issues": ["Error reviewing architecture"],
                "suggestions": [],
                "severity": "low",
                "confidence": 0.5
            }]
        }

def security_agent(state: CodeReviewState) -> CodeReviewState:
    """Analyze code for security vulnerabilities."""
    
    print("\n🔒 SECURITY AGENT checking for vulnerabilities...")
    
    code = state["code"]
    language = state["language"]
    
    prompt = f"""Perform a security review of this {language} code:

```{language}
{code}
```

Check for:
1. Common vulnerabilities (SQL injection, XSS, etc.)
2. Authentication/authorization issues
3. Input validation problems
4. Cryptographic weaknesses
5. Sensitive data exposure

Respond in JSON format:
{{
    "issues": ["vulnerability 1", "vulnerability 2"],
    "suggestions": ["fix 1", "fix 2"],
    "severity": "low/medium/high/critical",
    "confidence": 0.0-1.0
}}"""

    response = security_llm.invoke([HumanMessage(content=prompt)])
    
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        feedback = json.loads(content)
        feedback["agent_name"] = "security"
        
        print(f"   Found {len(feedback.get('issues', []))} security issues")
        print(f"   Severity: {feedback.get('severity', 'unknown')}")
        
        return {
            "security_feedback": [feedback]
        }
        
    except Exception as e:
        print(f"   ⚠️ Error parsing feedback: {e}")
        return {
            "security_feedback": [{
                "agent_name": "security",
                "issues": ["Error checking security"],
                "suggestions": [],
                "severity": "low",
                "confidence": 0.5
            }]
        }

# ============================================================================
# COORDINATOR AND REFLECTION NODES
# ============================================================================

def coordinator_synthesize(state: CodeReviewState) -> CodeReviewState:
    """Coordinator synthesizes all agent feedback."""
    
    print("\n🎯 COORDINATOR synthesizing feedback...")
    
    analyzer_feedback = state.get("analyzer_feedback", [])
    architect_feedback = state.get("architect_feedback", [])
    security_feedback = state.get("security_feedback", [])
    
    all_feedback = {
        "analyzer": analyzer_feedback,
        "architect": architect_feedback,
        "security": security_feedback
    }
    
    prompt = f"""You are coordinating a code review. Here's feedback from all agents:

{json.dumps(all_feedback, indent=2)}

Analyze and synthesize:
1. Identify the most critical issues across all agents
2. Find any conflicting opinions between agents
3. Determine if agents reached consensus on major issues
4. Assess if another review iteration would be valuable

Respond in JSON format:
{{
    "priority_issues": [
        {{"issue": "...", "severity": "...", "agents": ["..."]}},
    ],
    "conflicts": [
        {{"issue": "...", "agent1": "...", "agent2": "...", "description": "..."}}
    ],
    "consensus_reached": true/false,
    "needs_refinement": true/false,
    "reasoning": "explanation"
}}"""

    response = coordinator_llm.invoke([HumanMessage(content=prompt)])
    
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        synthesis = json.loads(content)
        
        priority_issues = synthesis.get("priority_issues", [])
        conflicts = synthesis.get("conflicts", [])
        consensus = synthesis.get("consensus_reached", True)
        needs_refinement = synthesis.get("needs_refinement", False)
        
        print(f"   Priority Issues: {len(priority_issues)}")
        print(f"   Conflicts: {len(conflicts)}")
        print(f"   Consensus: {consensus}")
        print(f"   Needs Refinement: {needs_refinement}")
        
        # Check iteration limit
        iteration = state["iteration"] + 1
        max_iterations = state["max_iterations"]
        
        if iteration >= max_iterations:
            needs_refinement = False
            print(f"   ⚠️ Max iterations reached ({max_iterations})")
        
        return {
            "priority_issues": priority_issues,
            "conflicting_opinions": conflicts,
            "consensus_reached": consensus,
            "needs_refinement": needs_refinement,
            "iteration": iteration
        }
        
    except Exception as e:
        print(f"   ⚠️ Error synthesizing: {e}")
        return {
            "priority_issues": [],
            "conflicting_opinions": [],
            "consensus_reached": True,
            "needs_refinement": False,
            "iteration": state["iteration"] + 1
        }

def reflection_node(state: CodeReviewState) -> CodeReviewState:
    """Agents reflect on conflicting feedback and refine opinions."""
    
    print("\n💭 REFLECTION: Agents discussing conflicts...")
    
    conflicts = state.get("conflicting_opinions", [])
    
    if not conflicts:
        print("   No conflicts to resolve")
        return {"needs_refinement": False}
    
    # In a real system, this would facilitate agent-to-agent discussion
    print(f"   Resolving {len(conflicts)} conflicts...")
    
    for i, conflict in enumerate(conflicts[:2], 1):  # Limit to 2 for demo
        print(f"   Conflict {i}: {conflict.get('issue', 'Unknown')}")
    
    # Reset feedback for new round (in production, you'd do selective refinement)
    return {
        "analyzer_feedback": [],
        "architect_feedback": [],
        "security_feedback": [],
        "needs_refinement": True
    }

def generate_final_report(state: CodeReviewState) -> CodeReviewState:
    """Generate comprehensive final report."""
    
    print("\n📝 COORDINATOR generating final report...")
    
    priority_issues = state.get("priority_issues", [])
    all_feedback = {
        "analyzer": state.get("analyzer_feedback", []),
        "architect": state.get("architect_feedback", []),
        "security": state.get("security_feedback", [])
    }
    
    prompt = f"""Create a comprehensive code review report.

Priority Issues:
{json.dumps(priority_issues, indent=2)}

All Agent Feedback:
{json.dumps(all_feedback, indent=2)}

Generate a professional report with:
1. Executive Summary
2. Critical Issues (with severity)
3. Recommended Changes (prioritized)
4. Overall Assessment
5. Approval Status (approved/needs_revision)

Format as a clear, structured report."""

    response = coordinator_llm.invoke([HumanMessage(content=prompt)])
    
    # Determine approval status
    has_critical = any(
        issue.get("severity") == "critical"
        for issue in priority_issues
    )
    
    has_high = any(
        issue.get("severity") in ["high", "critical"]
        for issue in priority_issues
    )
    
    if has_critical:
        approval = "needs_revision"
    elif has_high:
        approval = "conditional_approval"
    else:
        approval = "approved"
    
    # Extract recommended changes
    recommended_changes = [
        issue.get("issue", "")
        for issue in priority_issues[:5]  # Top 5
    ]
    
    print(f"   Approval Status: {approval}")
    print(f"   Recommended Changes: {len(recommended_changes)}")
    
    return {
        "final_report": response.content,
        "recommended_changes": recommended_changes,
        "approval_status": approval,
        "needs_refinement": False
    }

def human_review_checkpoint(state: CodeReviewState) -> CodeReviewState:
    """Simulate human-in-the-loop review checkpoint."""
    
    print("\n👤 HUMAN REVIEW CHECKPOINT")
    print("   (In production, this would pause for human input)")
    
    approval = state.get("approval_status", "pending")
    print(f"   Current Status: {approval}")
    
    # Simulate automatic approval for demo
    # In production: from langgraph.checkpoint import interrupt
    # human_input = interrupt("Review the report and provide feedback")
    
    simulated_feedback = "Looks good, approved for deployment"
    print(f"   Simulated Feedback: {simulated_feedback}")
    
    return {
        "human_feedback": simulated_feedback
    }

# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

def should_refine(state: CodeReviewState) -> Literal["refine", "report"]:
    """Decide whether to do another iteration or generate final report."""
    if state.get("needs_refinement", False):
        return "refine"
    return "report"

# ============================================================================
# BUILD THE GRAPH
# ============================================================================

def create_code_review_graph():
    """Create the multi-agent code review system graph."""
    
    workflow = StateGraph(CodeReviewState)
    
    # Add agent nodes (these can run in parallel)
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("architect", architect_agent)
    workflow.add_node("security", security_agent)
    
    # Add coordinator and control nodes
    workflow.add_node("coordinator", coordinator_synthesize)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("report", generate_final_report)
    workflow.add_node("human_review", human_review_checkpoint)
    
    # Entry: Run all three agents in parallel (conceptually)
    # LangGraph will execute them sequentially, but they're independent
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "architect")
    workflow.add_edge("architect", "security")
    
    # After all agents run, coordinator synthesizes
    workflow.add_edge("security", "coordinator")
    
    # Conditional: refine or generate report
    workflow.add_conditional_edges(
        "coordinator",
        should_refine,
        {
            "refine": "reflection",    # Loop back for refinement
            "report": "report"         # Move to final report
        }
    )
    
    # Reflection loops back to agents
    workflow.add_edge("reflection", "analyzer")
    
    # Final report goes to human review
    workflow.add_edge("report", "human_review")
    
    # Human review ends the process
    workflow.add_edge("human_review", END)
    
    return workflow.compile()

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Run the multi-agent code review system."""
    
    print("=" * 70)
    print("MULTI-AGENT CODE REVIEW SYSTEM")
    print("=" * 70)
    
    # Create the graph
    app = create_code_review_graph()
    
    # Example code to review
    example_code = '''
def process_user_input(user_id, password):
    # Connect to database
    conn = mysql.connect(host="localhost", user="root", password="")
    cursor = conn.cursor()
    
    # Check user credentials
    query = "SELECT * FROM users WHERE id = '" + user_id + "' AND password = '" + password + "'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    
    if user:
        # Store password in session
        session['password'] = password
        return True
    return False
'''
    
    print("\n📄 CODE TO REVIEW:")
    print("-" * 70)
    print(example_code)
    print("-" * 70)
    
    # Initialize state
    initial_state = {
        "code": example_code,
        "language": "python",
        "analyzer_feedback": [],
        "architect_feedback": [],
        "security_feedback": [],
        "iteration": 0,
        "max_iterations": 2,
        "needs_refinement": False,
        "priority_issues": [],
        "consensus_reached": False,
        "conflicting_opinions": [],
        "final_report": "",
        "recommended_changes": [],
        "approval_status": "pending",
        "human_feedback": ""
    }
    
    # Run the review process
    result = app.invoke(initial_state)
    
    # Print results
    print("\n" + "=" * 70)
    print("FINAL REVIEW RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Statistics:")
    print(f"   Total Iterations: {result['iteration']}")
    print(f"   Approval Status: {result['approval_status']}")
    print(f"   Priority Issues: {len(result['priority_issues'])}")
    
    print(f"\n📝 Final Report:")
    print("-" * 70)
    print(result['final_report'])
    
    print(f"\n🔧 Top Recommended Changes:")
    for i, change in enumerate(result['recommended_changes'][:5], 1):
        print(f"   {i}. {change}")
    
    print(f"\n👤 Human Feedback: {result['human_feedback']}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()