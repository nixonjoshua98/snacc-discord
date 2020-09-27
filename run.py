
def set_env():
    from configparser import ConfigParser

    config = ConfigParser()

    config.read("config.ini")

    os.environ["DEBUG"] = "1"

    os.environ["BOTLIST_AUTH"] = config.get("vote", "BOTLIST_AUTH")
    os.environ["BOTLIST_TOKEN"] = config.get("vote", "BOTLIST_TOKEN")

    os.environ["DBL_AUTH"] = config.get("vote", "DBL_AUTH")
    os.environ["DBL_TOKEN"] = config.get("vote", "DBL_TOKEN")

    os.environ["BOT_TOKEN"] = config.get("bot", "TOKEN")

    os.environ["MONGO_STR"] = config.get("database", "MONGO_STR")

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

    if os.path.isfile("config.ini"):
        set_env()

    setup_loop()

    src.run()
