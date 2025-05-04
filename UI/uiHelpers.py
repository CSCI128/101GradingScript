"""
"""
import pandas as pd

from AzureAD import AzureAD
from FileHelpers.csvLoaders import loadGradescope, loadRunestone, loadPrairieLearn
from FileHelpers.excelLoaders import loadSpecialCases, loadPassFailAssignment
from Canvas import Canvas
from Grade.gradesheets import finalizeGradesheet


def getUserInput(allowedUserInput: str = None, allowedLowerRange: int = None, allowedUpperRange: int = None):
    if allowedLowerRange is None and allowedUpperRange is None and allowedUserInput is None:
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

    if allowedLowerRange is not None and allowedUpperRange is not None:
        usrIn = allowedLowerRange - 1
        errorOccurred = False
        while not (allowedLowerRange <= usrIn <= allowedUpperRange):
            try:
                usrIn = int(input(f"({allowedLowerRange} - {allowedUpperRange}): "))
            except ValueError:
                usrIn = allowedLowerRange - 1
                errorOccurred = True
                print("Invalid Input")
            finally:
                if allowedLowerRange <= usrIn <= allowedUpperRange:
                    return usrIn
                elif not errorOccurred:
                    print("Invalid Input")
                else:
                    errorOccurred = False


def setupAssignments(_canvas: Canvas):
    # TODO this function needs to cleaned up a bit more - need to reevaluate the process for selecting assignments
    print("Please enter common name of assignments to grade, typing \'done\' when finished")
    print("(EG: HW7 - Whatever and Whatever == HW7, Lab 18 - Crying myself to sleep == L18)")

    selectedAssignment: str = ""
    selectedAssignmentsCommonNames: list[str] = []
    while selectedAssignment.lower() != "done":
        selectedAssignment = getUserInput(allowedUserInput="Common Name or done")
        if selectedAssignment.lower() != "done" and not _canvas.validateAssignment(commonName=selectedAssignment):
            print("Unable to map Common Name to Canvas assignment")
            # TODO Implement assignment overriding
            # print("Would you like to override this warning?")
            # usrYN = getUserInput(allowedUserInput="y/n")
            # if usrYN.lower() == 'y':
            #     raise NotImplementedError("Manual Overriding is not implemented")
        elif selectedAssignment.lower() != "done":
            # TODO
            #  this is really hacky - but it will do until I get around to improving it
            #  I think a decent solution would be this function adding the assignments to the list to be graded rather
            #   than adding them all at the end - but that's kinda a pain, and I need to get this done :(
            print(
                f"Identified assignment {_canvas.getAssignments().loc[_canvas.getAssignments()['common_name'] == selectedAssignment, 'name'].values[0]}")
            print("Is this correct?")
            usrYN = getUserInput(allowedUserInput="y/n")
            if usrYN.lower() != 'y':
                selectedAssignment = ""
                continue
            selectedAssignmentsCommonNames.append(selectedAssignment)

    if len(selectedAssignmentsCommonNames) == 0:
        print("No assignments were selected for grading")
        return

    _canvas.selectAssignmentsToGrade(selectedAssignmentsCommonNames)


def setupGradescopeGrades(_canvas: Canvas) -> dict[int, pd.DataFrame]:
    # the IDs will always be unique per course - using those over the common names
    selectedAssignments: pd.DataFrame = _canvas.getAssignmentsToGrade()
    assignmentMap: dict[int, pd.DataFrame] = {}
    if selectedAssignments is None:
        return assignmentMap
    for i, row in selectedAssignments.iterrows():
        print(f"Enter path to Gradescope grades for {row['common_name']}")
        path = getUserInput(allowedUserInput="./path/to/gradescope/grades.csv")
        gradescopeDF: pd.DataFrame = loadGradescope(path)
        if gradescopeDF.empty:
            print(f"Failed to load file '{path}'")
            # TODO handle this case more elegantly
            return {}
        assignmentMap[row['id']] = gradescopeDF

    return assignmentMap

async def setupPLGrades(canvas: Canvas, azure: AzureAD) -> dict[int, pd.DataFrame]:
    # the IDs will always be unique per course - using those over the common names
    selectedAssignments: pd.DataFrame = canvas.getAssignmentsToGrade()
    assignmentMap: dict[int, pd.DataFrame] = {}
    if selectedAssignments is None:
        return assignmentMap
    for i, row in selectedAssignments.iterrows():
        print(f"Enter path to pl grades for {row['common_name']}")
        path = getUserInput(allowedUserInput="./path/to/pl/grades.csv")
        plDf: pd.DataFrame = await finalizeGradesheet(azure, loadPrairieLearn(path))
        if plDf.empty:
            print(f"Failed to load file '{path}'")
            # TODO handle this case more elegantly
            return {}
        assignmentMap[row['id']] = plDf

    return assignmentMap

def setupRunestoneGrades(_canvas: Canvas) -> dict[int, pd.DataFrame]:
    # the IDs will always be unique per course - using those over the common names
    selectedAssignments: pd.DataFrame = _canvas.getAssignmentsToGrade()
    assignmentMap: dict[int, pd.DataFrame] = {}
    if selectedAssignments is None:
        return assignmentMap
    for i, row in selectedAssignments.iterrows():
        print(f"Enter path to Runestone grades for {row['common_name']}")
        path = getUserInput(allowedUserInput="./path/to/runestone/grades.csv")
        runestoneDF: pd.DataFrame = loadRunestone(path, row['name'])
        if runestoneDF.empty:
            print(f"Failed to load file '{path}'")
            # TODO handle this case more elegantly
            return {}
        assignmentMap[row['id']] = runestoneDF

    return assignmentMap


def setupPassFailAssignments(_canvas: Canvas) -> dict[int, pd.DataFrame]:
    # the IDs will always be unique per course - using those over the common names
    selectedAssignments: pd.DataFrame = _canvas.getAssignmentsToGrade()
    assignmentMap: dict[int, pd.DataFrame] = {}
    if selectedAssignments is None:
        return assignmentMap
    for i, row in selectedAssignments.iterrows():
        print(f"Enter path to pass/fail assignment for {row['common_name']}")
        path = getUserInput(allowedUserInput="./path/to/assignment.xlsx")
        passFailAssignmentDF: pd.DataFrame = loadPassFailAssignment(path)
        if passFailAssignmentDF.empty:
            print(f"Failed to load file '{path}'")
            # TODO handle this case more elegantly
            return {}
        assignmentMap[row['id']] = passFailAssignmentDF

    return assignmentMap


def setupSpecialCases() -> pd.DataFrame:
    return loadSpecialCases()


def setupScaling(_assignmentPoints: float) -> (float, float, float, (float, None)):
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


def setupProofOfAttendance(_columnNames: list[str]) -> (bool, None or bool, str):
    print("Should proof of attendance be verified?")
    usrYN = getUserInput(allowedUserInput="y/n")
    if usrYN.lower() == 'y':
        print("Enter name of column where proof of attendance is. Available columns are:")
        for el in _columnNames:
            print(el, end=", ")
        print("\b\n", end='')
        userIn = ""
        while userIn not in _columnNames:
            userIn = str(input("(column_name): "))
            if userIn not in _columnNames:
                print(f"Invalid column name: {userIn}")
        return True, userIn

    return False, None


def setupPassFailScores() -> (float, float):
    print("Enter score for students who passed / completed this assignment")

    passScore = float(input("(passing_score): "))

    print("Enter score for students who failed / did *not* complete this assignment")

    failScore = float(input("(failing_score): "))

    return passScore, failScore
