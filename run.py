
if __name__ == "__main__":
    import snacc

    import os

    if os.path.isfile("config.ini"):
        from configparser import ConfigParser

        config = ConfigParser()

        config.read("config.ini")

        os.environ["SNACC_BOT_TOKEN"] = config.get("bot", "TOKEN")
        os.environ["CON_STR"] = config.get("postgres", "CON_STR")
        os.environ["DEBUG"] = "1"

    snacc.run()
