"""
Description
================

This module contains helper functions to post scores to Canvas.

This is the last step in the grading process and **IS** destructive. It will write the new scores to file and post them
to Canvas. It will also update the special cases file with the handled / not handled updates.

**AFTER GRADES ARE POSTED, THEY NEED TO BE MANUALLY PUBLISHED**

That functionality *is* supported by the Canvas api and can be added, but, for now, I am keeping it this way to
serve as a safety mechanism.
"""

from Canvas import Canvas
import pandas as pd
from datetime import date
import os
from FileHelpers.csvWriter import csvWriter
from FileHelpers.excelWriter import writeSpecialCases

BATCH_SIZE = 50


def writeUpdatedGradebookToFile(_canvasScores: dict[str, dict[any, any]],
                                _students: pd.DataFrame, _assignmentsToGrade: pd.DataFrame) -> bool:
    """
    :Description:

    This function generates a Canvas gradebook from the scores generated, the students pulled from canvas,
    and the all the assignments that have been selected to grade then writes it to file.
    This function generates all the metadata in a *very* specific way for Canvas. Because Mines uses SIS
    integration, we have to include the columns 'SIS User ID' and 'SIS Login ID'. Only one of those actually
    to be populated for Canvas to be able to process the gradebook. We also require the Canvas ID and student name.

    For the actual scores for assignments, again they have to be formatted in a very specific way to automatically
    import them. The format *required* by Canvas is ``Canvas Assignment Name (Canvas Assignment ID)``. For example:
    HW6 is ``HW6 - Hardware & Software (283462)``.

    This function requires that all assignment in ``_canvasScores`` to be in the ``_assignmentsToGrade``,
    otherwise a mismatched key error will be thrown.

    The filename used is: ``canvas_{current_date}_{assignments_in_grade_book}.csv``

    For example: a gradebook generated on Feb 2nd, 2022 for Late Passes and HW6 would be:
    ``canvas_02-02-22_HW6_LPL.csv``

    :param _canvasScores: The generated canvas scores, See ``Grade.score`` for more information
    :param _students: All the students in the pulled from the Canvas roster at the start of execution.
    :param _assignmentsToGrade: The assignments to grade. Must be the same length as ``_canvasScores``

    :return: True if the gradebook was successfully generated and written. False if not.
    """

    if not isinstance(_students, pd.DataFrame):
        raise TypeError("Students to post MUST be a Pandas dataframe")
    if not isinstance(_assignmentsToGrade, pd.DataFrame):
        raise TypeError("Assignments to grade MUST be a Pandas dataframe")

    # Even though indexes are not guaranteed to be the same from run to run, it doesn't matter as long as the name,
    #  SIS Login, and Canvas ID align, which they will as we are using Dataframes.
    formattedGradebook: pd.DataFrame = pd.DataFrame(
        {
            'Student': _students['name'],
            'ID': _students['id'],
            'SIS User ID': "",
            'SIS Login ID': _students['sis_id'],
            'Section': ""
        }
    )
    assignmentsInGradebook: str = ""
    for assignmentID, grades in _canvasScores.items():
        assignment = _assignmentsToGrade.loc[_assignmentsToGrade['id'] == assignmentID]

        assignmentsInGradebook += f"_{assignment['common_name'].values[0]}"
        fullGradebookName = f"{assignment['name'].values[0]} ({assignmentID})"
        formattedGradebook[fullGradebookName] = ""

        for i, row in formattedGradebook.iterrows():
            try:
                formattedGradebook.at[i, fullGradebookName] = grades[row['ID']]['score']
            except KeyError:
                pass

    print(f"Updated gradebook is ready to be written to file. ")
    print("Please confirm: This operation will write the updated canvas gradebook to file"
          " and CAN NOT be reversed.")

    usrConfirm = str(input("(y/n): "))

    if usrConfirm.lower() != 'y':
        return False

    print(f"Writing updated gradebook to file...")
    todayDate: str = date.today().strftime("%m-%d-%y")

    fullPath = f"./canvas/graded/canvas_{todayDate}{assignmentsInGradebook}_graded.csv"

    if not csvWriter(fullPath, formattedGradebook):
        print(f"\t\tWriting {fullPath} failed.")
        print("...Failed")
        return False

    print("...Done")
    return True


def postToCanvas(_canvas: Canvas, _canvasScores: dict[str, dict[any, any]],
                 studentsToPost: (pd.DataFrame, list, None) = None) -> bool:
    """
    :Description:

    This function generates form data from the Canvas scores to be sent to Canvas to be posted in the Gradebook.
    This function makes use of the Submission Canvas API, which allows us to post grades, comments, and actual
    student work - which may be nice if I decide to expand this project to mirror submissions on gradescope.

    Currently, this function generates the form data with student scores and comments in batches of 50 scores then sends
    that data to Canvas.

    **THIS FUNCTION DOES NOT PUBLISH GRADES FOR STUDENTS**

    While the Canvas API supports that functionality, the grader should manually verify that the posted scores are what
    they think they are then manually publish the scores.
    (done by clicking the column -> three dot menu -> post grades -> everyone -> post)

    Currently, this function only supports passing either a dataframe in for the students to post or a None type,
    which will map to all students.

    :param _canvas: The Canvas object.
    :param _canvasScores: The scores to post to Canvas.
    :param studentsToPost: The students to post. If it is None it will post all students.

    :return true if we received all 200 responses from canvas. See ``Canvas.postAssignment``. False if not
    """

    if studentsToPost is not None and type(studentsToPost) is not list:
        raise TypeError("Students to post MUST be a list of student names")

    # TODO Handle if not all students should be posted

    if studentsToPost is None:
        studentsToPost = _canvas.getStudents()

    # TODO Move this elsewhere
    # Really don't like how the status is not being checked after this
    writeUpdatedGradebookToFile(_canvasScores, studentsToPost, _canvas.getAssignmentsToGrade())

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


def writeUpdatedGradesheets(_gradescopeAssignments: dict[int, pd.DataFrame], _assignmentsToGrade: pd.DataFrame) -> bool:
    """
    :Description:

    Writes the modified gradescope dataframe to file.
    Includes student multipass, student scores, all submission comments, and assignment status
    (either 'Graded' or 'Missing')

    The file name written is: ``{common_name}_graded.csv``

    For example, grades for HW6 would be written as: ``HW6_graded.csv``

    :param _gradescopeAssignments: A dict that maps the assignment ids to its corresponding grade sheet.
    :param _assignmentsToGrade: The assignments to grade.

    :return: True if *all* gradesheets where written correctly. False if not.
    """
    if not isinstance(_assignmentsToGrade, pd.DataFrame):
        raise TypeError("Assignments to grade MUST be a Pandas dataframe")

    print(f"{len(_gradescopeAssignments)} assignment grades are ready to be written to file.")
    print("Please confirm: This operation will write the updated graded assignments to file"
          " and CAN NOT be reversed.")

    usrConfirm = str(input("(y/n): "))

    if usrConfirm.lower() != 'y':
        return False

    # TODO verify that './gradescope/graded/' exists and create it if it doesn't

    print(f"Writing {len(_gradescopeAssignments)} assignments to file...")
    for assignmentID, grades in _gradescopeAssignments.items():
        print(f"\tWriting '{_assignmentsToGrade.loc[_assignmentsToGrade['id'] == assignmentID, 'name'].values[0]}'"
              f" to file...",  end='')

        fullPath = f"./gradescope/graded/" \
                   f"{_assignmentsToGrade.loc[_assignmentsToGrade['id'] == assignmentID, 'common_name'].values[0]}" \
                   f"_graded.csv"

        if not csvWriter(fullPath, grades):
            print("Failed")
            print(f"\t\tWriting {fullPath} failed.")
            print("...Failed")
            return False
        print("Done")

    print("...Done")
    return True


def updateSpecialCases(_specialCasesDF: pd.DataFrame) -> bool:
    """
    :Description:

    Writes the updated special cases Dataframe to file. See ``FileHelpers.excelWriter.writeSpecialCases`` for more
    information.

    :param _specialCasesDF: The special cases dataframe to be written.

    :return: True if the special cases were successfully updated. False if not.
    """
    # no need to update the special cases
    if 'ignore' in _specialCasesDF.columns.values.tolist():
        return True
    print("Special cases are ready to be updated. Please enter the file name to write")
    fileName = str(input("(file_name.xlsx): "))

    if os.path.exists(fileName) and os.path.isfile(fileName):
        print(f"Warning: this operation will overwrite {fileName}")

    print("Please confirm: This operation will write the updated special cases to file"
          " and CAN NOT be reversed.")
    usrConfirm = str(input("(y/n): "))

    if usrConfirm.lower() != 'y':
        return False

    print(f"Writing special cases to file...")
    if not writeSpecialCases(fileName, _specialCasesDF):
        print(f"\tWriting updated special cases tp '{fileName}' failed.")
        print("...Failed")
        return False

    print("...Done")
    return True
