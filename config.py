import json


def locateConfigFiles():
    pass


def readConfig(_configFileName):

    with open(_configFileName, "r") as jsonDataFile:
        configFile = json.load(jsonDataFile)

    return configFile
