import requests
import json

'''
This function takes the canvas grade book and the shorthand assignment name (ie: HW4, Lab 1, Assessment 2)
and maps it to the canvas name. We have to map the current canvas name as we don't want to create a new assignment, 
nor define a map the assignment when we upload grades.
PARAMS:
    _canvasDF - canvas grade book as a pandas dataframe
    _assignment - the assignment to look for as a string 

'''


def locateAssignment(_canvasDF, _assignment):
    locatedAssignment = False
    print(f"Attempting to locate {_assignment}...", end="")
    for assignmentCanvasName in _canvasDF.columns.values.tolist():
        if _assignment in assignmentCanvasName:
            locatedAssignment = True
            _assignment = assignmentCanvasName
            print("Found.")
            break
    if locatedAssignment:
        print(f"Canvas assignment located at {_assignment}")
    else:
        print("Error")
        print(f"Failed to locate {_assignment}")
        return False

    return _assignment


def downloadUpdatedGradebook():
    accessToken = "9802~rZSno3rAikJOCuHgUz90JkQOzoSfFXrm2Rp5TlrhqQ4uehPQnq5xqT5dC6n5anOJ"
    endpoint = "/api/v1/courses/38531/gradebook_history/feed"  # this was found in files lol
    host = "https://elearning.mines.edu"

    url = host + endpoint
    headers = {"Authorization": f"Bearer {accessToken}"}

    result = requests.get(url, headers=headers)

    print(result.status_code)
    return result.json()
