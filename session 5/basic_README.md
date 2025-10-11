# Basic: Customer Support Triage Bot

## Overview

A simple customer support bot that demonstrates fundamental LangGraph concepts through intent classification and routing. This example is perfect for beginners learning LangGraph.

## Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Classify Intent │
└──────┬──────────┘
       │
       ▼
  ┌────┴────┐
  │ Router  │
  └────┬────┘
       │
   ┌───┴───┬───────┬──────┐
   ▼       ▼       ▼
┌────────┐ ┌────────┐ ┌────────┐
│Billing │ │Technical│ │General │
│Handler │ │Handler  │ │Handler │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────┬───┴──────────┘
           ▼
    ┌──────────────┐
    │   Response   │
    └──────────────┘
```

## Key Concepts

### 1. State Management
```python
class SupportState(TypedDict):
    messages: list  # Conversation history
    intent: str     # Classified intent
    resolved: bool  # Whether issue is resolved
```
- Uses `TypedDict` for type-safe state
- Simple, flat state structure
- Easy to understand and modify

### 2. Nodes (Functions)

**Node 1: Classify Intent**
```python
def classify_intent(state: SupportState) -> SupportState:
    # Analyzes user message
    # Returns updated state with intent
```
- Takes current state as input
- Uses LLM to classify intent
- Returns updated state

**Node 2-4: Handlers**
```python
def handle_billing(state: SupportState) -> SupportState:
def handle_technical(state: SupportState) -> SupportState:
def handle_general(state: SupportState) -> SupportState:
```
- Specialized response generators
- Each handles specific intent type
- Adds AI response to messages

### 3. Routing

**Conditional Routing**
```python
def route_query(state: SupportState) -> Literal["billing", "technical", "general"]:
    return state["intent"]
```
- Routes based on classified intent
- Returns the next node name
- Enables dynamic workflow

### 4. Graph Construction

```python
workflow = StateGraph(SupportState)

# Add nodes
workflow.add_node("classify", classify_intent)
workflow.add_node("billing", handle_billing)
workflow.add_node("technical", handle_technical)
workflow.add_node("general", handle_general)

# Set entry point
workflow.set_entry_point("classify")

# Add conditional routing
workflow.add_conditional_edges(
    "classify",
    route_query,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general"
    }
)

# All handlers end the workflow
workflow.add_edge("billing", END)
workflow.add_edge("technical", END)
workflow.add_edge("general", END)
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
python basic.py
```

### Example Output

```
============================================================
CUSTOMER SUPPORT TRIAGE BOT
============================================================

────────────────────────────────────────────────────────────
Query #1: I was charged twice for my subscription this month!
────────────────────────────────────────────────────────────
🔍 Intent classified as: billing

💬 Bot Response:
I understand your concern about being charged twice for your subscription.
I apologize for the inconvenience. Let me help you resolve this...

✅ Resolved: True
```

## How It Works

### Step-by-Step Flow

1. **User Input**: Customer submits a query
2. **Classification**: LLM analyzes and categorizes the intent
3. **Routing**: System routes to appropriate handler
4. **Response**: Specialized handler generates tailored response
5. **Complete**: Query marked as resolved

### Intent Categories

| Intent | Description | Examples |
|--------|-------------|----------|
| **billing** | Payment, refunds, subscriptions | "I was charged twice", "How do I get a refund?" |
| **technical** | Bugs, errors, login issues | "Can't log in", "App crashes on startup" |
| **general** | Features, policies, questions | "Do you have a mobile app?", "What are your hours?" |

## Code Walkthrough

### Main Function
```python
def main():
    app = create_support_graph()

    test_queries = [
        "I was charged twice for my subscription this month!",
        "I can't log into my account, it says invalid password",
        "Do you have a mobile app available?"
    ]

    for query in test_queries:
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "intent": "",
            "resolved": False
        }

        result = app.invoke(initial_state)
        print(result["messages"][-1].content)
```

### Classification Logic
```python
classification_prompt = f"""Classify this customer support message into ONE of these categories:
- billing: Questions about payments, refunds, subscriptions, invoices
- technical: Technical issues, bugs, errors, login problems
- general: General questions, feature requests, feedback

Customer message: "{user_message}"

Respond with ONLY the category name (billing, technical, or general)."""
```

## Customization

### Add New Intent Category

```python
# 1. Create new handler
def handle_sales(state: SupportState) -> SupportState:
    user_message = state["messages"][-1].content

    sales_prompt = f"""You are a sales representative.
    Help the customer with: "{user_message}" """

    response = llm.invoke([HumanMessage(content=sales_prompt)])
    state["messages"].append(AIMessage(content=response.content))
    state["resolved"] = True
    return state

# 2. Update classification prompt to include "sales"

# 3. Add to graph
workflow.add_node("sales", handle_sales)

# 4. Update routing
workflow.add_conditional_edges(
    "classify",
    route_query,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general",
        "sales": "sales"  # Add new route
    }
)

# 5. Add edge to END
workflow.add_edge("sales", END)
```

### Change LLM Model
```python
# Use faster, cheaper model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Use more capable model
llm = ChatOpenAI(model="gpt-4o", temperature=0)
```

### Add Conversation History
```python
def handle_billing(state: SupportState) -> SupportState:
    # Use full conversation history instead of just last message
    conversation = state["messages"]

    response = llm.invoke(conversation + [
        HumanMessage(content="Provide billing support based on the conversation above")
    ])

    state["messages"].append(AIMessage(content=response.content))
    state["resolved"] = True
    return state
```

## Learning Objectives

After studying this example, you should understand:

✅ How to define state with TypedDict
✅ How to create node functions
✅ How to build a StateGraph
✅ How to use conditional routing
✅ How to set entry points and edges
✅ How to invoke a compiled graph

## Next Steps

Once comfortable with basic.py, move to:
- **medium.py**: Learn tool integration and iterative loops
- **advance.py**: Build multi-agent systems with coordination

## Common Issues

### Issue: "OpenAI API key not found"
**Solution:** Set environment variable
```bash
export OPENAI_API_KEY="your-key"
```

### Issue: "Invalid intent returned"
**Solution:** The validation logic handles this:
```python
if intent not in ["billing", "technical", "general"]:
    intent = "general"  # Fallback
```

### Issue: "Module not found: langchain_openai"
**Solution:** Install dependencies
```bash
pip install langchain-openai
```

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [OpenAI API Docs](https://platform.openai.com/docs/)

## Summary

This basic example demonstrates:
- ✅ Simple state management
- ✅ Intent classification
- ✅ Conditional routing
- ✅ Specialized handlers
- ✅ Basic LangGraph patterns

Perfect starting point for learning LangGraph! 🚀
