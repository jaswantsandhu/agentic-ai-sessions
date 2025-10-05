"""
LangChain Expression Language (LCEL) Demo
Demonstrates the power of LCEL for building chains
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI


# Example 1: Simple Chain
def simple_chain_demo():
    """Basic LCEL chain: Prompt | LLM | Parser"""
    print("=== Example 1: Simple Chain ===\n")

    # Define components
    prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.7)
    output_parser = StrOutputParser()

    # Chain them with LCEL
    chain = prompt | model | output_parser

    # Run the chain
    result = chain.invoke({"topic": "programming"})
    print(f"Result: {result}\n")


# Example 2: Chain with Multiple Steps
def multi_step_chain_demo():
    """Chain with preprocessing and postprocessing"""
    print("=== Example 2: Multi-Step Chain ===\n")

    # Preprocessing function
    def preprocess(inputs: dict) -> dict:
        """Convert topic to uppercase"""
        return {"topic": inputs["topic"].upper()}

    # Postprocessing function
    def postprocess(text: str) -> str:
        """Add emoji to output"""
        return f"😄 {text}"

    prompt = ChatPromptTemplate.from_template("Write a haiku about {topic}")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.8)

    # Build chain with preprocessing and postprocessing
    chain = (
        RunnableLambda(preprocess)
        | prompt
        | model
        | StrOutputParser()
        | RunnableLambda(postprocess)
    )

    result = chain.invoke({"topic": "ocean"})
    print(f"Result: {result}\n")


# Example 3: Parallel Chains
def parallel_chains_demo():
    """Run multiple chains in parallel"""
    print("=== Example 3: Parallel Chains ===\n")

    from langchain_core.runnables import RunnableParallel

    prompt = ChatPromptTemplate.from_template("Describe {subject} in one word")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.5)
    parser = StrOutputParser()

    # Create a chain
    chain = prompt | model | parser

    # Run multiple prompts in parallel
    parallel_chain = RunnableParallel(
        adjective=chain,
        subject=RunnablePassthrough()
    )

    result = parallel_chain.invoke({"subject": "sunset"})
    print(f"Subject: {result['subject']['subject']}")
    print(f"Adjective: {result['adjective']}\n")


# Example 4: Chain with Fallbacks
def fallback_chain_demo():
    """Chain with error handling using fallbacks"""
    print("=== Example 4: Chain with Fallbacks ===\n")

    # Primary chain (might fail)
    primary_prompt = ChatPromptTemplate.from_template("Translate to French: {text}")
    primary_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    primary_chain = primary_prompt | primary_model | StrOutputParser()

    # Fallback chain
    fallback_prompt = ChatPromptTemplate.from_template("Translate to French: {text}")
    fallback_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    fallback_chain = fallback_prompt | fallback_model | StrOutputParser()

    # Chain with fallback
    chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])

    result = chain_with_fallback.invoke({"text": "Hello, how are you?"})
    print(f"Translation: {result}\n")


# Example 5: Chain with Retry
def retry_chain_demo():
    """Chain with automatic retry on failure"""
    print("=== Example 5: Chain with Retry ===\n")

    prompt = ChatPromptTemplate.from_template("Summarize in 10 words: {text}")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

    # Add retry logic
    chain = (prompt | model | StrOutputParser()).with_retry(
        stop_after_attempt=3,
        wait_exponential_jitter=True
    )

    result = chain.invoke({
        "text": "LangChain Expression Language (LCEL) makes it easy to build complex chains from basic components."
    })
    print(f"Summary: {result}\n")


# Example 6: Streaming Chain
def streaming_chain_demo():
    """Stream results from a chain"""
    print("=== Example 6: Streaming Chain ===\n")

    prompt = ChatPromptTemplate.from_template("Write a short story about {topic}")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.9, streaming=True)

    chain = prompt | model | StrOutputParser()

    print("Streaming output:")
    for chunk in chain.stream({"topic": "a robot learning to paint"}):
        print(chunk, end="", flush=True)
    print("\n")


# Example 7: Batch Processing
def batch_chain_demo():
    """Process multiple inputs in batch"""
    print("=== Example 7: Batch Processing ===\n")

    prompt = ChatPromptTemplate.from_template("What is the capital of {country}?")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

    chain = prompt | model | StrOutputParser()

    # Process multiple inputs at once
    inputs = [
        {"country": "France"},
        {"country": "Japan"},
        {"country": "Brazil"}
    ]

    results = chain.batch(inputs)
    for country_input, result in zip(inputs, results):
        print(f"{country_input['country']}: {result}")
    print()


# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("LangChain LCEL Demo")
    print("=" * 50)
    print()

    # Note: Make sure to set your GOOGLE_API_KEY environment variable
    import os
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Please set GOOGLE_API_KEY environment variable")
        print("   export GOOGLE_API_KEY='your-api-key'\n")
        exit(1)

    try:
        simple_chain_demo()
        multi_step_chain_demo()
        parallel_chains_demo()
        fallback_chain_demo()
        retry_chain_demo()
        streaming_chain_demo()
        batch_chain_demo()

        print("=" * 50)
        print("All demos completed successfully! ✅")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have set GOOGLE_API_KEY and have the required packages installed.")
