#!/usr/bin/env -S uv run --script
import argparse
import os
import time

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
	ChatPromptTemplate,
	HumanMessagePromptTemplate,
	SystemMessagePromptTemplate)
from langchain_core.runnables import RunnableMap

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status
from rich.text import Text


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
cmd_args = len(args.cmd_list) > 1
cmd = ' '.join(args.cmd_list) if cmd_args else args.cmd_list[0]

# Load .env file
load_dotenv()
console = Console()

google_key = os.getenv("GOOGLE_API_KEY")
chat_google = ChatGoogleGenerativeAI(
	api_key=google_key, model="gemini-2.5-flash")

llm = chat_google

system_prompt_single = SystemMessagePromptTemplate.from_template(
	"""You are an AI assistant that explains Unix commands in {lang}.
Your responses must be accurate, minimal, and clear with very rich Markdown.

Follow the style of TLDR pages, tealdeer or similar tools:

- Describe the general purpose of the command (2-3 sentences max).

- Show minimal usage or syntax of different uses (2-6 sentences max).

Do not include '$', '#', or any other symbols before the command or output.
Avoid extra commentary, greetings, or formatting outside the Markdown.""",
	input_variables=["lang"]
)

system_prompt_args = SystemMessagePromptTemplate.from_template(
	"""You are an AI assistant that explains Unix commands in {lang}.
Your responses must be accurate, minimal, and clear with very rich Markdown.

If the command has no arguments, follow the style of TLDR pages:

- Describe the general purpose of the command (2-3 sentences max).

- Show minimal usage or syntax of different uses.

In case of commands with arguments, follow this style:
Respond with a **very short** paragraph (2-3 sentences max),
formatted in Markdown (very rich), that explains what the command does and when to use it.
If the command includes multiple parts or arguments, briefly explain each part.

If helpful, include **a single compact code block example**, also in Markdown.
The code block should include both the command and its expected output,
all within **1-2 lines** and **no more than 80 characters wide**.
Ensure the command and output appear **together in the same code block**,
and that the Markdown syntax is complete and properly closed.

Do not include '$', '#', or any other symbols before the command or output.
Avoid extra commentary, greetings, or formatting outside the Markdown.""",
	input_variables=["lang"]
)

system_prompt = system_prompt_args if cmd_args else system_prompt_single

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

chain = (
	RunnableMap({
		"cmd": lambda x: x["cmd"],  # type: ignore
		"lang": lambda x: x["lang"]  # type: ignore
	})
	| chat_prompt
	| llm
)

tokens = []
content = ""

with Status("", spinner="bouncingBar", spinner_style="green") as status:
	# Esperar el primer token (sin actualizar Live aún)
	first_token = next(chain.stream({"cmd": cmd, "lang": lang}))
	tokens.append(first_token)
	content += first_token.content  # type: ignore

# 2. Cerrar el spinner y continuar con Live para el resto del stream
with Live(Text(content), console=console, transient=True) as live:
	for token in chain.stream({"cmd": cmd, "lang": lang}):
		tokens.append(token)
		content += token.content  # type: ignore
		live.update(Text(content))
	time.sleep(0.4)  # Pequeña pausa al final


# Show final result in Markdown
token_markdown = "".join(token.content for token in tokens)  # type: ignore
markdown = Markdown(token_markdown)
console.print(markdown)
