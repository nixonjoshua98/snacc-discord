import ssl

from configparser import ConfigParser


def read_config_section(path: str, section: str):
    config = ConfigParser()

    config.read(path)

    return config.items(section)


def create_heroku_database_ssl():
    ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
