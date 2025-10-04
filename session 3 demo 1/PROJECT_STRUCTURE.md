# Project Structure

## Directory Tree

```
session 3 demo 1/
│
├── 📱 Core Application Files
│   ├── app.py                          # Main Streamlit application (9.3KB)
│   ├── requirements.txt                # Python dependencies
│   └── .env.example                    # Environment variables template
│
├── 📚 Documentation
│   ├── README.md                       # Comprehensive documentation (4.8KB)
│   ├── QUICKSTART.md                   # Quick start guide (4.0KB)
│   ├── PROJECT_SUMMARY.md              # Project overview (7.1KB)
│   ├── PROJECT_STRUCTURE.md            # This file
│   ├── SAMPLE_DOCUMENTS.md             # Guide for test documents (3.0KB)
│   └── TESTING_CHECKLIST.md            # Testing guidelines (6.7KB)
│
├── 🔧 Utilities
│   ├── simple_pdf_creator.py           # PDF creation script (5.6KB)
│   └── create_sample_pdf.py            # Alternative PDF creator (5.3KB)
│
├── 📄 Sample Data
│   ├── sample_nda.txt                  # Sample NDA text (4.8KB)
│   └── sample_documents/               # Directory for test PDFs
│
└── ⚙️ Configuration
    ├── .gitignore                      # Git ignore rules
    └── .streamlit/
        └── config.toml                 # Streamlit configuration
```

## File Descriptions

### Core Application Files

#### `app.py` (Main Application)
- **Purpose**: Primary Streamlit web application
- **Key Functions**:
  - `extract_text_from_pdf()` - PDF text extraction with error handling
  - `chunk_text()` - Text splitting using RecursiveCharacterTextSplitter
  - `create_vector_store()` - FAISS vector database creation
  - `answer_question()` - RAG-based Q&A pipeline
  - `generate_summary()` - Document summarization
- **Dependencies**: Streamlit, LangChain, PyPDF2, FAISS, Google Gemini
- **Session State**:
  - `vector_store` - FAISS database
  - `extracted_text` - PDF content
  - `chunks` - Text chunks

#### `requirements.txt`
- Streamlit 1.32.0
- LangChain 0.1.16
- langchain-google-genai 1.0.1
- PyPDF2 3.0.1
- faiss-cpu 1.8.0
- python-dotenv 1.0.1

#### `.env.example`
- Template for environment variables
- GOOGLE_API_KEY placeholder

### Documentation Files

#### `README.md`
- Complete project documentation
- Installation instructions
- Usage guide
- Architecture explanation
- Deployment instructions
- Troubleshooting guide

#### `QUICKSTART.md`
- 5-minute setup guide
- Step-by-step instructions
- Sample questions
- Common troubleshooting

#### `PROJECT_SUMMARY.md`
- Assignment requirements checklist
- Technology stack overview
- Implementation details
- Success metrics
- Future enhancements

#### `SAMPLE_DOCUMENTS.md`
- Guide for creating test PDFs
- Multiple methods provided
- Sample document descriptions
- Test questions for each type

#### `TESTING_CHECKLIST.md`
- Comprehensive test cases
- Functional testing scenarios
- Edge case coverage
- Performance benchmarks
- Security testing

### Utility Files

#### `simple_pdf_creator.py`
- Creates sample PDF documents
- Uses fpdf2 library
- Generates NDA and Service Agreement PDFs
- Fallback if reportlab unavailable

#### `create_sample_pdf.py`
- Alternative PDF creator
- Uses reportlab library
- More advanced formatting
- Professional document layout

### Sample Data

#### `sample_nda.txt`
- Complete NDA text content
- TechCorp Industries Inc. vs Digital Solutions LLC
- 5-year confidentiality term
- Comprehensive legal clauses

#### `sample_documents/`
- Directory for generated PDFs
- Test documents storage
- Ignored in git (.gitignore)

### Configuration

#### `.gitignore`
- Python cache files
- Virtual environments
- Environment variables (.env)
- IDE files
- OS files
- Generated PDFs

#### `.streamlit/config.toml`
- Streamlit theme configuration
- Server settings
- Security settings (CORS, XSRF)

## Data Flow Diagram

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       │ 1. Upload PDF
       ↓
┌─────────────────┐
│   Streamlit     │
│   Frontend      │
└────────┬────────┘
         │
         │ 2. Extract Text
         ↓
┌─────────────────┐
│    PyPDF2       │
│ Text Extraction │
└────────┬────────┘
         │
         │ 3. Split into Chunks
         ↓
┌──────────────────────┐
│ RecursiveCharacter   │
│   TextSplitter       │
└──────────┬───────────┘
           │
           │ 4. Generate Embeddings
           ↓
┌──────────────────────┐
│  Google Gemini       │
│  Embedding Model     │
└──────────┬───────────┘
           │
           │ 5. Store Vectors
           ↓
┌──────────────────────┐
│   FAISS Vector DB    │
└──────────┬───────────┘
           │
           │ 6. User Question
           ↓
┌──────────────────────┐
│  Similarity Search   │
│  (Top 4 Chunks)      │
└──────────┬───────────┘
           │
           │ 7. Context + Question
           ↓
┌──────────────────────┐
│  Gemini 1.5 Flash    │
│  (LLM Response)      │
└──────────┬───────────┘
           │
           │ 8. Display Answer
           ↓
┌──────────────────────┐
│  User Interface      │
└──────────────────────┘
```

## Technology Stack Visualization

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
│  ┌─────────────────────────────────┐   │
│  │         Streamlit UI            │   │
│  │  • File Upload                  │   │
│  │  • API Key Input                │   │
│  │  • Question Input               │   │
│  │  • Results Display              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Processing Layer                │
│  ┌─────────────────────────────────┐   │
│  │           LangChain             │   │
│  │  • Text Splitting               │   │
│  │  • Chain Management             │   │
│  │  • Prompt Templates             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           Data Layer                    │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   PyPDF2     │  │    FAISS     │    │
│  │ • Extract    │  │ • Vector DB  │    │
│  │ • Validate   │  │ • Search     │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│             AI Layer                    │
│  ┌─────────────────────────────────┐   │
│  │      Google Gemini API          │   │
│  │  • Gemini 1.5 Flash (LLM)       │   │
│  │  • Embedding Model              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Module Dependencies

```
app.py
├── streamlit
├── PyPDF2
│   └── BytesIO (from io)
├── langchain
│   ├── text_splitter.RecursiveCharacterTextSplitter
│   ├── vectorstores.FAISS
│   ├── chains.RetrievalQA
│   ├── prompts.PromptTemplate
│   └── schema.Document
└── langchain_google_genai
    ├── GoogleGenerativeAIEmbeddings
    └── ChatGoogleGenerativeAI
```

## Key Components Interaction

### 1. PDF Processing Pipeline
```
PDF File → PyPDF2.PdfReader → Extract Text → Validation → Display Preview
                                    ↓
                            Handle Encrypted/Scanned
```

### 2. Embedding Pipeline
```
Raw Text → RecursiveCharacterTextSplitter
            ↓
         Chunks (1000 chars, 200 overlap)
            ↓
         GoogleGenerativeAIEmbeddings
            ↓
         Vector Embeddings
            ↓
         FAISS.from_documents
            ↓
         Vector Store (Session State)
```

### 3. RAG Pipeline
```
User Question → Embed Question
                     ↓
              FAISS Similarity Search (Top 4)
                     ↓
              Retrieved Chunks
                     ↓
              Construct Context
                     ↓
              PromptTemplate (Context + Question)
                     ↓
              Gemini 1.5 Flash
                     ↓
              Generated Answer
```

## Session State Management

```python
st.session_state = {
    'vector_store': FAISS_instance,  # Persists between interactions
    'extracted_text': str,           # Cached PDF text
    'chunks': List[str]              # Text chunks
}
```

## File Sizes Summary

| File | Size | Purpose |
|------|------|---------|
| app.py | 9.3 KB | Main application |
| PROJECT_SUMMARY.md | 7.1 KB | Project overview |
| TESTING_CHECKLIST.md | 6.7 KB | Test scenarios |
| simple_pdf_creator.py | 5.6 KB | PDF generation |
| create_sample_pdf.py | 5.3 KB | Alt PDF creator |
| README.md | 4.8 KB | Documentation |
| sample_nda.txt | 4.8 KB | Sample data |
| QUICKSTART.md | 4.0 KB | Quick guide |
| SAMPLE_DOCUMENTS.md | 3.0 KB | Sample doc guide |

**Total Documentation**: ~40 KB
**Total Code**: ~20 KB
**Total Project**: ~60 KB

## Deployment Structure

### Local Development
```
session 3 demo 1/
└── Run: streamlit run app.py
```

### Streamlit Cloud
```
GitHub Repo
├── session 3 demo 1/
│   ├── app.py
│   ├── requirements.txt
│   └── .streamlit/config.toml
└── Streamlit Cloud Dashboard
    └── Secrets: GOOGLE_API_KEY
```

## Version Control

```
.gitignore excludes:
├── __pycache__/
├── venv/
├── .env
├── .vscode/
├── .DS_Store
└── sample_documents/*.pdf
```

## Quick Navigation

- **Start Here**: [QUICKSTART.md](QUICKSTART.md)
- **Full Docs**: [README.md](README.md)
- **Testing**: [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)
- **Overview**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **This File**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
