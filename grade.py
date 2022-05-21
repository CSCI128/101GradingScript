import math

import pandas as pd

'''
This function scales the scores by the scale factor. It also takes into account different extra credit scaling. 
This function does NOT consider lateness or page flagging in its calculations

Returns the modified gradescope dataframe. 
PARAMS:
    _gradescopeDF - the current grades for the current assigment  
    _scaleFactor - the scaling to apply to each grade
    assignmentPoints - the total amount of *regular* *scaled* points the assignment has.
        If not set, function assumes that *no* extra credit scaling is required
    maxScore - the maximum *total* *scaled* score a student can get. Includes extra credit
        If not set, function assumes that there is *no* upper score bound
    XCScaleFactor - the scaling to apply to any points above the 'assignmentPoints' var
        If not set, function assumes that normal scaling (as defined in '_scaleFactor')
        also applies to extra credit
EXAMPLE:
    If we have an assignment that is worth 5 points, but has the option to earn a quarter point of extra credit for each
    point earned over the normal amount we would set 
    _scaleFactor = 1, assignmentPoints = 5, XCScaleFactor = .25
'''


def scaleScores(_gradescopeDF, _scaleFactor, assignmentPoints=None, maxScore=None, XCScaleFactor=None):
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


'''
This function handles the students who didnt submit their work at the time that this script is being run.
Supports not scoring missing work as well.
Returns the modified
PARAMS:
    _gradescopeDF - The assignment being graded
    score - The score to give students or None if they shouldn't be scored.
    exceptions - Any exceptions that exist with the students multipass and they score they should receive 
        Follows the same rules as score - not currently implemented
        Might want to expand to include sections
'''


def scoreMissingAssignments(_gradescopeDF, score=0, exceptions=None):
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


'''
This function calculates the late penalty according to the special cases 
Returns modified gradescope dataframe and special cases dataframe
The special cases MUST be narrowed to one assignment before being passed. Other wise undefined behavior will happen 
(like extensions may be improperly granted)
PARAMS:
    _gradescopeDF - the assignment being graded
    _specialCasesDF - the special cases for the assignment being graded
'''


def calculateLatePenalty(_gradescopeDF, _specialCasesDF, latePenalty=None):
    if latePenalty is None:
        latePenalty = [1, .8, .6, .4, 0]

    specialCaseStudents = []
    latePenaltyStudents = 0
    for i, row in _gradescopeDF.iterrows():
        # Skip over students who didnt submit - they already got a zero
        if row['Status'] == "Missing":
            continue
        # Gradescope store lateness in H:M:S format
        hours, minutes, seconds = row['Lateness'].split(':')
        # We handled the grace period when we loaded the assignments
        hoursLate = float(hours) + (float(minutes) / 60) + (float(seconds) / 60 / 60)
        if row['SIS Login ID'] in _specialCasesDF['multipass'].values.tolist():
            # reduce the number of hours that a submission is late
            #  accomplished by subtracting the days that a submission was extended by
            hoursLate -= (_specialCasesDF.loc[_specialCasesDF['multipass'] == row['SIS Login ID']]['extension_days'][0]) * 24
            if hoursLate < 0:
                hoursLate = 0

            _specialCasesDF.loc[_specialCasesDF['multipass'] == row['SIS Login ID']]['handled'] = True
            specialCaseStudents.append(row['Name'])

        # clac days late
        daysLate = math.ceil(hoursLate / 24)
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
