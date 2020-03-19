import os

RESOURCES_DIR = os.path.join(os.getcwd(), "src", "resources")

ALL_CHANNEL_TAGS = ("abo", "game")
ALL_ROLE_TAGS = ("member", "default")

JSON_URL_LOOKUP = {
	"game_stats.json": "https://jsonblob.com/api/jsonBlob/5d04ce93-6a08-11ea-b0e9-1d54085d8a5b",
	"coins.json": "https://jsonblob.com/api/jsonBlob/540a8726-6a08-11ea-b0e9-afc94a09b20c",
	"pet_stats.json": "https://jsonblob.com/api/jsonBlob/499670fe-6a08-11ea-b0e9-111aec71ac68",
	"server_settings.json": "https://jsonblob.com/api/jsonBlob/68d9380b-6a08-11ea-b0e9-6b2859d79e7a"
}
