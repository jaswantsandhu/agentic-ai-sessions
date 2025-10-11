import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import operator
import json
import os

# Page config
st.set_page_config(
    page_title="Multi-Agent Code Review System",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #d62728;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .severity-critical { color: #d62728; font-weight: bold; }
    .severity-high { color: #ff7f0e; font-weight: bold; }
    .severity-medium { color: #ffbb00; font-weight: bold; }
    .severity-low { color: #2ca02c; font-weight: bold; }
    .code-container {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔒 Multi-Agent Code Review System</h1>', unsafe_allow_html=True)
st.markdown("**Complexity:** Advanced | **Pattern:** Multi-agent collaboration with consensus")

# State schemas
class AgentFeedback(TypedDict):
    agent_name: str
    issues: List[str]
    suggestions: List[str]
    severity: str
    confidence: float

class CodeReviewState(TypedDict):
    code: str
    language: str
    analyzer_feedback: Annotated[List[AgentFeedback], operator.add]
    architect_feedback: Annotated[List[AgentFeedback], operator.add]
    security_feedback: Annotated[List[AgentFeedback], operator.add]
    iteration: int
    max_iterations: int
    needs_refinement: bool
    priority_issues: List[dict]
    consensus_reached: bool
    conflicting_opinions: List[dict]
    final_report: str
    recommended_changes: List[str]
    approval_status: str

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key"
    )

    max_iterations = st.slider("Max Iterations", 1, 3, 2)

    st.divider()

    st.header("👥 Review Agents")
    st.markdown("""
    <div class="agent-card">
        <strong>🔍 Analyzer Agent</strong><br>
        Bugs, performance, code quality
    </div>
    <div class="agent-card">
        <strong>🏗️ Architect Agent</strong><br>
        Design patterns, SOLID principles
    </div>
    <div class="agent-card">
        <strong>🔒 Security Agent</strong><br>
        Vulnerabilities, best practices
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.header("💡 Example Code")
    examples = {
        "SQL Injection": '''def login(user_id, password):
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)''',
        "Poor Design": '''def process(data):
    if data['type'] == 'A':
        # 100 lines of code
    elif data['type'] == 'B':
        # 100 lines of code''',
        "Memory Leak": '''class DataCache:
    def __init__(self):
        self.cache = []
    def add(self, item):
        self.cache.append(item)'''
    }

    for label, code in examples.items():
        if st.button(label, key=f"ex_{label}", use_container_width=True):
            st.session_state.example_code = code

# Initialize session state
if 'review_history' not in st.session_state:
    st.session_state.review_history = []
if 'example_code' not in st.session_state:
    st.session_state.example_code = ""

# Agent functions
def create_agent_llm(api_key):
    return ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=api_key)

def analyzer_agent(state: CodeReviewState, llm) -> dict:
    code = state["code"]
    language = state["language"]

    prompt = f"""Analyze this {language} code for issues:

```{language}
{code}
```

Identify: bugs, logical errors, performance issues, code quality problems.

Respond in JSON:
{{
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["fix 1", "fix 2"],
    "severity": "low/medium/high/critical",
    "confidence": 0.0-1.0
}}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        feedback = json.loads(content)
        feedback["agent_name"] = "analyzer"
        return {"analyzer_feedback": [feedback]}
    except:
        return {"analyzer_feedback": [{"agent_name": "analyzer", "issues": ["Error analyzing"], "suggestions": [], "severity": "low", "confidence": 0.5}]}

def architect_agent(state: CodeReviewState, llm) -> dict:
    code = state["code"]
    language = state["language"]

    prompt = f"""Review architecture and design of this {language} code:

```{language}
{code}
```

Evaluate: design patterns, structure, modularity, SOLID principles.

Respond in JSON:
{{
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["improvement 1", "improvement 2"],
    "severity": "low/medium/high/critical",
    "confidence": 0.0-1.0
}}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        feedback = json.loads(content)
        feedback["agent_name"] = "architect"
        return {"architect_feedback": [feedback]}
    except:
        return {"architect_feedback": [{"agent_name": "architect", "issues": ["Error analyzing"], "suggestions": [], "severity": "low", "confidence": 0.5}]}

def security_agent(state: CodeReviewState, llm) -> dict:
    code = state["code"]
    language = state["language"]

    prompt = f"""Security review of this {language} code:

```{language}
{code}
```

Check: vulnerabilities (SQL injection, XSS), auth issues, input validation.

Respond in JSON:
{{
    "issues": ["vulnerability 1", "vulnerability 2"],
    "suggestions": ["fix 1", "fix 2"],
    "severity": "low/medium/high/critical",
    "confidence": 0.0-1.0
}}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        feedback = json.loads(content)
        feedback["agent_name"] = "security"
        return {"security_feedback": [feedback]}
    except:
        return {"security_feedback": [{"agent_name": "security", "issues": ["Error analyzing"], "suggestions": [], "severity": "low", "confidence": 0.5}]}

def coordinator_synthesize(state: CodeReviewState, llm) -> dict:
    analyzer_feedback = state.get("analyzer_feedback", [])
    architect_feedback = state.get("architect_feedback", [])
    security_feedback = state.get("security_feedback", [])

    all_feedback = {
        "analyzer": analyzer_feedback,
        "architect": architect_feedback,
        "security": security_feedback
    }

    prompt = f"""Coordinate code review feedback:

{json.dumps(all_feedback, indent=2)}

Analyze and synthesize:
1. Critical issues across agents
2. Conflicting opinions
3. Consensus on major issues
4. Need for refinement

Respond in JSON:
{{
    "priority_issues": [{{"issue": "...", "severity": "...", "agents": ["..."]}}],
    "conflicts": [],
    "consensus_reached": true/false,
    "needs_refinement": true/false,
    "reasoning": "explanation"
}}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        synthesis = json.loads(content)

        iteration = state["iteration"] + 1
        needs_refinement = synthesis.get("needs_refinement", False) and iteration < state["max_iterations"]

        return {
            "priority_issues": synthesis.get("priority_issues", []),
            "conflicting_opinions": synthesis.get("conflicts", []),
            "consensus_reached": synthesis.get("consensus_reached", True),
            "needs_refinement": needs_refinement,
            "iteration": iteration
        }
    except:
        return {
            "priority_issues": [],
            "conflicting_opinions": [],
            "consensus_reached": True,
            "needs_refinement": False,
            "iteration": state["iteration"] + 1
        }

def generate_final_report(state: CodeReviewState, llm) -> dict:
    priority_issues = state.get("priority_issues", [])
    all_feedback = {
        "analyzer": state.get("analyzer_feedback", []),
        "architect": state.get("architect_feedback", []),
        "security": state.get("security_feedback", [])
    }

    prompt = f"""Create comprehensive code review report.

Priority Issues:
{json.dumps(priority_issues, indent=2)}

All Feedback:
{json.dumps(all_feedback, indent=2)}

Generate report with:
1. Executive Summary
2. Critical Issues
3. Recommended Changes
4. Overall Assessment
5. Approval Status"""

    response = llm.invoke([HumanMessage(content=prompt)])

    has_critical = any(issue.get("severity") == "critical" for issue in priority_issues)
    has_high = any(issue.get("severity") in ["high", "critical"] for issue in priority_issues)

    if has_critical:
        approval = "needs_revision"
    elif has_high:
        approval = "conditional_approval"
    else:
        approval = "approved"

    recommended_changes = [issue.get("issue", "") for issue in priority_issues[:5]]

    return {
        "final_report": response.content,
        "recommended_changes": recommended_changes,
        "approval_status": approval,
        "needs_refinement": False
    }

def should_refine(state: CodeReviewState) -> Literal["refine", "report"]:
    return "refine" if state.get("needs_refinement", False) else "report"

def create_code_review_graph(llm):
    workflow = StateGraph(CodeReviewState)

    workflow.add_node("analyzer", lambda s: analyzer_agent(s, llm))
    workflow.add_node("architect", lambda s: architect_agent(s, llm))
    workflow.add_node("security", lambda s: security_agent(s, llm))
    workflow.add_node("coordinator", lambda s: coordinator_synthesize(s, llm))
    workflow.add_node("report", lambda s: generate_final_report(s, llm))

    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "architect")
    workflow.add_edge("architect", "security")
    workflow.add_edge("security", "coordinator")

    workflow.add_conditional_edges(
        "coordinator",
        should_refine,
        {"refine": "analyzer", "report": "report"}
    )

    workflow.add_edge("report", END)

    return workflow.compile()

# Main interface
st.header("💻 Code to Review")

col1, col2 = st.columns([3, 1])

with col1:
    language = st.selectbox("Language", ["python", "javascript", "java", "go", "rust"])

    if st.session_state.example_code:
        code = st.text_area("Enter code:", value=st.session_state.example_code, height=200)
        st.session_state.example_code = ""
    else:
        code = st.text_area("Enter code:", height=200, placeholder="Paste your code here...")

    col_submit, col_clear = st.columns([1, 4])
    with col_submit:
        review_button = st.button("🔍 Review Code", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.review_history = []
            st.rerun()

with col2:
    st.header("📊 Stats")
    st.metric("Reviews", len(st.session_state.review_history))

# Process review
if review_button and code:
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key!")
    else:
        try:
            with st.spinner("🔄 Reviewing code..."):
                llm = create_agent_llm(api_key)
                app = create_code_review_graph(llm)

                initial_state = {
                    "code": code,
                    "language": language,
                    "analyzer_feedback": [],
                    "architect_feedback": [],
                    "security_feedback": [],
                    "iteration": 0,
                    "max_iterations": max_iterations,
                    "needs_refinement": False,
                    "priority_issues": [],
                    "consensus_reached": False,
                    "conflicting_opinions": [],
                    "final_report": "",
                    "recommended_changes": [],
                    "approval_status": "pending"
                }

                result = app.invoke(initial_state)

                st.session_state.review_history.append({
                    "code": code,
                    "language": language,
                    "result": result
                })

                st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display latest review
if st.session_state.review_history:
    latest = st.session_state.review_history[-1]
    result = latest["result"]

    st.divider()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Iterations", result["iteration"])
    with col2:
        st.metric("Priority Issues", len(result["priority_issues"]))
    with col3:
        approval = result["approval_status"].replace("_", " ").title()
        st.metric("Status", approval)
    with col4:
        consensus = "✅ Yes" if result["consensus_reached"] else "❌ No"
        st.metric("Consensus", consensus)

    # Approval status
    status_colors = {
        "approved": "success",
        "conditional_approval": "warning",
        "needs_revision": "error"
    }
    status_color = status_colors.get(result["approval_status"], "info")
    if status_color == "success":
        st.success(f"✅ Code Status: {approval}")
    elif status_color == "warning":
        st.warning(f"⚠️ Code Status: {approval}")
    else:
        st.error(f"❌ Code Status: {approval}")

    # Agent Feedback Tabs
    tabs = st.tabs(["🔍 Analyzer", "🏗️ Architect", "🔒 Security", "📝 Final Report"])

    with tabs[0]:
        for feedback in result.get("analyzer_feedback", []):
            st.markdown(f"**Severity:** <span class='severity-{feedback['severity']}'>{feedback['severity'].upper()}</span>", unsafe_allow_html=True)
            st.markdown(f"**Confidence:** {feedback['confidence']:.0%}")
            st.markdown("**Issues:**")
            for issue in feedback.get("issues", []):
                st.markdown(f"- {issue}")
            st.markdown("**Suggestions:**")
            for suggestion in feedback.get("suggestions", []):
                st.markdown(f"- {suggestion}")

    with tabs[1]:
        for feedback in result.get("architect_feedback", []):
            st.markdown(f"**Severity:** <span class='severity-{feedback['severity']}'>{feedback['severity'].upper()}</span>", unsafe_allow_html=True)
            st.markdown(f"**Confidence:** {feedback['confidence']:.0%}")
            st.markdown("**Issues:**")
            for issue in feedback.get("issues", []):
                st.markdown(f"- {issue}")
            st.markdown("**Suggestions:**")
            for suggestion in feedback.get("suggestions", []):
                st.markdown(f"- {suggestion}")

    with tabs[2]:
        for feedback in result.get("security_feedback", []):
            st.markdown(f"**Severity:** <span class='severity-{feedback['severity']}'>{feedback['severity'].upper()}</span>", unsafe_allow_html=True)
            st.markdown(f"**Confidence:** {feedback['confidence']:.0%}")
            st.markdown("**Issues:**")
            for issue in feedback.get("issues", []):
                st.markdown(f"- {issue}")
            st.markdown("**Suggestions:**")
            for suggestion in feedback.get("suggestions", []):
                st.markdown(f"- {suggestion}")

    with tabs[3]:
        st.markdown(result["final_report"])

        if result["recommended_changes"]:
            st.markdown("### 🔧 Top Recommended Changes")
            for i, change in enumerate(result["recommended_changes"], 1):
                st.markdown(f"{i}. {change}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Advanced Example:</strong> Multi-Agent Code Review System</p>
    <p>Demonstrates: Multiple agents, coordination, consensus building</p>
    <p>Learn more: <a href="advance_README.md">advance_README.md</a></p>
</div>
""", unsafe_allow_html=True)
