# %%
import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableMap

from rich.console import Console
from rich.markdown import Markdown


# load .env file
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
chat_groq = ChatGroq(api_key=groq_key, model="llama-3.1-8b-instant")

google_key = os.getenv("GOOGLE_API_KEY")
chat_google = ChatGoogleGenerativeAI(
	api_key=google_key, model="gemini-2.5-flash")

llm = chat_google

# %%
system_prompt = SystemMessagePromptTemplate.from_template(
	"""You are an AI assistant that explains Unix commands in {lang}.
	Your answers must be accurate, minimal, and clear.
	Respond with a **very short** paragraph (2-3 sentences max),
	formatted in Markdown, that explains what the command does
	and when to use it.
	If useful, add **one concise code block example**, also in
	Markdown, showing the command and the expected output
	(1-3 sentences max, use ellipsis `...` if needed).
	Do not include any extra information or greetings.""",
	input_variables=["lang"])

user_prompt = HumanMessagePromptTemplate.from_template(
	"""Follow the previous instructions strictly.
Explain the following Unix command: `{cmd}`.
Do not add anything else beyond the explanation and example.""",
	input_variables=["cmd"])

chat_prompt = ChatPromptTemplate.from_messages(
	[
		system_prompt,
		user_prompt
	]
)
# filled_prompt = chat_prompt.format(cmd="Cayo Mario", lang="spanish")

chain = (
	RunnableMap({
		"cmd": lambda x: x["cmd"],
		"lang": lambda x: x["lang"]
	})
	| chat_prompt
	| llm
)


cmd = "ps aux"
lang = "spanish"
console = Console()

tokens = []
for token in chain.stream({"cmd": cmd, "lang": lang}):
	tokens.append(token)
	render_markup = Markdown(token.content)
	console.print(render_markup)
	# print(token.content, end="", flush=True)
