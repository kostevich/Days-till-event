from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboards:

	def __init__(self):
		pass

	def SettingsMenu(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		ChangeReminder = types.InlineKeyboardButton("🔔 Change reminder", callback_data = f"Change_reminder")
		DeleteReminder = types.InlineKeyboardButton("🔕 Deactivate reminders", callback_data = f"Delete_reminder")
		Сhange = types.InlineKeyboardButton("🔁 Change name", callback_data = f"Change")
		Info = types.InlineKeyboardButton("ℹ️ Info", callback_data = f"Info")
		Return = types.InlineKeyboardButton("🔙 Back", callback_data = f"Return")
		# Добавление кнопок в меню.
		Menu.add(DeleteReminder, ChangeReminder, Сhange, Info, Return, row_width= 1) 

		return Menu

	def OK(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		OK = types.InlineKeyboardButton("That's clear!", callback_data = f"OK")
		
		# Добавление кнопок в меню.
		Menu.add(OK, row_width= 1) 

		return Menu

	def RemoveEvent(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		RemoveEvent = types.InlineKeyboardButton(
			"Delete", 
			callback_data = f"remove_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(RemoveEvent)

		return Menu
	
	def ChoiceEventToChangeReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			"Change reminder", 
			callback_data = f"choice_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu
	
	def ChoiceReminderForNewEvent(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			"Set up reminders", 
			callback_data = f"choice_event_{EventID}_"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu
	
	def AddShare(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			"Share", 
			switch_inline_query='\n\nJust a top bot for time-tracking reminders 🥳'
			)
		
		Menu.add(Share)

		return Menu

	def AddNewEvent(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Create = types.InlineKeyboardButton(
			"Create an event", 
			callback_data = "create_event"
			)
		
		Menu.add(Create)

		return Menu

	def RemoveReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		RemoveReminder = types.InlineKeyboardButton(
			"🔕 Deactivate", 
			callback_data = f"remove_reminder_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(RemoveReminder)

		return Menu
	
	def ChoiceFormat(self, user: UserData, FreeID: str) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		Remained = types.InlineKeyboardButton(
			"Days left", 
			callback_data = f"remained_days_{FreeID}"
			)
		Passed = types.InlineKeyboardButton(
			"Days passed", 
			callback_data = f"passed_days_{FreeID}"
			)

		# Добавление кнопок в меню.
		Menu.add(Remained, Passed, row_width = 1)
		
		return Menu
	
	def ChoiceFormatReminderChange(self, user: UserData) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		EveryDayReminders = types.InlineKeyboardButton(
			"Turn on daily reminders", 
			callback_data = "every_day_reminder"
			)
		OnceReminder = types.InlineKeyboardButton(
			"Turn on a one-time reminder", 
			callback_data = "once_reminder"
			)
		WithOutReminders = types.InlineKeyboardButton(
			"No reminders", 
			callback_data = "without_reminders"
			)

		# Добавление кнопок в меню.
		Menu.add(EveryDayReminders, OnceReminder, WithOutReminders, row_width = 1)
		
		return Menu
	

	def ChoiceFormatReminderNew(self, user: UserData) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		EveryDayReminders = types.InlineKeyboardButton(
			"Keep daily reminders on", 
			callback_data = "every_day_reminder"
			)
		OnceReminder = types.InlineKeyboardButton(
			"Create a one-time reminder", 
			callback_data = "once_reminder"
			)
		WithOutReminders = types.InlineKeyboardButton(
			"No reminders", 
			callback_data = "without_reminders"
			)

		# Добавление кнопок в меню.
		Menu.add(EveryDayReminders, OnceReminder, WithOutReminders, row_width = 1)
		
		return Menu