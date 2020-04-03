import os


def config(f: str) -> str: return os.path.join(os.getcwd(), f)


def resource(f: str) -> str: return os.path.join(os.getcwd(), "src", "resources", f)


def query(f: str) -> str: return os.path.join(os.getcwd(), "src", "queries", f)