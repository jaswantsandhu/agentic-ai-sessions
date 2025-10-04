"""
Simple Gemini + LangChain Demo
This script demonstrates how to use Google's Gemini model with LangChain
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

def main():
    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )

    # Create a simple prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that answers questions concisely."),
        ("human", "{question}")
    ])

    # Create a chain
    chain = prompt | llm | StrOutputParser()

    # Example usage
    print("Gemini + LangChain Demo")
    print("-" * 50)

    # Ask a question
    question = "What are the three laws of robotics?"
    print(f"\nQuestion: {question}")

    response = chain.invoke({"question": question})
    print(f"\nResponse:\n{response}")

    # Another example with a different question
    question2 = "Explain quantum computing in one sentence."
    print(f"\n\nQuestion: {question2}")

    response2 = chain.invoke({"question": question2})
    print(f"\nResponse:\n{response2}")

if __name__ == "__main__":
    main()
