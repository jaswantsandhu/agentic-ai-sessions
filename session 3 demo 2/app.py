import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableMap, RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import tempfile
import re

# Load environment variables
load_dotenv()

# Set up API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Resume Screening Application",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .score-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .analysis-section {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📄 Resume Screening Application</h1>', unsafe_allow_html=True)
st.markdown("### Powered by LangChain & Google Gemini 2.0")

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

# Initialize LLM and Embeddings
@st.cache_resource
def initialize_llm():
    return GoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)

@st.cache_resource
def initialize_embeddings():
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

llm = initialize_llm()
embeddings = initialize_embeddings()

# Function to load resume based on file type
def load_resume(uploaded_file):
    """Load and extract text from uploaded resume file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Determine file type and use appropriate loader
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        if file_extension == '.pdf':
            loader = PyPDFLoader(tmp_file_path)
        elif file_extension in ['.docx', '.doc']:
            loader = Docx2txtLoader(tmp_file_path)
        elif file_extension == '.txt':
            loader = TextLoader(tmp_file_path)
        else:
            st.error("Unsupported file format. Please upload PDF, DOCX, or TXT file.")
            return None

        documents = loader.load()

        # Clean up temporary file
        os.unlink(tmp_file_path)

        return documents
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        return None

# Function to split text into chunks
def split_text(documents):
    """Split documents into smaller chunks for processing"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

# Function to create vector store
def create_vector_store(chunks):
    """Create a Chroma vector store from document chunks"""
    try:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_store"
        )
        return vectorstore
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None

# Create analysis prompt template
analysis_prompt = PromptTemplate(
    input_variables=["job_requirements", "resume_content"],
    template="""
You are an expert HR professional and resume analyzer. Analyze the following resume against the job requirements and provide a detailed, structured assessment.

Job Requirements:
{job_requirements}

Resume Content:
{resume_content}

Please provide a comprehensive analysis in the following structure:

**MATCH SCORE**: Provide a percentage score (0-100%) indicating how well the candidate matches the job requirements.

**SKILLS ASSESSMENT**:
- List the relevant skills found in the resume that match the job requirements
- Identify missing critical skills

**EXPERIENCE RELEVANCE**:
- Evaluate the candidate's work experience in relation to the job requirements
- Highlight relevant projects or achievements

**EDUCATION EVALUATION**:
- Assess the candidate's educational background
- Note any relevant certifications or training

**STRENGTHS**:
- List 3-5 key strengths of the candidate for this position

**WEAKNESSES/GAPS**:
- Identify 2-4 areas where the candidate may fall short

**OVERALL RECOMMENDATION**:
- Provide a clear recommendation (Highly Recommended / Recommended / Consider with Reservations / Not Recommended)
- Brief justification for the recommendation

**ADDITIONAL NOTES**:
- Any other relevant observations or suggestions

Please be objective, fair, and thorough in your analysis.
"""
)

# Function to extract score from analysis
def extract_score(analysis_text):
    """Extract the match score percentage from analysis text"""
    match = re.search(r'(\d+)%', analysis_text)
    if match:
        return match.group(1)
    return "N/A"

# Create the analysis chain using LCEL
def create_analysis_chain():
    """Create a LangChain chain for resume analysis using LCEL"""

    # Create the chain using RunnableMap and pipe operator
    chain = (
        RunnableMap({
            "job_requirements": lambda x: x["job_requirements"],
            "resume_content": lambda x: x["resume_content"]
        })
        | analysis_prompt
        | llm
        | StrOutputParser()
    )

    return chain

# Main application layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<h2 class="sub-header">📋 Job Requirements</h2>', unsafe_allow_html=True)
    job_requirements = st.text_area(
        "Enter the job requirements, skills, and qualifications:",
        height=300,
        placeholder="Example:\n- 5+ years of Python development experience\n- Strong knowledge of Django/Flask frameworks\n- Experience with RESTful APIs\n- Familiarity with cloud platforms (AWS/Azure)\n- Bachelor's degree in Computer Science or related field"
    )

with col2:
    st.markdown('<h2 class="sub-header">📎 Upload Resume</h2>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload candidate's resume (PDF, DOCX, or TXT):",
        type=['pdf', 'docx', 'doc', 'txt']
    )

    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / 1024:.2f} KB")

# Analysis button
st.markdown("---")
analyze_button = st.button("🔍 Analyze Resume", use_container_width=True, type="primary")

if analyze_button:
    if not job_requirements:
        st.error("❌ Please enter job requirements before analyzing.")
    elif not uploaded_file:
        st.error("❌ Please upload a resume before analyzing.")
    else:
        with st.spinner("🔄 Analyzing resume... This may take a few moments."):
            try:
                # Load resume
                documents = load_resume(uploaded_file)

                if documents:
                    # Extract full text from documents
                    resume_text = "\n".join([doc.page_content for doc in documents])
                    st.session_state.resume_text = resume_text

                    # Split text into chunks
                    chunks = split_text(documents)

                    # Create vector store
                    vectorstore = create_vector_store(chunks)

                    if vectorstore:
                        st.success("✅ Vector store created successfully!")

                        # Create analysis chain
                        analysis_chain = create_analysis_chain()

                        # Run analysis
                        analysis_result = analysis_chain.invoke({
                            "job_requirements": job_requirements,
                            "resume_content": resume_text[:4000]  # Limit to avoid token limits
                        })

                        st.session_state.analysis_result = analysis_result

                        st.success("✅ Analysis completed!")
                    else:
                        st.error("❌ Failed to create vector store.")
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")

# Display results
if st.session_state.analysis_result:
    st.markdown("---")
    st.markdown('<h2 class="sub-header">📊 Analysis Results</h2>', unsafe_allow_html=True)

    # Extract and display score
    score = extract_score(st.session_state.analysis_result)
    if score != "N/A":
        st.markdown(f'<div class="score-box">🎯 Match Score: {score}%</div>', unsafe_allow_html=True)

    # Display full analysis
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown(st.session_state.analysis_result)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download button for analysis
    st.download_button(
        label="📥 Download Analysis Report",
        data=st.session_state.analysis_result,
        file_name="resume_analysis_report.txt",
        mime="text/plain",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with ❤️ using LangChain, LCEL, and Streamlit</p>
    <p>Powered by Google Gemini 2.0 Flash & Chroma Vector Store</p>
</div>
""", unsafe_allow_html=True)
