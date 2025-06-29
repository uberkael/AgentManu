#!/usr/bin/env -S uv run --script
import argparse
from argparse import RawTextHelpFormatter
import time

from langchain_core.prompts import (
	ChatPromptTemplate,
	HumanMessagePromptTemplate,
	SystemMessagePromptTemplate)

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status
from rich.text import Text

from model import llm


# Argparse
parser = argparse.ArgumentParser(
	description="Manual AI Agent Helper for Unix",
	epilog="https://github.com/uberkael/AgentManu\n© Kael <uberkael@gmail.com>",
	formatter_class=RawTextHelpFormatter,
	prog="AgentManu")
parser.add_argument(
	'-l', "-lang", "-i", "--idiom", "--language",
	dest='lang',
	help='Output Language',
	default='spanish')
parser.add_argument('-v', '--version',
	action='version',
	version="""%(prog)s 1.0\n
https://github.com/uberkael/AgentManu
© Kael <uberkael@gmail.com>""",
	help='Show program version and exit')
parser.add_argument(
	'cmd_list',
	nargs=argparse.REMAINDER,
	help='Command to explain')

args = parser.parse_args()
# Early exit if no command is provided
if len(args.cmd_list) < 1:
	parser.print_help()
	exit(0)
lang = args.lang.capitalize()
cmd_args = len(args.cmd_list) > 1
cmd = ' '.join(args.cmd_list) if cmd_args else args.cmd_list[0]

console = Console()

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
Respond with a **very short** paragraph (2-3 sentences max), formatted in
Markdown (very rich), that explains what the command does and when to use it.
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
	{  # type: ignore
		"cmd": lambda x: x["cmd"],
		"lang": lambda x: x["lang"]
	}
	| chat_prompt
	| llm
)

tokens = []
content = ""

with Status("", spinner="bouncingBar", spinner_style="green") as status:
	# Wait for the first token (do not update Live yet)
	first_token = next(chain.stream({"cmd": cmd, "lang": lang}))
	tokens.append(first_token)
	content += f"{first_token.content}█"  # type: ignore

# Close the spinner and continue with Live for the rest of the stream
with Live(Text(content), console=console, transient=True) as live:
	for token in chain.stream({"cmd": cmd, "lang": lang}):
		tokens.append(token)
		content = content.rstrip('█')
		content += f"{token.content}█"  # type: ignore
		live.update(Text(content))
	content = content.rstrip('█')
	live.update(Text(content))
	time.sleep(0.4)  # Pause at the end

# Show final result in Markdown
content_markdown = Markdown(content)
console.print(content_markdown)
