from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Define the state schema
class SupportState(TypedDict):
    messages: list  # Conversation history
    intent: str     # Classified intent
    resolved: bool  # Whether issue is resolved

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Node 1: Classify user intent
def classify_intent(state: SupportState) -> SupportState:
    """Analyze the user's message and classify their intent."""
    
    user_message = state["messages"][-1].content
    
    classification_prompt = f"""Classify this customer support message into ONE of these categories:
    - billing: Questions about payments, refunds, subscriptions, invoices
    - technical: Technical issues, bugs, errors, login problems
    - general: General questions, feature requests, feedback
    
    Customer message: "{user_message}"
    
    Respond with ONLY the category name (billing, technical, or general)."""
    
    response = llm.invoke([HumanMessage(content=classification_prompt)])
    intent = response.content.strip().lower()
    
    # Validate intent
    if intent not in ["billing", "technical", "general"]:
        intent = "general"
    
    print(f"🔍 Intent classified as: {intent}")
    
    return {
        **state,
        "intent": intent
    }

# Node 2: Handle billing queries
def handle_billing(state: SupportState) -> SupportState:
    """Respond to billing-related queries."""
    
    user_message = state["messages"][-1].content
    
    billing_prompt = f"""You are a billing support specialist. Help the customer with their billing question.
    Be professional, empathetic, and provide clear information about:
    - Payment methods and processing
    - Refund policies
    - Subscription management
    - Invoice questions
    
    Customer question: "{user_message}"
    
    Provide a helpful, concise response."""
    
    response = llm.invoke([HumanMessage(content=billing_prompt)])
    
    state["messages"].append(AIMessage(content=response.content))
    state["resolved"] = True
    
    return state

# Node 3: Handle technical issues
def handle_technical(state: SupportState) -> SupportState:
    """Respond to technical support queries."""
    
    user_message = state["messages"][-1].content
    
    technical_prompt = f"""You are a technical support specialist. Help the customer with their technical issue.
    Be clear and methodical. Provide:
    - Step-by-step troubleshooting
    - Possible causes
    - Solutions or workarounds
    
    Customer issue: "{user_message}"
    
    Provide a helpful, structured response."""
    
    response = llm.invoke([HumanMessage(content=technical_prompt)])
    
    state["messages"].append(AIMessage(content=response.content))
    state["resolved"] = True
    
    return state

# Node 4: Handle general queries
def handle_general(state: SupportState) -> SupportState:
    """Respond to general questions."""
    
    user_message = state["messages"][-1].content
    
    general_prompt = f"""You are a friendly customer service representative. Help the customer with their question.
    Be helpful and informative about:
    - Product features
    - Company policies
    - General guidance
    
    Customer question: "{user_message}"
    
    Provide a warm, helpful response."""
    
    response = llm.invoke([HumanMessage(content=general_prompt)])
    
    state["messages"].append(AIMessage(content=response.content))
    state["resolved"] = True
    
    return state

# Router: Decide which handler to use based on intent
def route_query(state: SupportState) -> Literal["billing", "technical", "general"]:
    """Route to the appropriate handler based on classified intent."""
    return state["intent"]

# Build the graph
def create_support_graph():
    """Create and compile the support triage graph."""
    
    workflow = StateGraph(SupportState)
    
    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("billing", handle_billing)
    workflow.add_node("technical", handle_technical)
    workflow.add_node("general", handle_general)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add conditional routing after classification
    workflow.add_conditional_edges(
        "classify",
        route_query,
        {
            "billing": "billing",
            "technical": "technical",
            "general": "general"
        }
    )
    
    # All handlers lead to END
    workflow.add_edge("billing", END)
    workflow.add_edge("technical", END)
    workflow.add_edge("general", END)
    
    return workflow.compile()

# Example usage
def main():
    """Run example queries through the support bot."""
    
    print("=" * 60)
    print("CUSTOMER SUPPORT TRIAGE BOT")
    print("=" * 60)
    
    # Create the graph
    app = create_support_graph()
    
    # Test queries
    test_queries = [
        "I was charged twice for my subscription this month!",
        "I can't log into my account, it says invalid password",
        "Do you have a mobile app available?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 60}")
        print(f"Query #{i}: {query}")
        print('─' * 60)
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "intent": "",
            "resolved": False
        }
        
        # Run the graph
        result = app.invoke(initial_state)
        
        # Print response
        print(f"\n💬 Bot Response:")
        print(result["messages"][-1].content)
        print(f"\n✅ Resolved: {result['resolved']}")

if __name__ == "__main__":
    main()