"""
This module contains the functions that grade students assignments.
They work directly with the Gradescope assignment Dataframe and the special cases Dataframe
(and eventually the page flagging dataframe)

This file **non-destructively** edits the grades. Meaning that nothing is written to file or Canvas - it
has to be committed by the user using a different module.
"""
import math
import pandas as pd


def scaleScores(_gradescopeDF: pd.DataFrame, _scaleFactor: float,
                assignmentPoints: float = None, maxScore: float = None, XCScaleFactor: float = None) -> pd.DataFrame:
    """
   Description
    --------
    This function scales the scores by the scale factor. It also takes into account different extra credit scaling.
    This function does NOT consider lateness or page flagging in its calculations
   Example
    --------
    If we have an assignment that is worth 5 points, but has the option to earn a quarter point of extra credit for each
    point earned over the normal amount we would set
    _scaleFactor = 1, assignmentPoints = 5, XCScaleFactor = .25

    :param _gradescopeDF: the current grades for the current assigment
    :param _scaleFactor: the scaling to apply to each grade
    :param assignmentPoints: the total amount of *regular* *scaled* points the assignment has.
            If not set, function assumes that *no* extra credit scaling is required
    :param maxScore: the maximum *total* *scaled* score a student can get. Includes extra credit.
            If not set, function assumes that there is *no* upper score bound
    :param XCScaleFactor: the scaling to apply to any points above the 'assignmentPoints' var.
            If not set, function assumes that normal scaling (as defined in '_scaleFactor')
            also applies to extra credit
    :return: the modified gradescope dataframe.
    """
    # Validation - we need to enforce types for the gradescope stuff
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


def scoreMissingAssignments(_gradescopeDF: pd.DataFrame, score: float = 0, exceptions=None):
    """
   Description
    --------
    This function handles the students who didn't submit their work at the time that this script is being run.
    Supports not scoring missing work as well.

    :param _gradescopeDF: The assignment being graded
    :param score: The score to give students or None if they shouldn't be scored.
    :param exceptions: Any exceptions that exist with the students multipass, and the score they should receive
    Follows the same rules as score - not currently implemented Might want to expand to include sections
    :return: the modified gradescope dataframe
    """
    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope grades MUST be passed as a Pandas DataFrame")

    if exceptions is not None:  # TODO Implement exception processing
        raise AttributeError("Unable to process exceptions")

    missingAssignments = 0

    for i, row in _gradescopeDF.iterrows():
        if row['Status'] == "Missing":
            missingAssignments += 1
            _gradescopeDF.at[i, "Total Score"] = score

    print(f"Graded {missingAssignments} missing assignments")
    return _gradescopeDF


def calculateLatePenalty(_gradescopeDF: pd.DataFrame, _specialCasesDF: pd.DataFrame,
                         _assignment: str, latePenalty: list[float] = None):
    """
   Description
    --------
    This function calculates the late penalty according to the special cases
    Returns modified gradescope dataframe and special cases dataframe. This can only grade one
    assignment at a time due to limitations in how .loc works in pandas and updating the master dataframe
    would require iterating over everywhere individually and merging them.

    :param _assignment: The assignment name to look up in the special cases file.
    :param _gradescopeDF: the assignment being graded
    :param _specialCasesDF: the special cases for the assignment being graded
    :param latePenalty: an array of floats that contains the score mods for the late penalty
    :return: the updated special cases dataframe and the updated gradescope dataframe
    """
    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope grades MUST be passed as a Pandas DataFrame")

    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise TypeError("Special cases MUST be passed as a Pandas DataFrame")

    if type(_assignment) is not str:
        raise TypeError("Assignment MUST be passed a string")

    if latePenalty is None:
        latePenalty = [1, .8, .6, .4, 0]

    print(f"Applying late penalties for {_assignment}...")
    _gradescopeDF['lateness_comment'] = ""
    specialCaseStudents = 0
    latePenaltyStudents = 0
    for i, row in _gradescopeDF.iterrows():
        # Skip over students who didn't submit - they already got a zero
        if row['Status'] == "Missing":
            continue
        # Gradescope store lateness in H:M:S format
        hours, minutes, seconds = row['Lateness'].split(':')
        hoursLate = float(hours) + (float(minutes) / 60) + (float(seconds) / 60 / 60)
        # this is safe - if no students are found in the special cases, then it will be empty
        #  and the loop will just not run.
        if row['sis_id'] in _specialCasesDF.loc[_assignment == _specialCasesDF['assignment'], 'multipass'].values.tolist():
            # reduce the number of hours that a submission is late
            #  accomplished by subtracting the days that a submission was extended by
            hoursLate -= (_specialCasesDF.loc[
                (_specialCasesDF['assignment'] == [_assignment]) &
                (_specialCasesDF['multipass'] == row['sis_id'])
                , 'extension_days'].values[0]) * 24
            if hoursLate < 0:
                hoursLate = 0

            _specialCasesDF.loc[
                (_specialCasesDF['multipass'] == row['sis_id']) &
                (_specialCasesDF['assignment'] == [_assignment])
                , 'handled'] = True

            specialCaseStudents += 1

        # clac days late
        daysLate = math.ceil(hoursLate / 24)
        # if over penalty
        if daysLate > len(latePenalty) - 1:
            daysLate = len(latePenalty) - 1

        # actually applying the late penalty
        #  looking up in the list what it should be with the index as the index and daysLate directly correspond
        _gradescopeDF.at[i, 'Total Score'] *= latePenalty[daysLate]

        # add students who actually received a penalty to a list
        #  and update comment stating where points went to
        if daysLate != 0:
            latePenaltyStudents += 1
            _gradescopeDF.at[i, 'lateness_comment'] = f"-{1 - latePenalty[daysLate]}%: {daysLate} Days late"

    # the only possible case here is if a student has a special case requested but was not found in gradescope
    if specialCaseStudents != len(_specialCasesDF['multipass']):
        print("\tNot all special cases where handled automatically...")
        # '!= True' here because it may be null or false depending on who entered the special case
        #  != because this is a bool mask - not a normal boolean expression
        for student in _specialCasesDF.loc[_specialCasesDF['handled'] != True, 'student_name'].values.tolist():
            print(f"\t\t...{student} was not found in Gradescope")

    print(f"\t{specialCaseStudents} special cases were applied for {_assignment}")
    print(f"\t{latePenaltyStudents} late penalties were applied for {_assignment}")

    if specialCaseStudents != len(_specialCasesDF['multipass']):
        print("...Warning")
    else:
        print("...Done")

    return _gradescopeDF, _specialCasesDF
