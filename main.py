#==========================================================================================#
# >>>>> ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ <<<<< #
#==========================================================================================#

from Source.Instruments import Calculator, CheckValidDate, GetFreeID, Skinwalker, FormatDays
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboard import ReplyKeyboard
from Source.Thread import Reminder
from Source.AdminPanel import Panel

from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.TelebotUtils import UsersManager
from dublib.Polyglot import Markdown
from telebot import types
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import telebot
import logging

#==========================================================================================#
# >>>>> ЛОГГИРОВАНИЕ <<<<< #
#==========================================================================================#

logging.basicConfig(level=logging.INFO, encoding="utf-8", filename="LOGING.log", filemode="w",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

#==========================================================================================#
# >>>>> СИСТЕМНЫЕ НАСТРОЙКИ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(["Data/Users"])
Clear()

#==========================================================================================#
# >>>>> НАСТРОЙКИ БОТА <<<<< #
#==========================================================================================#

Settings = ReadJSON("Settings.json")
Bot = telebot.TeleBot(Settings["token"])

#==========================================================================================#
# >>>>> СОЗДАНИЕ ОБЪЕКТОВ КЛАССОВ <<<<< #
#==========================================================================================#

Manager = UsersManager("Data/Users")
InlineKeyboardsBox = InlineKeyboards()
ReplyKeyboardBox = ReplyKeyboard()
scheduler = BackgroundScheduler()
reminder = Reminder(Bot, Manager)
AdminPanel = Panel()

#==========================================================================================#
# >>>>> НАСТРОЙКИ APSHEDULER <<<<< #
#==========================================================================================#

StartRemindering = Settings["start_remindering"]
ContinueRemindering = Settings["continue_remindering"]

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ ЗАДАНИЙ В APSHEDULER <<<<< #
#==========================================================================================#

scheduler.add_job(reminder.StartRemindering, 'cron', hour = StartRemindering["hour"], minute=StartRemindering["minute"])
scheduler.add_job(reminder.ContinueRemindering, 'cron', hour = ContinueRemindering["hour"], minute=ContinueRemindering["minute"])
scheduler.start()

#==========================================================================================#
# >>>>> ПАНЕЛЬ АДМИНИСТИРОВАНИЯ <<<<< #
#==========================================================================================#

AdminPanel.decorators.commands(Bot, Manager, Settings["password"])

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = Manager.auth(Message.from_user)
	User.set_expected_type(None)

	User.set_property("events", {}, False)
	Bot.send_message(
		Message.chat.id, 
		"🎉 Welcome! 🎉\n\nI am a chatbot that will remind you about events and let you track the time left before them."
		)
	User.set_temp_property("emoji", False)

	try:
		call = User.get_property("call")
		Bot.send_message(
			Message.chat.id, 
			f"{call}, we are happy to see you again! 🤗",
			reply_markup= ReplyKeyboardBox.AddMenu(User)
			)
		
	except KeyError:
		Bot.send_message(
			Message.chat.id, 
			"Let`s get to know each other!\nWrite down your name! 🤗"
			)
		User.set_expected_type("call")
	
AdminPanel.decorators.reply_keyboards(Bot, Manager)

@Bot.message_handler(content_types = ["text"], regexp = "⚙️ Settings")
def ProcessTextReminders(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)
	Bot.send_message(
		Message.chat.id, 
		"Choose the setting you`d like to customize:", reply_markup= InlineKeyboardsBox.SettingsMenu(User))
		
@Bot.message_handler(content_types = ["text"], regexp = "➕ New event")
def ProcessTextNewEvent(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(
		Message.chat.id, 
		"Please, enter the name of the event you are expecting\\! 😉 \n\n",
			parse_mode = "MarkdownV2"
		)
	User.set_expected_type("name")

@Bot.message_handler(content_types = ["text"], regexp = "🗓 My events")
def ProcessTextMyEvents(Message: types.Message):
	User = Manager.auth(Message.from_user)

	if not User.get_property("events"):
		Bot.send_message(
			Message.chat.id, 
			"You haven\\`t created any events yet 🙄\nLet\\`s fix this!)\\!\\)",
			parse_mode = "MarkdownV2", 
			reply_markup= InlineKeyboardsBox.AddNewEvent()
			)

	else:
		call = Markdown(str(User.get_property("call"))).escaped_text
		Events = User.get_property("events")
		Bot.send_message(
					Message.chat.id,
					f"Hello, {call}\\!",
					parse_mode = "MarkdownV2")
		
		for EventID in Events.keys():
			remains = Calculator(User.get_property("events")[EventID]["Date"])
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			days = FormatDays(remains)

			if remains == 0:
				Bot.send_message(
					Message.chat.id,
					f"Your event *{name}* today\\.",
					parse_mode = "MarkdownV2")

			elif remains > 0:
				remains = Markdown(str(remains)).escaped_text
				Bot.send_message(
					Message.chat.id, f"*{name}* is in {remains} {days}\\!",
					parse_mode = "MarkdownV2"
				)
			else:
				if "Format" in Events[EventID]:
					if Events[EventID]["Format"] == "Passed":
						remains = Markdown(str(abs(remains))).escaped_text
						Bot.send_message(
							Message.chat.id, f"*{name}* was {remains} {days} ago\\!",
							parse_mode = "MarkdownV2"
						)

					if Events[EventID]["Format"] == "Remained":
						newdate = Skinwalker(User.get_property("events")[EventID]["Date"])
						remainsnew = Calculator(newdate)
						days = FormatDays(remainsnew)
						if remainsnew == 0:
							Bot.send_message(
								Message.chat.id,
								f"Your event *{name}* is today\\.",
								parse_mode = "MarkdownV2"
								)
						else:
							remainsnew = Markdown(str(remainsnew)).escaped_text
							Bot.send_message(
								Message.chat.id, 
								f"*{name}* is in {remainsnew} {days}\\!",
								parse_mode = "MarkdownV2"
						)
				else:
					remains = Markdown(str(abs(remains))).escaped_text
					Bot.send_message(
						Message.chat.id, f"*{name}* was {remains} {days} ago\\!",
						parse_mode = "MarkdownV2"
					)
			sleep(0.1)
		Bot.send_message(
						Message.chat.id,
						f"_Have a nice day\\!\\)_",
						parse_mode = "MarkdownV2"
						)
	
@Bot.message_handler(content_types = ["text"], regexp = "📢 Share with friends")
def ProcessShareWithFriends(Message: types.Message):
	User = Manager.auth(Message.from_user)
	
	Bot.send_photo(
		Message.chat.id, 
		photo = Settings["qr_id"],
		caption='@Daystill_bot\n@Daystill_bot\n@Daystill_bot\n\nA top-notch chatbot for time-tracking reminders 🥳', 
		reply_markup=InlineKeyboardsBox.AddShare()
		)

@Bot.message_handler(content_types=["text"])
def ProcessText(Message: types.Message):
	User = Manager.auth(Message.from_user)
	if AdminPanel.procedures.text(Bot, User, Message): return

	if User.expected_type == "call":
		User.set_property("call", Message.text)
		User.set_expected_type(None)

		call = Markdown(str(User.get_property("call"))).escaped_text
		if User.get_property("emoji"):
			Bot.send_message(
				Message.chat.id,
				f"Nice to meet you, {call}! 😎",
			reply_markup = ReplyKeyboardBox.AddMenu(User)
			)
		else: 
			Bot.send_message(
				Message.chat.id,
				f"Nice to meet you, {call}!",
			reply_markup = ReplyKeyboardBox.AddMenu(User)
			)
			User.clear_temp_properties()
			sleep(0.1)

		if not User.get_property("events"):
			Bot.send_message(
			Message.chat.id, 
			text= "To have the chatbot running, create your first event! 🙌",
			reply_markup = InlineKeyboardsBox.AddNewEvent()
			)
		
		return
	
	if User.expected_type == "date":
		name = Markdown(User.get_property("date")).escaped_text
		if CheckValidDate(Message.text) == True:
			Events = User.get_property("events")
			FreeID = str(GetFreeID(Events))
			Events[FreeID] = {"Name": User.get_property("date"), "Date": Message.text, "ReminderFormat": "EveryDay"}
			User.set_expected_type(None)
			User.set_property("events", Events)

			remains = Calculator(User.get_property("events")[FreeID]["Date"])
			name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
			days = FormatDays(remains)
			

			if remains > 0:
				Bot.send_message(
					Message.chat.id,
					text = f"Your data has been saved\\!\n\nThe event *{name}* is in {remains} {days}\\!\n\nLet\\`s be waiting for it together\\! 💪", 
					parse_mode = "MarkdownV2"
					)
				
			elif remains == 0:
				Bot.send_message(
					Message.chat.id,
					text = f"Your data has been saved\\!\n\nYour event *{name}* is today\\!\\!\\! 😊", 
					parse_mode = "MarkdownV2"
					)
			else: 
				Bot.send_message(
					Message.chat.id,
					text ="Tell us what countdown format is more preferable?",
					reply_markup= InlineKeyboardsBox.ChoiceFormat(User, FreeID)
				)

			User.clear_temp_properties()
			User.set_temp_property("EventsID", FreeID)

		else:
			Bot.send_message(
				Message.chat.id, 
				"You have entered a date that does not match the format. Please try again!"
				)

		return

	if User.expected_type == "name":
		User.set_temp_property("date", Message.text)
		Bot.send_message(
			Message.chat.id,
			"And now I need the date of the event 🤔 \n\n_For example_\\: 01\\.01\\.2025", 
			parse_mode = "MarkdownV2")

		User.set_expected_type("date")

		return
	
	if User.expected_type == "reminder":
		
		if Message.text.isdigit() and int(Message.text) >= 1 and int(Message.text) <= 366:
			Events: dict = User.get_property("events")
			ReminderDict: dict = {"Reminder": Message.text}
			Events[User.get_property("EventsID")].update(ReminderDict)
			User.set_property("events", Events)
			User.set_expected_type(None)

			Bot.send_message(
				Message.chat.id,
				"Your data has been saved!🫡 We'll keep an eye on everything!")
		else:
			Bot.send_message(
				Message.chat.id,
				"Я не совсем понял, что вы от меня хотите.")
		return

AdminPanel.decorators.inline_keyboards(Bot, Manager)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event"))
def InlineButtonRemoveEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	EventID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	del Events[EventID]
	User.set_property("events", Events)

	Bot.delete_message(Call.message.chat.id, Call.message.id)
	if not User.get_property("events"):
		Bot.delete_message(Call.message.chat.id, User.get_property("ID_DelMessage"))
		User.clear_temp_properties()
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_reminder"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	Delete = 0 
	User = Manager.auth(Call.from_user)
	
	EventID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	try:
		del Events[EventID]["Reminder"]
		del Events[EventID]["ReminderFormat"]
	except:
		del Events[EventID]["ReminderFormat"]
	
	User.set_property("events", Events)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	for EventID in User.get_property("events"):
		if "ReminderFormat" in User.get_property("events")[EventID].keys() and User.get_property("events")[EventID]["ReminderFormat"] != "WithoutReminders": 
			Delete += 1

	if Delete == 0:
		Bot.delete_message(Call.message.chat.id, User.get_property("ID_DelMessage"))
		User.clear_temp_properties()

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("create_event"))
def InlineButtonCreateEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Bot.send_message(
		Call.message.chat.id, 
		"Please, enter the name of the event you are expecting\\! 😉 \n\n_For example_\\: My Birthday",
		parse_mode = "MarkdownV2"
	)
	User.set_expected_type("name")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("choice_event"))
def InlineButtonChoiceEventToAddReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	CountReminders = 0
	Events = User.get_property("events").copy()
	for EventID in Events.keys():
		if "ReminderFormat" in Events[EventID].keys():
			CountReminders +=1

	
	EventsID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	Name = Markdown(Events[EventsID]["Name"]).escaped_text
	User.set_temp_property("EventsID", EventsID)

	Bot.send_message(
		Call.message.chat.id,
		f"Choose the reminder type:",
		reply_markup= InlineKeyboardsBox.ChoiceFormatReminder(User)
	)
	User.set_expected_type("reminder")


	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("passed_days"))
def InlineButtonPassedDays(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	FreeID = Call.data.split("_")[-1]
	name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
	remains = Calculator(User.get_property("events")[FreeID]["Date"])

	Event: dict = User.get_property("events")
	Format: dict = {"Format": "Passed"}
	ReminderFormat: dict = {"ReminderFormat": "WithoutReminders"}
	Event[FreeID].update(Format)
	Event[FreeID].update(ReminderFormat)
	User.set_property("events", Event)

	days = FormatDays(remains)

	Bot.send_message(
		Call.message.chat.id,
		text = f"Your data has been saved\\!\n\n*{name}* was {abs(remains)} {days} ago\\!", 
		parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remained_days"))
def InlineButtonRemainedDays(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	FreeID = Call.data.split("_")[-1]
	name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
	newevent = Skinwalker(User.get_property("events")[FreeID]["Date"])
	remains = Calculator(newevent)

	Event: dict = User.get_property("events")
	Format: dict = {"Format": "Remained"}
	Event[FreeID].update(Format)
	User.set_property("events", Event)

	days = FormatDays(remains)
	if remains == 365:
		Bot.send_message(
				Call.message.chat.id,
				text = f"Your data has been saved\\!\n\nYour event *{name}* is today\\!\\!\\! 😊", 
				parse_mode = "MarkdownV2"
				)
	else:
		Bot.send_message(
			Call.message.chat.id,
			f"Your data has been saved\\!\n\nThe event *{name}* is in {remains} {days}\\!\n\nLet\\`s be waiting for it together\\! 💪", 
			parse_mode = "MarkdownV2"
			)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Remove_event"))
def ProcessDeleteEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	if not User.get_property("events"):
		Bot.send_message(
			Call.message.chat.id, 
			"You haven\\`t created any reminders 🙄\nLet\\`s fix this\\!\\)",
			parse_mode = "MarkdownV2", 
			reply_markup= InlineKeyboardsBox.AddNewEvent()
		)

	else:
		somedict = User.get_property("events").copy()
		DeleteMessage = Bot.send_message(
					Call.message.chat.id,
					f" Your events: ")
		
		User.set_temp_property("ID_DelMessage", DeleteMessage.id)
		for EventID in somedict.keys():
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			Bot.send_message(
				Call.message.chat.id,
				f"*{name}*",
				reply_markup = InlineKeyboardsBox.RemoveEvent(EventID),
				parse_mode = "MarkdownV2")
			sleep(0.1)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Create_reminder"))
def ProcessTextNewReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events = User.get_property("events")
			
	if User.get_property("events"):

		Bot.send_message(
			Call.message.chat.id, 
			"Choose an event to create a reminder for:")
		
		for EventID in Events.keys():
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			if "ReminderFormat" in Events[EventID].keys():
				Bot.send_message(
					Call.message.chat.id,
					f"*{name}*",
					reply_markup = InlineKeyboardsBox.ChoiceEventToChangeReminder(EventID),
					parse_mode = "MarkdownV2")
				sleep(0.1)

			else:	
				Bot.send_message(
					Call.message.chat.id,
					f"*{name}*",
					reply_markup = InlineKeyboardsBox.ChoiceEventToAddReminder(EventID),
					parse_mode = "MarkdownV2")
				sleep(0.1)

	elif not User.get_property("events"):
		Bot.send_message(
			Call.message.chat.id, 
			text= "To create a reminder, first create an event!",
			reply_markup = InlineKeyboardsBox.AddNewEvent()
			)
		
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Delete_reminder"))
def ProcessDeleteReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	CountReminder = 0
	somedict = User.get_property("events").copy()

	for EventID in somedict.keys():
		if "ReminderFormat" in User.get_property("events")[EventID].keys() and User.get_property("events")[EventID]["ReminderFormat"] != "WithoutReminders":
			CountReminder += 1
	
	if CountReminder < 1:
		Bot.send_message(
			Call.message.chat.id, 
			"You haven`t created any reminders."
			)
	else:
		DeleteMessage = Bot.send_message(
					Call.message.chat.id,
					f"Your reminders: ")
		User.set_temp_property("ID_DelMessage", DeleteMessage.id)

		for EventID in somedict.keys():
			Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
		
			if "ReminderFormat" in somedict[EventID].keys():
				
				if somedict[EventID]["ReminderFormat"] == "EveryDay":
					if "Format" not in somedict[EventID].keys():
						Bot.send_message(
						Call.message.chat.id,
						f"*{Name}*\nУстановлены ежедневные напоминания\\!",
						reply_markup = InlineKeyboardsBox.RemoveReminder(EventID),
						parse_mode = "MarkdownV2")
				if somedict[EventID]["ReminderFormat"] == "OnceDay":
					if "Reminder" in somedict[EventID].keys():

						Reminder = Markdown(User.get_property("events")[EventID]["Reminder"]).escaped_text
						days = FormatDays(Reminder)
						Bot.send_message(
							Call.message.chat.id,
							f"*{Name}*\nНапоминание установлено за {Reminder} {days}\\!",
							reply_markup = InlineKeyboardsBox.RemoveReminder(EventID),
							parse_mode = "MarkdownV2")

			sleep(0.1)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Change"))
def ProcessChangeName(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	User.set_temp_property("emoji", True)
	Bot.send_message(
		Call.message.chat.id,
		"Enter your new name!")
	User.set_expected_type("call")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Info"))
def ProcessInfo(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Bot.send_message(
		Call.message.chat.id,
		text = "@Dnido\\_bot bot serves to remind you about events and let you track the time left before them\\.\n\n1\\) When you create an event, *daily reminders* 🔔 are on by default\\. You can turn them off any moment in the settings by clicking on \"deactivate reminder\"\\. The event itself won\\`t be deleted\\.\n\n2\\) Even if you delete the reminders, don\\`t worry – we\\`ll send you a notification on the day of the event anyway\\! We won\\`t let you forget about it\\! 🤓 You can also set a *one\\-time reminder*, for example, 10 days before the event 📆\\.\n\n_*Use it with pleasure and share with your friends\\!*_",
		parse_mode= "MarkdownV2",
		reply_markup= InlineKeyboardsBox.OK()
	)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("every_day_reminder"))
def ProcessEveryDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "EveryDay"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
		f"Daily reminders for the event *{name}* are on\\!",
		parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("once_reminder"))
def ProcessOnceDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "OnceDay"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
			f"How many days until the event *{Name}*would you like to get a reminder? 🔊\n\n_For example_\\: 10",
			parse_mode = "MarkdownV2"
		)
	User.set_expected_type("reminder")
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("without_reminders"))
def ProcessWithoutReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "WithoutReminders"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
			f"Reminders are off for the event *{Name}*\\!\n\nYou can see how many days are left by choosing *My events* 🖲",
			parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Return"))
def ProcessWithoutReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("OK"))
def ProcessWithoutOK(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	Bot.answer_callback_query(Call.id)
	
@Bot.message_handler(content_types = ["audio", "document", "video"])
def File(Message: types.Message):
	User = Manager.auth(Message.from_user)
	AdminPanel.procedures.files(Bot, User, Message)

AdminPanel.decorators.photo(Bot, Manager)

Bot.infinity_polling()
