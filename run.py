
def set_env():
    from configparser import ConfigParser

    config = ConfigParser()

    config.read("config.ini")

    os.environ["SNACC_BOT_TOKEN"] = config.get("bot", "TOKEN")
    os.environ["CON_STR"] = config.get("postgres", "CON_STR")
    os.environ["DEBUG"] = "1"


if __name__ == "__main__":
    import os
    import snacc

    if os.path.isfile("config.ini"):
        set_env()

    snacc.run()
