# grade module

## Description

This module contains the functions that grade students assignments.
They work directly with the Gradescope assignment Dataframe and the special cases Dataframe
(and eventually the page flagging dataframe)

This file **non-destructively** edits the grades. Meaning that nothing is written to file or Canvas - it
has to be committed by the user using a different module.


### grade.calculateLatePenalty(_gradescopeDF, _specialCasesDF, _statusAssignmentsDF, _statusAssignmentScoresDF, _assignmentCommonName, latePenalty=None)

* **Description**


This function calculates the late penalty according to the special cases
Returns modified gradescope dataframe and special cases dataframe. This can only grade one
assignment at a time due to limitations in how `.loc` works in pandas and updating the master dataframe
would require iterating over everywhere individually and merging them.
This function also updates the lateness comment with student’s special cases. If they have a status assignment
trigger in their special case then a comment saying that it was handled is also added, assuming that it was a valid
request.


* **Parameters**

    
    * **_statusAssignmentScoresDF** (`DataFrame`) – The scores for the current each status assignment


    * **_statusAssignmentsDF** (`DataFrame`) – The current status assignments


    * **_assignmentCommonName** (`str`) – The assignment name to look up in the special cases file.


    * **_gradescopeDF** (`DataFrame`) – the assignment being graded


    * **_specialCasesDF** (`DataFrame`) – the special cases for the assignment being graded


    * **latePenalty** (`Optional`[`list`[`float`]]) – an array of floats that contains the score mods for the late penalty



* **Returns**

    the updated special cases dataframe, the updated gradescope dataframe, and the status assignment scores dataframe



### grade.scaleScores(_gradescopeDF, _scaleFactor, assignmentPoints=None, maxScore=None, XCScaleFactor=None)

* **Description**


This function scales the scores by the scale factor. It also takes into account different extra credit scaling.
This function does NOT consider lateness or page flagging in its calculations


* **Examples**


If we have an assignment that is worth 5 points, but has the option to earn a quarter point of extra credit for each
point earned over the normal amount we would set
`_scaleFactor = 1, assignmentPoints = 5, XCScaleFactor = .25`


* **Parameters**

    
    * **_gradescopeDF** (`DataFrame`) – the current grades for the current assigment


    * **_scaleFactor** (`float`) – the scaling to apply to each grade


    * **assignmentPoints** (`Optional`[`float`]) – the total amount of *regular* *scaled* points the assignment has.
    If not set, function assumes that *no* extra credit scaling is required


    * **maxScore** (`Optional`[`float`]) – the maximum *total* *scaled* score a student can get. Includes extra credit.
    If not set, function assumes that there is *no* upper score bound


    * **XCScaleFactor** (`Optional`[`float`]) – the scaling to apply to any points above the ‘assignmentPoints’ var.
    If not set, function assumes that normal scaling (as defined in ‘_scaleFactor’)
    also applies to extra credit



* **Return type**

    `DataFrame`



* **Returns**

    the modified gradescope dataframe.



### grade.scoreMissingAssignments(_gradescopeDF, score=0, exceptions=None)

* **Description**


This function handles the students who didn’t submit their work at the time that this script is being run.
Supports not scoring missing work as well.


* **Parameters**

    
    * **_gradescopeDF** (`DataFrame`) – The assignment being graded


    * **score** (`float`) – The score to give students or None if they shouldn’t be scored.


    * **exceptions** – Any exceptions that exist with the students multipass, and the score they should receive
    Follows the same rules as score - not currently implemented. Might want to expand to include sections



* **Returns**

    the modified gradescope dataframe



### grade.validateAndUpdateStatusAssignments(_gradescopeDF, _specialCasesDF, _statusAssignmentsDF, _statusAssignmentScoresDF, _assignmentCommonName)

* **Description**


This function updates the status assignments according to special case file. It checks to see if the student both
submitted and if they submitted late to avoid docking a status assignment unless necessary. It also validates
that the student is actually able to request the extension that they requested. If the status assignment is
available, update the points to post to canvas and automatically approve the extension.
This function will also add a comment to both the special cases sheet and the students submission


* **Parameters**

    
    * **_statusAssignmentScoresDF** (`DataFrame`) – The scores for the current each status assignment


    * **_statusAssignmentsDF** (`DataFrame`) – The current status assignments


    * **_assignmentCommonName** (`str`) – The assignment name to look up in the special cases file.


    * **_gradescopeDF** (`DataFrame`) – the assignment being graded


    * **_specialCasesDF** (`DataFrame`) – the special cases for the assignment being graded



* **Return type**

    (`DataFrame`, `DataFrame`, `DataFrame`)



* **Returns**

    the updated special cases dataframe, the updated gradescope dataframe, and the status assignment scores dataframe
