import discord

from discord.ext import commands


class VoiceChannelsState:
    def __init__(self, guild: discord.Guild):
        self.guild = guild

        self.channels = {}

        self.update_voice_channels(add_members=True)

    def __str__(self):
        s = ""
        for k, v in self.channels.items():
            if v:
                s += f"\nVoice Channel: {k.name}\n"
                s += ", ".join(map(lambda ele: str(ele), v)) + "\n"

        return "-" + s + "-"

    def update_voice_channels(self, *, add_members: bool):
        for channel in self.guild.voice_channels:
            self.channels[channel] = self.channels.get(channel, [])

            if add_members:
                for member in channel.members:
                    self.channels[channel].append(member)

    def on_user_join_voice(self, channel, member):
        self.channels[channel].append(member)

    def on_user_left_voice(self, channel, member):
        self.channels[channel].remove(member)

    def on_user_change_voice(self, old_channel, new_channel, member):
        self.channels[old_channel].remove(member)
        self.channels[new_channel].append(member)


class Devils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.guild = None
        self.state = None

    @commands.Cog.listener(name="on_ready")
    async def update_voice_channels(self):
        self.guild = self.bot.get_guild(693550889352560693)
        self.state = VoiceChannelsState(self.guild)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        pass

    async def on_user_join_voice(self, member: discord.Member, old: discord.VoiceState, new: discord.VoiceState):
        print(f"{member} joined {new.channel.name}")

        self.state.on_user_join_voice(new.channel, member)

    async def on_user_left_voice(self, member: discord.Member, old: discord.VoiceState, new: discord.VoiceState):
        print(f"{member} left {old.channel.name}")

        self.state.on_user_left_voice(old.channel, member)

    async def on_user_change_voice(self, member: discord.Member, old: discord.VoiceState, new: discord.VoiceState):
        print(f"{member} switched from {old.channel.name} to {new.channel.name}")

        self.state.on_user_left_voice(old.channel, member)
        self.state.on_user_join_voice(new.channel, member)

    @commands.Cog.listener(name="on_voice_state_update")
    async def on_voice_update(self, member: discord.Member, old: discord.VoiceState, new: discord.VoiceState):
        if not self.state:
            return

        self.state.update_voice_channels(add_members=False)

        if old.channel is None and new.channel:
            await self.on_user_join_voice(member, old, new)

        elif old.channel and not new.channel:
            await self.on_user_left_voice(member, old, new)

        elif old.channel and new.channel and old.channel.id != new.channel.id:
            await self.on_user_change_voice(member, old, new)

def setup(bot):
    bot.add_cog(Devils(bot))