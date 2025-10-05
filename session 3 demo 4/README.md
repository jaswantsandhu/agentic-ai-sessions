# LangChain Expression Language (LCEL) Demo

A comprehensive demonstration of LangChain Expression Language (LCEL) using Google's Gemini 2.0 Flash model.

## Overview

This demo showcases the power and flexibility of LCEL for building AI chains. LCEL provides a declarative way to compose chains using the pipe (`|`) operator, making it easy to build complex workflows from simple components.

## What is LCEL?

LangChain Expression Language (LCEL) is a declarative way to compose chains in LangChain. Key benefits include:
- **Composability**: Chain components together with the `|` operator
- **Streaming Support**: Built-in streaming capabilities
- **Async Support**: Native async/await support
- **Parallel Execution**: Run multiple chains concurrently
- **Fallbacks & Retries**: Built-in error handling
- **Batch Processing**: Process multiple inputs efficiently

## Project Structure

```
session 3 demo 4/
├── lcel_demo.py         # Main demo with 7 examples
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Google API key:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Get your API key from: https://makersuite.google.com/app/apikey

## Demo Examples

### Example 1: Simple Chain
Basic LCEL chain demonstrating the core concept: `Prompt | LLM | Parser`

```python
chain = prompt | model | output_parser
result = chain.invoke({"topic": "programming"})
```

### Example 2: Multi-Step Chain
Chain with preprocessing and postprocessing using `RunnableLambda`:

```python
chain = (
    RunnableLambda(preprocess)
    | prompt
    | model
    | StrOutputParser()
    | RunnableLambda(postprocess)
)
```

### Example 3: Parallel Chains
Execute multiple chains in parallel using `RunnableParallel`:

```python
parallel_chain = RunnableParallel(
    adjective=chain,
    subject=RunnablePassthrough()
)
```

### Example 4: Chain with Fallbacks
Automatic fallback to backup chain if primary fails:

```python
chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])
```

### Example 5: Chain with Retry
Automatic retry logic with exponential backoff:

```python
chain = (prompt | model | StrOutputParser()).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)
```

### Example 6: Streaming Chain
Stream results as they're generated:

```python
for chunk in chain.stream({"topic": "a robot learning to paint"}):
    print(chunk, end="", flush=True)
```

### Example 7: Batch Processing
Process multiple inputs efficiently in a single batch:

```python
results = chain.batch([
    {"country": "France"},
    {"country": "Japan"},
    {"country": "Brazil"}
])
```

## Running the Demo

Execute the demo script:

```bash
python lcel_demo.py
```

### Expected Output

```
==================================================
LangChain LCEL Demo
==================================================

=== Example 1: Simple Chain ===
Result: [A programming joke from Gemini]

=== Example 2: Multi-Step Chain ===
Result: 😄 [A haiku about the ocean]

... (more examples)

==================================================
All demos completed successfully! ✅
==================================================
```

## Key Concepts Demonstrated

### The Pipe Operator (`|`)
The core of LCEL - chains components sequentially:
```python
chain = component1 | component2 | component3
```

### Runnables
All LCEL components implement the `Runnable` interface with methods:
- `invoke()`: Single input execution
- `batch()`: Multiple inputs execution
- `stream()`: Streaming output
- `ainvoke()`, `abatch()`, `astream()`: Async versions

### RunnableLambda
Wraps Python functions to make them LCEL-compatible:
```python
RunnableLambda(lambda x: x.upper())
```

### RunnableParallel
Executes multiple chains concurrently:
```python
RunnableParallel(task1=chain1, task2=chain2)
```

### RunnablePassthrough
Passes input through unchanged (useful for parallel chains):
```python
RunnablePassthrough()
```

## Why Use LCEL?

1. **Readability**: Chains read like natural pipelines
2. **Modularity**: Easy to swap components
3. **Performance**: Built-in optimizations for streaming and batching
4. **Error Handling**: Simple fallbacks and retries
5. **Type Safety**: Better IDE support and type checking
6. **Observability**: Built-in support for tracing and monitoring

## Using Gemini 2.0 Flash

This demo uses Google's Gemini 2.0 Flash model (`gemini-2.0-flash-exp`):
- Fast response times
- High-quality outputs
- Cost-effective
- Supports streaming

## Troubleshooting

### API Key Issues
```
⚠️ Please set GOOGLE_API_KEY environment variable
```
**Solution**: Export your Google API key:
```bash
export GOOGLE_API_KEY='your-api-key'
```

### Import Errors
```
ModuleNotFoundError: No module named 'langchain_google_genai'
```
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Rate Limiting
If you hit rate limits, the retry logic (Example 5) will automatically retry with exponential backoff.

## Next Steps

Extend these examples by:
- Adding custom output parsers
- Implementing conditional branching
- Creating agent workflows
- Building RAG (Retrieval Augmented Generation) pipelines
- Adding memory to chains
- Integrating with vector databases
- Creating multi-agent systems

## Resources

- [LangChain LCEL Documentation](https://python.langchain.com/docs/expression_language/)
- [Google Gemini API](https://ai.google.dev/)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)
