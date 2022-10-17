from UI.uiHelpers import getUserInput
from UI.standardGrading import standardGrading
from UI.exitGrading import exitGrading
from UI.createNewConfig import newConfig
from UI.passFail import passFail


def mainMenu():
    print("Please enter action to take:")
    print("1) Standard Grading")
    print("2) Post Pass Fail Assignment")
    print("3) Create New Config")
    print("4) Exit Grading")
    choice = getUserInput(allowedLowerRanger=1, allowedUpperRange=4)
    if choice == 1:
        return standardGrading
    if choice == 2:
        return passFail
    if choice == 3:
        return newConfig
    if choice == 4:
        return exitGrading
