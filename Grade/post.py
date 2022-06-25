"""
This module contains helper functions to post scores to Canvas.

This is the last step in the grading process and **IS** destructive. It will write the new scores to file and post them
to Canvas. It will also update the special cases file with the handled / not handled updates.

**AFTER GRADES ARE POSTED, THEY NEED TO BE MANUALLY PUBLISHED**

That functionality *is* supported by the Canvas API and can be added, but, for now, I am keeping it this way to
serve as a safety mechanism.
"""

from Canvas import Canvas
import pandas as pd
from datetime import date
import os

BATCH_SIZE = 50


def writeUpdatedGradebookToFile(_canvas: Canvas, _canvasScores: dict[str, dict[any, any]], _students: pd.DataFrame):
    formattedGradebook: pd.DataFrame = pd.DataFrame(
        {'Student': _students['name'],
         'ID': _students['id'],
         'SIS User ID': "",
         'SIS Login ID': _students['sis_id'],
         'Section': ""
         }
    )
    for assignmentID, grades in _canvasScores.items():
        assignment = _canvas.getAssignmentFromID(int(assignmentID))
        assignment = f"{assignment['name'].values[0]} ({assignmentID})"
        formattedGradebook[assignment] = ""
        for i, row in formattedGradebook.iterrows():
            try:
                formattedGradebook.at[i, assignment] = grades[row['ID']]['score']
            except KeyError:
                pass

    print(f"Updated gradebook is ready to be written to file. ")
    print("Please confirm: This operation will write the updated canvas gradebook to file"
          " and CAN NOT be reversed.")

    usrConfirm = str(input("(y/n): "))

    if usrConfirm.lower() != 'y':
        return False

    print(f"Writing updated gradebook to file...")
    todayDate: str = date.today().strftime("%y-%m-%d")

    fullPath = f"./canvas/graded/canvas_{todayDate}_graded.csv"
    try:
        with open(fullPath, "w") as fileOut:
            formattedGradebook.to_csv(path_or_buf=fileOut, index=False)
    except:
        print(f"\t\tWriting {fullPath} failed.")
        print("...Failed")
        return False
    print("...Done")


def postToCanvas(_canvas: Canvas, _canvasScores: dict[str, dict[any, any]], studentsToPost: pd.DataFrame = None):
    if studentsToPost is not None and type(studentsToPost) is not list:
        raise TypeError("Students to post MUST be a list of student names")

    if studentsToPost is None:
        studentsToPost = _canvas.getStudents()

    writeUpdatedGradebookToFile(_canvas, _canvasScores, studentsToPost)

    print(f"{len(_canvasScores)} assignments are ready to be posted to Canvas.")

    print("Please confirm: This operation will post the current scores to Canvas and"
          " CAN NOT be reversed")

    usrConfirm = str(input("(y/n): "))
    if usrConfirm.lower() != 'y':
        return False

    print(f"Posting scores for {len(studentsToPost)} students across {len(_canvasScores)} assignments...")

    for assignment, grades in _canvasScores.items():
        batchedAssignments: list[str] = []
        currentBatch: str = ""
        currentBatchSize: int = 0

        for student, grade in grades.items():
            # We don't know how many scores can be posted at once to canvas because
            #  naturally, it isn't documented anywhere. So I am playing it safe and limiting the size that we will
            #  be sending to canvas at a time.
            if currentBatchSize >= BATCH_SIZE:
                batchedAssignments.append(currentBatch)
                currentBatchSize = 0
                currentBatch = ""
            # TODO Validate grade
            if currentBatchSize == 0:
                currentBatch += f"grade_data[{grade['id']}][posted_grade]={grade['score']}&" \
                                f"grade_data[{grade['id']}][text_comment]={grade['comment']}"
            else:
                currentBatch += f"&grade_data[{grade['id']}][posted_grade]={grade['score']}&" \
                                f"grade_data[{grade['id']}][text_comment]={grade['comment']}"

            currentBatchSize += 1
        # Handle if we have a non-multiple of 50 currently batched - this check worked bc current batch size
        #  will be zero if it was reset.
        if currentBatchSize != 0:
            batchedAssignments.append(currentBatch)

        print(f"\tPosting scores for id {assignment} in {len(batchedAssignments)} batches...")
        if not _canvas.postAssignment(assignment, batchedAssignments):
            print("...Failed")
            return False

    print("...Done")
    return True


def writeGrades(_gradescopeAssignments: dict[str, pd.DataFrame]):
    print(f"{len(_gradescopeAssignments)} assignment grades are ready to be written to file.")
    print("Please confirm: This operation will write the updated graded assignments to file"
          " and CAN NOT be reversed.")

    usrConfirm = str(input("(y/n): "))

    if usrConfirm.lower() != 'y':
        return False

    print(f"Writing {len(_gradescopeAssignments)} assignments to file...")
    for assignment, grades in _gradescopeAssignments.items():
        print(f"\tWriting {assignment} to file...", end='')
        fullPath = f"./gradescope/graded/{assignment}_graded.csv"
        try:
            with open(fullPath, "w") as fileOut:
                grades.to_csv(path_or_buf=fileOut, index=False)
        except:
            print("Failed")
            print(f"\t\tWriting {fullPath} failed.")
            print("...Failed")
            return False
        print("Done")

    print("...Done")
    return True


def updateSpecialCases(_specialCases: pd.DataFrame):
    _specialCases.drop(columns={'multipass'}, inplace=True)

    print("Special cases are ready to be updated. Please enter the file name to write")
    fileName = str(input("(file_name.csv): "))

    completePath: str = "./" + fileName
    if ".csv" not in completePath:
        completePath += ".csv"

    if os.path.exists(completePath) and os.path.isfile(completePath):
        print(f"Warning: this operation will overwrite {completePath}")

    print("Please confirm: This operation will write the updated special cases to file"
          " and CAN NOT be reversed.")
    usrConfirm = str(input("(y/n): "))

    if usrConfirm.lower() != 'y':
        return False

    print(f"Writing special cases to file...")
    try:
        with open(completePath, 'w') as fileOut:
            _specialCases.to_csv(path_or_buf=fileOut, index=False)
    except:
        print(f"\tWriting {completePath} to file failed.")
        print("...Failed")
        return False

    print("...Done")
    return True
