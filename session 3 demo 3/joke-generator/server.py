from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langserve import add_routes
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that generates clean and funny jokes."),
    ("human", "Tell me a joke about {topic}.")
])

# Initialize the Gemini model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Create the output parser
output_parser = StrOutputParser()

# Build the chain
chain = prompt | model | output_parser

# Initialize FastAPI app
app = FastAPI(
    title="Joke Generator API",
    version="1.0",
    description="A simple API for generating jokes using Google Gemini 1.5 Flash"
)

# Add the chain route
add_routes(
    app,
    chain,
    path="/joke-generator"
)

# Homepage route
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Joke Generator API",
        "docs": "/docs",
        "playground": "/joke-generator/playground/"
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
