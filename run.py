
def set_env():
    from configparser import ConfigParser

    config = ConfigParser()

    config.read("config.ini")

    os.environ["DEBUG"] = "1"

    os.environ["BOT_TOKEN"] = config.get("bot", "TOKEN")
    os.environ["DBL_TOKEN"] = config.get("api", "DBL_TOKEN")
    os.environ["MONGO_CON_STR"] = config.get("database", "MONGO_CON_STR")

    os.environ["RAID_API_KEY"] = config.get("api", "RAID_API_KEY")


def setup_loop():
    import sys
    import subprocess
    import platform

    if platform.system() == "Linux":
        try:
            import uvloop
        except ImportError:
            if subprocess.check_call([sys.executable, "-m", "pip", "install", 'uvloop']) == 0:
                import uvloop

        uvloop.install()


if __name__ == "__main__":
    import os
    import src

    """ 
    import json, random

    with open(r"C:\Repos\snacc-bot\data\heroes.json", "r") as fh:
        data = json.load(fh)

    stats = {"Z": 2000, "S": 700, "A": 600, "B": 500, "C": 400, "D": 300, "E": 200, "F": 100}

    new_data = dict()

    for k, v in data.copy().items():
        max_stats = stats.get(v["grade"]) + random.randint(0, 75)

        ATK = random.randint(max_stats // 4, max_stats // 2)

        HP = (max_stats - ATK)

        data[k]["atk"] = ATK
        data[k]["hp"] = HP

        new_data[int(k)] = data[k]

    with open(r"C:\Repos\snacc-bot\data\heroes.json", "w") as fh:
        json.dump(new_data, fh, indent=4, sort_keys=True)
    """

    if os.path.isfile("config.ini"):
        set_env()

    setup_loop()

    src.run()
