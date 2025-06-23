#!/usr/bin/env -S uv run --script
import argparse
import os
import shutil
import sys
import time

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
	SystemMessagePromptTemplate,
	HumanMessagePromptTemplate,
	ChatPromptTemplate)
from langchain_core.runnables import RunnableMap

from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status


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

# Load .env file
load_dotenv()

google_key = os.getenv("GOOGLE_API_KEY")
chat_google = ChatGoogleGenerativeAI(
	api_key=google_key, model="gemini-2.5-flash")

llm = chat_google

system_prompt = SystemMessagePromptTemplate.from_template(
	"""You are an AI assistant that explains Unix commands in {lang}.
Your answers must be accurate, minimal, and clear.
Respond with a **very short** paragraph (2-3 sentences max),
formatted in Markdown, that explains what the command does and when to use it.
If the command contains multiple parts or arguments, briefly explain each part.
If helpful, include **a single compact code block example**, also in Markdown.

The code block should contain both the command and its expected output,
all within **1-2 lines** and **no more than 80 characters wide**.
Ensure the command and output appear **together in the same code block**,
and that the Markdown syntax is complete and properly closed.
Do not include '$', '#', or any other symbols before the command or output.

Do not include any extra commentary, greetings, or explanations outside of that.
""",
	input_variables=["lang"]
)

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

console = Console()
tokens = []
terminal_width = shutil.get_terminal_size((80, 20)).columns
printed_lines = 0
current_line = ""

with Status("", spinner="bouncingBar", spinner_style="green") as status:
	for token in chain.stream({"cmd": cmd, "lang": lang}):
		tokens.append(token)
		content = token.content
		print(content, end="", flush=True)
		current_line += content  # type: ignore

time.sleep(0.4)

# Calculate visual lines according to terminal width
for line in current_line.splitlines() or [""]:
	# If it's longer than the width, it wraps
	wrapped_lines = (len(line) // terminal_width) + 1
	printed_lines += wrapped_lines
printed_lines -= 1  # Terminal Prompt + Spinner

# Erase each visual line
for _ in range(printed_lines):
	sys.stdout.write("\033[F")  # Cursor up
	sys.stdout.write("\033[K")  # Clear line
sys.stdout.flush()

# Show final result in Markdown
token_markdown = "".join(token.content for token in tokens)  # type: ignore
markdown = Markdown(token_markdown)
console.print(markdown)
