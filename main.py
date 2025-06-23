# %%
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap


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
	"""You are a AI assistant that helps generating very accurate explanations
	for unix commands in {lang}.
	The response need to be simple but complete.
	And it should be a single paragraph of explanation followed (if necessary)
	by a simple example.""",
	input_variables=["lang"])

user_prompt = HumanMessagePromptTemplate.from_template(
	"""Generate a paragraph explaining the following command {cmd}
	(and nothing more).""",
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
		"cmd": lambda x: x["topic"],
		"lang": lambda x: x["lang"]
	})
	| chat_prompt
	| llm
)

tokens = []
for token in chain.stream({"topic": "ls -l", "lang": "spanish"}):
	tokens.append(token)
	print(token.content, end="", flush=True)
