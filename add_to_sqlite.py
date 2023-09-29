import datetime
import sqlite3
import random


conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS robots_robot (
        id INTEGER PRIMARY KEY,
        model TEXT,
        version TEXT,
        count INTEGER,
        date TEXT
    )""")

# Дата производства больше недели
old_date = '2010-10-10 20:10:10.100000'
cur.execute("INSERT INTO robots_robot (model, version, count, date) VALUES (?, ?, ?, ?)", ('A1', 'A1', 1, old_date))
cur.execute("INSERT INTO robots_robot (model, version, count, date) VALUES (?, ?, ?, ?)", ('A2', 'A2', 1, old_date))
conn.commit()

for i in range(10):
    letter = random.choice("BCDEFGHIJKLMNOPQRS")
    number = random.randint(1, 9)
    model = letter + str(number)
    versions = random.randint(2, 7)
    
    for j in range(versions):
        version = random.choice("ABCDEFGHIJKLMNOPQRS") + str(random.randint(1, 9))
        count = random.randint(0, 20)
        date = str(datetime.datetime.now())
        robot = {"model": model, "version": version, "count": count, "date": date}

        # добавляем данные в таблицу robots_robot с помощью SQL-запроса
        cur.execute("""INSERT INTO robots_robot (model, version, count, date)
        VALUES (:model, :version, :count, :date)""", robot)

    # сохраняем изменения в базе данных
    conn.commit()

# закрываем подключение к базе данных
conn.close()
