from discord.ext import commands


def get_message_text(ctx):
    msg = ctx.message.content
    prefix_used = ctx.prefix
    alias_used = ctx.invoked_with

    return msg[len(prefix_used) + len(alias_used):]


class DarknessBot(commands.Bot):
    TOKEN = "NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y"
    PREFIX = "!"
    
    def __init__(self):
        super().__init__(command_prefix=DarknessBot.PREFIX)

    @staticmethod
    async def on_ready():
        print("Bot ready")

    def run(self):
        super().run(DarknessBot.TOKEN)