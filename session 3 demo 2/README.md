# Resume Screening Application with LangChain

## Overview
This is a **Resume Screening Application** developed using **LangChain** that assists HR professionals in efficiently screening candidate resumes against job requirements. The application pulls text from uploaded resumes, analyzes them based on an AI model, and gives a detailed compatibility report with match scores, skills assessment, and suggestions.

## Scenario
A company is looking for a **Senior Python Developer** post and receives hundreds of résumé applications. The HR team needs to rapidly filter these resumes to discover candidates whose abilities, experience, and qualifications best match the job criteria. Manually examining each CV is time-consuming and prone to human bias, leading to potential oversight of eligible individuals. The team requires an automated system to analyze applications against the job description, provide a complete compatibility assessment, and select the best prospects for further examination.

## Problem Statement
Create a **Resume Screening Application** using LangChain that lets HR managers enter job requirements, submit a candidate's résumé (in PDF, DOCX, or TXT format), and examine the resume to find fit for the post. The application should extract text from the resume, compare it against the job requirements using an artificial intelligence model, and offer a structured analysis including a match score, skills assessment, experience relevance, education evaluation, strengths, weaknesses, and general candidate recommendation. The answer has to be easy to use, handle several file types, and let users download the analysis report for keeping records.

## Approach
Building a **Resume Screening Application** using **LangChain** and **Streamlit**, where users can:
- Input job requirements in a text area.
- Upload a resume in PDF, DOCX, or TXT format.
- Analyze the resume using Google's **Gemini 2.0 Flash** model to get a detailed compatibility report.
- Download the analysis as a TXT file for record-keeping.

The application uses **LangChain document loaders** (PyPDFLoader, Docx2txtLoader, TextLoader) to extract text from resumes, and **LangChain's LCEL** (LangChain Expression Language) with a custom prompt to generate a structured analysis. **Streamlit** provides a user-friendly interface with custom styling for better readability.

---

## 🚀 Features

- ✅ Upload resumes in **PDF, DOCX, or TXT** formats
- ✅ Extract and analyze resume content using **Google Gemini** model
- ✅ Score resume suitability in **percentage**
- ✅ Store analysis results in a **Chroma vector store**
- ✅ View **structured AI-generated feedback**
- ✅ Download analysis as a **text report**

---

## 📦 Tech Stack

- **LangChain** for building chains, embeddings, and document processing
- **LangChain Expression Language (LCEL)** for modular pipeline workflows
- **Streamlit** for the frontend web interface
- **Google Generative AI** (Gemini & Embeddings) for LLM and vector representations
- **Chroma** as a persistent vector store
- **dotenv** for API key and environment config

---

## 📄 Project Structure

```plaintext
session 3 demo 2/
├── app.py                  # Main Streamlit application
├── chroma_store/           # Folder to store vector DB files (auto-created)
├── .env                    # Contains API key (not committed to version control)
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Setup Instructions

### 1. Create a Virtual Environment

Navigate to the project directory and create a virtual environment:

```bash
cd "session 3 demo 2"
python -m venv venv
```

### 2. Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Ensure `requirements.txt` is in the project directory, then run:

```bash
pip install -r requirements.txt
```

### 4. Set Up the API Key

Create a `.env` file in the project directory and add your Google API key:

```
GOOGLE_API_KEY=your_api_key_here
```

> **Note:** You can get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5. Run the Application Locally

Run the following command to start the Streamlit app:

```bash
streamlit run app.py
```

Open the provided URL (e.g., `http://localhost:8501`) in your browser to access the app.

---

## ☁️ Deploying on Streamlit Cloud

### 1. Prepare Your Project

- Ensure `app.py`, `requirements.txt`, and `.env.example` are in the project directory.
- Create a **Streamlit Cloud** account at [https://streamlit.io/cloud](https://streamlit.io/cloud).

### 2. Upload to Streamlit Cloud

- Log in to **Streamlit Cloud**.
- Create a new app and connect it to your project repository (GitHub, GitLab, etc.).
- Specify `app.py` as the main script.

### 3. Configure Environment Variables

- In Streamlit Cloud, go to your app's **settings**.
- Add the `GOOGLE_API_KEY` as a **secret environment variable**.
- **Do not** include the `.env` file in your uploaded files for security.

### 4. Deploy the App

- Click **"Deploy"** in Streamlit Cloud.
- Once deployed, access the app via the provided URL (e.g., `https://your-app-name.streamlit.app`).

### 5. Test the Deployed App

- Input job requirements, upload a resume, and analyze it.
- Verify that the analysis report is generated and downloadable.

---

## 📚 LangChain Concepts Used

- ✅ **Components & Modules**: PromptTemplate, LLM, Output Parsers
- 📄 **Document Loaders**: PDF, DOCX, TXT via LangChain community
- ✂️ **Text Splitting**: RecursiveCharacterTextSplitter
- 🧠 **Embeddings**: GoogleGenerativeAIEmbeddings
- 🗃️ **Vector DB**: Chroma for persistent storage
- 🧩 **LCEL**: RunnableMap, pipes (`|`), and chain composition
- 🧪 **Chains**: Custom chain for job/resume comparison
- 📤 **Deployment**: Streamlit as the UI layer

---

## 📝 Usage

1. **Run the app** locally or access the deployed version on Streamlit Cloud.
2. **Enter job requirements** in the text area (e.g., skills, experience, qualifications).
3. **Upload a resume** in PDF, DOCX, or TXT format.
4. **Click "Analyze Resume"** to generate the AI-driven analysis.
5. **Review the structured report**, including match score, skills assessment, and recommendation.
6. **Download the analysis** as a TXT file for records.

---

## 📈 Example Output

```
Structured Analysis:
- Strengths: Relevant experience, strong communication skills, etc.
- Weaknesses: Lacks experience in X, missing Y certification...

Suitability Score: 84%
```

---

## 🧑‍💼 Ideal For

- HR professionals and recruiters
- Resume screening automation tools
- Educational and project demos for LangChain and LCEL
- Hackathons and AI/ML showcases

---

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use `.env.example` as a template for required environment variables
- When deploying to Streamlit Cloud, use their secrets management feature

---

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements or bug fixes.

---

## 📧 Support

For issues or questions, please create an issue in the project repository.

---

**Built with ❤️ using LangChain, LCEL, and Streamlit**
