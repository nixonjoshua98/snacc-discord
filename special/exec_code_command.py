import os
import asyncio
import importlib

from discord.ext import commands

from typing import Callable

from src.common import checks


class PythonCode(commands.Converter):
	async def convert(self, ctx, argument):
		if not argument.startswith("```py") and not argument.endswith("```"):
			raise commands.CommandError("Python code should be wrapped as a Python code block.")

		elif "async def run(ctx)" not in argument:
			raise commands.CommandError("No function matching the signature `async def run(ctx)` found")

		return argument[5:-3]


@checks.snaccman_only()
@commands.command(name="exec")
async def exec_code(ctx: commands.Context, *, code: PythonCode()):
	"""[Snacc] Dynamically run code. VERY DANGEROUS! """

	path = os.path.join(os.getcwd(), "temp")

	os.makedirs(path, exist_ok=True)

	name = hash(ctx)

	with open(f"temp/{name}.py", "w") as fh:
		fh.write(code)

	result = "None"

	try:
		module: Callable = importlib.import_module(f"temp.{name}")

		if hasattr(module, "run") and asyncio.iscoroutinefunction(module.run):
			result = await module.run(ctx)

	except Exception as e:
		result = e

	os.remove(f"temp/{name}.py")

	del module

	await ctx.send(f'```{result or "OK"}```')
