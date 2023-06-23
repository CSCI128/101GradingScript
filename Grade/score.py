"""
Description
================

This module contains the functions used to create Canvas scores. Basically,
all the functions in here merge the Dataframes produced by ``Grade.grade``.
This module does **not** create new grades nor does it modify existing grades.

This module **non-destructively** creates Canvas scores, meaning that nothing is committed to Canvas
and the source data is **not** modified.
"""
import pandas as pd
from Canvas import Canvas


# TODO Clean up unnecessary fields from this file.


def createCanvasScores(_gradescopeDF: pd.DataFrame,
                       _students: pd.DataFrame) -> dict[str, any]:
    """
    :Description:

    This function generates scores for **one** assignment. It builds all the comments that will be sent to the student
    in Canvas and assigns scores for each student.

    See ``score.createCanvasScoresForAssignments`` for an example of what this looks like.

    :param _gradescopeDF: The gradesheet to create scores from
    :param _students: the current canvas roster.

    :return: the dict representation of the assignment scores.
    """

    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope Grades MUST be passed as a Pandas DataFrame")

    if not isinstance(_students, pd.DataFrame):
        raise TypeError("Students MUST be passed as a Pandas DataFrame")

    gradedAssignment: dict = {}
    _students['graded'] = False
    for i, student in _students.iterrows():
        gradescopeCurrentStudent = _gradescopeDF['multipass'] == student['sis_id']
        # Handle the student not existing in gradescope
        if len(_gradescopeDF.loc[gradescopeCurrentStudent]) == 0:
            continue

        studentComment: str = ""
        # If the student has comment explaining where points went
        if _gradescopeDF.loc[gradescopeCurrentStudent]['lateness_comment'].values[0]:
            # Handle if the student has another comment already
            studentComment = _gradescopeDF.loc[gradescopeCurrentStudent]['lateness_comment'].values[0]

        score = _gradescopeDF.loc[gradescopeCurrentStudent]['Total Score'].values[0]

        gradedAssignment[student['id']] = {
            'name': student['name'],
            'id': str(student['id']),
            # If we chose to not score missing students - post an empty score to canvas
            'score': str(score) if score is not None else "",
            'comment': studentComment
        }
        _students.at[i, 'graded'] = True

    ungradedStudents: pd.Series = _students.loc[_students['graded'] == False]['name']
    if len(ungradedStudents) != 0:
        print("Warning")
        print(f"\t\t...{len(ungradedStudents)} unmatched students")
        for student in ungradedStudents:
            print(f"\t\t\t...{student} was not found")
    else:
        print("Done")

    return gradedAssignment

def createCanvasScoresForAssignments(_gradescopeAssignments: dict[int, pd.DataFrame],
                                     _canvas: Canvas, _assignments: pd.DataFrame) -> dict[str, dict[str, any]]:
    """
    :Description:

    This function grades a batch of assignments and creates a dict that can be posted to canvas. At a basic level,
    this function is mapping the gradescope scores that have been put through processing to canvas student ids.

    This function calls ``createCanvasScores`` internally to generate the scores for each assignment.

    This function also calls ``createCanvasScoresForStatusAssignments`` internally to create scores for those
    assignments, but that functionality is likely to be removed in favor of a solution that treats status assignments
    the same as normal assignments.


    :Example:

    .. code-block:: json

        {
             assignment_id: {
                  id: {
                       name:
                       id:
                       score:
                       comments:
                }
             }
        }

    :param _assignments: A dataframe containing all the assignments to grade.
    :param _gradescopeAssignments: A dict containing the assignment ids mapped to the grade sheets
    :param _canvas: the canvas object.

    :return: A map containing the assignment id and the scores to be posted under that id.
    """
    if type(_gradescopeAssignments) is not dict:
        raise TypeError("Gradescope assignments must be passed as a dict mapping the id to the assignment as "
                        "a Pandas DataFrame")

    if not isinstance(_canvas, Canvas):
        raise TypeError("Canvas must be an instance of the Canvas api Wrapper")

    students: pd.DataFrame = _canvas.getStudents()

    assignmentsToPost: dict[str, dict[str, any]] = {}

    print(f"Creating scores for {len(students)} students across {len(_gradescopeAssignments)} assignments...")

    for i, row in _assignments.iterrows():
        print(f"\tScoring {row['name']} for {len(students)} students...", end='')
        assignmentsToPost[row['id']] = \
            createCanvasScores(_gradescopeAssignments[row['id']],
                               students)

    print("...Done")
    return assignmentsToPost
