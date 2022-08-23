import sqlite3
import requests
import os

def user_in_db(user_id):
    con = sqlite3.connect("all_database.sqlite3")

    cur = con.cursor()

    info = cur.execute('SELECT * FROM users WHERE id=?', (user_id, ))
    if info.fetchone() is None:
        con.close()
        return False
    else:
        con.close()
        return True

def add_user(age, sex, town, marstat, name, surname, ph1, ph2, ph3, id):
    p = requests.get(ph1)
    out = open("ph1.jpg", "wb")
    out.write(p.content)
    out.close()
    p = requests.get(ph2)
    out = open("ph2.jpg", "wb")
    out.write(p.content)
    out.close()
    p = requests.get(ph3)
    out = open("ph3.jpg", "wb")
    out.write(p.content)
    out.close()

    f = open("ph1.jpg", 'rb')
    ph1 = sqlite3.Binary(f.read())
    f.close()
    f = open("ph2.jpg", 'rb')
    ph2 = sqlite3.Binary(f.read())
    f.close()
    f = open("ph3.jpg", 'rb')
    ph3 = sqlite3.Binary(f.read())
    f.close()

    con = sqlite3.connect("all_database.sqlite3")

    cur = con.cursor()

    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (age, sex, town, marstat, name, surname, ph1, ph2, ph3, id))
    con.commit()
    con.close()
    os.remove("ph1.jpg")
    os.remove("ph2.jpg")
    os.remove("ph3.jpg")
