# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd "session 3 demo 1"
pip install -r requirements.txt
```

If you encounter environment errors, use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Using the Application

### Step 1: Enter API Key
- In the sidebar, paste your Google Gemini API key
- The key is only stored in your session (not saved)

### Step 2: Upload a PDF
- Click "Browse files" to upload a legal PDF
- Wait for text extraction and processing
- View extracted text in the preview section

### Step 3: Ask Questions
- Type a question in the text input
- Click "Get Answer" to get AI-powered responses
- Or click "Generate Summary" for a document overview

## Sample Questions to Try

### For NDA Documents:
- "What is the duration of the confidentiality obligation?"
- "Who are the parties involved in this agreement?"
- "What are the exceptions to confidentiality?"
- "What happens in case of breach?"

### For Service Agreements:
- "What are the terms for termination?"
- "What are the payment terms and amounts?"
- "What services are included in this agreement?"
- "How long is the initial term?"

### For General Legal Documents:
- "What are the key obligations of each party?"
- "Are there any liability limitations?"
- "What is the governing law?"
- "What are the conditions for renewal?"

## Testing Without Sample PDFs

If you don't have sample PDFs ready:

1. **Download free legal templates**:
   - [Docracy](https://www.docracy.com/) - Free legal documents
   - [Rocket Lawyer](https://www.rocketlawyer.com/sem/free-legal-documents.rl) - Sample agreements
   - [LawDepot](https://www.lawdepot.com/) - Legal forms

2. **Use public documents**:
   - SEC EDGAR filings
   - Creative Commons licenses
   - Open source project licenses

3. **Create a simple PDF**:
   - Copy text from `sample_nda.txt`
   - Use Google Docs or Word to create a PDF
   - Save to your computer

## Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt
```

### "API Key Error"
- Verify your API key is correct
- Check you have Gemini API access enabled
- Ensure you have API quota remaining

### "No text could be extracted"
- Ensure PDF is text-based (not a scanned image)
- Try a different PDF document
- Check if PDF is encrypted

### "Slow processing"
- Large documents take longer
- First-time API calls may be slower
- Check your internet connection

## Features Overview

✅ **PDF Upload** - Text-based legal PDFs
✅ **Text Extraction** - PyPDF2 with error handling
✅ **Semantic Search** - FAISS vector embeddings
✅ **Question Answering** - RAG with Gemini 1.5 Flash
✅ **Document Summarization** - AI-generated summaries
✅ **Session Management** - Preserves state during session
✅ **Error Handling** - User-friendly error messages

## Architecture

```
User uploads PDF
    ↓
PyPDF2 extracts text
    ↓
RecursiveCharacterTextSplitter creates chunks (1000 chars, 200 overlap)
    ↓
Google Gemini creates embeddings
    ↓
FAISS stores vectors for fast search
    ↓
User asks question
    ↓
Question is embedded → FAISS finds top 4 similar chunks
    ↓
Chunks + question → Gemini 1.5 Flash → Answer
```

## Next Steps

- Try different types of legal documents
- Experiment with various question types
- Test the summarization feature
- Deploy to Streamlit Cloud for sharing

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [SAMPLE_DOCUMENTS.md](SAMPLE_DOCUMENTS.md) for test data
- Ensure all dependencies are installed correctly
