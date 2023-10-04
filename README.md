# purchase-pubg-uc-selenium-telegram-bot
automate the process of purchasing pubg uc using selenium web driver for purchasing, telegram bot enables authenticated users to start purchases and view their history, and Tkinter desktop app for administration.

--**Kindly see ```usage.mp4``` for a quick example of how it works.**

### Overview
- **Selenium bot**: for purchasing pubg uc on the official pubg website (payment is via pre-added SMS codes), the bot opens pubg website and signs in, then chooses Iraq as the country, chooses payment method and amount (static), waits for any user to start a purchase, enters the player_id and do payment n times as requested.

- **Telegram bot**: enables users to start purchases by sending the player_id purchasing for and choosing how many codes to purchase, sends a message upon finishing the purchase, and enables the users to view their history.

- **Tkinter desktop app**: GUI app for the admin enables him to start/stop the bot, add users to the bot via their telegram username, edit/delete/disable users, set limit and reset usage for users, view/search all users and their usage, and add/delete SMS codes

- **How it works**: the main file here is ```bot_manager.py```, uses functions from ```purchase_bot.py``` and ```db_manager.py```,
  - it runs the tkinter app in a new thread,
  - starts the telegram bot that listens to updates, responds to users, and appends purchases to the ```PURCHASE_QUEUE```
  - starts a new thread for managing purchases which starts the web driver, waits for a new purchase to be in the ```PURCHASE_QUEUE```, and tries to make it.
  - saves the codes, users, and purchases to **SQLite3** db.


### Notes:
- the admin is the person who runs/stops the bot, adds users to it, adds mobile SMS codes used for payment, tracks users' usage, and resets it
- the payment method used in this app works ONLY with **Iraqi player_id and Iraqi IP address.**
- **The source code for telegram and selenium bots is removed as the client requested.**
