import os

RESOURCES_DIR = os.path.join(os.getcwd(), "src", "resources")

MEMBER_ROLE_ID = 666615010579054614
SNACC_ID = 281171949298647041

SECRET_CHANNEL = 666760256277446686

GAME_CHANNELS = [
	SECRET_CHANNEL,
	666748718183088138
]

RANK_CHANNELS = [
	SECRET_CHANNEL,
	678550428127985686
]

BOT_CHANNELS = set(GAME_CHANNELS + RANK_CHANNELS)

JSON_URL_LOOKUP = {
	"game_stats.json": "https://api.myjson.com/bins/1d98rq",
	"coins.json": "https://api.myjson.com/bins/fb9yk"
}

BACKUP_DELAY = 300

MAX_DAYS_NO_UPDATE = 5

ANIMAL_EMOJI = """
				:dog: :cat: :mouse: :hamster: :rabbit: :fox: :bear: :panda_face: :koala: :tiger: :monkey:
				:monkey_face: :frog: :pig: :cow: :lion_face: :chicken: :penguin: :bird: :baby_chick: :hatched_chick: 
				:duck: :eagle: :owl: :shell: :butterfly: :unicorn: :horse: :boar: :wolf: :squid: :octopus: :crab: 
				:blowfish: :tropical_fish: :rabbit2: :dove: :flamingo: :swan: :parrot: :turkey: :rooster: :cat2: 
				:poodle: :racehorse: :pig2: :ram: :llama: :sheep: :goat: :deer: :dog2: :guide_dog: :service_dog: 
				:cow2: :ox: :water_buffalo: :kangaroo: :camel: :dromedary_camel: :rhino: :elephant: :dolphin: :whale: 
				:shark: :tiger2: :zebra:
				""".split()
