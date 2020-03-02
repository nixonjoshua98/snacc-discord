
from .discord_account import DiscordAccount
from .server_stats import ServerStats
from .gamestats import GameStats
from .greetings import Greetings
from .casino import Casino
from .floor import Floor
from .bank import Bank
from .misc import Misc
from .pet import Pet

ALL_COGS = (
	DiscordAccount,
	ServerStats,
	GameStats,
	Greetings,
	Casino,
	Floor,
	Bank,
	Misc,
	Pet
)
