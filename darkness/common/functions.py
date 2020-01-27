
from datetime import datetime


def format_date_str(s, f: str = "%d/%m/%Y"):
	try:
		date = datetime.strptime(s, "%d/%m/%Y %H:%M:%S")
	except ValueError:
		date = datetime.strptime(s, "%d/%m/%Y")

	return date.strftime(f)