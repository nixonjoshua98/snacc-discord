from darkness.darkness_bot import DarknessBot

from darkness.common import myjson


def run():
	myjson.download_all()

	bot = DarknessBot()

	bot.run()