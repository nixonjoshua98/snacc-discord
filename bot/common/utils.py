import os


def config(f: str) -> str: return os.path.join(os.getcwd(), f)


def resource(f: str) -> str: return os.path.join(os.getcwd(), "bot", "resources", f)


def query(f: str) -> str: return os.path.join(os.getcwd(), "bot", "queries", f)