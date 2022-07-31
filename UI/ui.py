from UI.uiHelpers import getUserInput
from UI.standardGrading import standardGrading
from UI.exitGrading import exitGrading


def mainMenu():
    print("Please enter action to take:")
    print("1) Standard Grading")
    print("2) Exit Grading")
    choice = getUserInput(allowedLowerRanger=1, allowedUpperRange=2)
    if choice == 1:
        return standardGrading
    if choice == 2:
        return exitGrading
