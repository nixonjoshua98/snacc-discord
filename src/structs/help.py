import discord

from discord.ext.commands import DefaultHelpCommand

from src.menus import PageMenu


class Help(DefaultHelpCommand):
	def __init__(self):
		super(Help, self).__init__()

	def get_bot_mapping(self):
		mapping = super(Help, self).get_bot_mapping()

		return {k: v for k, v in mapping.items() if k is not None and v}

	async def create_embeds(self, mapping):
		bot = self.context.bot

		embeds = []

		for i, (cog, cog_cmds) in enumerate(mapping.items()):
			chunked_cmds = [cog_cmds[i:i + 10] for i in range(0, len(cog_cmds), 10)]

			for j, chunk in enumerate(chunked_cmds):
				title = f"{cog.qualified_name} | Page {j + 1} / {len(chunked_cmds)}"

				embed = discord.Embed(
					title=title,
					description=cog.__doc__ or "",
					color=discord.Color.orange()
				)

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

		await PageMenu(self.context.bot, embeds, timeout=60.0).send(self.context)

	async def send_cog_help(self, cog):
		await self.send_bot_help({cog: cog.get_commands()})

	async def send_command_help(self, command):
		if command.cog is not None:
			await self.send_bot_help({command.cog: [command]})
