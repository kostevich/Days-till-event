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
					f"Приветствую, {Call}!"
					)
			
		except: pass

	def send(self, ID: int, event: dict, Every: bool, Today: bool):
		Name = Markdown(str(event["Name"])).escaped_text
		User = self.__Manager.get_user(ID)
		if Today:
			try:
				self.__Bot.send_message(
					ID, 
					f"🔔 *REMINDER\\!* 🔔\n\nYour event *{Name}* is today\\!\n\nHave a nice day\\!",
					parse_mode = "MarkdownV2"
				)
			except: User.set_chat_forbidden(True)
			

		else:
			Reminder = Markdown(str(event["Reminder"])).escaped_text
			days = FormatDays(int(event["Reminder"]))
			try:
				self.__Bot.send_message(
				ID, 
				f"🔔 *REMINDER\\!* 🔔\n\nThe event *{Name}* is in {Reminder} {days}\\!\n\nHave a nice day\\!",
				parse_mode = "MarkdownV2"
				)
			except: User.set_chat_forbidden(True)

	def send_long_messages(self, Messages):

		for ID in Messages.keys():
			User = self.__Manager.get_user(ID)
			Reminders = list()
			Call = Markdown(str(Messages[ID]["Call"])).escaped_text
			for i in range(len(Messages[ID]["Events"])):
				
				Name = Markdown(str(Messages[ID]["Events"][i]["Name"])).escaped_text
				
				Remain = Calculator(Messages[ID]["Events"][i]["Date"])	
				if Remain < 0 and "Format" in Messages[ID]["Events"][i].keys():
					if Messages[ID]["Events"][i]["Format"] == "Remained":
						skinwalker = Skinwalker(Messages[ID]["Events"][i]["Date"])
						Remain = Calculator(skinwalker)
						Days = FormatDays(Remain)


				Days = FormatDays(Remain)
				Reminders.append(f"*{Name}* is in {Remain} {Days}\\!")

			base = f"Приветствую, {Call}\\!\n\n"
			end = f"_Have a nice day\\!\\)_"
			for i in range(len(Reminders)):

				if len(base + Reminders[i] + end) < 2000: base += Reminders[i] + "\n\n" 
				
				if len(base + Reminders[i] + end) >= 2000 or i == len(Reminders) - 1:
					try:
						self.__Bot.send_message(ID, base + end, parse_mode="MarkdownV2")
						logging.info(f"Отправлены ежедневные напоминания {ID}")
					except ApiTelegramException: User.set_chat_forbidden(True)
					base = ""

	def StartRemindering(self):
		Messages: dict = {}
		CountID = 0
		UsersID = self.__GetUsersID()
		
		for ID in UsersID:
		
			Data = ReadJSON(f"Data/Users/{ID}.json")
			IsHello = False
			Events = []
			logging.info(f"Начата рассылка: {ID} ")

			if "events" in Data["data"].keys():
				
				for EventID in Data["data"]["events"].keys():
		
					Event: dict = Data["data"]["events"][EventID]
					Call = Data["data"]["call"]
					if self.__CheckTodayRemind(Event) and self.__CheckTodayDate(Event):
						if not IsHello:
							self.SayHello(ID, Call)
							IsHello = True
						self.send(ID, Event, Every=False, Today=True)
						logging.info(f"Отправленно сегодняшнее напоминание {ID}")
							

					if "ReminderFormat" in Event.keys() and self.__CheckFormatRemained(Event):
						if not self.__CheckTodayDate(Event) and Event["ReminderFormat"] == "EveryDay":
							CountID +=1
							Events.append(Event)
							if not IsHello:
								Messages[ID] = {"Call": Call}
								IsHello = True	
							Messages[ID].update({"Events": Events})
					
					if self.__CheckRemind(Event) and self.__CheckRemindDate(Event):

							if not IsHello:
								self.SayHello(ID, Call)
								IsHello = True
				
							self.send(ID, Event, Today=False, Every=False)
							logging.info(f"Отправленно разовое напоминание {ID}")

		self.send_long_messages(Messages)
