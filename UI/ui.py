from typing import Callable
from UI.bartikGrading import bartikGrading
from UI.uiHelpers import getUserInput
from UI.standardGrading import standardGrading
from UI.exitGrading import exitGrading
from UI.createNewConfig import newConfig
from UI.passFail import passFail


def mainMenu() -> Callable:
    print("Please enter action to take:")
    print("1) Standard Grading")
    print("2) Bartik Grading")
    print("3) Post Pass Fail Assignment")
    print("4) Create New Config")
    print("5) Exit Grading")
    choice = getUserInput(allowedLowerRange=1, allowedUpperRange=5)
    if choice == 1:
        return standardGrading
    if choice == 2:
        return bartikGrading
    if choice == 3:
        return passFail
    if choice == 4:
        return newConfig
    if choice == 5:
        return exitGrading

    return lambda _: print("Invalid Choice")
