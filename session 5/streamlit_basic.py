import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import os

# Page config
st.set_page_config(
    page_title="Customer Support Triage Bot",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .billing { background-color: #90EE90; color: #006400; }
    .technical { background-color: #FFB6C1; color: #8B0000; }
    .general { background-color: #ADD8E6; color: #00008B; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎯 Customer Support Triage Bot</h1>', unsafe_allow_html=True)
st.markdown("**Complexity:** Beginner | **Pattern:** Basic routing with conditional edges")

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

    st.header("📊 How It Works")
    st.markdown("""
    1. **Classify Intent**: LLM analyzes the query
    2. **Route**: System routes to appropriate handler
    3. **Respond**: Specialized handler generates response

    **Intent Categories:**
    - 🟢 **Billing**: Payments, refunds, subscriptions
    - 🔴 **Technical**: Bugs, errors, login issues
    - 🔵 **General**: Features, policies, questions
    """)

    st.divider()

    st.header("💡 Example Queries")
    example_queries = {
        "Billing Issue": "I was charged twice for my subscription this month!",
        "Technical Problem": "I can't log into my account, it says invalid password",
        "General Question": "Do you have a mobile app available?",
        "Refund Request": "How do I request a refund for my last payment?",
        "Login Error": "Getting error 500 when I try to access dashboard"
    }

    for label, query in example_queries.items():
        if st.button(label, key=f"example_{label}", use_container_width=True):
            st.session_state.selected_query = query

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""

# Define the state schema
class SupportState(TypedDict):
    messages: list
    intent: str
    resolved: bool

# Functions
def classify_intent(state: SupportState, llm) -> SupportState:
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

    return {
        **state,
        "intent": intent
    }

def handle_billing(state: SupportState, llm) -> SupportState:
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

def handle_technical(state: SupportState, llm) -> SupportState:
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

def handle_general(state: SupportState, llm) -> SupportState:
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

def route_query(state: SupportState) -> Literal["billing", "technical", "general"]:
    """Route to the appropriate handler based on classified intent."""
    return state["intent"]

def create_support_graph(llm):
    """Create and compile the support triage graph."""
    workflow = StateGraph(SupportState)

    # Add nodes with LLM passed to each function
    workflow.add_node("classify", lambda s: classify_intent(s, llm))
    workflow.add_node("billing", lambda s: handle_billing(s, llm))
    workflow.add_node("technical", lambda s: handle_technical(s, llm))
    workflow.add_node("general", lambda s: handle_general(s, llm))

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

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Customer Query")

    # Query input
    if st.session_state.selected_query:
        query = st.text_area(
            "Enter your support query:",
            value=st.session_state.selected_query,
            height=100,
            placeholder="Type your customer support question here..."
        )
        st.session_state.selected_query = ""
    else:
        query = st.text_area(
            "Enter your support query:",
            height=100,
            placeholder="Type your customer support question here..."
        )

    col_submit, col_clear = st.columns([1, 4])
    with col_submit:
        submit_button = st.button("🚀 Submit Query", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

with col2:
    st.header("📊 Statistics")
    total_queries = len([m for m in st.session_state.messages if isinstance(m, HumanMessage)])
    st.metric("Total Queries", total_queries)

    if st.session_state.messages:
        # Count intents
        billing_count = sum(1 for i, m in enumerate(st.session_state.messages)
                          if hasattr(m, 'additional_kwargs') and
                          m.additional_kwargs.get('intent') == 'billing')
        technical_count = sum(1 for i, m in enumerate(st.session_state.messages)
                            if hasattr(m, 'additional_kwargs') and
                            m.additional_kwargs.get('intent') == 'technical')
        general_count = sum(1 for i, m in enumerate(st.session_state.messages)
                          if hasattr(m, 'additional_kwargs') and
                          m.additional_kwargs.get('intent') == 'general')

        st.metric("🟢 Billing", billing_count)
        st.metric("🔴 Technical", technical_count)
        st.metric("🔵 General", general_count)

# Process query
if submit_button and query:
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar!")
    else:
        try:
            with st.spinner("🔄 Processing your query..."):
                # Initialize LLM
                llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

                # Create graph
                app = create_support_graph(llm)

                # Initialize state
                initial_state = {
                    "messages": [HumanMessage(content=query)],
                    "intent": "",
                    "resolved": False
                }

                # Run the graph
                result = app.invoke(initial_state)

                # Store intent in message metadata
                user_msg = HumanMessage(content=query)
                user_msg.additional_kwargs = {"intent": result["intent"]}

                # Add to session state
                st.session_state.messages.append(user_msg)
                st.session_state.messages.append(result["messages"][-1])

                st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display conversation history
if st.session_state.messages:
    st.divider()
    st.header("📜 Conversation History")

    for i in range(0, len(st.session_state.messages), 2):
        if i < len(st.session_state.messages):
            user_msg = st.session_state.messages[i]

            # Get intent if available
            intent = user_msg.additional_kwargs.get('intent', 'unknown') if hasattr(user_msg, 'additional_kwargs') else 'unknown'

            # Create expander for each conversation
            with st.expander(f"Query {i//2 + 1}: {user_msg.content[:50]}...", expanded=(i == len(st.session_state.messages) - 2)):
                st.markdown("**👤 Customer:**")
                st.info(user_msg.content)

                # Show intent badge
                if intent != 'unknown':
                    badge_class = intent
                    st.markdown(f'<div class="intent-badge {badge_class}">Intent: {intent.upper()}</div>', unsafe_allow_html=True)

                if i + 1 < len(st.session_state.messages):
                    ai_msg = st.session_state.messages[i + 1]
                    st.markdown("**🤖 Support Agent:**")
                    st.success(ai_msg.content)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Basic Example:</strong> Customer Support Triage Bot</p>
    <p>Demonstrates: Intent classification, conditional routing, specialized handlers</p>
    <p>Learn more: <a href="basic_README.md">basic_README.md</a></p>
</div>
""", unsafe_allow_html=True)
