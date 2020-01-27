import os

# - Paths
RESOURCES_DIR = os.path.join(os.getcwd(), "darkness", "resources")

# - Names
MEMBER_ROLE_NAME = "Darkness Employee"

# - Urls
JSON_URL_LOOKUP = {"member_stats.json": "https://api.myjson.com/bins/1d98rq"}

# IDs
BOT_CHANNELS = [666760256277446686, 666748718183088138]

# - Cooldowns
SET_STATS_COOLDOWN = 60

# - Attributes
MAX_NUM_STAT_ENTRIES = 3

# - Debug
# if os.getenv("DEBUG", False):
# JSON_URL_LOOKUP["member_stats.json"] = "https://api.myjson.com/bins/17xtpy"
