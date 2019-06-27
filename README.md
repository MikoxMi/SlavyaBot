[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Slavya bot
![Image](https://i.imgur.com/Oxv2kKf.png)
## Description

**Bot is local, it allows you to bring together most of the people for social development**

## Todo:
- Add Incom at the end of the day

## Installation

This bot work on MongoDB

1. Register on the site [mlab](https://mlab.com)
2. Create a database
3. Add next collection to the database:
- member_inventory
- members
- server_settings
- shop
4. Add new user in "Users"

5. Install Python 3.6.2

6. Clone repository:
``` git clone https://github.com/MikoxMi/SlavyaBot.git ```

7. Install requirements:
```pip install -r requirements.txt```

8. Set envinronment variable
For Windows in cmd:
- setx TOKEN = BOT_TOKEN
- setx URL_MONGO = YOUR_URL_MONGO Example: mongodb://<dbuser>:<dbpassword>@dsXXXXXX.mlab.com:XXXXX/XXXXX

9. Add bot to your server and run it
```python main.py```

## Used Libraries
- [discord.py](https://github.com/Rapptz/discord.py)
- [googletrans](https://pypi.org/project/googletrans/)
- [pymongo](https://pypi.org/project/pymongo/)
- [asyncio](https://pypi.org/project/asyncio/)

## Commands
### Admin module
- set_prefix <prefix> - Set bot prefix for your server [Administrator]
- set_descriptor <'en', 'ru'> - Set language descriptor for your server [Administrator]
- set_emoji <emoji> - Set money emoji for your server [Administrator]
### Event
- on_message - Checks the message and translates it if it was written in another language
### Owner
- rld <cogs.standart | etc.> - Reload modules [Owner]
- unload <cogs.standart | etc.> - Unload modules [Owner]
- logout - Disable Bot [Owner]
- add_money @member <money> - Give money to member [Owner]
### Shop
- shop <category=None> <page=None> - Show you all items in category
- buy <item> - Buy item from the shop
- add_item <item_name> - Add item to the shop [Administrator]
- [del, delete] <item_name> - Delete item from the shop [Administrator]
- edit - show all subcommands for edit [Administrator]
### Standard
- [money, bal] <@member:None> - Check your balance or member
- dep <money> - Deposit Your money to the Soviet Bank
- with <money> - Withed Your money from the Soviet Bank
- rep <@member> - give +rep for you Bro
- give <@member> money - Give money to member
- profile - Shows your custom profile
- profile_edit - Allows you to edit your profile. Just follow the instructions
### Waifu
- waifu - get help about the Waifu commands
- waifu like <@member> - Putting in a profile of who you like
- waifu marry <@member> - Give invite of marry to user
- waifu declaim - Break off relations
- waifu profile - Shows your waifu profile
### Author
Discord - **Comrade Woodpacker#9345**
