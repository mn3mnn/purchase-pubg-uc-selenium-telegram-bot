# purchase-pubg-uc-selenium-telegram-bot
automate the process of purchasing pubg uc using selenium for purchasing, telegram bot enables users to start purchases and view their history, and Tkinter desktop app for administration.


### Overview
- **Selenium bot**: for purchasing pubg uc on the official pubg website (payment is via pre-added SMS codes), the bot opens pubg website and signs in, then chooses Iraq as the country, chooses payment method and amount (static), waits for any user to start a purchase, enters the player_id and do payment n times as requested.

- **Telegram bot**: enables users to start purchases by sending the player_id purchasing for and choosing how many codes to purchase, sends a message upon finishing the purchase, and enables the users to view their history.

- **Tkinter desktop app**: GUI app for the admin enables him to start/stop the bot, add users to the bot via their telegram username, edit/delete/disable users, set limit and reset usage for users, view/search all users and their usage, and add/delete SMS codes


## Features

- **User-Friendly Interaction**: The bot offers a user-friendly interface with options to start a new purchase or view purchase history.

- **Multi-User Support**: Users can initiate UC purchases concurrently, and the bot manages a purchase queue.

- **Purchase History**: Users can request their purchase history, which includes details of completed transactions.

- **Error Handling**: The bot includes robust error handling to handle exceptions gracefully.
