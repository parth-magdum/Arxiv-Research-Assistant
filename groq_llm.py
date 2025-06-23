from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base=os.getenv("GROQ_API_BASE"),
    model=os.getenv("GROQ_MODEL"),
    temperature=0.2
)
