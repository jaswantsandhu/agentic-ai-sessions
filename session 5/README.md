# Session 5: LangGraph Multi-Agent Systems

This session demonstrates four progressive examples of building multi-agent systems using LangGraph and OpenAI, showcasing different complexity levels and architectural patterns - from basic routing to advanced RAG integration.

## 📁 Files Overview

### 1. **basic.py** - Customer Support Triage Bot
**Complexity:** Beginner
**Concepts:** Basic routing, conditional edges, state management

A simple customer support bot that demonstrates fundamental LangGraph concepts through intent classification and routing.

**Architecture:**
```
User Query → Classify Intent → Route to Handler → Response
                                ├─ Billing Handler
                                ├─ Technical Handler
                                └─ General Handler
```

**Key Features:**
- Intent classification (billing/technical/general)
- Conditional routing based on classification
- Specialized handlers for each intent type
- Simple state management with TypedDict

**Use Case:** Automated customer support triage system

---

### 2. **medium.py** - Research Assistant with Tool Use
**Complexity:** Intermediate
**Concepts:** Tool calling, iterative loops, reflection, state accumulation

An intelligent research assistant that uses tools iteratively to gather information and synthesize comprehensive answers.

**Architecture:**
```
Query → Plan → Execute Tools → Evaluate → Synthesize
         ↑         ↓              ↓
         └─────────┴──────────────┘
              (Loop if needed)
```

**Key Features:**
- Multiple tools (web_search, calculator, get_current_date)
- Iterative research cycles with max iteration limits
- Progress evaluation and confidence scoring
- Tool result accumulation using Annotated types
- Dynamic decision making (continue vs. stop)

**Use Case:** Automated research and information gathering

---

### 3. **advance.py** - Multi-Agent Code Review System
**Complexity:** Advanced
**Concepts:** Multiple specialized agents, parallel execution, consensus building, human-in-the-loop

A sophisticated code review system with multiple specialized agents that collaborate, debate, and reach consensus on code quality.

**Architecture:**
```
Code → [Analyzer Agent] ──┐
       [Architect Agent] ──┼→ Coordinator → Evaluate
       [Security Agent] ───┘                   ↓
                                    ┌──────────┴──────────┐
                                    ↓                     ↓
                              Need Refinement?      Final Report
                                    ↓                     ↓
                              Reflection           Human Review
                                    ↓                     ↓
                              Back to Agents            END
```

**Key Features:**
- **Three specialized agents:**
  - Analyzer: Code quality, bugs, performance
  - Architect: Design patterns, structure, SOLID principles
  - Security: Vulnerabilities, best practices
- **Coordinator agent:** Synthesizes feedback, identifies conflicts
- **Reflection mechanism:** Agents refine opinions when conflicts arise
- **State accumulation:** Using `Annotated[List, operator.add]` for feedback collection
- **Human-in-the-loop:** Review checkpoint (simulated)
- **Consensus building:** Identifies agreements and conflicts
- **Iterative refinement:** Multiple review cycles

**Use Case:** Automated code review with multi-perspective analysis

---

### 4. **super_advance.py** - Customer Care RAG System with ChromaDB
**Complexity:** Super Advanced / Production-Ready
**Concepts:** RAG integration, vector databases, semantic search, customer context, ticket management, quality assurance

An enterprise-grade customer care system combining multi-agent architecture with Retrieval-Augmented Generation (RAG) using ChromaDB vector database for intelligent knowledge retrieval.

**Architecture:**
```
Query + Context → RAG (ChromaDB) → [Triage, Knowledge, Solution Agents]
                                          ↓
                                    Coordinator → Refinement Loop
                                          ↓
                              Final Response → QA Check → END
```

**Key Features:**
- **Five specialized agents:**
  - Triage: Category, priority, sentiment analysis, ticket creation
  - Knowledge Synthesis: Extract insights from retrieved documents
  - Solution Generation: Create actionable solutions with steps
  - Quality Assurance: Validate response quality
  - Coordinator: Orchestrate all agents and refinement
- **RAG Integration:** Semantic search with ChromaDB vector store
- **Customer Context:** Personalized responses based on tier, history, satisfaction
- **Knowledge Base:** Product docs + historical tickets embedded and searchable
- **Ticket Management:** Priority, categorization, escalation, estimated resolution
- **Iterative Refinement:** Loop back to RAG for additional context
- **Quality Assurance:** Automated response validation and scoring
- **Production Features:** Error handling, caching, monitoring ready

**Use Case:** Enterprise customer support, help desk automation, knowledge base integration

**Documentation:** See [super_advance_README.md](super_advance_README.md) for detailed guide

---

## 🚀 Setup

### 1. Install Dependencies

```bash
cd "session 5"
source .venv/bin/activate

# For basic, medium, advance examples:
pip install langgraph langchain-openai langchain-core

# For super_advance.py (includes ChromaDB):
pip install langgraph langchain-openai langchain-core langchain-community chromadb
```

### 2. Set OpenAI API Key

**Option 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option 2: .env File**

Create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Add to the top of each Python file:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Option 3: Directly in Code (Not Recommended)**
```python
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key="your-api-key-here")
```

---

## 🎯 Running the Examples

```bash
# Basic example - Customer support triage
python basic.py

# Medium example - Research assistant
python medium.py

# Advanced example - Multi-agent code review
python advance.py

# Super Advanced example - Customer care with RAG
python super_advance.py
```

---

## 🧠 Key LangGraph Concepts Demonstrated

### Progression from Basic to Super Advanced

| Concept | Basic | Medium | Advanced | **Super Advanced** |
|---------|-------|--------|----------|-------------------|
| **State Management** | Simple TypedDict | State with lists | Complex nested state | **15+ field state** |
| **Routing** | Conditional edges | Loop-back routing | Multi-level routing | **RAG-aware routing** |
| **Agents** | Single agent | Single agent + tools | Multiple specialized agents | **5 specialized agents** |
| **Iteration** | Single pass | Iterative with evaluation | Multi-round refinement | **RAG refinement loops** |
| **State Updates** | Direct updates | Accumulation | Operator-based merging | **Advanced accumulation** |
| **Tool Use** | None | Multiple tools | Agent-specific logic | **Extensible + RAG** |
| **Coordination** | N/A | Self-evaluation | Coordinator agent | **Multi-stage coordinator** |
| **Human Interaction** | None | None | Human-in-the-loop | **Context-aware** |
| **Knowledge Base** | ❌ | Mock data | ❌ | **✅ ChromaDB RAG** |
| **Vector Search** | ❌ | ❌ | ❌ | **✅ Semantic search** |
| **Personalization** | ❌ | ❌ | ❌ | **✅ Customer context** |
| **Quality Assurance** | ❌ | ❌ | ❌ | **✅ QA agent** |
| **Ticket System** | ❌ | ❌ | ❌ | **✅ Full management** |

### Common Patterns

1. **State Schema Design**
   - Use TypedDict for type safety
   - Use `Annotated[List, operator.add]` for accumulating feedback

2. **Node Functions**
   - Each node receives and returns state
   - Partial state updates merge automatically
   - Nodes should be focused and single-purpose

3. **Routing Strategies**
   - `add_edge()`: Direct transitions
   - `add_conditional_edges()`: Dynamic routing based on state
   - Loop-backs: Create iterative workflows

4. **Tool Integration**
   - Use `@tool` decorator for tool definitions
   - Bind tools to LLM with `llm.bind_tools()`
   - Handle tool calls in execution nodes

5. **Multi-Agent Coordination**
   - Each agent has specialized role/prompt
   - Coordinator synthesizes multiple perspectives
   - Reflection enables agent refinement

---

## 📊 Architectural Approaches

### 1. Linear Pipeline (basic.py)
- Best for: Simple workflows with clear decision points
- Pros: Easy to understand, predictable flow
- Cons: Limited flexibility

### 2. Iterative Loop (medium.py)
- Best for: Tasks requiring research or refinement
- Pros: Can gather comprehensive information
- Cons: Need careful iteration limits

### 3. Multi-Agent Collaboration (advance.py)
- Best for: Complex analysis requiring multiple perspectives
- Pros: Diverse viewpoints, robust analysis
- Cons: More complex, higher token usage

### 4. RAG-Enhanced Multi-Agent (super_advance.py)
- Best for: Knowledge-intensive tasks, customer support, help desk
- Pros: Semantic search, personalization, production-ready
- Cons: Requires vector database setup, more infrastructure

---

## 💡 Learning Path

1. **Start with basic.py**
   - Understand state graphs, nodes, edges
   - Learn conditional routing
   - Master basic state management

2. **Progress to medium.py**
   - Add tool integration
   - Implement iterative loops
   - Practice state accumulation

3. **Master advance.py**
   - Build multi-agent systems
   - Implement coordination logic
   - Handle complex state merging
   - Add human-in-the-loop patterns

4. **Excel at super_advance.py**
   - Integrate RAG with ChromaDB
   - Build production-ready systems
   - Implement customer context awareness
   - Add quality assurance systems
   - Handle enterprise-scale requirements

---

## 🔧 Common Modifications

### Change LLM Model
```python
# In any file, modify the model parameter
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # Faster, cheaper
llm = ChatOpenAI(model="gpt-4o", temperature=0)       # More capable
```

### Adjust Iteration Limits
```python
# In medium.py or advance.py
"max_iterations": 5  # Increase for more thorough analysis
```

### Add More Tools (medium.py)
```python
@tool
def your_custom_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result

tools = [web_search, calculator, get_current_date, your_custom_tool]
```

### Add More Agents (advance.py)
```python
# Create new specialized agent
performance_llm = create_agent_llm("performance")

def performance_agent(state: CodeReviewState) -> CodeReviewState:
    # Implementation
    pass

# Add to workflow
workflow.add_node("performance", performance_agent)
```

---

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)

---

## 🎓 Key Takeaways

1. **Start simple, add complexity gradually** - Each example builds on previous concepts
2. **State design is crucial** - Well-structured state makes complex flows manageable
3. **Agents specialize** - Give each agent a clear, focused role
4. **Iteration enables depth** - Loop-backs allow thorough analysis
5. **Coordination matters** - For multi-agent systems, coordinator logic is essential
6. **Tool use extends capabilities** - Integrate external tools for richer functionality
7. **Human-in-the-loop adds control** - Critical for production systems
8. **RAG amplifies intelligence** - Vector search + LLMs = powerful knowledge systems
9. **Context awareness drives personalization** - Customer data enables tailored responses
10. **Quality assurance builds trust** - Automated validation ensures consistency

## 📖 Detailed Documentation

Each Python file has its own comprehensive README:

- **[basic_README.md](basic_README.md)** - Customer Support Triage Bot guide
- **[medium_README.md](medium_README.md)** - Research Assistant with Tools guide
- **[advance_README.md](advance_README.md)** - Multi-Agent Code Review guide
- **[super_advance_README.md](super_advance_README.md)** - Customer Care RAG System guide

## 🌟 What Makes This Session Special

This is the **most comprehensive LangGraph tutorial series** covering:

✅ **Progressive Learning** - From basic to production-ready in 4 examples
✅ **Real-World Patterns** - Production-grade architectures and best practices
✅ **Complete Documentation** - 1000+ lines of detailed explanations
✅ **RAG Integration** - Modern vector database integration with ChromaDB
✅ **Enterprise Ready** - Error handling, monitoring, scalability considerations
✅ **Practical Examples** - Customer support, code review, research assistant
✅ **Best Practices** - State management, agent coordination, quality assurance
