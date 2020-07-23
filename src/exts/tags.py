import discord


from discord.ext import commands

import xml.etree.ElementTree as ET

EXAMPLE_XML = """
<embed title="Mercenaries" color="15105570" description="A **brief** description of the page">
	<field name="Mage">			
		Mages can **heal**!		
	</field>
	
	<field name="Warrior">			
		Warriors are the __tanks__ of the game.
	</field>
	
	<field name="Archer">			
		Archers are *very* strong!
	</field>
	
	<footer>
		<icon_url>https://cdn.discordapp.com/avatars/281171949298647041/6ae331be885b043d80e22db97932083a.webp?size=1024</icon_url>
		<text>Made by Snaccman</text>		
	</footer>
		
</embed>
"""


class Tags(commands.Cog):
	@staticmethod
	def parse_xml(s):
		def parse_root():
			title = root.attrib["title"]
			desc = root.attrib.get("description", None)
			color = root.attrib.get("color", 0)

			if not color.isdigit():
				raise commands.UserInputError(f"Color '{color}' cannot be converted to an integer.")

			data = {"title": title, "description": desc, "color": int(color)}

			return {k: v for k, v in data.items() if v is not None}

		root = ET.fromstring(s)

		output = dict(**parse_root(), fields=[])

		for field in root.findall("field"):
			output["fields"].append({"name": field.attrib["name"], "value": field.text})

		footer = root.find("footer")

		if footer:
			output["footer"] = dict(
				text=getattr(footer.find("text"), "text", None),
				icon_url=getattr(footer.find("icon_url"), "text", None)
			)

		return output

	@commands.group(name="tag", aliases=["t"], hidden=True)
	async def group(self, ctx):
		""" Parent Command. """

	@group.command(name="preview", aliases=["pre"])
	async def preview(self, ctx, *, xml_string):
		""" Recieve a preview of what the emebed will look like. """

		output = self.parse_xml(xml_string)

		embed = discord.Embed.from_dict(data=output)

		await ctx.send(embed=embed)

	@group.command("example", aliases=["ex"])
	async def example(self, ctx):
		""" Show the example XML and embed. """

		output = self.parse_xml(EXAMPLE_XML)

		embed = discord.Embed.from_dict(data=output)

		await ctx.send(content=f"```xml\n{EXAMPLE_XML}```", embed=embed)


def setup(bot):
	bot.add_cog(Tags())
