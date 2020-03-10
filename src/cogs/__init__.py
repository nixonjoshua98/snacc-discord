
from .auto_battles_online import AutoBattlesOnline
from .discord_account import DiscordAccount
from .server_stats import ServerStats
from .greetings import Greetings
from .backup import Backup
from .config import Config
from .casino import Casino
from .floor import Floor
from .bank import Bank
from .pet import Pet

ALL_COGS = (
	AutoBattlesOnline,
	DiscordAccount,
	Greetings,
	Casino,
	Backup,
	Config,
	Floor,
	Bank,
	Pet
)
