import json
import random


robot_statistics = []

for i in range(10):
    letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    number = random.randint(1, 9)
    model = letter + str(number)
    versions = random.randint(2, 7)
    for j in range(versions):
        version = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + str(random.randint(1, 9))
        count = random.randint(0, 20)
        robot = {"model": model, "version": version, "count": count}
        # добавляем словарь в список robot_statistics
        robot_statistics.append(robot)
        # создаем словарь с ключом "robot_statistics" и значением - списком robot_statistics
        data = {"robot_statistics": robot_statistics}
        # открываем файл robots.json в режиме записи
        with open("robots.json", "w") as f:
        # записываем данные в файл в формате JSON с отступами для читабельности
            json.dump(data, f, indent=4)
