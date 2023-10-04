import datetime
import sqlite3
import regex


def get_codes_from_file():
    with open('add_codes.txt', 'r', encoding='utf-8') as f:
        data = f.read()
        # extract codes from text, the codes are 6 ascii characters after the word "كود"
        codes = regex.findall(r'كود\s(\w{6})', data)
        return codes


def add_user_to_db(user):
    # add a new user to the database
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user['username'], user['mobile'], user['name'], user['active'], user[
            'limit']))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def update_user_db(user):
    try:
        # update the user in database
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET mobile = ?, name = ?, active = ?, usage_limit = ? WHERE username = ?", (user['mobile'], user['name'], user['active'], user['limit'], user['username']))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def get_all_users_from_db():
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()

        # replace the value of 1 in active column with active and 0 with inactive
        users = [list(user) for user in users]
        for user in users:
            if user[3] == 1:
                user[3] = 'active'
            else:
                user[3] = 'inactive'

        return users

    except Exception as e:
        print(e)
        return []


def get_active_users_from_db():
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE active = 1")
        users = cursor.fetchall()
        conn.close()
        return [user[0] for user in users]

    except Exception as e:
        print(e)
        return []


def get_user_limit(username):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT usage_limit FROM users WHERE username = ?", (username,))
        limit = cursor.fetchone()[0]
        conn.close()
        return int(limit)

    except Exception as e:
        print(e)
        return 0


def delete_user_from_db(username):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def reset_usage(username='all'):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        c = conn.cursor()
        if username == 'all':
            c.execute('DELETE FROM codes_users')
        else:
            c.execute('DELETE FROM codes_users WHERE user = ?', (username,))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def get_unused_codes():
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM codes WHERE status = 'unused'")
        # get the earliest unused code
        codes = cursor.fetchall()
        conn.close()
        if len(codes) > 0:
            return [code[0] for code in codes]
        else:
            return []

    except Exception as e:
        print(e)
        return []


def get_n_used_codes_for_user(username):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM codes_users WHERE user = ?", (username,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    except Exception as e:
        print(e)
        return 0


def append_codes_to_db(codes):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        for code in codes:
            try:
                added_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO codes VALUES (?, ?, ?)", (code, added_at, 'unused'))
            except sqlite3.IntegrityError:
                pass
            except Exception as e:
                print(e)
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def update_code_status(code, status):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE codes SET status = ? WHERE code = ?", (status, code))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def update_codes_status_from_to(codes, from_status, to_status):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        for code in codes:
            cursor.execute("UPDATE codes SET status = ? WHERE code = ? AND status = ?", (to_status, code, from_status))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def delete_code_db(code):
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM codes WHERE code = ?", (code,))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def insert_code_user(code, user, chat_id, player_id):
    # record the code and user in the database
    try:
        conn = sqlite3.connect('pubg_uc.db')
        cursor = conn.cursor()
        used_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO codes_users VALUES (?, ?, ?, ?, ?)", (code, user, used_at, chat_id, player_id))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)


def get_login_info_from_file():
    # read login info from a file
    # return email, password
    try:
        with open('login.txt', 'r') as f:
            email = f.readline().strip().replace('\n', '')
            password = f.readline().strip().replace('\n', '')
            return email, password

    except Exception as e:
        print("Can't read login.txt : " + str(e))
        return None, None
