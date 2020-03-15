import os

RESOURCES_DIR = os.path.join(os.getcwd(), "src", "resources")

ALL_CHANNEL_TAGS = ("abo", "game")
ALL_ROLE_TAGS = ("member", "default")

JSON_URL_LOOKUP = {
	"game_stats.json": "https://api.myjson.com/bins/1d98rq",
	"coins.json": "https://api.myjson.com/bins/fb9yk",
	"pet_stats.json": "https://api.myjson.com/bins/leyri",
	"server_settings.json": "https://api.myjson.com/bins/f4aku"
}
