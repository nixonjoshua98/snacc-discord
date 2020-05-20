from configparser import ConfigParser


def load_config(file: str, section: str) -> dict:
    config = ConfigParser()

    config.read(file)

    return dict(config.items(section))


def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]
