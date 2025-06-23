# %%
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# load .env file
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
chat_groq = ChatGroq(api_key=groq_key, model="llama-3.1-8b-instant")

google_key = os.getenv("GOOGLE_API_KEY")
chat_google = ChatGoogleGenerativeAI(
	api_key=google_key, model="gemini-2.0-flash")

llm = chat_google

# %%
# Normal
# llm_out = llm.invoke("Hello there")
# print(llm_out)

##########
# Stream #
##########
# Pedimos un stream de tokens en lugar de una respuesta completa
# Esto es útil para aplicaciones que necesitan mostrar resultados a medida que se generan
tokens = []
for token in llm.stream("Qué es NLP?"):
	tokens.append(token)
	print(token.content, end="|", flush=True)
