import discord


class MenuBase:
    def __init__(self, bot, **options):
        self._bot = bot

        self._destination = None
        self._message = None

        self._timeout = options.get("timeout", None)

    @staticmethod
    async def _remove_react(react, user):
        try:
            await react.remove(user)

        except (discord.Forbidden, discord.HTTPException):
            """ Failed. """

    async def send(self, destination: discord.abc.Messageable):
        """ Sends the menu / form. """

    def wait_for(self, message: discord.Message) -> bool:
        """ Check function used for the event listener. """
