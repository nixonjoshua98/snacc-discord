
# TODO: Set the default money to 2_500 in the table and remove `get_balance()` since it
#  wont be needed after modifying the query


def set_env():
    from configparser import ConfigParser

    config = ConfigParser()

    config.read("config.ini")

    os.environ["BOT_TOKEN"] = config.get("bot", "TOKEN")
    os.environ["CON_STR"] = config.get("postgres", "CON_STR")
    os.environ["DEBUG"] = "1"


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
