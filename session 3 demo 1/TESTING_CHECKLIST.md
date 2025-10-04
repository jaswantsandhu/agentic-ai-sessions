# Testing Checklist

## Pre-Testing Setup

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Google Gemini API key obtained
- [ ] Sample PDF documents prepared

## Functional Testing

### 1. Application Launch
- [ ] Application starts without errors
- [ ] UI loads correctly in browser
- [ ] All sections visible (sidebar, upload, Q&A)
- [ ] No console errors

### 2. API Key Input
- [ ] API key input field visible in sidebar
- [ ] Password-type input (hidden characters)
- [ ] Help text displays correctly
- [ ] Key accepts valid Gemini API key

### 3. PDF Upload
- [ ] File uploader accepts PDF files
- [ ] Upload button works correctly
- [ ] File size limits respected
- [ ] Multiple upload attempts work

### 4. Text Extraction
- [ ] Text successfully extracted from text-based PDF
- [ ] Preview section displays extracted text
- [ ] Text is readable and properly formatted
- [ ] Success message appears

### 5. Error Handling - PDF
- [ ] Encrypted PDF detected and rejected with clear error
- [ ] Scanned PDF (no text) shows appropriate warning
- [ ] Invalid file format shows error message
- [ ] Empty PDF handled gracefully

### 6. Text Chunking & Embedding
- [ ] Document processing completes successfully
- [ ] Chunk count displayed correctly
- [ ] Vector store created without errors
- [ ] Processing time is reasonable (<30s for typical doc)

### 7. Question Answering
- [ ] Question input field accepts text
- [ ] "Get Answer" button functions
- [ ] Answer displays in info box
- [ ] Answer is relevant to document content
- [ ] Multiple questions work in sequence

### 8. Summarization
- [ ] "Generate Summary" button works
- [ ] Summary appears in success box
- [ ] Summary is concise (not too long/short)
- [ ] Summary captures key legal points
- [ ] Summary includes parties, terms, obligations

### 9. Session State
- [ ] Vector store persists across questions
- [ ] No need to re-upload for multiple queries
- [ ] State clears on page refresh
- [ ] No memory leaks with large documents

### 10. Error Handling - API
- [ ] Invalid API key shows clear error
- [ ] Network errors handled gracefully
- [ ] API quota exceeded shows helpful message
- [ ] Timeout errors managed properly

## Sample Questions Testing

### NDA Document
Test these questions and verify accuracy:
- [ ] "What is the duration of the confidentiality obligation?"
  - Expected: 5 years (or as per document)
- [ ] "Who are the parties involved?"
  - Expected: Lists both parties correctly
- [ ] "What are the exceptions to confidentiality?"
  - Expected: Lists 5 exceptions from Section 4
- [ ] "What happens in case of breach?"
  - Expected: Mentions equitable relief, injunction

### Service Agreement
Test these questions and verify accuracy:
- [ ] "What are the terms for termination?"
  - Expected: 60 days notice or immediate for breach
- [ ] "What are the payment terms?"
  - Expected: Initial fee + monthly maintenance
- [ ] "What services are included?"
  - Expected: Lists 4 main services
- [ ] "How long is the initial term?"
  - Expected: 12 months

### General Legal Questions
- [ ] "What is the governing law?" → Correct jurisdiction
- [ ] "Are there any liability limitations?" → Correct limits
- [ ] "What are renewal terms?" → Auto-renewal details
- [ ] "What are each party's obligations?" → Lists obligations

## UI/UX Testing

- [ ] Layout is responsive
- [ ] Text is readable (font size, contrast)
- [ ] Buttons are clearly labeled
- [ ] Error messages are user-friendly
- [ ] Success messages are encouraging
- [ ] Loading spinners appear during processing
- [ ] No UI elements overlap
- [ ] Sidebar toggle works
- [ ] Expand/collapse features work

## Performance Testing

- [ ] Small PDF (<5 pages) processes in <10s
- [ ] Medium PDF (5-20 pages) processes in <30s
- [ ] Large PDF (20-50 pages) completes without timeout
- [ ] Multiple questions answered quickly (<5s each)
- [ ] Summary generation completes in <10s
- [ ] No memory issues with session state

## Edge Cases

- [ ] Very long document (100+ pages)
- [ ] Document with special characters
- [ ] Document with tables and lists
- [ ] Document with multiple sections
- [ ] Empty question submission
- [ ] Very long question (500+ chars)
- [ ] Rapid-fire question submission
- [ ] Browser refresh during processing

## Security Testing

- [ ] API key not visible in page source
- [ ] API key not logged to console
- [ ] API key not stored in browser storage
- [ ] No sensitive data in URLs
- [ ] CORS properly configured
- [ ] XSS protection enabled

## Documentation Testing

- [ ] README.md is clear and complete
- [ ] QUICKSTART.md gets user running quickly
- [ ] All commands in docs work correctly
- [ ] Sample questions produce expected results
- [ ] Installation instructions accurate
- [ ] Deployment guide is followable

## Deployment Testing (Streamlit Cloud)

- [ ] App deploys successfully
- [ ] Environment variables/secrets configured
- [ ] All features work in deployed version
- [ ] No local-only dependencies
- [ ] URLs and links work correctly
- [ ] App accessible via public URL

## Regression Testing

After any code changes, verify:
- [ ] PDF upload still works
- [ ] Text extraction still works
- [ ] Question answering still accurate
- [ ] Summarization still functions
- [ ] All error handling intact
- [ ] No new console errors

## User Acceptance Testing

Have a test user verify:
- [ ] Interface is intuitive
- [ ] No training needed to use basic features
- [ ] Error messages are helpful
- [ ] Results are valuable
- [ ] Would use for actual work
- [ ] Performance meets expectations

## Final Checks

- [ ] All dependencies in requirements.txt
- [ ] No hardcoded API keys in code
- [ ] .gitignore properly configured
- [ ] README badges/links work
- [ ] License file included (if applicable)
- [ ] Code is commented appropriately

## Test Results Template

```
Test Date: ___________
Tester: ___________
Version: ___________

Passed: ___ / ___
Failed: ___ / ___
Blocked: ___ / ___

Critical Issues:
1. ___________
2. ___________

Minor Issues:
1. ___________
2. ___________

Notes:
___________
___________
```

## Known Issues / Limitations

Document any identified issues:
- [ ] Scanned PDFs not supported (expected)
- [ ] Requires internet for API calls (expected)
- [ ] Processing time varies with document size (expected)
- [ ]

## Sign-off

- [ ] All critical tests passed
- [ ] No blocking issues
- [ ] Minor issues documented
- [ ] Ready for user demo
- [ ] Ready for deployment

**Tested by**: _________________
**Date**: _________________
**Approved by**: _________________
**Date**: _________________
