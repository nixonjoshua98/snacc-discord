import os

from darkness.darkness_bot import DarknessBot

from darkness.common import myjson


def run():
	if not os.getenv("DEBUG", False):
		myjson.download_all()

	bot = DarknessBot()

	bot.run()