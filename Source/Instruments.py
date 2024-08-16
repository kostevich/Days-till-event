from datetime import date
import dateparser

def CheckValidDate(Date: str)-> bool:
	try:
		dateparser.parse(Date, settings={'DATE_ORDER': 'DMY'}).date()
		return True
	except:
		return False
	
def Skinwalker(event: str) -> str:

	yearnew = int(date.today().year) + 1 
	day = dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).day
	month = dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).month
	newevent = str(day) + "." + str(month) + "." + str(yearnew)
	remains = Calculator(newevent)
	if remains > 364:
		yearnew = int(date.today().year)
		newevent = str(day) + "." + str(month) + "." + str(yearnew)

	return newevent

def Calculator(event: str) -> int:
	today = date.today()
	remains = (dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).date() - today).days
	
	return remains

def GetFreeID(Events: dict) -> int:
	Increment = list()
	for key in Events.keys(): Increment.append(int(key))
	Increment.sort()
	FreeID = 1
	if Increment: FreeID = max(Increment) + 1

	return FreeID

def FormatDays(remains: int) -> str:
	days = "days"
	
	if remains in [1]: days = "day"	
		
	return days
