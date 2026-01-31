from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load variables from .env into the system environment
load_dotenv() 

def get_llm():
    return ChatOpenAI(
        model="gpt-4",
        temperature=0
    )
