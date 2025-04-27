from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os  

# Load environment variables
load_dotenv()

# Initialize the LLM model
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),  
    model_name="llama3-8b-8192"
)

if __name__ == "__main__":
    response = llm.invoke("What are the two main ingredients in a samosa?")
    print(response.content)