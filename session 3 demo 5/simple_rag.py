"""
Simple RAG (Retrieval Augmented Generation) Demo with LangChain
Uses Google Gemini 2.0 Flash for generation and embeddings
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# Sample documents for our knowledge base
SAMPLE_DOCUMENTS = """
Python is a high-level, interpreted programming language known for its simplicity and readability.
It was created by Guido van Rossum and first released in 1991.

LangChain is a framework for developing applications powered by language models.
It provides tools for chaining together different components like prompts, models, and data sources.

RAG (Retrieval Augmented Generation) is a technique that combines information retrieval with
text generation. It retrieves relevant documents from a knowledge base and uses them as context
for generating responses.

Vector databases store data as high-dimensional vectors, enabling efficient similarity search.
They are essential for RAG systems as they allow quick retrieval of relevant documents.

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and
clustering of dense vectors. It's commonly used in RAG applications.
"""


def setup_vectorstore():
    """Create vector store directly from text"""
    print("=== Setting up Vector Store ===\n")

    # Create document directly from text
    documents = [Document(page_content=SAMPLE_DOCUMENTS, metadata={"source": "sample_knowledge"})]
    print(f"📄 Created {len(documents)} document(s)")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    splits = text_splitter.split_documents(documents)
    print(f"✂️  Split into {len(splits)} chunks")

    # Create embeddings and vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(splits, embeddings)
    print(f"🗄️  Created FAISS vector store with {len(splits)} vectors\n")

    return vectorstore


def create_rag_chain(vectorstore):
    """Create a RAG chain using LCEL"""
    print("=== Creating RAG Chain ===\n")

    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}  # Retrieve top 3 relevant chunks
    )

    # Create prompt template
    template = """You are a helpful assistant. Use the following context to answer the question.
If you don't know the answer based on the context, say so.

Context:
{context}

Question: {question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3
    )

    # Format retrieved documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Create RAG chain using LCEL
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ RAG chain created successfully\n")
    return rag_chain, retriever


def demo_retrieval(retriever, query):
    """Demonstrate the retrieval step"""
    print(f"🔍 Retrieving documents for: '{query}'")
    docs = retriever.get_relevant_documents(query)
    print(f"\n📚 Retrieved {len(docs)} relevant chunks:\n")
    for i, doc in enumerate(docs, 1):
        print(f"Chunk {i}:")
        print(f"{doc.page_content[:150]}...")
        print()


def ask_question(rag_chain, question):
    """Ask a question using the RAG chain"""
    print("=" * 60)
    print(f"❓ Question: {question}")
    print("=" * 60)

    response = rag_chain.invoke(question)

    print(f"\n💡 Answer:\n{response}\n")
    return response


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("Simple RAG Demo with LangChain & Gemini")
    print("=" * 60 + "\n")

    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Please set GOOGLE_API_KEY environment variable")
        print("   export GOOGLE_API_KEY='your-api-key'\n")
        exit(1)

    # Setup vector store
    vectorstore = setup_vectorstore()

    # Create RAG chain
    rag_chain, retriever = create_rag_chain(vectorstore)

    # Example questions
    questions = [
        "What is Python?",
        "Explain what RAG is",
        "What is FAISS used for?",
        "Who invented the internet?"  # This should say it doesn't know
    ]

    # First, demonstrate retrieval for one question
    print("=" * 60)
    print("DEMONSTRATION: How Retrieval Works")
    print("=" * 60 + "\n")
    demo_retrieval(retriever, questions[1])

    # Now answer all questions
    print("=" * 60)
    print("QUESTION & ANSWER SESSION")
    print("=" * 60 + "\n")

    for question in questions:
        ask_question(rag_chain, question)

    print("\n" + "=" * 60)
    print("RAG Demo Completed Successfully! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    main()
