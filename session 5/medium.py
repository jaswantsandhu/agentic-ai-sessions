from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
import json

# Define tools
@tool
def web_search(query: str) -> str:
    """Search the web for information. Returns search results."""
    # In production, integrate with real search API (Tavily, Serper, etc.)
    # This is a mock implementation
    mock_results = {
        "climate change": "Recent studies show global temperatures rising 1.1°C since pre-industrial times. Key impacts include sea level rise, extreme weather events, and ecosystem disruption.",
        "artificial intelligence": "AI has advanced rapidly with transformer models like GPT and Claude. Applications span healthcare, education, and automation. Ethical considerations include bias and job displacement.",
        "quantum computing": "Quantum computers use qubits to perform calculations. Companies like IBM, Google achieved quantum advantage. Applications in cryptography, drug discovery, and optimization.",
        "default": f"Search results for '{query}': Multiple sources discuss various aspects of {query}. Key findings include recent developments, expert opinions, and statistical data."
    }
    
    result = mock_results.get(query.lower(), mock_results["default"])
    print(f"🔍 Web Search: '{query}'")
    return result

@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions. Example: '2 + 2' or '100 * 0.15'"""
    try:
        # Safe evaluation of math expressions
        result = eval(expression, {"__builtins__": {}}, {})
        print(f"🧮 Calculator: {expression} = {result}")
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"

@tool
def get_current_date() -> str:
    """Get the current date and time."""
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 Current date: {now}")
    return now

# State schema
class ResearchState(TypedDict):
    query: str                    # Original research question
    messages: List                # Conversation history
    research_data: List[dict]     # Collected research findings
    iteration: int                # Current iteration count
    max_iterations: int           # Maximum allowed iterations
    needs_more_research: bool     # Whether more research is needed
    final_answer: str             # The synthesized answer
    confidence: str               # Confidence level (low/medium/high)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# Available tools
tools = [web_search, calculator, get_current_date]
llm_with_tools = llm.bind_tools(tools)

# Node 1: Plan research strategy
def plan_research(state: ResearchState) -> ResearchState:
    """Analyze the query and plan the research approach."""
    
    print(f"\n{'='*60}")
    print(f"🎯 ITERATION {state['iteration'] + 1}/{state['max_iterations']}")
    print(f"{'='*60}")
    
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
    
    print(f"\n📋 Research Plan:\n{response.content}\n")
    
    state["messages"].append(AIMessage(content=f"Plan: {response.content}"))
    
    return state

# Node 2: Execute research with tools
def execute_research(state: ResearchState) -> ResearchState:
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
    
    # Get tool calls from LLM
    response = llm_with_tools.invoke([HumanMessage(content=research_prompt)])
    
    # Execute tool calls
    findings = []
    if response.tool_calls:
        print("🔧 Executing tools:")
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute the tool
            for tool_func in tools:
                if tool_func.name == tool_name:
                    result = tool_func.invoke(tool_args)
                    findings.append({
                        "tool": tool_name,
                        "input": tool_args,
                        "output": result
                    })
                    break
    
    # Add findings to research data
    state["research_data"].extend(findings)
    state["iteration"] += 1
    
    return state

# Node 3: Evaluate if more research is needed
def evaluate_progress(state: ResearchState) -> ResearchState:
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
        # Parse the evaluation
        eval_text = response.content.strip()
        # Remove markdown code blocks if present
        if "```json" in eval_text:
            eval_text = eval_text.split("```json")[1].split("```")[0].strip()
        elif "```" in eval_text:
            eval_text = eval_text.split("```")[1].split("```")[0].strip()
        
        evaluation = json.loads(eval_text)
        
        sufficient = evaluation.get("sufficient", False)
        confidence = evaluation.get("confidence", "medium")
        reasoning = evaluation.get("reasoning", "")
        
        print(f"\n📊 Evaluation:")
        print(f"   Sufficient: {sufficient}")
        print(f"   Confidence: {confidence}")
        print(f"   Reasoning: {reasoning}")
        
        state["confidence"] = confidence
        
        # Decide if more research needed
        if iteration >= max_iterations:
            state["needs_more_research"] = False
            print("   ⚠️ Max iterations reached")
        elif sufficient:
            state["needs_more_research"] = False
            print("   ✅ Sufficient information gathered")
        else:
            state["needs_more_research"] = True
            print("   🔄 More research needed")
            
    except Exception as e:
        print(f"   ⚠️ Evaluation parsing error: {e}")
        # Default: stop if we've done at least 2 iterations
        state["needs_more_research"] = iteration < 2
        state["confidence"] = "medium"
    
    return state

# Node 4: Synthesize final answer
def synthesize_answer(state: ResearchState) -> ResearchState:
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

# Router: Decide whether to continue research or synthesize
def should_continue(state: ResearchState) -> Literal["continue", "synthesize"]:
    """Route based on whether more research is needed."""
    if state["needs_more_research"]:
        return "continue"
    return "synthesize"

# Build the graph
def create_research_graph():
    """Create and compile the research assistant graph."""
    
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("plan", plan_research)
    workflow.add_node("research", execute_research)
    workflow.add_node("evaluate", evaluate_progress)
    workflow.add_node("synthesize", synthesize_answer)
    
    # Set entry point
    workflow.set_entry_point("plan")
    
    # Create the cycle: plan → research → evaluate
    workflow.add_edge("plan", "research")
    workflow.add_edge("research", "evaluate")
    
    # Conditional routing after evaluation
    workflow.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "continue": "plan",      # Loop back for more research
            "synthesize": "synthesize"  # Move to final answer
        }
    )
    
    # Synthesize leads to END
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()

# Example usage
def main():
    """Run example research queries."""
    
    print("=" * 60)
    print("RESEARCH ASSISTANT WITH TOOL USE")
    print("=" * 60)
    
    # Create the graph
    app = create_research_graph()
    
    # Test queries
    test_queries = [
        "What are the latest developments in artificial intelligence?",
        "What's the impact of climate change on global sea levels?",
    ]
    
    for query in test_queries:
        print(f"\n\n{'#'*60}")
        print(f"📝 RESEARCH QUERY: {query}")
        print(f"{'#'*60}")
        
        # Initialize state
        initial_state = {
            "query": query,
            "messages": [],
            "research_data": [],
            "iteration": 0,
            "max_iterations": 3,
            "needs_more_research": True,
            "final_answer": "",
            "confidence": "low"
        }
        
        # Run the research process
        result = app.invoke(initial_state)
        
        # Print final results
        print(f"\n{'='*60}")
        print("📊 FINAL RESULTS")
        print(f"{'='*60}")
        print(f"\n🎯 Original Query: {result['query']}")
        print(f"\n🔬 Research Iterations: {result['iteration']}")
        print(f"\n📈 Confidence: {result['confidence']}")
        print(f"\n💡 Final Answer:\n{result['final_answer']}")
        print(f"\n📚 Research Data Points: {len(result['research_data'])}")

if __name__ == "__main__":
    main()