from configparser import ConfigParser

from . import dis, database, settings


def load_config(file: str, section: str) -> dict:
    config = ConfigParser()

    config.read(file)

    return dict(config.items(section))
