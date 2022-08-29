"""
This file will handle all conversions to grade sheets as to treat not normal grades (ie from canvas)
as normal assignments in last steps in the grading process.

All generated gradesheets must have the fields: ``multipass``, ``Total Score``, and ``lateness_comment``.
The ``multipass`` is the students multipass as found from their email and Canvas. ``Total Score`` is the score
the student will receive on their assignment. ``lateness_comment`` is any comments that will be added to the student's
submission on canvas. When converting, ``lateness_comment`` might not be needed or might not exist, in which case it's
ok to just leave it as an empty string for all assignments.

This file **non-destructively** creates gradesheets. The generated gradesheets still have to be 'selected' in Canvas
in order to be scored and posted with everything else.
"""
import pandas as pd


def convertStatusAssignmentToGradesheet(_statusAssignment: pd.DataFrame) -> pd.DataFrame:
    """
    :Description:



    :param _statusAssignment:

    :return:
    """

    numOfAssignments = len(pd.unique(_statusAssignment['status_assignment_id']))

    if numOfAssignments != 1:
        raise AttributeError("Unable to process status assignments. More than one status assignment is present.")

    gradesheetForStatusAssignment: pd.DataFrame = pd.DataFrame()

    commentAvailable: bool = False
    if 'comment' in _statusAssignment.columns.values.tolist():
        commentAvailable = True

    # create required columns
    gradesheetForStatusAssignment['multipass'] = _statusAssignment['multipass']
    gradesheetForStatusAssignment['Total Score'] = _statusAssignment['student_score']
    # As of right now this functionality is not implemented in the scorer - but I want to have it for future revisions
    gradesheetForStatusAssignment['lateness_comment'] = _statusAssignment['comment'] if commentAvailable else ""

    return gradesheetForStatusAssignment
