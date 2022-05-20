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


def scaleScores(_gradescopeDF, _scaleFactor, assignmentPoints=None,  maxScore=None, XCScaleFactor=None):
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
