# Canvas module


### _class_ Canvas.Canvas(_API_KEY='', _USER_ID='', _COURSE_ID='', _ENDPOINT='')
Bases: `object`


* **Description**


This class helps us interface directly with canvas and abstracts some weirdness away
Importantly - this class supports paginated responses and handles them elegantly -
regardless of the size of the response


#### getAssignmentFromCommonName(_assignment)

* **Description**



* **Parameters**

    **_assignment** (`str`) – 



* **Return type**

    (`DataFrame`, `None`)



* **Returns**

    


#### getAssignmentFromID(_id)

* **Description**


Maps the id to a canvas assignment in the main assignment list.


* **Parameters**

    **_id** (`int`) – the id to parse



* **Return type**

    `DataFrame`



* **Returns**

    a dataframe containing the id or an empty dataframe if it was not found.



#### getAssignmentGroupsFromCanvas()

* **Description**


This function gets the assignment groups from canvas, then formats them such that we only have the
group name and the group id.
This allows us to not have to pull all 118 assignments from canvas when we will only need a few and know the groups.


* **Example**


Pulled from CSCI 101 SPR22

```json
{
'Quizzes (6%)': 56566,
'Gradescope': 55687,
'Python Labs (6%)': 56567,
...
}
```

the first col is the group name and the second col is the canvas id


* **Returns**

    the formatted assignment groups



#### getAssignmentIDsFromCommonName(_assignmentList)

* **Description**


This function takes in the assignment common names and generates a map of the assignment common name to its ID.
This is to make the user interface slightly simpler for the user.

**Deprecated:** Deprecated since version 1.0.0: Do not use this. Use the assignmentToGrade workflow instead. For an example, look at UI.standardGrading.
Deprecated as part of improving assignment handling internally. See [#13](https://github.com/TriHardStudios/101GradingScript/issues/13) and [#6](https://github.com/TriHardStudios/101GradingScript/issues/6)


* **Parameters**

    **_assignmentList** (`list`[`str`]) – A list of assignment common names.



* **Return type**

    `dict`[`str`, `str`]



* **Returns**

    a map mapping the assignment common names to the assignment ids.



#### getAssignments()

#### getAssignmentsFromCanvas(_assignmentGroups)

* **Description**


This function pulls assignments from canvas that it finds in the groups passed as parameters. It strips out
the unnecessary fields provided by the canvas api.
:Example:

```json
{
    common_name: "HW8",
    name: "HW8 - Hardware and Software',
    id: "56383",
    points: 6.0
},
```


* **Parameters**

    **_assignmentGroups** – The list of ids of the desired groups to pull from.



* **Return type**

    `list`



* **Returns**

    formatted assignments



#### getAssignmentsFromConfig(_configFile)

* **Description**


This function reads in the assignments from the config file and updates the internal members.
First it validates that there is at least one assignment.


* **Parameters**

    **_configFile** – the config file containing the assignments to be loaded



#### getAssignmentsToGrade()

#### getCourseList()

* **Description**


Retrieves the list of courses from canvas that the user in enrolled in, then filters out the student ones
to ensure that they will have write access.


* **Returns**

    The list of courses with the course ID, name, and enrollment type



#### getStatusAssignmentScores()

#### getStatusAssignments()

#### getStudents()

#### getStudentsFromCanvas()

* **Description**


This function gets a list of users from canvas, filtering out the non-students. This will allow us to post
grades for students without needed to download the entire gradebook. Because the list of students changes
frequently as they add and drop classes, this is pulled before grades are posted every run. This will update
the student list internally.


#### loadSettings(_configFile)

* **Description**


This function gets the config file as a dict, validates it, then updates the internal members.


* **Parameters**

    **_configFile** – The config file we are using



#### postAssignment(_assignment, _batchedAssignment)

* **Description**


This function post assignments to Canvas in batches of at most 50. It waits for a response from the
api and validates to check if the posting was successful or not.


* **Parameters**
    
    * **_assignment** (`str`) – the assigment *ID* to be posted. Must be the ID and *NOT* the name

    * **_batchedAssignment** (`list`[`str`]) – the list of assignments



* **Return type**

    `bool`



* **Returns**

    True on a success False on a failure



#### s_unknownAssignments(_: in_ _ = _ )

#### selectAssignmentsToGrade(_assignments)

* **Description**


This function maps the common name of the assignment to the actual assignment - this will help clean up a lot of
the logic and make the rest of the program a lot more consistent with the way that it handles them


* **Parameters**

    **_assignments** (`list`[`str`]) – the list of assignment common names.



#### updateStatusAssignmentScores()

* **Description**


This function pulls the scores for all the status assignments found in the config file. Stores the current
scores in a dataframe internally


#### validateAssignment(commonName=None, canvasID=None)

* **Description**



* **Parameters**
    
    * **commonName** – 

    * **canvasID** – 



* **Returns**
