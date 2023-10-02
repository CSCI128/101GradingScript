from typing import Optional
from UI import uiHelpers
from Canvas import Canvas 
from Grade import gradesheets, score, post
import pandas as pd


async def bartikGrading(canvas, azure, bartik, **kwargs) -> bool:
    uiHelpers.setupAssignments(canvas)

    bartikAssignmentsToGrade: dict[int, pd.DataFrame] = {}
    assignmentsToGrade = canvas.getAssignmentsToGrade()
    
    for i, row in assignmentsToGrade.iterrows():
        print("=" * 4, f"Now grading {row['name']}", "=" * 4)
        studioNumber: str = uiHelpers.getUserInput("studio number")
        requiredProblems: int = int(uiHelpers.getUserInput("required problems"))

        bartikAssignmentsToGrade[row['id']] = await gradesheets.convertBartikToGradesheet(azure, bartik, canvas.getStudents(), studioNumber, row['points'], requiredProblems)


    print("\nGrades have been generated. Would you like to continue?")
    usrYN: str = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    studentScores = score.createCanvasScoresForAssignments(
        bartikAssignmentsToGrade,
        canvas,
        assignmentsToGrade
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeUpdatedGradesheets(bartikAssignmentsToGrade, assignmentsToGrade) \
            and post.postToCanvas(canvas, studentScores):
        return True

    return False
