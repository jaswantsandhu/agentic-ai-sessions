# Basic LangGraph Demo

A simple demonstration of LangGraph fundamentals, showing how to create a basic graph with nodes and edges.

## Overview

This demo illustrates the core concepts of LangGraph:
- **State Management**: Using TypedDict to define graph state
- **Nodes**: Functions that process and transform state
- **Edges**: Connections between nodes that define workflow
- **Graph Compilation**: Building and executing the graph

## Project Structure

```
session 4 demo basic setup of langgraph/
├── basic_langgraph_demo.py    # Main demo script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## How It Works

### 1. State Definition
The graph uses a `GraphState` TypedDict with:
- `messages`: List of strings (accumulated using operator.add)
- `counter`: Integer to track processing steps

### 2. Graph Structure
```
input_node → process_node → output_node → END
```

Each node:
- Receives the current state
- Performs its operation
- Returns updated state

### 3. Execution Flow
1. **Input Node**: Initializes processing
2. **Process Node**: Performs main computation
3. **Output Node**: Generates final result
4. **END**: Terminates the graph

## Running the Demo

```bash
python basic_langgraph_demo.py
```

### Expected Output

```
=== Basic LangGraph Demo ===

Running graph...

Messages:
  - Processing input...
  - Processing step 1
  - Generating output...

Final counter: 3
```

## Key Concepts

- **StateGraph**: The main graph class that manages state transitions
- **Annotated Types**: Using `Annotated[list[str], operator.add]` to specify how state is merged
- **Entry Point**: `set_entry_point()` defines where execution begins
- **Edges**: Define the flow between nodes
- **END**: Special constant marking graph termination

## Next Steps

To extend this demo, you could:
- Add conditional edges for branching logic
- Implement cycles for iterative processing
- Add error handling nodes
- Integrate with LLMs for AI-powered workflows
