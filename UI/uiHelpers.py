"""
"""
import pandas as pd
from FileHelpers.csvLoaders import loadGradescope
from FileHelpers.excelLoaders import loadSpecialCases
from Canvas import Canvas


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
