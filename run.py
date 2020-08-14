
def set_env():
    from configparser import ConfigParser

    config = ConfigParser()

    config.read("config.ini")

    os.environ["DEBUG"] = "1"

    os.environ["BOT_TOKEN"] = config.get("bot", "TOKEN")
    os.environ["PG_CON_STR"] = config.get("database", "PG_CON_STR")
    os.environ["DBL_TOKEN"] = config.get("api", "DBL_TOKEN")

    return "x"


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
