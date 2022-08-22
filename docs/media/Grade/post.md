# post module

## Description

This module contains helper functions to post scores to Canvas.

This is the last step in the grading process and **IS** destructive. It will write the new scores to file and post them
to Canvas. It will also update the special cases file with the handled / not handled updates.

**AFTER GRADES ARE POSTED, THEY NEED TO BE MANUALLY PUBLISHED**

That functionality *is* supported by the Canvas api and can be added, but, for now, I am keeping it this way to
serve as a safety mechanism.


### post.postToCanvas(_canvas, _canvasScores, studentsToPost=None)

* **Description**


This function generates form data from the Canvas scores to be sent to Canvas to be posted in the Gradebook.
This function makes use of the Submission Canvas API, which allows us to post grades, comments, and actual
student work - which may be nice if I decide to expand this project to mirror submissions on gradescope.

Currently, this function generates the form data with student scores and comments in batches of 50 scores then sends
that data to Canvas.

**THIS FUNCTION DOES NOT PUBLISH GRADES FOR STUDENTS**

While the Canvas API supports that functionality, the grader should manually verify that the posted scores are what
they think they are then manually publish the scores.
(done by clicking the column -> three dot menu -> post grades -> everyone -> post)

Currently, this function only supports passing either a dataframe in for the students to post or a None type,
which will map to all students.


* **Parameters**

    
    * **_canvas** – The Canvas object.


    * **_canvasScores** – The scores to post to Canvas.


    * **studentsToPost** – The students to post. If it is None it will post all students.


:return true if we received all 200 responses from canvas. See `Canvas.postAssignment`. False if not


### post.updateSpecialCases(_specialCasesDF)

* **Description**


Writes the updated special cases Dataframe to file. See `FileHelpers.excelWriter.writeSpecialCases` for more
information.


* **Parameters**

    **_specialCasesDF** (`DataFrame`) – The special cases dataframe to be written.



* **Return type**

    `bool`



* **Returns**

    True if the special cases were successfully updated. False if not.



### post.writeUpdatedGradebookToFile(_canvasScores, _students, _assignmentsToGrade)

* **Description**


This function generates a Canvas gradebook from the scores generated, the students pulled from canvas,
and the all the assignments that have been selected to grade then writes it to file.
This function generates all the metadata in a *very* specific way for Canvas. Because Mines uses SIS
integration, we have to include the columns ‘SIS User ID’ and ‘SIS Login ID’. Only one of those actually
to be populated for Canvas to be able to process the gradebook. We also require the Canvas ID and student name.

For the actual scores for assignments, again they have to be formatted in a very specific way to automatically
import them. The format *required* by Canvas is `Canvas Assignment Name (Canvas Assignment ID)`. For example:
HW6 is `HW6 - Hardware & Software (283462)`.

This function requires that all assignment in `_canvasScores` to be in the `_assignmentsToGrade`,
otherwise a mismatched key error will be thrown.

The filename used is: `canvas_{current_date}_{assignments_in_grade_book}.csv`

For example: a gradebook generated on Feb 2nd, 2022 for Late Passes and HW6 would be:
`canvas_02-02-22_HW6_LPL.csv`


* **Parameters**

    
    * **_canvasScores** (`dict`[`str`, `dict`[`any`, `any`]]) – The generated canvas scores, See `Grade.score` for more information


    * **_students** (`DataFrame`) – All the students in the pulled from the Canvas roster at the start of execution.


    * **_assignmentsToGrade** (`DataFrame`) – The assignments to grade. Must be the same length as `_canvasScores`



* **Return type**

    `bool`



* **Returns**

    True if the gradebook was successfully generated and written. False if not.



### post.writeUpdatedGradesheets(_gradescopeAssignments, _assignmentsToGrade)

* **Description**


Writes the modified gradescope dataframe to file.
Includes student multipass, student scores, all submission comments, and assignment status
(either ‘Graded’ or ‘Missing’)

The file name written is: `{common_name}_graded.csv`

For example, grades for HW6 would be written as: `HW6_graded.csv`


* **Parameters**

    
    * **_gradescopeAssignments** (`dict`[`int`, `DataFrame`]) – A dict that maps the assignment ids to its corresponding grade sheet.


    * **_assignmentsToGrade** (`DataFrame`) – The assignments to grade.



* **Return type**

    `bool`



* **Returns**

    True if *all* gradesheets where written correctly. False if not.
