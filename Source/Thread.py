from .Instruments import FormatDays, Calculator, Skinwalker

import os
import dateparser
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import Clear
from dublib.TelebotUtils import UsersManager
from dublib.Polyglot import Markdown
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from datetime import datetime, timedelta

import logging
Clear()

class Reminder:

	def __GetUsersID(self) -> list[int]:
		# Получение списка файлов в директории.
		Files = os.listdir("Data/Users")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda List: List.endswith(".json"), Files))
		# Список ID пользователей.
		UsersID = list()

		# Для каждого файла.
		for File in Files:
			# Получение ID пользователя.
			ID = int(File.replace(".json", ""))
			# Добавление ID в список.
			UsersID.append(ID)

		return UsersID

	def __CheckFormatRemained(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed": return False
		return True
	
	def __CheckRemind(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed": return False
		if not "Reminder" in event.keys(): return False
		return True
	
	def __CheckTodayRemind(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed": return False
		return True

	def __CheckRemindDate(self, event: dict) -> bool:
		EventDate = dateparser.parse(event["Date"], settings={'DATE_ORDER': 'DMY'})
		CurrentDate = datetime.now().date()
		Day = EventDate.day
		Month = EventDate.month
		Year = CurrentDate.year
		CurrentYearEventDate = datetime(Year, Month, Day)
		if CurrentYearEventDate.date() < datetime.now().date(): CurrentYearEventDate = datetime(Year + 1, Month, Day)
		Period = timedelta(days = int(event["Reminder"]))
		RemindDate = CurrentYearEventDate - Period
		if CurrentDate == RemindDate.date(): return True

		return False
	
	def __CheckTodayDate(self, event: dict) -> bool:
		EventDate = dateparser.parse(event["Date"], settings={'DATE_ORDER': 'DMY'})
		CurrentDate = datetime.now().date()
		Day = EventDate.day
		Month = EventDate.month
		Year = CurrentDate.year
		CurrentYearEventDate = datetime(Year, Month, Day)
		if CurrentYearEventDate.date() < datetime.now().date(): CurrentYearEventDate = datetime(Year + 1, Month, Day)
		if CurrentDate == CurrentYearEventDate.date(): return True

		return False

	def __init__(self, bot: TeleBot, Manager: UsersManager):
		self.__Bot = bot
		self.__Manager = Manager

	def SayHello(self, ID: int, Call: str):
		Call = Markdown(Call).escaped_text
		try:
			self.__Bot.send_message(
					ID, 
					f"Hello, {Call}!"
					)
		except: pass

	def send(self, ID: int, event: dict, EventID: str, Every: bool, Today: bool):
		Name = Markdown(str(event["Name"])).escaped_text
		User = self.__Manager.get_user(ID)
		if Today:
			try:
				self.__Bot.send_message(
					ID, 
					f"🔔 *REMINDER\\!* 🔔\n\nYour event *{Name}* is today\\!\n\nDon't forget\\!\\)",
					parse_mode = "MarkdownV2"
				)
				Events: dict = User.get_property("events")
				ReminderDict: dict = {"ReminderFormat": "WithoutReminders"}
				Events[EventID].update(ReminderDict)
				User.set_property("events", Events)
				logging.info(f"Отправленно сегодняшнее напоминание {ID}")
			except Exception as E: 
				logging.info(f"{E}, {ID}")
				User.set_chat_forbidden(True)
			
		else:
			Reminder = Markdown(str(event["Reminder"])).escaped_text
			days = FormatDays(int(event["Reminder"]))
			try:
				self.__Bot.send_message(
				ID, 
				f"🔔 *REMINDER\\!* 🔔\n\nThe event *{Name}* is in {Reminder} {days}\\!\n\nHave a nice day\\!",
				parse_mode = "MarkdownV2"
				)
				logging.info(f"Отправленно разовое напоминание {ID}")
			except Exception as E: 
				logging.info(f"{E}, {ID}")
				User.set_chat_forbidden(True)

	def send_long_messages(self, Messages):

		for ID in Messages.keys():
			Call = ""
			User = self.__Manager.get_user(ID)
			Reminders = list()
			if "Call" in Messages[ID].keys():
				Call = Markdown(str(Messages[ID]["Call"])).escaped_text
			for i in range(len(Messages[ID]["Events"])):
				
				Name = Markdown(str(Messages[ID]["Events"][i]["Name"])).escaped_text
				
				Remain = Calculator(Messages[ID]["Events"][i]["Date"])
				if Remain < 0 and "Format" not in Messages[ID]["Events"][i].keys():
					skinwalker = Skinwalker(Messages[ID]["Events"][i]["Date"])
					Remain = Calculator(skinwalker)
					Days = FormatDays(Remain)	
				if Remain < 0 and "Format" in Messages[ID]["Events"][i].keys():
					if Messages[ID]["Events"][i]["Format"] == "Remained":
						skinwalker = Skinwalker(Messages[ID]["Events"][i]["Date"])
						Remain = Calculator(skinwalker)
						Days = FormatDays(Remain)

				Days = FormatDays(Remain)
				Reminders.append(f"*{Name}* is in {Remain} {Days}\\!")
			
			base = ""
			for i in range(len(Reminders)):

				if len(base + Reminders[i]) < 2000: base += Reminders[i] + "\n\n" 
				
				if len(base + Reminders[i]) >= 2000 or i == len(Reminders) - 1:
					try:
						self.__Bot.send_message(ID, base, parse_mode="MarkdownV2")
						logging.info(f"Отправлены ежедневные напоминания {ID}")
					except Exception as E: 
						logging.info(f"{E}, {ID}")
						User.set_chat_forbidden(True)

	def StartRemindering(self):
		Messages: dict = {}
		CountID = 0
		UsersID = self.__GetUsersID()
		
		for ID in UsersID:
		
			Data = ReadJSON(f"Data/Users/{ID}.json")
			Events = []
			logging.info(f"Начата рассылка: {ID} ")

			if "events" in Data["data"].keys():	

				for EventID in Data["data"]["events"].keys():
		
					Event: dict = Data["data"]["events"][EventID]
					Call = Data["data"]["call"]
					if "ReminderFormat" in Event.keys() and self.__CheckFormatRemained(Event):
						if not self.__CheckTodayDate(Event) and Event["ReminderFormat"] == "EveryDay":
							CountID +=1
							Events.append(Event)
							Messages[ID] = {"Events": Events}

		self.send_long_messages(Messages)

	def ContinueRemindering(self):
		Messages: dict = {}
		CountID = 0
		UsersID = self.__GetUsersID()
		
		for ID in UsersID:
		
			Data = ReadJSON(f"Data/Users/{ID}.json")
			Events = []

			if "events" in Data["data"].keys():
				
				for EventID in Data["data"]["events"].keys():
		
					Event: dict = Data["data"]["events"][EventID]
					Call = Data["data"]["call"]

					if self.__CheckTodayRemind(Event) and self.__CheckTodayDate(Event):
						self.send(ID, Event, EventID, Every=False, Today=True)
								
					if self.__CheckRemind(Event) and self.__CheckRemindDate(Event):
							self.send(ID, Event, EventID, Today=False, Every=False)


