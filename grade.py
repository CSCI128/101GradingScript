import math

import pandas as pd

from Canvas import Canvas


def scaleScores(_gradescopeDF: pd.DataFrame, _scaleFactor: float,
                assignmentPoints: float = None, maxScore: float = None, XCScaleFactor: float = None):
    """
    This function scales the scores by the scale factor. It also takes into account different extra credit scaling.
    This function does NOT consider lateness or page flagging in its calculations

    :param _gradescopeDF: the current grades for the current assigment
    :param _scaleFactor: the scaling to apply to each grade
    :param assignmentPoints: the total amount of *regular* *scaled* points the assignment has.
            If not set, function assumes that *no* extra credit scaling is required
    :param maxScore: the maximum *total* *scaled* score a student can get. Includes extra credit
            If not set, function assumes that there is *no* upper score bound
    :param XCScaleFactor: the scaling to apply to any points above the 'assignmentPoints' var
            If not set, function assumes that normal scaling (as defined in '_scaleFactor')
            also applies to extra credit
    :example:
        If we have an assignment that is worth 5 points, but has the option to earn a quarter point of extra credit for each
        point earned over the normal amount we would set
        _scaleFactor = 1, assignmentPoints = 5, XCScaleFactor = .25
    :return: the modified gradescope dataframe.
    """
    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope grades MUST be passed as a Pandas DataFrame")
    if XCScaleFactor is None:
        XCScaleFactor = _scaleFactor

    for i, row in _gradescopeDF.iterrows():
        grade = row['Total Score']
        extraPoints = 0

        if assignmentPoints is not None:
            extraPoints = grade - (assignmentPoints / _scaleFactor)
            grade = grade - extraPoints

        grade *= _scaleFactor
        extraPoints *= XCScaleFactor

        grade += extraPoints

        if maxScore is not None:
            if grade >= maxScore:
                grade = maxScore
        _gradescopeDF.at[i, 'Total Score'] = grade

    return _gradescopeDF


def scoreMissingAssignments(_gradescopeDF: pd.DataFrame, score=0, exceptions=None):
    """
    This function handles the students who didnt submit their work at the time that this script is being run.
    Supports not scoring missing work as well.

    :param _gradescopeDF: The assignment being graded
    :param score: The score to give students or None if they shouldn't be scored.
    :param exceptions: Any exceptions that exist with the students multipass and they score they should receive
    Follows the same rules as score - not currently implemented Might want to expand to include sections

    :return: the modified gradescope dataframe
    """
    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope grades MUST be passed as a Pandas DataFrame")

    if exceptions is not None:
        raise AttributeError("Unable to process exceptions")

    missingAssignments = 0

    if score is not None:
        for i, row in _gradescopeDF.iterrows():
            if row['Status'] == "Missing":
                missingAssignments += 1
                _gradescopeDF.at[i, "Total Score"] = score

    print(f"Graded {missingAssignments} missing assignments")
    return _gradescopeDF


def calculateLatePenalty(_gradescopeDF: pd.DataFrame, _specialCasesDF: pd.DataFrame, latePenalty: list[float] = None):
    """
    This function calculates the late penalty according to the special cases
    Returns modified gradescope dataframe and special cases dataframe
    The special cases MUST be narrowed to one assignment before being passed. Otherwise, undefined behavior will happen
    (like extensions may be improperly granted)

    :param _gradescopeDF: the assignment being graded
    :param _specialCasesDF: the special cases for the assignment being graded
    :param latePenalty: an array of floats that contains the score mods for the late penalty
    """
    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope grades MUST be passed as a Pandas DataFrame")

    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise TypeError("Special cases MUST be passed as a Pandas DataFrame")
    if latePenalty is None:
        latePenalty = [1, .8, .6, .4, 0]

    specialCaseStudents = []
    latePenaltyStudents = 0
    for i, row in _gradescopeDF.iterrows():
        # Skip over students who didn't submit - they already got a zero
        if row['Status'] == "Missing":
            continue
        # Gradescope store lateness in H:M:S format
        hours, minutes, seconds = row['Lateness'].split(':')
        # We handled the grace period when we loaded the assignments
        hoursLate = float(hours) + (float(minutes) / 60) + (float(seconds) / 60 / 60)
        if row['sis_id'] in _specialCasesDF['multipass'].values.tolist():
            # reduce the number of hours that a submission is late
            #  accomplished by subtracting the days that a submission was extended by
            hoursLate -= (_specialCasesDF.loc[_specialCasesDF['multipass'] == row['sis_id']]['extension_days'][0]) * 24
            if hoursLate < 0:
                hoursLate = 0

            _specialCasesDF.loc[_specialCasesDF['multipass'] == row['sis_id']]['handled'] = True
            specialCaseStudents.append(row['Name'])

        # clac days late
        daysLate = math.ceil(hoursLate / 24)
        # if over penalty
        if daysLate > len(latePenalty) - 1:
            daysLate = len(latePenalty) - 1

        # actually applying the late penalty
        #  looking up in the list what it should be with the index as the index and daysLate directly correspond
        _gradescopeDF.at[i, 'Total Score'] *= latePenalty[daysLate]

        # add students who actually received a penalty to a list
        if daysLate != 0:
            latePenaltyStudents += 1

    # the only possible case here is if a student has a special case requested but was not found in gradescope
    if len(specialCaseStudents) != len(_specialCasesDF['multipass']):
        print("WARNING: Not all special cases were handled")
        for student in _specialCasesDF['student_name'].values.tolist():
            if student not in specialCaseStudents:
                print(f"\t{student} was not found in Gradescope")

    print(f"{len(specialCaseStudents)} of {len(_specialCasesDF['multipass'])} special cases were handled automatically")
    print(f"{latePenaltyStudents} late penalties were applied")

    return _gradescopeDF, _specialCasesDF


def createCanvasScores(_gradescopeDF: pd.DataFrame, _specialCasesDF: pd.DataFrame,
                       _students: pd.DataFrame, _assignmentId: str):
    """

    :param _assignmentId:
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

    if type(_assignmentId) is not str or len(_assignmentId) < 5:
        raise TypeError("Assignment ID MUST be a string containing a valid Canvas assignment id")

    gradedAssignment: dict = {}
    _students['graded'] = False
    for i, row in _students.iterrows():
        # Handle the student not existing in gradescope in either gradescope or canvas
        if len(_gradescopeDF.loc[_gradescopeDF['sis_id'] == row['sis_id']]) == 0:
            continue

        studentComment: str = ""
        # get the student's special cases
        studentSpecialCase: pd.DataFrame = _specialCasesDF.loc[_specialCasesDF['multipass'] == row['sis_id']]
        # add a comment to the student's submission explaining any extension or special cases
        if len(studentSpecialCase['extension_days']) != 0 and studentSpecialCase['extension_days'][0] > 0:
            studentComment = f"Extended by {studentSpecialCase['extension_days'][0]} days."
            if studentSpecialCase['extension_type'][0] == "Late Pass":
                studentComment += f"\n{studentSpecialCase['extension_days'][0]} late passes used"

        gradedAssignment[row['name']] = {
            'id': row['id'],
            'score': _gradescopeDF.loc[_gradescopeDF['sis_id'] == row['sis_id']]['Total Score'],
            'comment': studentComment
        }
        _students.at[i, 'graded'] = True

    ungradedStudents: pd.DataFrame = _students.loc[_students['graded'] == False]['name']
    if len(ungradedStudents) != 0:
        print("Warning")
        print(f"\t...{len(ungradedStudents)} unmatched students")
        for student in ungradedStudents['name']:
            print(f"\t\t...{student} was not found")
    else:
        print("Done")

    return gradedAssignment


def createCanvasScoresForAssignments(_gradescopeAssignments: dict[str, pd.DataFrame],
                                     _specialCasesDF: pd.DataFrame, _canvas: Canvas):
    """

    :param _gradescopeAssignments:
    :param _specialCasesDF:
    :param _canvas:
    :return:
    :example:
        {
            assignment_id: {
                name: {
                    id:
                    score:
                    comments:
                },
            }
        }

    """
    # TODO Handle _gradescopeAssignments
    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise TypeError("Special cases MUST be passed as a Pandas DataFrame")

    if not isinstance(_canvas, Canvas):
        raise TypeError("Canvas must be an instance of the Canvas API Wrapper")

    students: pd.DataFrame = _canvas.getStudents()

    assignmentsToPost: dict[str, dict[str, any]] = {}

    print(f"Creating scores for {len(students)} students across {len(_gradescopeAssignments)} assignments...", end='')

