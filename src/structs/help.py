import discord

from discord.ext.commands import HelpCommand

from src import inputs


class Help(HelpCommand):
	def __init__(self):
		super(Help, self).__init__(verify_checks=False)

	async def update_bot_mapping(self, mapping):
		for k, v in mapping.items():
			mapping[k] = await self.filter_commands(v)

		return {k: v for k, v in mapping.items() if k is not None and v}

	async def create_embeds(self, mapping):
		bot = self.context.bot

		embeds = []

		mapping = await self.update_bot_mapping(mapping)

		for i, (cog, cog_cmds) in enumerate(mapping.items()):
			cog_cmds = await self.filter_commands(cog_cmds, sort=True)

			chunked_cmds = [cog_cmds[i:i + 10] for i in range(0, len(cog_cmds), 10)]

			for j, chunk in enumerate(chunked_cmds):
				title = f"{cog.qualified_name} | Page {j + 1} / {len(chunked_cmds)}"

				embed = discord.Embed(title=title, description=cog.__doc__ or "", color=discord.Color.orange())

				embed.set_thumbnail(url=bot.user.avatar_url)
				embed.set_footer(text=f"{bot.user.name} | Page {i + 1}/{len(mapping)}", icon_url=bot.user.avatar_url)

				for ii, cmd in enumerate(chunk):
					signature = cmd.usage or cmd.signature.replace("[", "<").replace("]", ">")
					name = f"[{'|'.join([cmd.name] + cmd.aliases)}] {signature}"

					embed.add_field(name=name, value=str(cmd.callback.__doc__), inline=False)

				embeds.append(embed)

		return embeds

	async def send_bot_help(self, mapping):
		embeds = await self.create_embeds(mapping)

		if embeds:
			await inputs.send_pages(self.context, embeds)

		else:
			await self.context.send("You do not have access to help for this command.")

	async def send_cog_help(self, cog):
		await self.send_bot_help({cog: cog.get_commands()})

	async def send_command_help(self, command):
		if command.cog is not None:
			await self.send_bot_help({command.cog: [command]})