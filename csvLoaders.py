import pandas as pd
import os

# When dropping all the unnecessary rows, drop all but these guys ALWAYS.
# Exceptions (like for canvas we want to drop all but the assignment we are posting) exist,
# and are handled in each function
CANVAS_NEVER_DROP = ['Student', 'ID', 'SIS Login ID', 'Section']
GRADESCOPE_NEVER_DROP = ['Name', 'Email', 'Total Score', 'Status', 'Lateness']
# Grace Period of 15 minutes - to allow
GRADESCOPE_GRACE_PERIOD = 15 * 60

'''
This function attempts to locate the file in a few different places:
./, ./grades/, ./canvas/, ./gradescope/
'''


def findFile(_filename):
    directoriesToCheck = ["./", "./grades/", "./canvas/", "./gradescope/"]

    for directory in directoriesToCheck:
        print(f"\tChecking \'{directory}\'...", end="")
        if os.path.exists(f"{directory}{_filename}"):
            print("Found.")
            return f"{directory}{_filename}"
        print("Not Found.")

    return False


'''
This function validates that a CSV file with the name '_filename' exists 
If it does, it loads it in to a Pandas dataframe to be returned 
'''


def loadCSV(_filename):
    print(f"Attempting to load {_filename}...")

    # TODO Add check to see if file is actually a CSV.
    #  If this is not added the pandas pd.read_csv() will fail in certain edge cases

    _filename = findFile(_filename)
    if not _filename:
        print("...Error")
        return pd.DataFrame()

    loadedData = pd.read_csv(_filename)

    print(f"...Loaded successfully from {_filename}")
    # maybe print stats about file here? idk.
    return loadedData


'''
This function loads the selected gradescope CSV file, drops all unnecessary columns, 
and modifies the existing columns to be more easily merged when the resulting CSV
'''


def loadGradescope(_filename):
    gradescopeDF = loadCSV(_filename)

    if gradescopeDF.empty:
        print("Loading Gradescope CSV failed.")
        return gradescopeDF

    gradescopeDF.rename(columns={'Lateness (H:M:S)': 'Lateness'}, inplace=True)
    for col in gradescopeDF.columns.values.tolist():
        # for gradescope, because we only care about the 'never drop' columns
        # we can drop all but those
        if col not in GRADESCOPE_NEVER_DROP:
            gradescopeDF = gradescopeDF.drop(columns=col)

    # print(gradescope.columns.values.tolist())
    # Process and apply grace period. Add days counter.
    for i, row in gradescopeDF.iterrows():
        # In the gradescope CSV, lateness is store as H:M:S (Hours, Minutes, Seconds).
        hours, minutes, seconds = gradescopeDF.at[i, 'Lateness'].split(':')
        # converting everything to minutes to make this once step easier
        lateness = (float(hours) * 60) + float(minutes) + (float(seconds) / 60)
        if lateness <= GRADESCOPE_GRACE_PERIOD:
            gradescopeDF.at[i, 'Lateness'] = f"0:0:0:0"  # set format to D:H:M:S (Days, Hours, Minutes, Seconds)
        else:
            pass
            # we are now adding days to make later stuff easier when we have to compare timestamps
            # of when special cases need to be applied and what late penitently should be applied.
            days = hours % 24
            hours -= days * 24
            gradescopeDF.at[i, 'Lateness'] = f"{days}:{hours}:{minutes}:{seconds}"

    # Get multipass from email
    for i, row in gradescopeDF.iterrows():
        gradescopeDF.at[i, 'Email'] = gradescopeDF.at[i, 'Email'].split('@')[0]  # get multipass out of email
        # this approach doesn't work as great if students aren't in gradescope with their correct emails, but I digress
    # change name to what canvas uses for slightly easier joining - all SIS id are guaranteed to be unique by ITS
    gradescopeDF.rename(columns={'Email': 'SIS Login ID'}, inplace=True)

    print(gradescopeDF.columns.values.tolist())
    print(gradescopeDF.head().values.tolist())
    return gradescopeDF


'''
This function loads the selected canvas grade book, drops all assignments that are not selected,
drops all unnecessary columns, and modifies the existing columns to be more easily merged.   
'''


def loadCanvas(_filename, _assignment):
    canvasDF = loadCSV(_filename)
    if canvasDF.empty:
        print("Loading Canvas Grade book failed.")
        return canvasDF

    # map common assignment name to canvas name - is impractical to do this in a config
    #  file because canvas gives each assignment an id that changes every year.
    locatedAssignment = False
    print(f"Attempting to locate {_assignment}...", end="")
    for assignmentCanvasName in canvasDF.columns.values.tolist():
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
        return pd.DataFrame()

    # drop all unused columns - so every thing but the 'never drop' list and the now mapped assignment

    for col in canvasDF.columns.values.tolist():
        if col not in CANVAS_NEVER_DROP and col != _assignment:
            canvasDF = canvasDF.drop(columns=col)

    print(_assignment)
    print(canvasDF.columns.values.tolist())

    return canvasDF


'''
This function loads the special cases file, drops all rows whose 'assignment' column does not correspond 
to the selected assignment.
'''


def loadSpecialCases(_filename, _assignment):
    pass


'''
This function loads the page flagging file, drops all rows whose assignment column does not correspond to the 
selected assignment
'''


def loadPageFlagging(_filename, _assignment):
    pass
