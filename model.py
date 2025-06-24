import os

from dotenv import load_dotenv

from langchain_cerebras import ChatCerebras
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI


# Load .env file
load_dotenv()

key_groq = os.getenv("GROQ_API_KEY")
key_google = os.getenv("GOOGLE_API_KEY")
key_cerebras = os.getenv("CEREBRAS_API_KEY")

# Groq Llama 4
chat_groq = ChatGroq(
	api_key=key_groq,  # type: ignore
	max_retries=2,
	model="meta-llama/llama-4-maverick-17b-128e-instruct",
	streaming=True,
	temperature=0,
	timeout=5000,
)

# Google Gemini 2.5
chat_google = ChatGoogleGenerativeAI(
	api_key=key_google,
	max_retries=2,
	model="gemini-2.5-flash",
	temperature=0,
	timeout=5000,
)

# Cerebras Qwen-3
chat_cerebras = ChatCerebras(
	api_key=key_cerebras,  # type: ignore
	max_retries=2,
	model="llama-4-scout-17b-16e-instruct",
	streaming=True,
	temperature=0,
	timeout=5000,
)


llm: None | ChatGroq | ChatGoogleGenerativeAI | ChatCerebras = None

if key_groq:
	llm = chat_groq
elif key_google:
	llm = chat_google
elif key_cerebras:
	llm = chat_cerebras
else:
	print("No API key found for Groq, Google, or Cerebras.")
	exit(1)
