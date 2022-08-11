from UI.uiHelpers import getUserInput
from UI.standardGrading import standardGrading
from UI.exitGrading import exitGrading
from UI.createNewConfig import newConfig


def mainMenu():
    print("Please enter action to take:")
    print("1) Standard Grading")
    print("2) Create New Config")
    print("3) Exit Grading")
    choice = getUserInput(allowedLowerRanger=1, allowedUpperRange=3)
    if choice == 1:
        return standardGrading
    if choice == 2:
        return newConfig
    if choice == 3:
        return exitGrading
