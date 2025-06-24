import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI

# Load .env file
load_dotenv()

# Groq
groq_key = os.getenv("GROQ_API_KEY")
chat_groq = ChatGroq(api_key=groq_key, model="meta-llama/llama-4-maverick-17b-128e-instruct")

# Google Gemini
google_key = os.getenv("GOOGLE_API_KEY")
chat_google = ChatGoogleGenerativeAI(
	api_key=google_key, model="gemini-2.5-flash")

# XAI
xai_key = os.getenv("XAI_API_KEY")
chat_xai = ChatXAI(
	model="grok-beta",
	temperature=0,
	max_tokens=None,
	timeout=None,
	max_retries=2,
	api_key=xai_key,
)


llm = chat_xai
