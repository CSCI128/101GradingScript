from UI import uiHelpers
from Canvas import Canvas
from Grade import grade, score, post
import pandas as pd


def standardGrading(_canvas: Canvas):
    uiHelpers.setupAssignments(_canvas)
    gradescopeGrades: dict[int, pd.DataFrame] = uiHelpers.setupGradescopeGrades(_canvas)
    specialCasesDF = uiHelpers.setupSpecialCases()

    assignmentsToGrade: pd.DataFrame = _canvas.getAssignmentsToGrade()

    print("\n===\tGenerating Grades\t===\n")

    for assignmentID, gradesDF in gradescopeGrades.items():
        # we know that if we got here that the id will exist and only map to one assignment
        currentAssignment: pd.DataFrame = assignmentsToGrade.loc[assignmentsToGrade['id'] == assignmentID]
        print(f"Now grading {currentAssignment['name'].values[0]}...")

        scaleFactor, standardPoints, maxPoints, xcScaleFactor = uiHelpers.setupScaling(currentAssignment['points'].values[0])
        gradescopeGrades[assignmentID] = \
            grade.scaleScores(gradesDF, scaleFactor, standardPoints, maxPoints, xcScaleFactor)

        missingScore, exceptions = uiHelpers.setupMissingAssignments()
        gradescopeGrades[assignmentID] = \
            grade.scoreMissingAssignments(gradesDF, score=missingScore, exceptions=exceptions)

        gradescopeGrades[assignmentID], specialCasesDF = \
            grade.calculateLatePenalty(gradesDF, specialCasesDF, currentAssignment['common_name'].values[0])

    print("\nGrades have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    studentScores = score.createCanvasScoresForAssignments(
        gradescopeGrades,
        specialCasesDF,
        _canvas,
        assignmentsToGrade
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeGrades(gradescopeGrades, assignmentsToGrade) \
            and post.updateSpecialCases(specialCasesDF) \
            and post.postToCanvas(_canvas, studentScores):
        return True

    return False
