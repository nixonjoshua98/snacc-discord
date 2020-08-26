
from discord import HTTPException, Forbidden

from src.data import Military, Workers


def net_income(units, levels) -> int:
	"""
	Calculate the net hourly income

	:param units: Units which the user owns
	:param levels: Levels of the units

	:return:
	Returns a value 'int' which is the users net hourly income
	"""

	hourly_income = max(0, Workers.get_total_hourly_income(units, levels))
	hourly_upkeep = max(0, Military.get_total_hourly_upkeep(units, levels))

	return hourly_income - hourly_upkeep


async def send(destination, content=None, embed=None) -> bool:
	"""
	Send a message to Discord, while ignoring errors.

	:param destination: Channel, DM, etc. the message is being sent to
	:param content: Message to be sent (optional)
	:param embed: Embed message to be sent (optional)

	:return:
	Returns 'bool' which symbolises if the message was sent.
	"""

	try:
		await destination.send(content, embed=embed)

	except (HTTPException, Forbidden):
		return False

	return True
