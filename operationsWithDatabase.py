import sqlite3

def find_user(user_id):
    con = sqlite3.connect("all_database.sqlite3")

    cur = con.cursor()

    info = cur.execute('SELECT photo1 FROM users WHERE id=?', (user_id, ))
    if info.fetchone() is None:
        con.close()
        return False
    else:
        photo = cur.execute('SELECT photo1 FROM users WHERE id=?', (user_id, )).fetchone()
        con.close()
        return photo

f = open('Фотография из базы данных.jpg', 'wb')
f.write(find_user('478103493')[0])
f.close()