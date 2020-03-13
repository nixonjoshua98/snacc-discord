import os

from .auto_battles_online import AutoBattlesOnline
from .greetings import Greetings
from .backup import Backup
from .config import Config
from .casino import Casino
from .bank import Bank
from .pet import Pet

ALL_COGS = [
	AutoBattlesOnline,
	Greetings,
	Casino,
	Backup,
	Config,
	Bank,
	Pet
]

# Remove Greetings COG
if os.getenv("DEBUG", False):
	ALL_COGS.pop(ALL_COGS.index(Greetings))
