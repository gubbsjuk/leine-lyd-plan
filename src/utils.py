import json


def load_json(path, base=None):
    if base is None:
        base = {}
    try:
        with open(path, "r") as file:
            content = json.load(file)
    except FileNotFoundError:
        content = base

    return content


def write_json(path, content):
    with open(path, "w") as file:
        json.dump(content, file, indent=4)
