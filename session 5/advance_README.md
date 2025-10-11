# Advanced: Multi-Agent Code Review System

## Overview

A sophisticated code review system with multiple specialized agents that collaborate, debate, and reach consensus on code quality. This advanced example demonstrates multi-agent coordination, parallel execution patterns, reflection, and human-in-the-loop workflows.

## Architecture

```
                    ┌──────────────────┐
                    │   Code Input     │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  Analyzer    │ │ Architect    │ │  Security    │
      │   Agent      │ │   Agent      │ │   Agent      │
      │              │ │              │ │              │
      │ • Bugs       │ │ • Design     │ │ • Vulns      │
      │ • Quality    │ │ • Structure  │ │ • Auth       │
      │ • Performance│ │ • SOLID      │ │ • Validation │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             └────────┬───────┴────────────────┘
                      ▼
              ┌──────────────────┐
              │   Coordinator    │
              │   Synthesizes    │
              │   - Priority     │
              │   - Conflicts    │
              │   - Consensus    │
              └────────┬─────────┘
                       │
                  ┌────┴────┐
                  │ Refine? │
                  └────┬────┘
                       │
                  Yes ─┴─ No
                  │       │
                  ▼       ▼
          ┌──────────────────┐  ┌──────────────────┐
          │   Reflection     │  │  Final Report    │
          │   - Discuss      │  │  - Executive     │
          │   - Resolve      │  │  - Issues        │
          │   Conflicts      │  │  - Recommendations│
          └────────┬─────────┘  └────────┬─────────┘
                   │                     │
                   │                     ▼
                   │             ┌──────────────────┐
                   │             │  Human Review    │
                   │             │  Checkpoint      │
                   │             └────────┬─────────┘
                   │                      │
                   └──────────────────────▼
                                     ┌────────┐
                                     │  END   │
                                     └────────┘
```

## Key Concepts

### 1. Complex Multi-Agent State

```python
class AgentFeedback(TypedDict):
    """Feedback from a single agent."""
    agent_name: str
    issues: List[str]
    suggestions: List[str]
    severity: str  # low, medium, high, critical
    confidence: float  # 0-1

class CodeReviewState(TypedDict):
    """Main state for the code review system."""
    code: str
    language: str

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
```

**Key Innovation: State Accumulation with Operators**
```python
analyzer_feedback: Annotated[List[AgentFeedback], operator.add]
```
- Multiple nodes can append to the same list
- LangGraph automatically merges updates
- Prevents overwriting previous agent feedback

### 2. Specialized Agent System

Each agent has a unique perspective and expertise:

#### Analyzer Agent
```python
def analyzer_agent(state: CodeReviewState) -> CodeReviewState:
    """Analyze code for bugs, performance, and quality issues."""
    # Focus areas:
    # - Logical errors
    # - Performance bottlenecks
    # - Code quality
    # - Best practices
```

#### Architect Agent
```python
def architect_agent(state: CodeReviewState) -> CodeReviewState:
    """Review code architecture and design patterns."""
    # Focus areas:
    # - Design patterns
    # - Code structure
    # - Modularity and coupling
    # - SOLID principles
```

#### Security Agent
```python
def security_agent(state: CodeReviewState) -> CodeReviewState:
    """Analyze code for security vulnerabilities."""
    # Focus areas:
    # - SQL injection, XSS
    # - Authentication issues
    # - Input validation
    # - Cryptographic weaknesses
```

### 3. Agent Creation Pattern

```python
def create_agent_llm(agent_type: str) -> ChatOpenAI:
    """Create specialized LLM for each agent type."""

    system_prompts = {
        "analyzer": "You are a Code Analyzer Agent...",
        "architect": "You are a Software Architect Agent...",
        "security": "You are a Security Expert Agent...",
        "coordinator": "You are a Coordinator Agent..."
    }

    return ChatOpenAI(model="gpt-4o", temperature=0.2)

# Create independent agent instances
analyzer_llm = create_agent_llm("analyzer")
architect_llm = create_agent_llm("architect")
security_llm = create_agent_llm("security")
coordinator_llm = create_agent_llm("coordinator")
```

### 4. Coordinator Agent

The coordinator synthesizes all agent feedback:

```python
def coordinator_synthesize(state: CodeReviewState) -> CodeReviewState:
    """Coordinator synthesizes all agent feedback."""

    # Collect feedback from all agents
    all_feedback = {
        "analyzer": analyzer_feedback,
        "architect": architect_feedback,
        "security": security_feedback
    }

    # Analyze and synthesize:
    # 1. Identify critical issues
    # 2. Find conflicting opinions
    # 3. Determine consensus
    # 4. Assess if refinement needed

    return {
        "priority_issues": [...],
        "conflicting_opinions": [...],
        "consensus_reached": True/False,
        "needs_refinement": True/False,
        "iteration": iteration + 1
    }
```

### 5. Reflection Mechanism

When agents disagree, the reflection node facilitates discussion:

```python
def reflection_node(state: CodeReviewState) -> CodeReviewState:
    """Agents reflect on conflicting feedback and refine opinions."""

    conflicts = state.get("conflicting_opinions", [])

    if not conflicts:
        return {"needs_refinement": False}

    # In production: facilitate agent-to-agent discussion
    # Agents reconsider their positions
    # Update their feedback

    # Reset feedback for new round
    return {
        "analyzer_feedback": [],
        "architect_feedback": [],
        "security_feedback": [],
        "needs_refinement": True
    }
```

### 6. Human-in-the-Loop Pattern

```python
def human_review_checkpoint(state: CodeReviewState) -> CodeReviewState:
    """Human-in-the-loop review checkpoint."""

    # In production with checkpointing:
    # from langgraph.checkpoint import interrupt
    # human_input = interrupt("Review the report and provide feedback")

    approval = state.get("approval_status", "pending")

    # Return human feedback
    return {
        "human_feedback": human_input
    }
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
python advance.py
```

### Example Output

```
======================================================================
MULTI-AGENT CODE REVIEW SYSTEM
======================================================================

📄 CODE TO REVIEW:
----------------------------------------------------------------------
def process_user_input(user_id, password):
    # Connect to database
    conn = mysql.connect(host="localhost", user="root", password="")
    cursor = conn.cursor()

    # Check user credentials
    query = "SELECT * FROM users WHERE id = '" + user_id + "' AND password = '" + password + "'"
    cursor.execute(query)
    ...
----------------------------------------------------------------------

🔍 ANALYZER AGENT analyzing code...
   Found 3 issues
   Severity: high

🏗️ ARCHITECT AGENT reviewing design...
   Found 2 design issues
   Severity: medium

🔒 SECURITY AGENT checking for vulnerabilities...
   Found 4 security issues
   Severity: critical

🎯 COORDINATOR synthesizing feedback...
   Priority Issues: 5
   Conflicts: 0
   Consensus: True
   Needs Refinement: False

📝 COORDINATOR generating final report...
   Approval Status: needs_revision
   Recommended Changes: 5

👤 HUMAN REVIEW CHECKPOINT
   Current Status: needs_revision
   Simulated Feedback: Looks good, approved for deployment

======================================================================
FINAL REVIEW RESULTS
======================================================================

📊 Statistics:
   Total Iterations: 1
   Approval Status: needs_revision
   Priority Issues: 5

📝 Final Report:
----------------------------------------------------------------------
EXECUTIVE SUMMARY
This code review has identified several critical security vulnerabilities
that must be addressed before deployment...

CRITICAL ISSUES:
1. SQL Injection vulnerability in query construction
2. Hardcoded database credentials
3. Plain-text password storage
...

🔧 Top Recommended Changes:
   1. Use parameterized queries to prevent SQL injection
   2. Move credentials to environment variables
   3. Implement password hashing
   4. Add input validation
   5. Implement proper error handling

👤 Human Feedback: Looks good, approved for deployment
```

## How It Works

### Step-by-Step Flow

1. **Parallel Agent Execution**: Three agents analyze code simultaneously (conceptually)
2. **Feedback Collection**: Each agent's feedback accumulates in state
3. **Coordinator Synthesis**:
   - Identifies priority issues
   - Finds conflicting opinions
   - Assesses consensus
4. **Refinement Decision**:
   - If conflicts → Reflection → Loop back to agents
   - If consensus → Generate final report
5. **Final Report Generation**: Comprehensive review document
6. **Human Review**: Checkpoint for human approval
7. **Complete**: System ends with all feedback collected

### Agent Interaction Patterns

#### Sequential Execution (Current)
```
Analyzer → Architect → Security → Coordinator
```

#### True Parallel Execution (Advanced)
```python
# With async support:
async_results = await asyncio.gather(
    analyzer_agent(state),
    architect_agent(state),
    security_agent(state)
)
```

## Code Walkthrough

### Main Execution

```python
def main():
    app = create_code_review_graph()

    example_code = '''
    def process_user_input(user_id, password):
        query = "SELECT * FROM users WHERE id = '" + user_id + "'"
        # ... SQL injection vulnerability
    '''

    initial_state = {
        "code": example_code,
        "language": "python",
        "analyzer_feedback": [],
        "architect_feedback": [],
        "security_feedback": [],
        "iteration": 0,
        "max_iterations": 2,
        "needs_refinement": False,
        # ... other fields
    }

    result = app.invoke(initial_state)
    print(result["final_report"])
```

### Agent Feedback Pattern

```python
def analyzer_agent(state: CodeReviewState) -> CodeReviewState:
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
    feedback = json.loads(response.content)
    feedback["agent_name"] = "analyzer"

    # Return ONLY the feedback for this agent
    # LangGraph merges with existing state using operator.add
    return {
        "analyzer_feedback": [feedback]
    }
```

### State Merging Magic

```python
# When agents return partial state:
return {"analyzer_feedback": [new_feedback]}

# LangGraph automatically merges:
# Because analyzer_feedback is: Annotated[List[AgentFeedback], operator.add]
# The new feedback is ADDED to existing feedback, not replaced

# Final state contains feedback from ALL agents
```

## Customization

### Add New Agent

```python
# 1. Add to state
class CodeReviewState(TypedDict):
    # ... existing fields
    performance_feedback: Annotated[List[AgentFeedback], operator.add]

# 2. Create agent
performance_llm = create_agent_llm("performance")

def performance_agent(state: CodeReviewState) -> CodeReviewState:
    """Analyze performance and optimization."""
    # Implementation
    return {"performance_feedback": [feedback]}

# 3. Add to workflow
workflow.add_node("performance", performance_agent)
workflow.add_edge("security", "performance")
workflow.add_edge("performance", "coordinator")

# 4. Update coordinator to include performance feedback
```

### Change Approval Criteria

```python
def generate_final_report(state: CodeReviewState) -> CodeReviewState:
    # Custom approval logic
    critical_count = sum(1 for issue in priority_issues
                        if issue["severity"] == "critical")
    high_count = sum(1 for issue in priority_issues
                    if issue["severity"] == "high")

    if critical_count > 0:
        approval = "needs_revision"
    elif high_count > 2:
        approval = "conditional_approval"
    else:
        approval = "approved"
```

### Enable True Parallel Execution

```python
# Use async patterns
import asyncio

async def run_agents_parallel(state):
    results = await asyncio.gather(
        analyzer_agent_async(state),
        architect_agent_async(state),
        security_agent_async(state)
    )

    # Merge results
    merged_state = {}
    for result in results:
        for key, value in result.items():
            if key in merged_state:
                merged_state[key].extend(value)
            else:
                merged_state[key] = value

    return merged_state
```

### Implement Real Human-in-the-Loop

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create checkpointer
memory = SqliteSaver.from_conn_string(":memory:")

# Compile with checkpointer
app = workflow.compile(checkpointer=memory)

def human_review_checkpoint(state: CodeReviewState) -> CodeReviewState:
    # This will pause execution and wait for human input
    from langgraph.checkpoint import interrupt

    human_input = interrupt({
        "type": "human_review",
        "report": state["final_report"],
        "approval_status": state["approval_status"]
    })

    return {"human_feedback": human_input}
```

## Learning Objectives

After studying this example, you should understand:

✅ How to build multi-agent systems
✅ How to use `Annotated` with `operator.add` for state accumulation
✅ How to coordinate multiple specialized agents
✅ How to implement reflection and refinement
✅ How to identify and resolve conflicts
✅ How to build consensus mechanisms
✅ How to integrate human-in-the-loop patterns
✅ How to handle complex nested state

## Advanced Patterns

### 1. Operator-Based State Merging
```python
# Using operator.add for lists
feedback: Annotated[List, operator.add]

# Other operators available:
# operator.mul, operator.sub, custom reducers
```

### 2. Multi-Level Routing
```python
# First level: Should refine?
workflow.add_conditional_edges("coordinator", should_refine, {...})

# Second level: Which refinement type?
workflow.add_conditional_edges("reflection", refinement_type, {...})
```

### 3. Consensus Building
```python
def build_consensus(feedbacks: List[AgentFeedback]) -> dict:
    # Extract common themes
    # Weight by confidence
    # Identify majority opinions
    # Flag disagreements
```

## Production Considerations

### 1. Async Execution
```python
# For true parallelism, use async
async with aiohttp.ClientSession() as session:
    tasks = [agent(state) for agent in agents]
    results = await asyncio.gather(*tasks)
```

### 2. Checkpointing
```python
# Enable state persistence for human-in-the-loop
from langgraph.checkpoint import SqliteSaver
memory = SqliteSaver.from_conn_string("reviews.db")
app = workflow.compile(checkpointer=memory)
```

### 3. Error Handling
```python
try:
    feedback = json.loads(response.content)
except:
    # Fallback feedback
    feedback = {
        "agent_name": agent_name,
        "issues": ["Error analyzing code"],
        "severity": "low",
        "confidence": 0.5
    }
```

### 4. Rate Limiting
```python
import time

def rate_limited_agent(state):
    time.sleep(1)  # Avoid API rate limits
    return agent_function(state)
```

## Common Issues

### Issue: State Overwriting Instead of Accumulating
**Solution:** Use `Annotated[List, operator.add]`
```python
# Wrong:
feedback: List[AgentFeedback]

# Right:
feedback: Annotated[List[AgentFeedback], operator.add]
```

### Issue: Infinite Refinement Loop
**Solution:** Always check iteration limits
```python
if iteration >= max_iterations:
    needs_refinement = False
```

### Issue: JSON Parsing Errors
**Solution:** Robust parsing with fallbacks
```python
content = response.content.strip()
if "```json" in content:
    content = content.split("```json")[1].split("```")[0]
feedback = json.loads(content)
```

## Resources

- [LangGraph Multi-Agent Systems](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [State Reducers](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)
- [Checkpointing](https://langchain-ai.github.io/langgraph/how-tos/persistence/)

## Summary

This advanced example demonstrates:
- ✅ Multi-agent architecture
- ✅ Specialized agent roles
- ✅ State accumulation with operators
- ✅ Coordinator pattern
- ✅ Reflection and refinement
- ✅ Consensus building
- ✅ Conflict resolution
- ✅ Human-in-the-loop integration

The most sophisticated LangGraph pattern for complex decision-making! 🚀
