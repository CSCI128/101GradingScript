import config
from UI import uiHelpers
from Canvas import Canvas


def newConfig(_canvas: Canvas):
    print("Would you like to create a new config file?")
    userYN = uiHelpers.getUserInput(allowedUserInput="y/n")
    if userYN.lower() != "y":
        return False
    config.createNewConfig()
    return True

