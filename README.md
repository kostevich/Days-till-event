# Days-till-event 
**Days-till-event** – [telegram](https://telegram.org)-bot that will remind you about events and let you track the time left before them.

# Installation and use procedure
1. Download the repository. Unpack it.
2. Install [Python](https://www.python.org/downloads/) versions 3.10 and higher. It is recommended to add it to the PATH.
3. Install packages using the following command executed from the script directory.
```
pip install -r requirements.txt
```
4. Configure the bot by editing [_Settings.json_](#Settings).
5. Run the _main.py_ file.
```
python main.py
``` 
6. Go to the chat with the bot whose token is specified in the settings and follow its instructions.

# Settings.json

<a name="Settings"></a> 

```JSON
"token": "",
"password": "",
"start_remindering": {"hour": null, "minute": ""}
```

You need to enter the Telegram bot token here (you can get it from [BotFather](https://t.me/BotFather )).

---

_Copyright © Dub Irina. 2024._
