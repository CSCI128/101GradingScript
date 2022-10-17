from UI import uiHelpers
from Canvas import Canvas
from Grade import grade, score, post, gradesheets
import pandas as pd


def passFail(_canvas: Canvas) -> bool:
    uiHelpers.setupAssignments(_canvas)

    passFailAssignmentsToGrade: dict[int, pd.DataFrame] = uiHelpers.setupPassFailAssignments(_canvas)

    assignmentsToGrade: pd.DataFrame = _canvas.getAssignmentsToGrade()

    for assignmentID, assignmentDF in passFailAssignmentsToGrade.items():
        currentAssignment: pd.DataFrame = assignmentsToGrade.loc[assignmentsToGrade['id'] == assignmentID]

        print(f"Now grading {currentAssignment['name'].values[0]}...")

        passScore, failScore = uiHelpers.setupPassFailScores()

        proofOfAttendance, proofOfAttendanceColumn = \
            uiHelpers.setupProofOfAttendance(assignmentDF.columns.values.tolist())

        passFailAssignmentsToGrade[assignmentID] = gradesheets.createGradesheetForPassFailAssignment(
            assignmentDF, _canvas.getStudents(), passScore, failScore, proofOfAttendance, proofOfAttendanceColumn
        )

    print("\nGrades have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    studentScores = score.createCanvasScoresForAssignments(
        passFailAssignmentsToGrade,
        _canvas,
        assignmentsToGrade
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeUpdatedGradesheets(passFailAssignmentsToGrade, assignmentsToGrade) \
            and post.postToCanvas(_canvas, studentScores):
        return True

    return False
