from typing import Optional
from UI import uiHelpers
from Canvas import Canvas 
from Grade import gradesheets, score, post
import asyncio
import pandas as pd


def bartikGrading(canvas, azure, bartik, **kwargs) -> bool:
    uiHelpers.setupAssignments(canvas)

    bartikAssignmentsToGrade: dict[int, pd.DataFrame] = {}
    assignmentsToGrade = canvas.getAssignmentsToGrade()
    
    for _, row in assignmentsToGrade:
        studioNumber: str = uiHelpers.getUserInput("studio number")

        bartikAssignmentsToGrade[row['id']] = asyncio.run(gradesheets.convertBartikToGradesheet(azure, bartik, canvas.getStudents(), studioNumber))


    print("\nGrades have been generated. Would you like to continue?")
    usrYN: str = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    studentScores = score.createCanvasScoresForAssignments(
        bartikAssignmentsToGrade,
        kwargs['canvas'],
        assignmentsToGrade
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = uiHelpers.getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeUpdatedGradesheets(bartikAssignmentsToGrade, assignmentsToGrade) \
            and post.postToCanvas(kwargs['canvas'], studentScores):
        return True

    return False
