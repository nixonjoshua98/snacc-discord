
from datetime import datetime


def to_date(s):
	try:
		date = datetime.strptime(s, "%d/%m/%Y %H:%M:%S")
	except ValueError:
		date = datetime.strptime(s, "%d/%m/%Y")

	return date


def days_since(date) -> int:
	if isinstance(date, datetime):
		return (datetime.today() - date).days

	elif isinstance(date, str):
		return (datetime.today() - to_date(date)).days
