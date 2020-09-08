from discord.ext import commands

from src.structs.displaypages import DisplayPages


class Help(commands.HelpCommand):
	def __init__(self):
		super(Help, self).__init__(verify_checks=False, show_hidden=True)

	async def update_bot_mapping(self, mapping):
		for k, v in mapping.items():
			mapping[k] = await self.filter_commands(v)

		return {k: v for k, v in mapping.items() if k is not None and v}

	async def filter_commands(self, cmds, *, sort=False, key=None):
		if sort and key is None:
			key = lambda c: c.name

		iterator = cmds if self.show_hidden else filter(lambda c: not c.hidden, cmds)

		async def predicate(cmd):
			try:
				return await cmd.can_run(self.context)
			except commands.CommandError:
				return False

		ret = []
		for cmd in iterator:
			if await self.context.bot.is_command_disabled(self.context.guild, cmd):
				continue

			if getattr(cmd.cog, "__help_verify_checks__", self.verify_checks):
				valid = await predicate(cmd)

				if not valid:
					continue

			ret.append(cmd)

		if sort:
			ret.sort(key=key)

		return ret

	async def create_embeds(self, mapping):
		def get_cmd_title(cmd_, *, signature: bool = True):
			s_ = " " + str(cmd_.usage or cmd_.signature.replace("[", "<").replace("]", ">")) if signature else ""
			n_ = f"[{'|'.join([cmd_.name] + cmd_.aliases)}]{s_}"

			return n_

		bot = self.context.bot

		embeds = []

		mapping = await self.update_bot_mapping(mapping)

		for i, (cog, cog_cmds) in enumerate(mapping.items()):
			cog_cmds = await self.filter_commands(cog_cmds, sort=False)

			chunked_cmds = [cog_cmds[i:i + 10] for i in range(0, len(cog_cmds), 10)]

			for j, chunk in enumerate(chunked_cmds):
				title = f"{cog.qualified_name} | Page {j + 1} / {len(chunked_cmds)}"

				embed = bot.embed(title=title, description=(cog.__doc__ or "").strip())

				embed.set_footer(text=f"{str(bot.user)} | Module {i + 1}/{len(mapping)}", icon_url=bot.user.avatar_url)

				for ii, cmd in enumerate(chunk):
					if not cmd.hidden:
						embed.add_field(name=get_cmd_title(cmd), value=str(cmd.callback.__doc__).strip(), inline=False)

					if isinstance(cmd, commands.Group):
						for sub in cmd.commands:
							name = f"{get_cmd_title(sub.parent, signature=False)} {get_cmd_title(sub)}"

							embed.add_field(name=name, value=str(sub.callback.__doc__).strip(), inline=False)

				embeds.append(embed)

		return embeds

	async def send_bot_help(self, mapping):
		if embeds := await self.create_embeds(mapping):
			svr = await self.context.bot.get_server_data(self.context.guild)

			await DisplayPages(embeds, timeout=180.0).send(self.context, send_dm=svr.get("dm_help", False))

	async def send_cog_help(self, cog):
		await self.send_bot_help({cog: cog.get_commands()})

	async def send_command_help(self, command):
		if command.cog is not None:
			await self.send_bot_help({command.cog: [command]})

	async def send_group_help(self, group):
		if group.cog is not None:
			await self.send_bot_help({group.cog: [group]})

	async def send_error_message(self, error): pass
