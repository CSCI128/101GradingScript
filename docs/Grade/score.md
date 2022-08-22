# score module

## Description

This module contains the functions used to create Canvas scores. Basically,
all the functions in here merge the Dataframes produced by `Grade.grade`.
This module does **not** create new grades nor does it modify existing grades.

This module **non-destructively** creates Canvas scores, meaning that nothing is committed to Canvas
and the source data is **not** modified.


### score.createCanvasScores(_gradescopeDF, _students)

* **Description**


This function generates scores for **one** assignment. It builds all the comments that will be sent to the student
in Canvas and assigns scores for each student.

See `score.createCanvasScoresForAssignments` for an example of what this looks like.


* **Parameters**

    * **_gradescopeDF** (`DataFrame`) – The gradesheet to create scores from

    * **_students** (`DataFrame`) – the current canvas roaster.



* **Return type**

    `dict`[`str`, `any`]



* **Returns**

    the dict representation of the assignment scores.



### score.createCanvasScoresForAssignments(_gradescopeAssignments, _canvas, _assignments)

* **Description**


This function grades a batch of assignments and creates a dict that can be posted to canvas. At a basic level,
this function is mapping the gradescope scores that have been put through processing to canvas student ids.

This function calls `createCanvasScores` internally to generate the scores for each assignment.

This function also calls `createCanvasScoresForStatusAssignments` internally to create scores for those
assignments, but that functionality is likely to be removed in favor of a solution that treats status assignments
the same as normal assignments.


* **Example**


```json
{
     assignment_id: {
          id: {
               name:
               id:
               score:
               comments:
        }
     }
}
```


* **Parameters**
    
    * **_assignments** (`DataFrame`) – A dataframe containing all the assignments to grade.

    * **_gradescopeAssignments** (`dict`[`int`, `DataFrame`]) – A dict containing the assignment ids mapped to the grade sheets

    * **_canvas** ([`Canvas`](../Canvas.md#Canvas.Canvas)) – the canvas object.



* **Return type**

    `dict`[`str`, `dict`[`str`, `any`]]



* **Returns**

    A map containing the assignment id and the scores to be posted under that id.



### score.createCanvasScoresForStatusAssignments(statusAssignmentScoresDF, _students)

* **Description**


Creates score objects from the status assignment scores.

This method is likely to phased out in favor of a solution that does not require handling these assignments
differently from normal assignments.

Currently, the way that this is implemented will be able to update **1** status assignment regardless of the
presence of many in the config file.


* **Parameters**
    
    * **statusAssignmentScoresDF** (`DataFrame`) – The current scores for students for **all** status assignment

    * **_students** (`DataFrame`) – the list of students. Not *really* needed as we don’t super care about the students name at this
    point and already have their canvas IDs in this grade sheet.


* **Return type**

    `dict`[`str`, `any`]



* **Returns**

    the scores for the status assignments in a dict.
