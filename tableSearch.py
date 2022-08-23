import sqlite3

def find_user(user_id):
    con = sqlite3.connect("users_database.sqlite3")

    cur = con.cursor()

    info = cur.execute('SELECT * FROM users WHERE id=?', (user_id, ))
    if info.fetchone() is None:
        con.close()
        return False
    else:
        status = cur.execute('SELECT status FROM users WHERE id=?', (user_id, )).fetchone()[0]
        con.close()
        return status


def find_user2(user_id):
    con = sqlite3.connect("users_database.sqlite3")

    cur = con.cursor()

    info = cur.execute('SELECT * FROM users WHERE id=?', (user_id, ))
    if info.fetchone() is None:
        con.close()
        return False
    else:
        status = cur.execute('SELECT status2 FROM users WHERE id=?', (user_id, )).fetchone()[0]
        con.close()
        return status


def change_status2(user_id, status):
    con = sqlite3.connect("users_database.sqlite3")

    cur = con.cursor()
    cur.execute("UPDATE users SET status2 = ? WHERE id = ?", (status, user_id))
    con.commit()
    con.close()




def insert_user(user_id):
    con = sqlite3.connect("users_database.sqlite3")

    cur = con.cursor()

    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, 1, 1, None, None, None, None))
    con.commit()
    con.close()


def change_user(user_id, status, case, num):
    con = sqlite3.connect("users_database.sqlite3")

    cur = con.cursor()
    if case == 'age':
        cur.execute("UPDATE users SET status = ?, age = ? WHERE id = ?", (status, num, user_id))
    elif case == 'sex':
        cur.execute("UPDATE users SET status = ?, sex = ? WHERE id = ?", (status, num, user_id))
    elif case == 'town':
        cur.execute("UPDATE users SET status = ?, town = ? WHERE id = ?", (status, num, user_id))
    elif case == 'stat':
        cur.execute("UPDATE users SET status = ?, stat = ? WHERE id = ?", (status, num, user_id))
    else:
        cur.execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
    con.commit()
    con.close()


def user_info(user_id):
    con = sqlite3.connect("users_database.sqlite3")

    cur = con.cursor()
    data = cur.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    cur.close()
    return data
