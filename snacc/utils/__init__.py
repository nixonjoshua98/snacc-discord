from configparser import ConfigParser

from . import dis, pages


def load_config(file: str, section: str) -> dict:
    config = ConfigParser()

    config.read(file)

    return dict(config.items(section))
