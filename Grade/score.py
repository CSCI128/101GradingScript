"""
This module contains the functions used to create Canvas scores. Basically,
all the functions in here merge the Dataframes produced by ``Grade.grade``.
This module does **not** create new grades nor does it modify existing grades.

This module **non-destructively** creates Canvas scores, meaning that nothing is committed to Canvas
and the source data is **not** modified.
"""
import pandas as pd
from Canvas import Canvas


def createCanvasScores(_gradescopeDF: pd.DataFrame, _specialCasesDF: pd.DataFrame,
                       _students: pd.DataFrame, _assignmentID: int):
    """

    :param _assignmentID:
    :param _gradescopeDF:
    :param _specialCasesDF:
    :param _students:
    :return:
    """

    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope Grades MUST be passed as a Pandas DataFrame")

    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise TypeError("Special cases MUST be passed as a Pandas DataFrame")

    if not isinstance(_students, pd.DataFrame):
        raise TypeError("Students MUST be passed as a Pandas DataFrame")

    if type(_assignmentID) is not int or len(str(_assignmentID)) < 5:
        raise TypeError("Assignment ID MUST be a int containing a valid Canvas assignment id")

    gradedAssignment: dict = {}
    _students['graded'] = False
    for i, student in _students.iterrows():
        gradescopeCurrentStudent = _gradescopeDF['multipass'] == student['sis_id']
        # Handle the student not existing in gradescope
        if len(_gradescopeDF.loc[gradescopeCurrentStudent]) == 0:
            continue

        studentComment: str = ""
        # get the student's special cases
        studentSpecialCase: pd.DataFrame = _specialCasesDF.loc[_specialCasesDF['multipass'] == student['sis_id']]
        # add a comment to the student's submission explaining any extension or special cases
        if len(studentSpecialCase['extension_days']) != 0 and studentSpecialCase['extension_days'].values[0] > 0 and studentSpecialCase['handled'].values[0] == "TRUE":
            studentComment = f"Extended by {studentSpecialCase['extension_days'].values[0]} days."
            # Let students know where their late passes have gone
            if studentSpecialCase['extension_type'].values[0] == "Late Pass":
                studentComment += f"\n{studentSpecialCase['extension_days'].values[0]} late passes used"
            # maybe add comment if case was not handled correctly
        if _gradescopeDF.loc[gradescopeCurrentStudent]['lateness_comment'].values[0]:
            # Handle if the student has another comment already
            if studentComment:
                studentComment += "\n"
            studentComment += \
                _gradescopeDF.loc[gradescopeCurrentStudent]['lateness_comment'].values[0]

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


def createCanvasScoresForStatusAssignments(statusAssignmentScoresDF: pd.DataFrame, _students: pd.DataFrame) \
        -> dict[str, any]:
    if not isinstance(statusAssignmentScoresDF, pd.DataFrame):
        raise TypeError("Status Assignments MUST be passed as a Pandas DataFrame")
    if not isinstance(_students, pd.DataFrame):
        raise TypeError("Students MUST be passed as a Pandas DataFrame")

    # TODO currently the way that scoring is implemented will only allow one status assignment to be updated
    scoredStatusAssignments: dict[str, any] = {}
    for i, assignment in statusAssignmentScoresDF.iterrows():
        student = _students.loc[_students['sis_id'] == assignment['multipass']]
        scoredStatusAssignments[student['id'].values[0]] = {
            'name': student['name'].values[0],
            'id': str(student['id'].values[0]),
            'score': assignment['student_score'],
            'comment': ""
        }

    return scoredStatusAssignments


def createCanvasScoresForAssignments(_gradescopeAssignments: dict[int, pd.DataFrame],
                                     _specialCasesDF: pd.DataFrame, _canvas: Canvas, _assignments: pd.DataFrame) \
        -> dict[str, dict[str, any]]:
    """
   Description
    --------
    This function grades a batch of assignments and creates a dict that can be posted to canvas. At a basic level,
    this function is mapping the gradescope scores that have been put through processing to canvas student ids.
   Example
    --------
    {
     assignment_id: {
      id: {
       name:

       id:

       score:

       comments:
      },
     }
    }

    :param _assignments:
    :param _gradescopeAssignments:
    :param _specialCasesDF:
    :param _canvas:
    :return: A map containing the assignment id and the scores to be posted under that id.
    """
    if type(_gradescopeAssignments) is not dict:
        raise TypeError("Gradescope assignments must be passed as a dict mapping the id to the assignment as "
                        "a Pandas DataFrame")

    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise TypeError("Special cases MUST be passed as a Pandas DataFrame")

    if not isinstance(_canvas, Canvas):
        raise TypeError("Canvas must be an instance of the Canvas api Wrapper")

    students: pd.DataFrame = _canvas.getStudents()

    assignmentsToPost: dict[str, dict[str, any]] = {}

    print(f"Creating scores for {len(students)} students across {len(_gradescopeAssignments)} assignments...")

    for i, row in _assignments.iterrows():
        print(f"\tScoring {row['name']} for {len(students)} students...", end='')
        assignmentsToPost[row['id']] = \
            createCanvasScores(_gradescopeAssignments[row['id']],
                               _specialCasesDF.loc[_specialCasesDF['assignment'] == row['common_name']],
                               students, row['id'])

    statusAssignmentsScores = _canvas.getStatusAssignmentScores()
    print(f"Creating scores for {len(statusAssignmentsScores)} status assignments...")
    assignmentsToPost[statusAssignmentsScores['status_id'].values[0]] = \
        createCanvasScoresForStatusAssignments(statusAssignmentsScores, students)
    # add the status assignments to the actively graded assignments
    _canvas.selectAssignmentsToGrade([_canvas.getAssignmentFromID(statusAssignmentsScores['status_id'].values[0])['common_name'].values[0]])
    print("...Done")
    return assignmentsToPost
