
from datetime import datetime


def str_to_date(s):
	try:
		date = datetime.strptime(s, "%d/%m/%Y %H:%M:%S")
	except ValueError:
		date = datetime.strptime(s, "%d/%m/%Y")

	return date