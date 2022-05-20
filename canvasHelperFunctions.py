import pandas as pd

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
