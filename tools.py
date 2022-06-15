import os
import json

def loadJsonFile(path):
    result = None
    if os.path.exists(path):
        with open(path, "r") as file:
            result = json.load(file)
    return result

def dumpJsonFile(data, path):
    with open(path, "w") as file:
        json.dump(data, file)