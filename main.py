#!/usr/bin/env -S uv run --script
# %%
import argparse
import os
import shutil
import sys
import time

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableMap

from rich.console import Console
from rich.markdown import Markdown


# Argparse
parser = argparse.ArgumentParser(
	prog="AgentManu",
	description="Manual AI Agent Helper for Unix",
	epilog="Tested on Arch Linux")
parser.add_argument(
	'-l', "-lang", "-i", "--idiom", "--language",
	dest='lang',
	help='Output Language',
	default='spanish')
parser.add_argument(
	'cmd_list',
	nargs=argparse.REMAINDER,
	help='Command to explain')

args = parser.parse_args()
lang = args.lang.capitalize()
cmd = ' '.join(args.cmd_list)
# print(f"Idioma: {lang}")
# print(f"Comando: {cmd}")

# load .env file
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
chat_groq = ChatGroq(api_key=groq_key, model="llama-3.1-8b-instant")  # type: ignore

google_key = os.getenv("GOOGLE_API_KEY")
chat_google = ChatGoogleGenerativeAI(
	api_key=google_key, model="gemini-2.5-flash")

llm = chat_google

# %%
system_prompt = SystemMessagePromptTemplate.from_template(
	"""You are an AI assistant that explains Unix commands in {lang}.
Your answers must be accurate, minimal, and clear.
Respond with a **very short** paragraph (2-3 sentences max),
formatted in Markdown, that explains what the command does and
when to use it.
If the command contains multiple parts or arguments,
briefly explain the purpose of each one.
If useful, add **one concise code block example**, also in
Markdown, showing the command and the expected output.
Make sure this examples are all in the same block of code and make it as compact
as posible (1-2 lines max) and not beyond 80 characters width.
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
		"cmd": lambda x: x["cmd"],  # type: ignore
		"lang": lambda x: x["lang"]  # type: ignore
	})
	| chat_prompt
	| llm
)

console = Console()
tokens = []
terminal_width = shutil.get_terminal_size((80, 20)).columns
printed_lines = 0
current_line = ""

for token in chain.stream({"cmd": cmd, "lang": lang}):
	tokens.append(token)
	content = token.content
	print(content, end="", flush=True)
	current_line += content  # type: ignore

time.sleep(1)
print()
print("-" * terminal_width)

# Calcular líneas visuales según ancho de terminal
# for line in current_line.splitlines() or [""]:
# 	# Si es más largo que el ancho, se envuelve
# 	wrapped_lines = (len(line) // terminal_width) + 1
# 	printed_lines += wrapped_lines
# printed_lines -= 1  # Terminal Prompt

# # Borrar cada línea visual
# for _ in range(printed_lines):
# 	sys.stdout.write("\033[F")  # Cursor up
# 	sys.stdout.write("\033[K")  # Clear line
# sys.stdout.flush()

# Mostrar resultado final en Markdown
for token in tokens:
	console.print(Markdown(token.content))  # type: ignore
