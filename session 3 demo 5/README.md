# Simple RAG Demo with LangChain

A beginner-friendly demonstration of Retrieval Augmented Generation (RAG) using LangChain and Google Gemini 2.0 Flash.

## What is RAG?

**RAG (Retrieval Augmented Generation)** is a technique that enhances LLM responses by:
1. **Retrieving** relevant information from a knowledge base
2. **Augmenting** the LLM prompt with this context
3. **Generating** an informed response based on the retrieved information

This prevents hallucinations and grounds responses in your actual data.

## How RAG Works

```
Question → Embed → Search Vector DB → Retrieve Top K Docs →
→ Add to Prompt → LLM → Generate Answer
```

## Project Structure

```
session 3 demo 5/
├── simple_rag.py       # Main RAG implementation
├── requirements.txt    # Python dependencies
└── README.md          # This file
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

## Components Explained

### 1. Document Loader
Loads text files into LangChain documents:
```python
loader = TextLoader("knowledge_base.txt")
documents = loader.load()
```

### 2. Text Splitter
Breaks documents into smaller chunks for better retrieval:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,      # Max characters per chunk
    chunk_overlap=50     # Overlap between chunks
)
```

### 3. Embeddings
Converts text to numerical vectors for similarity search:
```python
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
```

### 4. Vector Store (FAISS)
Stores and searches document embeddings efficiently:
```python
vectorstore = FAISS.from_documents(splits, embeddings)
```

### 5. Retriever
Finds the most relevant documents for a query:
```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # Return top 3 results
)
```

### 6. RAG Chain (LCEL)
Combines retrieval and generation:
```python
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

## Running the Demo

```bash
python simple_rag.py
```

## Expected Output

```
============================================================
Simple RAG Demo with LangChain & Gemini
============================================================

=== Setting up Vector Store ===

📄 Loaded 1 document(s)
✂️  Split into 5 chunks
🗄️  Created FAISS vector store with 5 vectors

=== Creating RAG Chain ===

✅ RAG chain created successfully

============================================================
DEMONSTRATION: How Retrieval Works
============================================================

🔍 Retrieving documents for: 'Explain what RAG is'

📚 Retrieved 3 relevant chunks:

Chunk 1:
RAG (Retrieval Augmented Generation) is a technique that combines information retrieval with
text generation...

============================================================
QUESTION & ANSWER SESSION
============================================================

============================================================
❓ Question: What is Python?
============================================================

💡 Answer:
Python is a high-level, interpreted programming language known for its simplicity
and readability. It was created by Guido van Rossum and first released in 1991.

...
```

## Demo Features

### 1. Knowledge Base Creation
Creates a sample text file with information about Python, LangChain, RAG, etc.

### 2. Retrieval Demonstration
Shows which document chunks are retrieved for a given question.

### 3. Question Answering
Answers multiple questions using the RAG chain:
- Questions the knowledge base can answer
- Questions it cannot answer (demonstrates graceful handling)

### 4. Automatic Cleanup
Removes temporary files after completion.

## Key Concepts

### Chunking Strategy
- **chunk_size=200**: Each chunk is max 200 characters
- **chunk_overlap=50**: 50 characters overlap between chunks
- **separators**: Splits on paragraphs, sentences, then words

### Similarity Search
Uses cosine similarity to find relevant chunks:
- Converts question to embedding
- Compares with all document embeddings
- Returns top K most similar chunks

### Context Window
Retrieved chunks are added to the prompt as context, allowing the LLM to answer based on your data.

## Customization

### Use Your Own Documents

Replace the `SAMPLE_DOCUMENTS` string or load from files:
```python
loader = TextLoader("your_document.txt")
# or
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("your_document.pdf")
```

### Adjust Retrieval Parameters

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Retrieve more documents
)
```

### Change Chunk Size

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Larger chunks
    chunk_overlap=100    # More overlap
)
```

### Modify the Prompt

```python
template = """Your custom prompt here.

Context: {context}
Question: {question}
Answer:"""
```

## Advantages of RAG

1. **Reduces Hallucinations**: Grounds responses in real data
2. **Up-to-date Information**: Use current documents without retraining
3. **Domain Expertise**: Add specialized knowledge easily
4. **Transparency**: See which sources were used
5. **Cost-effective**: No need to fine-tune models

## Common Use Cases

- **Customer Support**: Answer questions from documentation
- **Internal Knowledge Base**: Company policies, procedures
- **Research Assistant**: Query scientific papers
- **Code Documentation**: Search codebases and docs
- **Legal/Compliance**: Query regulations and contracts

## Troubleshooting

### Out of Memory
If using large documents, reduce chunk size or use a different vector store:
```bash
# For GPU support
pip install faiss-gpu
```

### Poor Retrieval Quality
- Increase chunk overlap
- Adjust chunk size
- Use better embeddings
- Increase `k` (number of retrieved documents)

### API Rate Limits
Add delays between requests or implement caching.

## Next Steps

Extend this demo by:
- Loading PDF, CSV, or HTML documents
- Using persistent vector stores (ChromaDB, Pinecone)
- Adding document metadata filtering
- Implementing hybrid search (keyword + semantic)
- Building a chat interface with memory
- Adding source citations to answers
- Implementing re-ranking for better results

## Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Google Gemini Embeddings](https://ai.google.dev/tutorials/python_quickstart)
- [Vector Database Comparison](https://python.langchain.com/docs/integrations/vectorstores/)
