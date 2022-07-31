from uiHelpers import getUserInput




def mainMenu():
    print("Please enter action to take:")
    print("1) Standard Grading")
    print("2) Exit")
    choice = getUserInput(allowedLowerRanger=1, allowedUpperRange=2)
    if choice == 1:
        return standardGrading
    if choice == 2:
        return exit