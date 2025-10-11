import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Research Assistant with Tools",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2ca02c;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .iteration-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        background-color: #ff7f0e;
        color: white;
        font-weight: bold;
        margin: 0.3rem;
    }
    .confidence-high { color: #2ca02c; font-weight: bold; }
    .confidence-medium { color: #ff7f0e; font-weight: bold; }
    .confidence-low { color: #d62728; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔍 Research Assistant with Tool Use</h1>', unsafe_allow_html=True)
st.markdown("**Complexity:** Intermediate | **Pattern:** Iterative loops with tool integration")

# Define tools
@tool
def web_search(query: str) -> str:
    """Search the web for information. Returns search results."""
    mock_results = {
        "climate change": "Recent studies show global temperatures rising 1.1°C since pre-industrial times. Key impacts include sea level rise, extreme weather events, and ecosystem disruption.",
        "artificial intelligence": "AI has advanced rapidly with transformer models like GPT and Claude. Applications span healthcare, education, and automation. Ethical considerations include bias and job displacement.",
        "quantum computing": "Quantum computers use qubits to perform calculations. Companies like IBM, Google achieved quantum advantage. Applications in cryptography, drug discovery, and optimization.",
        "default": f"Search results for '{query}': Multiple sources discuss various aspects of {query}. Key findings include recent developments, expert opinions, and statistical data."
    }
    result = mock_results.get(query.lower(), mock_results["default"])
    return result

@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions. Example: '2 + 2' or '100 * 0.15'"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"

@tool
def get_current_date() -> str:
    """Get the current date and time."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now

# State schema
class ResearchState(TypedDict):
    query: str
    messages: List
    research_data: List[dict]
    iteration: int
    max_iterations: int
    needs_more_research: bool
    final_answer: str
    confidence: str

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key"
    )

    max_iterations = st.slider(
        "Max Iterations",
        min_value=1,
        max_value=5,
        value=3,
        help="Maximum research cycles"
    )

    st.divider()

    st.header("🛠️ Available Tools")
    st.markdown("""
    <div class="tool-card">
        <strong>🔍 web_search</strong><br>
        Search for information
    </div>
    <div class="tool-card">
        <strong>🧮 calculator</strong><br>
        Evaluate math expressions
    </div>
    <div class="tool-card">
        <strong>📅 get_current_date</strong><br>
        Get current date/time
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.header("💡 Example Queries")
    example_queries = {
        "AI Developments": "What are the latest developments in artificial intelligence?",
        "Climate Impact": "What's the impact of climate change on global sea levels?",
        "Quantum Computing": "Explain quantum computing and its applications",
        "Current Date": "What is today's date and time?",
        "Math Calculation": "Calculate 15% of 1000"
    }

    for label, query in example_queries.items():
        if st.button(label, key=f"example_{label}", use_container_width=True):
            st.session_state.selected_query = query

# Initialize session state
if 'research_history' not in st.session_state:
    st.session_state.research_history = []
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""
if 'current_research' not in st.session_state:
    st.session_state.current_research = None

# Node functions
def plan_research(state: ResearchState, llm) -> ResearchState:
    """Analyze the query and plan the research approach."""
    query = state["query"]
    previous_findings = state["research_data"]

    if previous_findings:
        context = f"Previous findings: {json.dumps(previous_findings, indent=2)}"
    else:
        context = "No previous research yet."

    planning_prompt = f"""You are a research assistant planning how to answer this question:
"{query}"

{context}

Determine what information you still need to gather. Consider:
1. What key aspects of the question need research?
2. What tools would be helpful? (web_search, calculator, get_current_date)
3. What specific searches or calculations should you perform?

Respond with a brief research plan (2-3 sentences)."""

    response = llm.invoke([HumanMessage(content=planning_prompt)])
    state["messages"].append({"role": "plan", "content": response.content, "iteration": state["iteration"]})

    return state

def execute_research(state: ResearchState, llm_with_tools, tools) -> ResearchState:
    """Use tools to gather information."""
    query = state["query"]
    previous_findings = state["research_data"]

    research_prompt = f"""Research question: "{query}"

Previous findings: {json.dumps(previous_findings) if previous_findings else "None yet"}

Use the available tools to gather information. You can:
- web_search(query): Search for information
- calculator(expression): Perform calculations
- get_current_date(): Get current date/time

Make 1-2 tool calls to gather relevant information. Be specific with your searches."""

    response = llm_with_tools.invoke([HumanMessage(content=research_prompt)])

    findings = []
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            for tool_func in tools:
                if tool_func.name == tool_name:
                    result = tool_func.invoke(tool_args)
                    findings.append({
                        "tool": tool_name,
                        "input": tool_args,
                        "output": result
                    })
                    break

    state["research_data"].extend(findings)
    state["iteration"] += 1

    return state

def evaluate_progress(state: ResearchState, llm) -> ResearchState:
    """Assess if we have enough information to answer the query."""
    query = state["query"]
    findings = state["research_data"]
    iteration = state["iteration"]
    max_iterations = state["max_iterations"]

    evaluation_prompt = f"""Research question: "{query}"

Collected findings:
{json.dumps(findings, indent=2)}

Current iteration: {iteration}/{max_iterations}

Evaluate:
1. Do we have sufficient information to provide a comprehensive answer?
2. Are there critical gaps in our research?
3. Would additional research significantly improve the answer?

Respond with a JSON object:
{{
    "sufficient": true/false,
    "confidence": "low/medium/high",
    "reasoning": "brief explanation"
}}"""

    response = llm.invoke([HumanMessage(content=evaluation_prompt)])

    try:
        eval_text = response.content.strip()
        if "```json" in eval_text:
            eval_text = eval_text.split("```json")[1].split("```")[0].strip()
        elif "```" in eval_text:
            eval_text = eval_text.split("```")[1].split("```")[0].strip()

        evaluation = json.loads(eval_text)

        sufficient = evaluation.get("sufficient", False)
        confidence = evaluation.get("confidence", "medium")

        state["confidence"] = confidence
        state["messages"].append({
            "role": "evaluation",
            "content": evaluation,
            "iteration": iteration
        })

        if iteration >= max_iterations:
            state["needs_more_research"] = False
        elif sufficient:
            state["needs_more_research"] = False
        else:
            state["needs_more_research"] = True

    except Exception:
        state["needs_more_research"] = iteration < 2
        state["confidence"] = "medium"

    return state

def synthesize_answer(state: ResearchState, llm) -> ResearchState:
    """Create a comprehensive answer from all research findings."""
    query = state["query"]
    findings = state["research_data"]
    confidence = state["confidence"]

    synthesis_prompt = f"""Based on the research findings, provide a comprehensive answer to:
"{query}"

Research findings:
{json.dumps(findings, indent=2)}

Confidence level: {confidence}

Provide:
1. A clear, well-structured answer
2. Key facts and data points
3. Any relevant caveats or limitations
4. Sources of information (which tools/searches were used)

Be thorough but concise."""

    response = llm.invoke([HumanMessage(content=synthesis_prompt)])
    state["final_answer"] = response.content
    state["needs_more_research"] = False

    return state

def should_continue(state: ResearchState) -> Literal["continue", "synthesize"]:
    """Route based on whether more research is needed."""
    if state["needs_more_research"]:
        return "continue"
    return "synthesize"

def create_research_graph(llm, llm_with_tools, tools):
    """Create and compile the research assistant graph."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("plan", lambda s: plan_research(s, llm))
    workflow.add_node("research", lambda s: execute_research(s, llm_with_tools, tools))
    workflow.add_node("evaluate", lambda s: evaluate_progress(s, llm))
    workflow.add_node("synthesize", lambda s: synthesize_answer(s, llm))

    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "research")
    workflow.add_edge("research", "evaluate")

    workflow.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "continue": "plan",
            "synthesize": "synthesize"
        }
    )

    workflow.add_edge("synthesize", END)

    return workflow.compile()

# Main interface
st.header("🔬 Research Query")

col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.selected_query:
        query = st.text_area(
            "Enter your research question:",
            value=st.session_state.selected_query,
            height=100,
            placeholder="What would you like to research?"
        )
        st.session_state.selected_query = ""
    else:
        query = st.text_area(
            "Enter your research question:",
            height=100,
            placeholder="What would you like to research?"
        )

    col_submit, col_clear = st.columns([1, 4])
    with col_submit:
        submit_button = st.button("🚀 Start Research", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.research_history = []
            st.session_state.current_research = None
            st.rerun()

with col2:
    st.header("📊 Statistics")
    st.metric("Total Researches", len(st.session_state.research_history))

    if st.session_state.current_research:
        st.metric("Current Iterations", st.session_state.current_research.get("iteration", 0))
        conf = st.session_state.current_research.get("confidence", "medium")
        conf_class = f"confidence-{conf}"
        st.markdown(f'<p class="{conf_class}">Confidence: {conf.upper()}</p>', unsafe_allow_html=True)

# Process query
if submit_button and query:
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar!")
    else:
        try:
            with st.spinner("🔄 Conducting research..."):
                # Initialize LLMs
                llm = ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=api_key)
                tools_list = [web_search, calculator, get_current_date]
                llm_with_tools = llm.bind_tools(tools_list)

                # Create graph
                app = create_research_graph(llm, llm_with_tools, tools_list)

                # Initialize state
                initial_state = {
                    "query": query,
                    "messages": [],
                    "research_data": [],
                    "iteration": 0,
                    "max_iterations": max_iterations,
                    "needs_more_research": True,
                    "final_answer": "",
                    "confidence": "low"
                }

                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Run the graph
                result = app.invoke(initial_state)

                progress_bar.progress(100)
                status_text.success("✅ Research completed!")

                # Store in session state
                st.session_state.current_research = result
                st.session_state.research_history.append({
                    "query": query,
                    "result": result,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display current research results
if st.session_state.current_research:
    st.divider()
    result = st.session_state.current_research

    # Summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Iterations", result["iteration"])
    with col2:
        st.metric("Tools Used", len(result["research_data"]))
    with col3:
        conf = result["confidence"]
        conf_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        st.metric("Confidence", f"{conf_emoji.get(conf, '⚪')} {conf.upper()}")
    with col4:
        st.metric("Messages", len(result.get("messages", [])))

    # Final Answer
    st.header("💡 Final Answer")
    st.success(result["final_answer"])

    # Research Process
    with st.expander("🔍 Research Process Details", expanded=False):
        tabs = st.tabs([f"Iteration {i+1}" for i in range(result["iteration"])])

        for i, tab in enumerate(tabs):
            with tab:
                # Show planning
                plans = [m for m in result.get("messages", []) if m.get("role") == "plan" and m.get("iteration") == i]
                if plans:
                    st.markdown("**📋 Research Plan:**")
                    st.info(plans[0]["content"])

                # Show tool calls
                tools_used = [d for j, d in enumerate(result["research_data"]) if j == i or (j < i + 2 and len(result["research_data"]) > i)]
                if tools_used:
                    st.markdown("**🛠️ Tools Executed:**")
                    for tool_idx, tool_data in enumerate(tools_used):
                        with st.container():
                            st.markdown(f"**{tool_data['tool']}**")
                            st.code(json.dumps(tool_data['input'], indent=2), language="json")
                            st.text_area("Result:", tool_data['output'], height=100, key=f"tool_iter_{i}_idx_{tool_idx}_{tool_data['tool']}")

                # Show evaluation
                evals = [m for m in result.get("messages", []) if m.get("role") == "evaluation" and m.get("iteration") == i+1]
                if evals:
                    st.markdown("**📊 Evaluation:**")
                    eval_data = evals[0]["content"]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sufficient", "✅ Yes" if eval_data.get("sufficient") else "❌ No")
                    with col2:
                        st.metric("Confidence", eval_data.get("confidence", "unknown").upper())
                    st.text(eval_data.get("reasoning", ""))

# Display history
if st.session_state.research_history:
    st.divider()
    st.header("📜 Research History")

    for i, research in enumerate(reversed(st.session_state.research_history), 1):
        with st.expander(f"Research {len(st.session_state.research_history) - i + 1}: {research['query'][:60]}... ({research['timestamp']})", expanded=False):
            st.markdown(f"**Query:** {research['query']}")
            st.markdown(f"**Iterations:** {research['result']['iteration']}")
            st.markdown(f"**Confidence:** {research['result']['confidence'].upper()}")
            st.markdown("**Answer:**")
            st.info(research['result']['final_answer'])

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Medium Example:</strong> Research Assistant with Tool Use</p>
    <p>Demonstrates: Tool integration, iterative research, evaluation loops</p>
    <p>Learn more: <a href="medium_README.md">medium_README.md</a></p>
</div>
""", unsafe_allow_html=True)
