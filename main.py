import pandas as pd

import csvLoaders
import csvLoaders as ld
from Grade import grade, score, post
from Canvas import Canvas
import config


def getUserInput(allowedUserInput: str = None, allowedLowerRanger: int = None, allowedUpperRange: int = None):
    if allowedLowerRanger is None and allowedUpperRange is None and allowedUserInput is None:
        raise AttributeError("No Valid User Input Allowed")
    usrIn: (str, int) = None
    if allowedUserInput is not None:
        try:
            usrIn = str(input(f"({allowedUserInput}): "))
        except Exception:
            usrIn = None
            print("Invalid Input")
        finally:
            return usrIn

    if allowedLowerRanger is not None and allowedUpperRange is not None:
        usrIn = allowedLowerRanger - 1
        errorOccurred = False
        while not (allowedLowerRanger <= usrIn <= allowedUpperRange):
            try:
                usrIn = int(input(f"({allowedLowerRanger} - {allowedUpperRange}): "))
            except ValueError:
                usrIn = allowedLowerRanger - 1
                errorOccurred = True
                print("Invalid Input")
            finally:
                if allowedLowerRanger <= usrIn <= allowedUpperRange:
                    return usrIn
                elif not errorOccurred:
                    print("Invalid Input")
                else:
                    errorOccurred = False


def assignmentsMenu(_canvas: Canvas):
    assignments: pd.DataFrame = _canvas.getAssignments()
    print("Please enter common name of assignment to grade")
    print("(EG: HW7 - Whatever and Whatever == HW7, Lab 18 - Crying myself to sleep == L18)")

    selectedAssignment = None
    while selectedAssignment not in assignments['common_name'].values.tolist():
        selectedAssignment = getUserInput(allowedUserInput="Common Name")
        if selectedAssignment not in assignments['common_name'].values.tolist():
            print("Warning: Unable to map Common Name to Canvas assignment")
            print("Would you like to override this warning?")
            usrYN = getUserInput(allowedUserInput="y/n")
            if usrYN.lower() == 'y':
                raise NotImplementedError("Manual Overriding is not implemented")
        else:
            print(
                f"Identified assignment {assignments.loc[assignments['common_name'] == selectedAssignment, 'name'].values[0]}")
            print("Is this correct?")
            usrYN = getUserInput(allowedUserInput="y/n")
            if usrYN.lower() != 'y':
                selectedAssignment = None

    return assignments.loc[assignments['common_name'] == selectedAssignment]


def setupScaling(_assignmentPoints: float) -> (float, float, float, float or None):
    assignmentScaleFactor: float = 1.0
    assignmentMaxPoints: float = _assignmentPoints
    assignmentXCScaleFactor: float or None = None

    print(f"Current standard points: {_assignmentPoints}")
    print("Would you like to override the standard points?")
    usrYN = getUserInput(allowedUserInput="y/n")
    if usrYN.lower() == 'y':
        _assignmentPoints = assignmentMaxPoints = float(input("(assignment_points): "))

    print("Should this assignment be scaled?")
    usrYN = getUserInput(allowedUserInput="y/n")
    if usrYN.lower() == 'y':
        assignmentScaleFactor = float(input("(assignment_scale_factor): "))

    print(f"Current max points: {assignmentMaxPoints}")
    print("Would you like to override the max points (doing this will allow extra credit)?")
    usrYN = getUserInput(allowedUserInput="y/n")
    if usrYN.lower() == 'y':
        assignmentMaxPoints = float(input("(assignment_max_points): "))

    if _assignmentPoints != assignmentMaxPoints:
        print("Should extra credit be scaled differently?")
        usrYN = getUserInput(allowedUserInput="y/n")
        if usrYN.lower() == 'y':
            assignmentXCScaleFactor = float(input("(xc_scaling): "))

    # returning in the same way that the grade.scale function expects its parameters
    return assignmentScaleFactor, _assignmentPoints, assignmentMaxPoints, assignmentXCScaleFactor


def setupMissingAssignments() -> (float or None, None):
    missingScore: float or None = None
    print("Should missing students be scored?")
    usrYN = getUserInput(allowedUserInput="y/n")
    if usrYN.lower() == 'y':
        missingScore = float(input("(missing_score): "))
        return missingScore, None
    return missingScore, None


def standardGrading(_canvas: Canvas):
    selectedAssignment: pd.DataFrame = assignmentsMenu(_canvas)
    print("Enter path to Gradescope grades")
    gradescopePath: str = getUserInput(allowedUserInput="./path/to/gradescope_grades.csv")
    specialCasesPath: str = getUserInput(allowedUserInput="./path/to/special_cases.cvs")
    gradescopeDF: pd.DataFrame = csvLoaders.loadGradescope(gradescopePath)
    if gradescopeDF.empty:
        print(f"Fatal: Failed to load Gradescope grades from {gradescopePath}")
        return False
    specialCasesDF: pd.DataFrame = csvLoaders.loadSpecialCases(specialCasesPath)
    if specialCasesDF.empty:
        print(f"Fatal: Failed to load Special Cases from {specialCasesPath}")
        return False

    print("\n===\tGenerating Grades\t===\n")
    scaleFactor, standardPoints, maxPoints, xcScaleFactor = setupScaling(selectedAssignment['points'].values[0])
    gradescopeDF = grade.scaleScores(gradescopeDF, scaleFactor, standardPoints, maxPoints, xcScaleFactor)
    missingScore, exceptions = setupMissingAssignments()
    gradescopeDF = grade.scoreMissingAssignments(gradescopeDF, score=missingScore, exceptions=exceptions)

    gradescopeDF, specialCasesDF = grade.calculateLatePenalty(gradescopeDF,
                                                              specialCasesDF,
                                                              selectedAssignment['common_name'].values[0])

    print("\nGrades have been generated. Would you like to continue?")
    usrYN = getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    gradescopeAssignments = {selectedAssignment['common_name'].values[0]: gradescopeDF}
    studentScores = score.createCanvasScoresForAssignments(
        gradescopeAssignments,
        specialCasesDF,
        _canvas,
        selectedAssignment['common_name'].values.tolist()
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeGrades(gradescopeAssignments) \
        and post.updateSpecialCases(specialCasesDF) \
            and post.postToCanvas(_canvas, studentScores):
        return True

    return False


def mainMenu():
    print("Please enter action to take:")
    print("1) Standard Grading")
    print("2) Exit")
    choice = getUserInput(allowedLowerRanger=1, allowedUpperRange=2)
    if choice == 1:
        return standardGrading
    if choice == 2:
        return exit


def main():
    loadedConfig = config.loadConfig()
    print("Connecting to Canvas...")
    canvas = Canvas()
    canvas.loadSettings(loadedConfig)
    canvas.getAssignmentsFromConfig(loadedConfig)
    canvas.getStudentsFromCanvas()

    operation = mainMenu()
    if not operation(canvas):
        print("Grading failed.")


if __name__ == "__main__":
    main()
