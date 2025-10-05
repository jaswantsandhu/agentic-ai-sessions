"""
Basic LangGraph Demo
This demonstrates a simple graph setup with LangGraph
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator


# Define the state
class GraphState(TypedDict):
    messages: Annotated[list[str], operator.add]
    counter: int


# Define nodes
def input_node(state: GraphState) -> GraphState:
    """Process initial input"""
    return {
        "messages": ["Processing input..."],
        "counter": state.get("counter", 0) + 1
    }


def process_node(state: GraphState) -> GraphState:
    """Process the data"""
    return {
        "messages": [f"Processing step {state['counter']}"],
        "counter": state["counter"] + 1
    }


def output_node(state: GraphState) -> GraphState:
    """Generate output"""
    return {
        "messages": ["Generating output..."],
        "counter": state["counter"] + 1
    }


# Build the graph
def create_graph():
    """Create and configure the graph"""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("process", process_node)
    workflow.add_node("output", output_node)

    # Add edges
    workflow.set_entry_point("input")
    workflow.add_edge("input", "process")
    workflow.add_edge("process", "output")
    workflow.add_edge("output", END)

    # Compile the graph
    app = workflow.compile()
    return app


# Run the demo
if __name__ == "__main__":
    print("=== Basic LangGraph Demo ===\n")

    # Create the graph
    graph = create_graph()

    # Initial state
    initial_state = {
        "messages": [],
        "counter": 0
    }

    # Run the graph
    print("Running graph...\n")
    result = graph.invoke(initial_state)

    # Display results
    print("Messages:")
    for msg in result["messages"]:
        print(f"  - {msg}")
    print(f"\nFinal counter: {result['counter']}")
