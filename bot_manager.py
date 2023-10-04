import os
import sys
import datetime
import time
import threading
import signal

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from db_manager import *

from pubg_uc_purchase_bot import purchase, sign_in, choose_iraq, close_popup, open_pubg_pay_page, close_cookies_popup, \
    send_player_id, choose_mobile_payment, choose_amount, close_popup_after_first_purchase, click_back

import get_users_usage

from selenium import webdriver
from selenium.webdriver.common.by import By

import telegram  # v 11.7
from telegram.ext import Updater
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler


##########################################################################################################
FF_BIN_PATH = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

BOT_TOKEN = ''

UN_AUTH_MSG = 'عذرا انت لست عضو في البوت. تواصل مع أ\خالد ليتم تسجيلك في البوت \n +20101101001'

# Define the reply keyboard buttons
reply_keyboard = [[u'شحن جديد', u'سجل الشحن']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Define the conversation states
START_PURCHASE, AMOUNT, PLAYER_ID, CONFIRMATION, PURCHASE_HISTORY, SELECT_OPTION = range(6)

##########################################################################################################
# telegram bot functions

def is_valid_user(user):
    global USERS
    USERS = get_active_users_from_db()
    return user in USERS


def limit_reached(username):
    # check if the user reached his limit
    limit = get_user_limit(username)
    return limit != 0 and get_n_used_codes_for_user(username) >= limit


def is_valid_player_id(p_id):
    return len(p_id) > 5 and p_id.isdigit()


def start_purchase(update, context):
    pass

def amount(update, context):
    pass

def player_id(update, context):
    pass

def confirmation(update, context):
    # # start purchase (add the purchase to the queue and send a message to the user)
    # update.message.reply_text('جار البدء في الشحن ستصلك رسالة تاكيد عند الانتهاء...'
    # PURCHASE_QUEUE.append({'user': context.user_data['user'], 'amount': context.user_data['amount'],
    #                        'player_id': context.user_data['player_id'], 'chat_id': update.message.chat_id,
    #                        'codes': unused_codes[0:context.user_data['amount']]}
    # return ConversationHandler.END
    pass


def purchase_history(update, context):
    pass


def cancel(update, context):
    # Function to handle cancel command
    # Cancel the conversation and remove the keyboard
    update.message.reply_text('Conversation canceled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(update, context):
    # Function to handle errors
    # Print the error to the console
    print(f"Update {update} caused error {context.error}")


def start(update, context):
    # Function to handle the start command
    # Send a welcome message along with the reply keyboard to the user

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('اهلا بك في khaled_rotana bot', reply_markup=reply_markup)


def select_option(update, context):
    # Function to handle the user's selection of an option from the reply keyboard
    # Take actions according to the selected option
    selected_option = update.message.text

    username = bot.get_chat(update.message.chat_id).username
    context.user_data['user'] = username

    if selected_option == reply_keyboard[0][0]:  # start purchase option
        print(username + ' trying to start purchase')
        if is_valid_user(username):
            update.message.reply_text('اهلا بك في بوت شحن UC ببجي موبايل')
            return start_purchase(update, context)
        else:
            update.message.reply_text(UN_AUTH_MSG)
            return ConversationHandler.END

    elif selected_option == reply_keyboard[0][1]:  # purchase history option
        update.message.reply_text('جاري البحث عن سجل الشحن...')
        return purchase_history(update, context)


def conversation_handler():
    global updater
    # Create a conversation handler instance
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler(Filters.regex('^(' + '|'.join(reply_keyboard[0]) + ')$'), select_option)],
        states={
            # SELECT_OPTION: [MessageHandler(Filters.regex('^(' + '|'.join(reply_keyboard[0]) + ')$'), select_option)],
            START_PURCHASE: [MessageHandler(Filters.text, start_purchase)],
            AMOUNT: [MessageHandler(Filters.text, amount)],
            PLAYER_ID: [MessageHandler(Filters.text, player_id)],
            CONFIRMATION: [MessageHandler(Filters.text, confirmation)],
            PURCHASE_HISTORY: [MessageHandler(Filters.text, purchase_history)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # Add the conversation handler to the updater
    updater.dispatcher.add_handler(conv_handler)

    # Add the error handler to the updater
    updater.dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


##########################################################################################################
# tkinter app

def get_all_emails():
    pass


class TkApp(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.users = []
        self.start()


    def callback(self):
        global updater, STOP_PURCHASE_THREAD, my_purchase_thread, bot
        # show a message box to confirm exit
        if messagebox.askyesno('Exit', 'Are you sure you want to exit?'):
            try:
                updater.stop()
                STOP_PURCHASE_THREAD = True
                get_users_usage.write_data_to_excel()
            except Exception as e:
                print(e)

            self.root.quit()
            self.root.destroy()


    def run(self):
        global KEEP_RUNNING, PURCHASING

        def update_bot_tab(status_label, n_codes_label):
            try:
                status = ''
                if KEEP_RUNNING:
                    status = ('Running', 'green')
                elif not KEEP_RUNNING and PURCHASING:
                    status = ('Stopping...', 'orange')
                else:
                    status = ('Stopped', 'red')

                status_label.configure(text=status[0], fg=status[1])
                n_codes_label.configure(text=len(get_unused_codes()))

            except Exception as e:
                print(e)


            self.root.after(1000, update_bot_tab, status_label, n_codes_label)

        def start_stop_bot():
            global KEEP_RUNNING, PURCHASING

            if KEEP_RUNNING: # stop the bot if it's running
                KEEP_RUNNING = False
                start_stop_button.configure(text='Start Bot', bg='#4CAF50')
                # stop bot async
                threading.Thread(target=stop_bot).start()

            else:
                KEEP_RUNNING = True
                start_stop_button.configure(text='Stop Bot', bg='#FF3B30')

        def reload_browser():
            # stop the purchase thread and restart it asynchrounously
            global STOP_PURCHASE_THREAD, my_purchase_thread
            nonlocal reload_status_label

            def restart_purchase_thread():
                global STOP_PURCHASE_THREAD, my_purchase_thread
                nonlocal reload_status_label

                STOP_PURCHASE_THREAD = True
                reload_status_label.pack(side=tk.LEFT) # show the reloading label
                my_purchase_thread.join()
                STOP_PURCHASE_THREAD = False
                reload_status_label.pack_forget() # hide the reloading label
                my_purchase_thread = threading.Thread(target=purchase_thread)
                my_purchase_thread.start()

            if STOP_PURCHASE_THREAD:  # if the thread is already reloading return
                return

            threading.Thread(target=restart_purchase_thread).start() # restart the thread async

        def load_codes_from_file():
            codes = get_codes_from_file()
            append_codes_to_db(codes)
            fill_codes_listbox(get_unused_codes())
            messagebox.showinfo('Codes Loaded', f'{len(codes)} codes were loaded.')


        def search_users(search_text):
            users = [ user for user in self.users if
                      search_text.lower() in str(user[0]).lower() or search_text.lower() in str(user[1]).lower()
                      or search_text.lower() in str(user[2]).lower() or search_text.lower() == str(user[3]).lower()
                        or search_text.lower() in str(user[4]).lower() ]
            # fill the table with the users
            fill_users_table(users)

        def fill_users_table(users):   # fill the table with the given users list
            # rearrange the data to be displayed in the table
            users = [(user[0], user[2], user[1],
                      f'{get_n_used_codes_for_user(user[0])}/{user[4]}', user[3])
                     for user in users]
            # clear the table
            users_table.delete(*users_table.get_children())
            # fill the table with the users
            for user in users:
                users_table.insert('', 'end', values=user, tags=(user[4],))

        def refresh_table():
            self.users = get_all_users_from_db()
            fill_users_table(self.users)

        def fill_codes_listbox(codes):
            codes_listbox.delete(0, tk.END)
            for code in codes:
                codes_listbox.insert(tk.END, code)

        def add_code():
            code = add_code_entry.get()
            if code == '':
                messagebox.showerror('Error', 'Please enter a code')
                return

            if code in get_unused_codes():
                messagebox.showerror('Error', 'This code already exists')
                return

            if len(code) < 5:
                messagebox.showerror('Error', 'Code must be >= 5 characters')
                return

            # add the code to the database
            append_codes_to_db([code])

            # refresh the listbox
            fill_codes_listbox(get_unused_codes())

        def delete_code():
            code = codes_listbox.get(tk.ACTIVE)
            if code == '':
                messagebox.showerror('Error', 'Please select a code to delete')
                return

            if messagebox.askyesno('Delete Code', f'Are you sure you want to delete {code}?'):
                # delete the code from the database
                delete_code_db(code)

                # refresh the listbox
                fill_codes_listbox(get_unused_codes())


        def get_selected_user():
            # get the selected user from the table
            selected = users_table.focus()
            return users_table.item(selected)['values']

        def open_user_window(user=None):

            def save_user(username, name, phone, limit, status):
                if not username or username == '':
                    messagebox.showerror('Error', 'Username is required')
                    return
                if limit != '' and (limit.isdigit() and int(limit) <= 0):
                    messagebox.showerror('Error', 'limit must be a digit > 0 or leave it empty')
                    return

                # remove extra spaces, limit=None if not set
                username, name, phone, limit, status = username.strip(), name.strip(), phone.strip(), None if limit == '' or limit == 'None' else int(limit), int(status_var.get())

                # replace empty str with ' '
                username, name, phone = username if username != '' else ' ', name if name != '' else ' ', phone if phone != '' else ' '

                # check if the user already exists
                if username in [user[0] for user in self.users]:

                    if limit and limit < get_n_used_codes_for_user(username):
                        messagebox.showerror('Error', 'limit must be > number of used codes')
                        return

                    # update the user in the database
                    update_user_db({'username': username, 'name': name, 'mobile': phone, 'active': status, 'limit': limit})

                else:
                    # add the user to the database
                    add_user_to_db({'username': username, 'name': name, 'mobile': phone, 'active': status, 'limit': limit})

                # refresh the table
                self.users = get_all_users_from_db()
                fill_users_table(self.users)

                # close the window
                user_window.destroy()

                # update usage.xlsx
                get_users_usage.write_data_to_excel()


            if user is None:
                user = ['', '', '', '', '']

            # open a new window to add or edit a user
            # make it block the main window
            user_window = tk.Toplevel(self.root)
            user_window.grab_set()
            user_window.focus_set()
            user_window.title('Add/Edit User')
            user_window.configure(bg='#BDBDBD')
            user_window.geometry('400x550')

            # username label and entry (disabled if editing)
            username_label = tk.Label(user_window, text='Username:', font=('Arial', 14), bg='#BDBDBD', fg='black')
            username_label.pack(pady=10)
            username_entry = tk.Entry(user_window, font=('Arial', 12), width=30)
            username_entry.pack(pady=5)
            username_entry.insert(0, user[0])
            if user[0] != '':
                username_entry.configure(state='disabled')

            # name label and entry
            name_label = tk.Label(user_window, text='Name:', font=('Arial', 14), bg='#BDBDBD', fg='black')
            name_label.pack(pady=10)
            name_entry = tk.Entry(user_window, font=('Arial', 12), width=30)
            name_entry.pack(pady=5)
            name_entry.insert(0, user[1])

            # phone label and entry
            phone_label = tk.Label(user_window, text='Phone:', font=('Arial', 14), bg='#BDBDBD', fg='black')
            phone_label.pack(pady=10)
            phone_entry = tk.Entry(user_window, font=('Arial', 12), width=30)
            phone_entry.pack(pady=5)
            phone_entry.insert(0, user[2])

            # limit label and entry
            limit_label = tk.Label(user_window, text='Limit:', font=('Arial', 14), bg='#BDBDBD', fg='black')
            limit_label.pack(pady=10)
            limit_entry = tk.Entry(user_window, font=('Arial', 12), width=30)
            limit_entry.pack(pady=5)
            limit_entry.insert(0, '' if user[3] == '' or user[3][user[3].find('/')+1:] == 'None' else user[3][user[3].find('/')+1:])

            # status label and entry
            status_label = tk.Label(user_window, text='Status:', font=('Arial', 14), bg='#BDBDBD', fg='black')
            status_label.pack(pady=10)
            # checkbox
            status_var = tk.IntVar()
            status_var.set(0 if user[4] == 'inactive' else 1)
            status_checkbox = tk.Checkbutton(user_window, text='Active', variable=status_var, font=('Arial', 12), bg='#BDBDBD', fg='black')
            status_checkbox.pack(pady=5)

            # save button
            save_button = tk.Button(user_window, text='Save', command= lambda: save_user(username_entry.get(), name_entry.get(), phone_entry.get(), limit_entry.get(), status_var.get()), font=('Arial', 15),
                                    bg='#4CAF50', fg='white', relief=tk.RAISED, bd=0, width=15, height=1)
            save_button.pack(pady=10)


        def add_user():
            open_user_window()

        def edit_user():
            user = get_selected_user()
            if user == '':
                messagebox.showerror('Error', 'Please select a user Edit')
                return
            open_user_window(user)

        def reset_user_usage():
            # get the selected user from the table
            user = get_selected_user()
            if user == '':
                messagebox.showerror('Error', 'Please select a user to reset usage')
                return

            username = user[0]

            # ask for confirmation
            if messagebox.askyesno('Reset Usage', f'Are you sure you want to reset {username} usage?'):
                # update usage.xlsx
                get_users_usage.write_data_to_excel()
                # reset user usage
                reset_usage(username)
                # refresh the table
                self.users = get_all_users_from_db()
                fill_users_table(self.users)

        def delete_user():
            global USERS
            # get the selected user from the table
            user = get_selected_user()
            if user == '':
                messagebox.showerror('Error', 'Please select a user to delete')
                return

            username = user[0]

            # ask for confirmation
            if messagebox.askyesno('Delete User', f'Are you sure you want to delete {username}? \nNote: if the user has purchases in queue they will be stopped.'):

                # delete user from the database
                delete_user_from_db(username)

                USERS = get_active_users_from_db() # refresh the users list

                # refresh the table
                self.users = get_all_users_from_db()
                fill_users_table(self.users)

                # update usage.xlsx
                get_users_usage.write_data_to_excel()


        # Create the main application window
        self.root = tk.Tk()
        self.root.title('Bot Manager')
        self.root.configure(bg='#BDBDBD')
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        # Configure main tab style
        style = ttk.Style()
        style.theme_create('custom', parent='clam', settings={
            'TNotebook.Tab': {
                'configure': {
                    'padding': [30, 10],  # Increase padding for the tabs
                    'background': '#4CAF50',  # Set the background color of the tabs to green
                    'font': ('Arial', 14, 'bold'),  # Set the font style of the tabs
                    'foreground': 'white',  # Set the text color of the tabs to white
                    'borderwidth': 0,  # Remove the default border
                    'focuscolor': '#BDBDBD',  # Set the focus color of the tabs to green
                    'focusthickness': 2,  # Increase the focus thickness for the tabs
                    'lightcolor': '#BDBDBD',  # Set the light color for the tabs to grey
                    'darkcolor': '#333333',  # Set the dark color for the tabs to black
                    'relief': tk.SOLID,  # Set the relief style for the tabs to solid
                }
            }
        })
        style.configure('TNotebook', background='#BDBDBD')  # Set the background color of the tab control to grey
        style.configure('TNotebook.Tab', background='#BDBDBD',
                        relief=tk.SOLID)  # Set the background color of the tabs to grey

        style.theme_use('custom')

        # Create tabs
        tab_control = ttk.Notebook(self.root)
        bot_tab = tk.Frame(tab_control, bg='#BDBDBD')
        users_tab = tk.Frame(tab_control, bg='#BDBDBD')
        codes_tab = tk.Frame(tab_control, bg='#BDBDBD')
        tab_control.add(bot_tab, text='Bot')
        tab_control.add(users_tab, text='Users')
        tab_control.add(codes_tab, text='Codes')
        tab_control.pack(expand=True, fill='both')

        # Bot tab #####
        bot_frame = tk.Frame(bot_tab, bg='#BDBDBD')
        bot_frame.pack(expand=True, padx=100, pady=40)

        # bot status label
        status_label = tk.Label(bot_frame, text='Status: ', font=('Arial', 14), bg='#BDBDBD', fg='black')
        status_label.pack()
        status = ('Running', 'green') if KEEP_RUNNING else ('Stopped', 'red')
        status_label = tk.Label(bot_frame, text=status[0], font=('Arial', 14), bg='#BDBDBD', fg=status[1])
        status_label.pack()
        # n codes label
        n_codes_label = tk.Label(bot_frame, text='Unused Codes: ', font=('Arial', 14), bg='#BDBDBD', fg='black')
        n_codes_label.pack()
        n_codes_label = tk.Label(bot_frame, text=len(get_unused_codes()), font=('Arial', 14), bg='#BDBDBD', fg='black')
        n_codes_label.pack()
        # start/stop bot button
        start_stop_button = tk.Button(bot_frame, text='Start Bot', command=start_stop_bot, font=('Arial', 15),
                                          bg='#4CAF50', fg='white', relief=tk.RAISED, bd=0, width=20, height=2)
        start_stop_button.pack(pady=20)
        # reload browser button
        reload_browser_button = tk.Button(bot_frame, text='Reload Browser', command=reload_browser, font=('Arial', 14),
                                            bg='orange', fg='white', relief=tk.RAISED, bd=0, width=14, height=1)
        reload_browser_button.pack(pady=20, side=tk.BOTTOM, padx=10)

        reload_status_label = tk.Label(bot_frame, text='Reloading browser...', font=('Arial', 11), bg='#BDBDBD',
                                       fg='black')


        # USERS TAB #####
        users_frame = tk.Frame(users_tab, bg='#BDBDBD')
        users_frame.pack(expand=True, padx=40, pady=20)

        # refresh button
        refresh_button = tk.Button(users_frame, text='Refresh', command=refresh_table, font=('Arial', 12),
                                            bg='#4CAF50', fg='white', relief=tk.RAISED, bd=0)
        refresh_button.pack(side=tk.LEFT, pady=10, padx=10)

        # search box filters the table each time the text changes
        search_entry = tk.Entry(users_frame, font=('Arial', 12), width=30)
        search_entry.pack(pady=5)
        search_entry.insert(0, 'search')
        search_entry.bind('<KeyRelease>', lambda e: search_users(search_entry.get()))

        # Users table
        table_frame = tk.Frame(users_frame, bg='#BDBDBD')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        users_table = ttk.Treeview(table_frame,
                                    columns=('username', 'name', 'phone', 'usage_limit', 'status'), show='headings',
                                    selectmode='browse')
        users_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), background='#333333', foreground='white')
        style.configure('Treeview', font=('Arial', 12), background='#BDBDBD')
        style.map('Treeview', background=[('selected', '#4CAF50')])

        users_table.heading('username', text='Username')
        users_table.heading('name', text='Name')
        users_table.heading('phone', text='Phone')
        users_table.heading('usage_limit', text='Usage/Limit')
        users_table.heading('status', text='Status')

        users_table.column('username', width=200, anchor=tk.CENTER)
        users_table.column('name', width=200, anchor=tk.CENTER)
        users_table.column('phone', width=200, anchor=tk.CENTER)
        users_table.column('usage_limit', width=150, anchor=tk.CENTER)
        users_table.column('status', width=150, anchor=tk.CENTER)

        # set the color of the rows according to the status
        users_table.tag_configure('inactive', background='grey')

        # Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=users_table.yview)
        users_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add button
        add_button = tk.Button(users_frame, text='Add User', command=add_user, font=('Arial', 12),
                                  bg='#4CAF50',
                                  fg='white', relief=tk.RAISED, bd=0)
        add_button.pack(side=tk.LEFT, pady=10, padx=10)

        # Edit button
        edit_button = tk.Button(users_frame, text='Edit User', command=edit_user, font=('Arial', 12),
                                  bg='orange',
                                  fg='white', relief=tk.RAISED, bd=0)
        edit_button.pack(side=tk.LEFT, pady=10, padx=10)

        # Reset button
        reset_button = tk.Button(users_frame, text='Reset Usage', command=reset_user_usage, font=('Arial', 12),
                                  bg='orange',
                                  fg='white', relief=tk.RAISED, bd=0)
        reset_button.pack(side=tk.LEFT, pady=10, padx=10)

        # Delete button
        delete_button = tk.Button(users_frame, text='Delete User', command=delete_user, font=('Arial', 12),
                                    bg='red',
                                    fg='white', relief=tk.RAISED, bd=0)
        delete_button.pack(side=tk.LEFT, pady=10, padx=10)

        self.users = get_all_users_from_db()
        # fill users table with all users by default
        fill_users_table(self.users)


        # CODES TAB #####
        codes_frame = tk.Frame(codes_tab, bg='#BDBDBD')
        codes_frame.pack(expand=True, padx=40, pady=20)

        # refresh button
        refresh_button = tk.Button(codes_frame, text='Refresh', command= lambda: fill_codes_listbox(get_unused_codes()), font=('Arial', 12),
                                            bg='#4CAF50', fg='white', relief=tk.RAISED, bd=0)
        refresh_button.pack(side=tk.TOP, pady=5, padx=10)

        # codes listbox with scrollbar
        codes_listbox = tk.Listbox(codes_frame, font=('Arial', 12), width=30, height=20)
        codes_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # delete code button
        delete_code_button = tk.Button(codes_frame, text='Delete Code', command=delete_code, font=('Arial', 12),
                                    bg='red',
                                    fg='white', relief=tk.RAISED, bd=0)
        delete_code_button.pack(side=tk.TOP, pady=5, padx=10)

        # add code entry and button
        add_code_entry = tk.Entry(codes_frame, font=('Arial', 12), width=30)
        add_code_entry.pack(pady=5, side=tk.TOP)
        add_code_entry.insert(0, 'add code')

        add_code_button = tk.Button(codes_frame, text='Add Code', command=add_code, font=('Arial', 12),
                                    bg='#4CAF50',
                                    fg='white', relief=tk.RAISED, bd=0)
        add_code_button.pack(side=tk.TOP, pady=5, padx=10)

        # load codes from file button
        load_codes_button = tk.Button(codes_frame, text='Load Codes from file', command=load_codes_from_file, font=('Arial', 14),
                                      bg='orange', fg='white', relief=tk.RAISED, bd=0, width=18, height=1)
        load_codes_button.pack(pady=7, side=tk.BOTTOM, padx=10)

        # fill codes listbox with all unused codes by default
        fill_codes_listbox(get_unused_codes())


        self.root.after(1000, update_bot_tab, status_label, n_codes_label)
        self.root.mainloop()


##########################################################################################################
# purchase bot functions

def purchase_thread():
    global PURCHASE_QUEUE, PURCHASING, KEEP_RUNNING, STOP_PURCHASE_THREAD
    driver = None
    try:
        # initialize the driver and go to pubg website
        driver = webdriver.Firefox(executable_path='geckodriver.exe',
                                   firefox_binary=FF_BIN_PATH)
        driver.maximize_window()

        open_pubg_pay_page(driver)
        close_popup(driver)

        if STOP_PURCHASE_THREAD:
            driver.quit()
            return

        # try to sign in
        email, password = get_login_info_from_file()
        if email and password:
            try:
                sign_in(driver, email, password)
                print('sign in successful')
            except Exception as e:
                print('sign in failed: ' + str(e))
                messagebox.showerror('Error', '\nحدث خطأ اثناء تسجيل الدخول' + str(e))

        if STOP_PURCHASE_THREAD:
            driver.quit()
            return

        # choose iraq as the country
        choose_iraq(driver)
        close_popup(driver)
        close_cookies_popup(driver)
        choose_mobile_payment(driver)
        choose_amount(driver)

        time.sleep(3)

        # while there is a purchase in the queue and the bot running,
        # update the database, remove the code from the file
        # send message to the user
        # remove the purchase from the queue
        while not STOP_PURCHASE_THREAD:
            try:
                if len(PURCHASE_QUEUE) > 0:
                    PURCHASING = True  # set the flag to indicate that there is a purchase in progress

                    # send player_id and check if it is the first purchase
                    send_player_id(driver, PURCHASE_QUEUE[0]['player_id'])

                    n_codes = PURCHASE_QUEUE[0]['amount']
                    n_done_codes = 0
                    for i in range(0, n_codes):  # loop through the codes and try to purchase them one by one
                        if STOP_PURCHASE_THREAD or not is_valid_user(PURCHASE_QUEUE[0]['user']): # if the thread should stop (reloading)
                            break

                        status = purchase(driver, PURCHASE_QUEUE[0]['codes'][i])  # purchase the code and get the status

                        try:
                            if len(driver.window_handles) > 1:  # close the payment tab if it's opened
                                driver.close()
                                time.sleep(2)
                                driver.switch_to.window(driver.window_handles[0])  # switch back to the main tab
                                time.sleep(1)
                                main_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe')
                                driver.switch_to.frame(main_iframe)
                                time.sleep(1.5)

                        except Exception as e:
                            print(e)

                        # close the popup after the first purchase only
                        close_popup_after_first_purchase(driver)

                        if status == 'success':
                            print('one purchase DONE for player_id: ' + PURCHASE_QUEUE[0]['player_id'])
                            n_done_codes += 1
                            # update the code status in the database
                            update_code_status(PURCHASE_QUEUE[0]['codes'][i], 'used')
                            # insert the code and user in the database
                            insert_code_user(PURCHASE_QUEUE[0]['codes'][i], PURCHASE_QUEUE[0]['user'],
                                             PURCHASE_QUEUE[0]['chat_id'], PURCHASE_QUEUE[0]['player_id'])

                        elif status == 'invalid':  # code is invalid, expired or already used
                            print('one INVALID code for player_id: ' + PURCHASE_QUEUE[0]['player_id'])
                            update_code_status(PURCHASE_QUEUE[0]['codes'][i], 'invalid')

                        else:  # status == 'error'  # something went wrong
                            print('one purchase FAILED for player_id: ' + PURCHASE_QUEUE[0]['player_id'])
                            update_code_status(PURCHASE_QUEUE[0]['codes'][i], 'unused')

                    print(f'purchase DONE for player_id: {PURCHASE_QUEUE[0]["player_id"]} with {n_done_codes}/{n_codes} codes')
                    bot.send_message(PURCHASE_QUEUE[0]['chat_id'], f' تم شحن {n_done_codes}/{n_codes}  اكواد بنجاح لمعرف اللاعب {PURCHASE_QUEUE[0]["player_id"]}')

                    PURCHASE_QUEUE.pop(0)

                else:
                    PURCHASING = False  # set the flag to indicate that there is no purchase in progress

            except Exception as e:
                print(e)
                try:  # send message to the user that the purchase failed, pop purchase, refresh
                    bot.send_message(PURCHASE_QUEUE[0]['chat_id'],
                                     f'حدث خطأ اثناء الشحن لمعرف اللاعب {PURCHASE_QUEUE[0]["player_id"]}')

                    update_codes_status_from_to(PURCHASE_QUEUE[0]['codes'], 'pending', 'unused')
                    PURCHASE_QUEUE.pop(0)

                    # click back in case of the player_id is invalid or purchasing from another country
                    time.sleep(7)
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)
                    main_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe')
                    driver.switch_to.frame(main_iframe)
                    time.sleep(1.5)
                    click_back(driver)

                except Exception as e:
                    print('error while handling failed purchase')
                    print(e)

    except Exception as e:
        print(e)
        messagebox.showerror('Error', '\nحدث خطأ اثناء تشغيل بوت الدفع' + str(e))

    finally:
        try:
            PURCHASING = False
            driver.quit()
        except Exception as e:
            print(e)

        return 1


def stop_bot():
    global PURCHASING, KEEP_RUNNING
    # Wait for purchases in the queue to be finished
    while PURCHASING:
        time.sleep(1)

    print('Updating usage.xlsx file...\n')
    get_users_usage.write_data_to_excel()  # generate usage.xlsx file before terminating the script


##########################################################################################################


if __name__ == '__main__':

    USERS = get_active_users_from_db()

    PURCHASE_QUEUE = []
    PURCHASING = False  # flag to indicate if there is a purchase in progress
    KEEP_RUNNING = False  # flag to indicate if the bot should keep accepting purchases
    STOP_PURCHASE_THREAD = False  # flag to indicate if the purchase thread should stop (reloading)

    tk_app = TkApp()

    # start the purchase thread that will handle the purchase queue
    my_purchase_thread = threading.Thread(target=purchase_thread)
    my_purchase_thread.start()

    # Create a bot instance
    bot = telegram.Bot(token=BOT_TOKEN)
    # Create an updater instance
    updater = Updater(bot.token, use_context=True)

    conversation_handler()



