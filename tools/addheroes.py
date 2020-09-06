import json

while True:
    name = input("Name: ")
    grade = input("Grade: ")

    with open(r"C:\Repos\snacc-bot\data\heroes.json", "r") as fh:
        data = json.load(fh)

    _id = max(map(int, data.keys())) + 1

    data[str(_id)] = dict(name=name, grade=grade)

    with open(r"C:\Repos\snacc-bot\data\heroes.json", "w") as fh:
        json.dump(data, fh, indent=4)
