import sqlite3

def create_db():
    connection = sqlite3.connect('all_database.sqlite3')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users
                  (Age INTEGER, Sex INTEGER, Town STRING, MarStat STRING, Name STRING,
                   Surname STRING, Photo1 BLOB, Photo2 BLOB, Photo3 BLOB, id INTEGER UNIQUE)''')

    connection.commit()
    connection.close()

    connection = sqlite3.connect('users_database.sqlite3')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users
                  (id INTEGER, status INTEGER, status2 INTEGER, age STRING, sex CHAR, town STRING, stat CHAR)''')

    connection.commit()
    connection.close()

create_db()
