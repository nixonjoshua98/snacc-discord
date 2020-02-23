import os

# Paths
RESOURCES_DIR = os.path.join(os.getcwd(), "src", "resources")

# Members & Roles
MEMBER_ROLE_ID = 666615010579054614
SNACC_ID = 281171949298647041

# Channels
SECRET_CHANNEL = 666760256277446686

# Channel Arrays
GAME_CHANNELS = (SECRET_CHANNEL, 666748718183088138)
RANK_CHANNELS = (SECRET_CHANNEL, 678550428127985686)

BOT_CHANNELS = set(GAME_CHANNELS + RANK_CHANNELS)

# Cloud Storage
JSON_URL_LOOKUP = {
	"game_stats.json": "https://api.myjson.com/bins/1d98rq",
	"coins.json": "https://api.myjson.com/bins/fb9yk"
}

# Cooldowns
BACKUP_DELAY = 60 * 5
MAX_DAYS_NO_UPDATE = 7
