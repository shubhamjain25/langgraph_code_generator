from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_creative_llm_model() -> ChatGroq:

    # Initialize Groq LLM
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.7
    )

    return llm

def get_deterministic_llm_model() -> ChatGroq:

    # Initialize Groq LLM
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.1
    )

    return llm