# Medium: Research Assistant with Tool Use

## Overview

An intelligent research assistant that uses tools iteratively to gather information and synthesize comprehensive answers. This intermediate example demonstrates tool integration, iterative loops, and reflection patterns.

## Architecture

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Plan Research│◄────────┐
└──────┬───────┘         │
       │                 │
       ▼                 │
┌──────────────┐         │
│Execute Tools │         │
│- web_search  │         │
│- calculator  │         │
│- get_date    │         │
└──────┬───────┘         │
       │                 │
       ▼                 │
┌──────────────┐         │
│  Evaluate    │         │
│  Progress    │         │
└──────┬───────┘         │
       │                 │
    ┌──┴──┐              │
    │ OK? │              │
    └──┬──┘              │
       │                 │
   No ─┴─ Yes            │
   │      │              │
   └──────┘              │
       │                 │
       ▼                 │
┌──────────────┐         │
│ Synthesize   │         │
│Final Answer  │         │
└──────────────┘
```

## Key Concepts

### 1. Enhanced State Management

```python
class ResearchState(TypedDict):
    query: str                    # Original research question
    messages: List                # Conversation history
    research_data: List[dict]     # Collected research findings
    iteration: int                # Current iteration count
    max_iterations: int           # Maximum allowed iterations
    needs_more_research: bool     # Whether more research is needed
    final_answer: str             # The synthesized answer
    confidence: str               # Confidence level (low/medium/high)
```

**Key Features:**
- Accumulates research data across iterations
- Tracks iteration count to prevent infinite loops
- Stores confidence levels for self-assessment

### 2. Tool Integration

#### Define Tools
```python
@tool
def web_search(query: str) -> str:
    """Search the web for information. Returns search results."""
    # Implementation
    return result

@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions. Example: '2 + 2' or '100 * 0.15'"""
    result = eval(expression, {"__builtins__": {}}, {})
    return str(result)

@tool
def get_current_date() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

#### Bind Tools to LLM
```python
tools = [web_search, calculator, get_current_date]
llm_with_tools = llm.bind_tools(tools)
```

### 3. Iterative Research Loop

The system performs multiple research cycles:

**Iteration 1:**
- Plan what to research
- Execute initial tool calls
- Evaluate if sufficient

**Iteration 2+ (if needed):**
- Review previous findings
- Plan additional research
- Execute more tool calls
- Re-evaluate

**Final:**
- Synthesize all findings
- Generate comprehensive answer

### 4. Nodes (Functions)

#### Node 1: Plan Research
```python
def plan_research(state: ResearchState) -> ResearchState:
    """Analyze the query and plan the research approach."""
    # Reviews query and previous findings
    # Determines what information is still needed
    # Plans which tools to use
```

#### Node 2: Execute Research
```python
def execute_research(state: ResearchState) -> ResearchState:
    """Use tools to gather information."""
    # LLM decides which tools to call
    # Executes tool calls
    # Accumulates findings in research_data
    # Increments iteration counter
```

#### Node 3: Evaluate Progress
```python
def evaluate_progress(state: ResearchState) -> ResearchState:
    """Assess if we have enough information to answer the query."""
    # Reviews all findings
    # Determines sufficiency
    # Sets confidence level
    # Decides if more research needed
```

#### Node 4: Synthesize Answer
```python
def synthesize_answer(state: ResearchState) -> ResearchState:
    """Create a comprehensive answer from all research findings."""
    # Reviews all research data
    # Generates structured answer
    # Includes sources and caveats
```

### 5. Dynamic Routing

```python
def should_continue(state: ResearchState) -> Literal["continue", "synthesize"]:
    """Route based on whether more research is needed."""
    if state["needs_more_research"]:
        return "continue"  # Loop back to plan_research
    return "synthesize"  # Move to final answer
```

## Setup

### 1. Install Dependencies
```bash
cd "session 5"
source .venv/bin/activate
pip install langgraph langchain-openai langchain-core
```

### 2. Set API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Running

```bash
python medium.py
```

### Example Output

```
============================================================
RESEARCH ASSISTANT WITH TOOL USE
============================================================

############################################################
📝 RESEARCH QUERY: What are the latest developments in artificial intelligence?
############################################################

============================================================
🎯 ITERATION 1/3
============================================================

📋 Research Plan:
I'll search for information about recent AI developments and trends.

🔧 Executing tools:
🔍 Web Search: 'artificial intelligence'

📊 Evaluation:
   Sufficient: False
   Confidence: medium
   Reasoning: Need more specific information about recent developments
   🔄 More research needed

============================================================
🎯 ITERATION 2/3
============================================================

📋 Research Plan:
I'll search for the current date to provide context on "latest" developments.

🔧 Executing tools:
📅 Current date: 2025-10-10 14:30:00

📊 Evaluation:
   Sufficient: True
   Confidence: high
   Reasoning: Have comprehensive information to answer
   ✅ Sufficient information gathered

============================================================
📊 FINAL RESULTS
============================================================

🎯 Original Query: What are the latest developments in artificial intelligence?

🔬 Research Iterations: 2

📈 Confidence: high

💡 Final Answer:
Based on the research conducted, here are the latest developments in AI...
[Comprehensive answer with data points and sources]

📚 Research Data Points: 2
```

## How It Works

### Step-by-Step Flow

1. **Initial Planning**: System analyzes the query and plans research strategy
2. **Tool Execution**: LLM decides which tools to call and with what parameters
3. **Data Collection**: Tool results are stored in `research_data`
4. **Evaluation**: System assesses if information is sufficient
5. **Loop Decision**:
   - If insufficient → Loop back to planning
   - If sufficient → Move to synthesis
6. **Synthesis**: Generate comprehensive final answer
7. **Complete**: Return results with confidence level

### Tool Selection Strategy

The LLM automatically selects appropriate tools:

| Query Type | Likely Tools Used |
|------------|------------------|
| "What is X?" | web_search |
| "Calculate X" | calculator |
| "When did X happen?" | web_search, get_current_date |
| "How much is X?" | web_search, calculator |

## Code Walkthrough

### Main Execution

```python
def main():
    app = create_research_graph()

    test_queries = [
        "What are the latest developments in artificial intelligence?",
        "What's the impact of climate change on global sea levels?",
    ]

    for query in test_queries:
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

        result = app.invoke(initial_state)
        print(result["final_answer"])
```

### Tool Execution Pattern

```python
def execute_research(state: ResearchState) -> ResearchState:
    # Get tool calls from LLM
    response = llm_with_tools.invoke([HumanMessage(content=research_prompt)])

    # Execute each tool call
    findings = []
    if response.tool_calls:
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

    # Accumulate findings
    state["research_data"].extend(findings)
    state["iteration"] += 1

    return state
```

### Evaluation Logic

```python
def evaluate_progress(state: ResearchState) -> ResearchState:
    evaluation_prompt = f"""
    Research question: "{query}"

    Collected findings:
    {json.dumps(findings, indent=2)}

    Evaluate:
    1. Do we have sufficient information?
    2. Are there critical gaps?
    3. Would additional research help?

    Respond with JSON:
    {{
        "sufficient": true/false,
        "confidence": "low/medium/high",
        "reasoning": "explanation"
    }}
    """

    response = llm.invoke([HumanMessage(content=evaluation_prompt)])
    evaluation = json.loads(response.content)

    # Check iteration limit
    if iteration >= max_iterations:
        state["needs_more_research"] = False
    elif evaluation["sufficient"]:
        state["needs_more_research"] = False
    else:
        state["needs_more_research"] = True

    return state
```

## Customization

### Add Custom Tool

```python
@tool
def database_query(sql: str) -> str:
    """Query a database and return results."""
    # Implementation
    conn = connect_to_db()
    results = conn.execute(sql)
    return json.dumps(results)

# Add to tools list
tools = [web_search, calculator, get_current_date, database_query]
llm_with_tools = llm.bind_tools(tools)
```

### Adjust Iteration Limits

```python
initial_state = {
    # ... other fields
    "max_iterations": 5,  # Allow more research rounds
}
```

### Change Confidence Thresholds

```python
def evaluate_progress(state: ResearchState) -> ResearchState:
    # Only stop if high confidence
    if evaluation["confidence"] == "high":
        state["needs_more_research"] = False
    else:
        state["needs_more_research"] = True
```

### Add Research Context

```python
class ResearchState(TypedDict):
    # ... existing fields
    research_context: str  # Domain-specific context
    sources_used: List[str]  # Track information sources
```

## Learning Objectives

After studying this example, you should understand:

✅ How to integrate tools with LLMs
✅ How to create iterative workflows with loops
✅ How to accumulate state across iterations
✅ How to implement self-evaluation logic
✅ How to handle dynamic tool selection
✅ How to manage iteration limits
✅ How to synthesize multi-source information

## Advanced Patterns

### 1. State Accumulation
```python
# Research data grows across iterations
state["research_data"].extend(new_findings)
```

### 2. Loop Control
```python
# Multiple mechanisms prevent infinite loops:
# - Iteration counter
# - Max iterations limit
# - Sufficiency evaluation
```

### 3. Dynamic Tool Use
```python
# LLM decides at runtime which tools to call
# Based on query context and previous findings
```

## Common Issues

### Issue: Too Many Iterations
**Solution:** Adjust max_iterations or improve evaluation logic
```python
"max_iterations": 2  # Reduce iterations
```

### Issue: Tools Not Being Called
**Solution:** Make prompts more explicit about tool use
```python
research_prompt = """Use the available tools to gather information.
You MUST call at least one tool to research the query."""
```

### Issue: JSON Parsing Errors
**Solution:** Add robust error handling
```python
try:
    evaluation = json.loads(response.content)
except:
    # Fallback logic
    state["needs_more_research"] = iteration < 2
```

## Next Steps

Once comfortable with medium.py, move to:
- **advance.py**: Build multi-agent systems with coordination and consensus

## Resources

- [LangGraph Tool Integration](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [Iterative Workflows](https://langchain-ai.github.io/langgraph/how-tos/branching/)

## Summary

This intermediate example demonstrates:
- ✅ Tool integration and binding
- ✅ Iterative research loops
- ✅ State accumulation
- ✅ Self-evaluation and reflection
- ✅ Dynamic routing decisions
- ✅ Comprehensive synthesis

A powerful pattern for research and information gathering tasks! 🔍
