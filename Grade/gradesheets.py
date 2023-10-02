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

from Bartik.Bartik import Bartik
from AzureAD import AzureAD

async def convertBartikToGradesheet(_azure: AzureAD, _bartik: Bartik, _students: pd.DataFrame, _assignment: str) -> pd.DataFrame:
    bartikGradesheet: pd.DataFrame = pd.DataFrame()
    bartikGradesheet['multipass'] = ""
    bartikGradesheet['Total Score'] = ""
    bartikGradesheet['lateness_comment'] = ""

    _bartik.openSession()

    counter = 0
    for _, row in _students.iterrows():
        counter += 1
        print(f"Now grading {row['name']} ({counter}/{len(_students)})...", end="")

        studentEmail: str = await _azure.getEmailFromCWID(row['sis_id'])
        
        if studentEmail == "":
            print(f"Failed to map email for {row['name']}")
            continue


        score: float = 0

        try:
            score = _bartik.getScoreForAssignment(studentEmail, _assignment)
        except Exception:
            print(f"Missing")

        bartikGradesheet = pd.concat([bartikGradesheet, pd.DataFrame(
                {
                    'multipass': row['sis_id'],
                    'Total Score': score,
                    'lateness_comment': "",
                }, index=[0]
            )], ignore_index=True)

        print("Done")
        

    return bartikGradesheet


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


def createGradesheetForPassFailAssignment(_passFailAssignment: pd.DataFrame, _students: pd.DataFrame,
                                          _passPoints: float, _failPoints: float,
                                          checkProofOfAttendance: bool = False,
                                          proofOfAttendanceColumn: (str, None) = None) \
        -> pd.DataFrame:

    if proofOfAttendanceColumn:
        proofOfAttendanceColumn = proofOfAttendanceColumn.replace(' ', '_')

    if checkProofOfAttendance and (proofOfAttendanceColumn not in _passFailAssignment.columns.values.tolist()):
        print(f"Unable to find column: {proofOfAttendanceColumn}")
        checkProofOfAttendance = False

    if not checkProofOfAttendance or not proofOfAttendanceColumn:
        print("Proof of attendance will not be verified")
        checkProofOfAttendance = False

    _passFailAssignment['Total Score'] = 0.0
    _passFailAssignment['lateness_comment'] = ""

    for i, row in _students.iterrows():
        currentStudent = _passFailAssignment['multipass'] == row['sis_id']
        # student has an entry - verify proof of attendance if needed
        if len(_passFailAssignment.loc[currentStudent]) == 1:
            # simply checking to see if there is *any* data in the proof of attendance column
            #  might want to expand this in the future
            if checkProofOfAttendance:
                if _passFailAssignment.loc[currentStudent, proofOfAttendanceColumn].values[0]:
                    _passFailAssignment.loc[currentStudent, 'Total Score'] = _passPoints

                else:
                    _passFailAssignment.loc[currentStudent, 'Total Score'] = _failPoints
                    _passFailAssignment.loc[currentStudent, 'lateness_comment'] = \
                        "Unable to verify proof of attendance.\nContact grader if you believe this is a mistake."

            else:
                _passFailAssignment.loc[currentStudent, 'Total Score'] = _passPoints
        else:
            # append a new student to the grade sheet and assign them a failure
            _passFailAssignment = \
                pd.concat([_passFailAssignment, pd.DataFrame({
                    'multipass': row['sis_id'],
                    'Total Score': _failPoints,
                    'lateness_comment': ''
                }, index=[0])], ignore_index=True)

    return _passFailAssignment



