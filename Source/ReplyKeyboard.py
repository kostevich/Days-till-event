from dublib.TelebotUtils import UserData
from telebot import types

class ReplyKeyboard:

	def __init__(self):
		pass

	def AddMenu(self, user: UserData) -> types.ReplyKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

		# Генерация кнопок.
		CreateEvent = types.KeyboardButton("➕ New event")
		ListEvents = types.KeyboardButton("🗓 My events")
		List = types.KeyboardButton("⚙️ Settings")
		Share = types.KeyboardButton("📢 Share with friends")

		# Добавление кнопок в меню.
		Menu.add(CreateEvent, ListEvents, List, Share, row_width = 2)
		
		return Menu
