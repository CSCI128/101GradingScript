"""
This module contains the functions that grade students assignments.
They work directly with the Gradescope assignment Dataframe and the special cases Dataframe
(and eventually the page flagging dataframe)

This file **non-destructively** edits the grades. Meaning that nothing is written to file or Canvas - it
has to be committed by the user using a different module.
"""
import datetime
import math
import pandas as pd
import inflect

p = inflect.engine()


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


def validateAndUpdateStatusAssignments(_gradescopeDF: pd.DataFrame, _specialCasesDF: pd.DataFrame,
                                       _statusAssignmentsDF: pd.DataFrame,
                                       _statusAssignmentScoresDF: pd.DataFrame, _assignmentCommonName: str):
    """
   Description
    --------
    This function updates the status assignments according to special case file. It checks to see if the student both
    1. submitted and 2. if they submitted late to avoid docking a status assignment unless necessary. It also validates
    that the student is actually able to request the extension that they requested. If the status assignment is
    available, update the points to post to canvas and automatically approve the extension.
    This function will also add a comment to both the special cases sheet
    :param _statusAssignmentScoresDF: The scores for the current each status assignment
    :param _statusAssignmentsDF: The current status assignments
    :param _assignmentCommonName: The assignment name to look up in the special cases file.
    :param _gradescopeDF: the assignment being graded
    :param _specialCasesDF: the special cases for the assignment being graded
    :return: the updated special cases dataframe, the updated gradescope dataframe, and the status assignment scores dataframe
    """

    for i, row in _gradescopeDF.iterrows():
        # If either of these are the case, we don't need to update the status assignments
        if row['Status'] == "Missing" or row['hours_late'] == 0:
            continue

        currentSpecialCase = (_specialCasesDF['multipass'] == row['multipass']) & \
                             (_specialCasesDF['assignment'] == _assignmentCommonName)

        # If there is no special case for the student
        if len(_specialCasesDF.loc[currentSpecialCase]) == 0:
            continue

        # If the special case has already been handled - do nothing
        elif _specialCasesDF.loc[currentSpecialCase, 'handled'].values[0] != "":
            continue

        if _specialCasesDF.loc[currentSpecialCase, 'extension_type'] in _statusAssignmentsDF['trigger'].values:
            # Create a bool mask for the current status assignment score for the student and the correct trigger
            currentStatusAssignment = \
                (_statusAssignmentScoresDF['multipass'] == row['multipass']) & \
                (_statusAssignmentScoresDF['status_id'] ==
                 (_statusAssignmentsDF.loc[_statusAssignmentsDF['trigger'] ==
                                           _specialCasesDF.loc[currentSpecialCase, 'extension_type'].values[0],
                                           'id'].values[0]))
            # Check to make sure that the student actually has a value for the status assignment
            #  This should only happen if the student dropped, or recently added and does not yet have a score
            #  for the assignment, either way, it will require manual intervention.
            if len(_statusAssignmentScoresDF.loc[currentStatusAssignment, 'student_score']) == 0:

                _specialCasesDF.loc[currentSpecialCase, 'handled'] = "FALSE"
                _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] = \
                    "Unable to process triggered special case: No status assignment found for student."

            # if the student requested more of an extension than they were entitled to
            elif _statusAssignmentScoresDF.loc[currentStatusAssignment, 'student_score'].values[0] < \
                    _specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0]:

                _specialCasesDF.loc[currentSpecialCase, 'handled'] = "FALSE"
                _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] = \
                    "Unable to process triggered special case: Limit exceeded."

            # Request is valid. approve and add a comment explaining that it was handled correctly.
            else:
                _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] = \
                    f"Automatically Approved on {datetime.date.today().strftime('%m-%d-%y')}"

                _statusAssignmentScoresDF.loc[currentStatusAssignment, 'student_score'] -= \
                    _specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0]

                _specialCasesDF.loc[currentSpecialCase, 'approved_by'] = "AUTOMATIC APPROVAL"
                extensionMessage: str = p.plural(_specialCasesDF.loc[currentSpecialCase, 'extension_type'].values[0],
                                                 _specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0])

                _gradescopeDF.at[i, 'lateness_comment'] = \
                    f"Extended with {_specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0]} " + \
                    f"{extensionMessage}"

    return _gradescopeDF, _specialCasesDF, _statusAssignmentScoresDF


def calculateLatePenalty(_gradescopeDF: pd.DataFrame, _specialCasesDF: pd.DataFrame, _statusAssignmentsDF: pd.DataFrame,
                         _statusAssignmentScoresDF: pd.DataFrame, _assignmentCommonName: str,
                         latePenalty: list[float] = None):
    """
   Description
    --------
    This function calculates the late penalty according to the special cases
    Returns modified gradescope dataframe and special cases dataframe. This can only grade one
    assignment at a time due to limitations in how .loc works in pandas and updating the master dataframe
    would require iterating over everywhere individually and merging them.
    This function also updates the lateness comment with student's special cases. If they have a status assignment
    trigger in their special case then a comment saying that it was handled is also added, assuming that it was a valid
    request.
    :param _statusAssignmentScoresDF: The scores for the current each status assignment
    :param _statusAssignmentsDF: The current status assignments
    :param _assignmentCommonName: The assignment name to look up in the special cases file.
    :param _gradescopeDF: the assignment being graded
    :param _specialCasesDF: the special cases for the assignment being graded
    :param latePenalty: an array of floats that contains the score mods for the late penalty
    :return: the updated special cases dataframe, the updated gradescope dataframe, and the status assignment scores dataframe
    """
    if not isinstance(_gradescopeDF, pd.DataFrame):
        raise TypeError("Gradescope grades MUST be passed as a Pandas DataFrame")

    if not isinstance(_specialCasesDF, pd.DataFrame):
        raise TypeError("Special cases MUST be passed as a Pandas DataFrame")

    if type(_assignmentCommonName) is not str:
        raise TypeError("Assignment MUST be passed a string")

    if latePenalty is None:
        latePenalty = [1, .8, .6, .4, 0]

    print(f"Applying late penalties for {_assignmentCommonName}...")
    _gradescopeDF['lateness_comment'] = ""

    _gradescopeDF, _specialCasesDF, _statusAssignmentScoresDF = \
        validateAndUpdateStatusAssignments(_gradescopeDF, _specialCasesDF, _statusAssignmentsDF,
                                           _statusAssignmentScoresDF, _assignmentCommonName)
    specialCaseStudents = 0
    latePenaltyStudents = 0
    for i, row in _gradescopeDF.iterrows():
        # This is just a bool mask - it allows us to filter out the rows that don't meet the criteria
        currentSpecialCase = (_specialCasesDF['multipass'] == row['multipass']) & \
                             (_specialCasesDF['assignment'] == _assignmentCommonName)

        # Skip over students who didn't submit - they already got a zero
        if row['Status'] == "Missing":
            if not _specialCasesDF.empty and len(_specialCasesDF.loc[currentSpecialCase]) != 0:
                # _specialCasesDF.loc[currentSpecialCase, 'handled'] = "FALSE"
                # If the student didn't submit - I'm considering that as handled. 
                _specialCasesDF.loc[currentSpecialCase, 'handled'] = "TRUE"
                _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] = "No Submission"

                _gradescopeDF.at[i, 'lateness_comment'] = "No Submission." \
                                                          "\nContact grader if you think this is a mistake."
            continue

        hoursLate = row['hours_late']
        # this is safe - if no students are found in the special cases, then it will be empty
        #  and the loop will just not run.
        if not _specialCasesDF.empty and len(_specialCasesDF.loc[currentSpecialCase]) != 0 and hoursLate == 0:
            _specialCasesDF.loc[currentSpecialCase, 'handled'] = "TRUE"
            _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] = "Student submission was NOT late"

        elif not _specialCasesDF.empty and len(_specialCasesDF.loc[currentSpecialCase]) != 0:
            if not _specialCasesDF.loc[currentSpecialCase, 'approved_by'].values[0]:
                _specialCasesDF.loc[currentSpecialCase, 'handled'] = "FALSE"

                if _specialCasesDF.loc[currentSpecialCase, 'grader_notes'].values[0]:
                    _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] += "; Special case is NOT Approved"
                else:
                    _specialCasesDF.loc[currentSpecialCase, 'grader_notes'] = "Special case is NOT Approved"

            # If the special case has already been handled
            elif _specialCasesDF.loc[currentSpecialCase, 'handled'].values[0] != "":
                pass
            # We only want to apply a special case if it is not already flagged as handled.
            else:
                # reduce the number of hours that a submission is late
                hoursLate -= (_specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0]) * 24
                if hoursLate < 0:
                    hoursLate = 0

                pluralizedDays: str = p.plural("day", _specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0])

                # Add a comment explaining any extension
                if _gradescopeDF.at[i, 'lateness_comment']:
                    _gradescopeDF.at[i, 'lateness_comment'] += \
                        f"\nExtended by {_specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0]} {pluralizedDays}"
                else:
                    _gradescopeDF.at[i, 'lateness_comment'] = \
                        f"Extended by {_specialCasesDF.loc[currentSpecialCase, 'extension_days'].values[0]} {pluralizedDays}"
                _specialCasesDF.loc[currentSpecialCase, 'handled'] = "TRUE"

                specialCaseStudents += 1

        # Convert to days rounding up
        daysLate = math.ceil(hoursLate / 24)

        if daysLate > len(latePenalty) - 1:
            daysLate = len(latePenalty) - 1

        # actually applying the late penalty
        #  looking up in the list what it should be with the index as the index and daysLate directly correspond
        _gradescopeDF.at[i, 'Total Score'] = round(_gradescopeDF.at[i, 'Total Score'] * latePenalty[daysLate], 3)

        # add students who actually received a penalty to a list
        #  and update comment stating where points went to
        # %25 is the percent sign
        if daysLate != 0:
            latePenaltyStudents += 1
            pluralizedDays: str = p.plural("day", daysLate)
            if _gradescopeDF.at[i, 'lateness_comment']:
                _gradescopeDF.at[i, 'lateness_comment'] += \
                    f"\n-{(1 - latePenalty[daysLate]) * 100:02.0f}%25: {daysLate} {pluralizedDays} late"
            else:
                _gradescopeDF.at[i, 'lateness_comment'] = \
                    f"-{(1 - latePenalty[daysLate]) * 100:02.0f}%25: {daysLate} {pluralizedDays} late"

    # the only possible case here is if a student has a special case requested but was not found in gradescope
    if not _specialCasesDF.empty and specialCaseStudents != len(

            _specialCasesDF.loc[_specialCasesDF['assignment'] == _assignmentCommonName, 'multipass']):
        print("\tNot all special cases where handled automatically...")
        # '!= True' here because it may be null or false depending on who entered the special case
        #  != because this is a bool mask - not a normal boolean expression
        for student in _specialCasesDF.loc[(_specialCasesDF['handled'] != "TRUE")
                                           & (_specialCasesDF['assignment'] == _assignmentCommonName),
                                           'full_name'].values.tolist():
            print(f"\t\t...{student} was unable to be handled automatically")
        print("\tCheck grader notes for more details")
        print("\tIf student special case was not updated, they were not found in gradescope")
    print(f"\t{specialCaseStudents} special cases were applied for {_assignmentCommonName}")
    print(f"\t{latePenaltyStudents} late penalties were applied for {_assignmentCommonName}")

    if not _specialCasesDF.empty and specialCaseStudents != len(
            _specialCasesDF.loc[_specialCasesDF['assignment'] == _assignmentCommonName, 'multipass']):
        print("...Warning")
    else:
        print("...Done")

    return _gradescopeDF, _specialCasesDF, _statusAssignmentScoresDF
