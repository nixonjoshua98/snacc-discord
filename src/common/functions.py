
from datetime import datetime

def pet_level_from_xp(data: dict) -> int:
	return 0

def abo_days_since_column(data: dict):
	days = (datetime.today() - datetime.strptime(data[0], "%d/%m/%Y %H:%M:%S")).days

	return f"{days} days ago" if days >= 7 else ""