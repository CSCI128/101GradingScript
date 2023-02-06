from UI import uiHelpers
from Canvas import Canvas
from Grade import grade, score, post, gradesheets
import pandas as pd


def standardGrading(**kwargs):
    statusAssignments: pd.DataFrame = kwargs['canvas'].getStatusAssignments()
    kwargs['canvas'].updateStatusAssignmentScores()
    statusAssignmentScores: pd.DataFrame = kwargs['canvas'].getStatusAssignmentScores()
    uiHelpers.setupAssignments(kwargs['canvas'])
    gradesheetsToGrade: dict[int, pd.DataFrame] = uiHelpers.setupGradescopeGrades(kwargs['canvas'])
    specialCasesDF = uiHelpers.setupSpecialCases()

    assignmentsToGrade: pd.DataFrame = kwargs['canvas'].getAssignmentsToGrade()

    print("\n===\tGenerating Grades\t===\n")

    for assignmentID, gradesDF in gradesheetsToGrade.items():
        # we know that if we got here that the id will exist and only map to one assignment
        currentAssignment: pd.DataFrame = assignmentsToGrade.loc[assignmentsToGrade['id'] == assignmentID]
        print(f"Now grading {currentAssignment['name'].values[0]}...")

        scaleFactor, standardPoints, maxPoints, xcScaleFactor = uiHelpers.setupScaling(
            currentAssignment['points'].values[0])
        gradesheetsToGrade[assignmentID] = \
            grade.scaleScores(gradesDF, scaleFactor, standardPoints, maxPoints, xcScaleFactor)

        missingScore, exceptions = uiHelpers.setupMissingAssignments()
        gradesheetsToGrade[assignmentID] = \
            grade.scoreMissingAssignments(gradesDF, score=missingScore, exceptions=exceptions)

        gradesheetsToGrade[assignmentID], specialCasesDF, statusAssignmentScores = \
            grade.calculateLatePenalty(gradesDF, specialCasesDF, statusAssignments, statusAssignmentScores,
                                       currentAssignment['common_name'].values[0], kwargs['latePenalty'])

    if len(statusAssignments) != 0:
        print("Updating Status Assignments...", end="")

        for i, row in statusAssignments.iterrows():
            currentAssignment: pd.DataFrame = \
                statusAssignmentScores.loc[statusAssignmentScores['status_assignment_id'] == row['id']]

            # if there are no assignments found
            if len(currentAssignment) == 0:
                continue

            gradesheetsToGrade[row['id']] = gradesheets.convertStatusAssignmentToGradesheet(currentAssignment)

            # 'activate' the assignments so that they can be graded
            kwargs['canvas'].selectAssignmentsToGrade([row['common_name']])

        assignmentsToGrade = kwargs['canvas'].getAssignmentsToGrade()

        print("Done")

    print("\nGrades have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    studentScores = score.createCanvasScoresForAssignments(
        gradesheetsToGrade,
        kwargs['canvas'],
        assignmentsToGrade
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeUpdatedGradesheets(gradesheetsToGrade, assignmentsToGrade) \
            and post.updateSpecialCases(specialCasesDF) \
            and post.postToCanvas(kwargs['canvas'], studentScores):
        return True

    return False
