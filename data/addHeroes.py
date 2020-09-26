import json
import random

stats = {"S": 700, "A": 600, "B": 500, "C": 400, "D": 300, "E": 200, "F": 100}

while True:
    with open(r"C:\Repos\snacc-bot\data\heroes.json", "r") as fh:
        data = json.load(fh)

    print(len(data.keys()))

    name = input("Name: ").title()

    if name.title() in [v["name"].title() for k, v in data.items()]:
        print("exists")

        continue
    
    grade = input("Grade: ").upper()

    max_stats = stats[grade] + random.randint(0, 75)

    atk = random.randint(max_stats // 4, max_stats // 2)

    hp = max_stats - atk

    _id = max([int(k) for k in data.keys()]) + 1

    data[str(_id)] = dict(atk=atk, hp=hp, name=name.title(), grade=grade)

    with open(r"C:\Repos\snacc-bot\data\heroes.json", "w") as fh:
        json.dump(data, fh, indent=4, sort_keys=True)

    
