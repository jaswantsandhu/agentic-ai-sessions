# Legal Document Review Application

A web-based AI-powered application for analyzing legal documents using LangChain, Google Gemini, and FAISS vector search.

## Features

- 📄 **PDF Upload**: Upload text-based legal PDF documents
- 🔍 **Semantic Search**: RAG-based question answering using FAISS vector embeddings
- 📝 **Document Summarization**: AI-generated summaries of key legal points
- 💬 **Interactive Q&A**: Ask specific questions about document content
- 🔒 **Secure**: API key input via sidebar (not stored)
- ⚡ **Fast**: Efficient vector search with FAISS

## Technology Stack

- **Frontend**: Streamlit
- **LLM Framework**: LangChain
- **AI Model**: Google Gemini 1.5 Flash
- **Embeddings**: Google Gemini Embedding Model
- **Vector Store**: FAISS
- **PDF Processing**: PyPDF2

## Installation

1. Clone or navigate to this directory:
```bash
cd "session 3 demo 1"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get a Google Gemini API key:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Enter your Google Gemini API key in the sidebar

3. Upload a legal PDF document (text-based, not scanned)

4. Wait for processing to complete

5. Ask questions or generate a summary

## Sample Use Cases

### Non-Disclosure Agreement (NDA)
- **Question**: "What is the duration of the confidentiality obligation?"
- **Question**: "What are the consequences of breach?"

### Service Agreement
- **Question**: "What are the terms for termination?"
- **Question**: "What are the payment terms?"

### Licensing Contract
- **Question**: "What are the key obligations?"
- **Question**: "What is the license duration?"

## How It Works

1. **PDF Text Extraction**: PyPDF2 extracts text from uploaded PDFs
2. **Text Chunking**: RecursiveCharacterTextSplitter divides text into 1000-character chunks with 200-character overlap
3. **Embedding Generation**: Google Gemini embedding model converts chunks to vectors
4. **Vector Storage**: FAISS stores embeddings for fast similarity search
5. **Question Answering**:
   - User question is embedded
   - Top 4 similar chunks are retrieved
   - Context + question sent to Gemini 1.5 Flash
   - AI generates answer based on document content
6. **Summarization**: Top 6 relevant chunks are used to generate a concise summary

## Error Handling

- ❌ Encrypted PDFs are detected and rejected
- ❌ Scanned PDFs with no extractable text are handled
- ❌ API errors are caught and displayed to users
- ❌ Invalid inputs are validated

## Configuration

### Environment Variables (Optional)
Create a `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

### Session State Management
- Vector store is maintained in session state
- Extracted text is cached
- Chunks are preserved for the session

## Deployment

### Streamlit Community Cloud

1. Push code to GitHub repository

2. Visit [Streamlit Cloud](https://streamlit.io/cloud)

3. Deploy from GitHub repository

4. Add `GOOGLE_API_KEY` to Streamlit secrets:
```toml
GOOGLE_API_KEY = "your_api_key_here"
```

5. Update app.py to read from secrets if needed:
```python
api_key = st.secrets.get("GOOGLE_API_KEY", "")
```

## File Structure

```
session 3 demo 1/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── .env.example           # Environment variable template
└── sample_documents/      # Sample legal documents for testing
```

## Limitations

- Only works with text-based PDFs (not scanned images)
- Requires Google Gemini API key
- Processing time depends on document size
- Accuracy depends on document quality and clarity

## Security Notes

- API keys are entered via password-protected input
- Keys are stored only in session state (not persisted)
- No document data is stored permanently
- For production use, implement proper authentication

## Troubleshooting

### "No text could be extracted"
- Ensure PDF is text-based, not a scanned image
- Try OCR preprocessing for scanned documents

### "API Key Error"
- Verify API key is correct
- Check API key has Gemini API enabled
- Ensure you have API quota remaining

### Slow Processing
- Large documents take longer to process
- Consider chunking strategy adjustments
- Check internet connection for API calls

## Future Enhancements

- Support for scanned PDFs with OCR
- Multi-document comparison
- Export summaries and Q&A to PDF/Word
- Document clause extraction
- Legal risk scoring
- Multi-language support

## License

This project is for educational purposes.

## Author

Built with LangChain and Google Gemini AI
