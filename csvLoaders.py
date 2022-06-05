from statistics import mean

import pandas as pd
import os

import canvasHelperFunctions as canvas

# When dropping all the unnecessary rows, drop all but these guys ALWAYS.
# Exceptions (like for canvas we want to drop all but the assignment we are posting) exist,
# and are handled in each function
CANVAS_NEVER_DROP = ['Student', 'ID', 'SIS Login ID', 'Section']
GRADESCOPE_NEVER_DROP = ['Name', 'Email', 'Total Score', 'Status', 'Lateness']
# Grace Period of 15 minutes
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
If it does, it loads it in to a Pandas dataframe to be returned. In the event of an error,
an empty pandas dataframe is returned
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
PARAMS:
    _filename - the filename of the assignment to be graded
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

        # Handles edge case where student has not submitted. Lateness will NaN rather than 0:0:0.
        if type(row['Lateness']) is not str:
            continue

        # In the gradescope CSV, lateness is store as H:M:S (Hours, Minutes, Seconds).
        hours, minutes, seconds = row['Lateness'].split(':')
        # converting everything to minutes to make this once step easier
        lateness = (float(hours) * 60) + float(minutes) + (float(seconds) / 60)
        if lateness <= GRADESCOPE_GRACE_PERIOD:
            gradescopeDF.at[i, 'Lateness'] = f"0:0:0"  # set format to H:M:S (Hours, Minutes, Seconds)

    # Get multipass from email
    for i, row in gradescopeDF.iterrows():
        gradescopeDF.at[i, 'Email'] = row['Email'].split('@')[0]  # get multipass out of email
        # this approach doesn't work as great if students aren't in gradescope with their correct emails, but I digress
    # change name to what canvas uses for slightly easier joining - all SIS id are guaranteed to be unique by ITS
    gradescopeDF.rename(columns={'Email': 'SIS Login ID'}, inplace=True)

    # put names in format Last, First so that it matches canvas and special cases
    for i, row in gradescopeDF.iterrows():
        # this will only capture the first name and last name. If the student has any other names - they will be ignored
        firstName, lastName = row['Name'].split(' ')[0:2]  # only get the first two elements
        gradescopeDF.at[i, 'Name'] = f"{lastName}, {firstName}"

    return gradescopeDF


'''
This function loads the selected canvas grade book, drops all assignments that are not selected,
drops all unnecessary columns, and modifies the existing columns to be more easily merged.   
PARAMS: 
    _filename - the file name of the canvas grade book. A string 
    _assignments - the *list* of assignments 
'''


def loadCanvas(_filename, _assignments):
    if type(_assignments) is not list:
        raise TypeError("loadCanvas(_filename, _assignments) -  _assignments MUST be a list." +
                        f"Type is {type(_assignments)}")

    canvasDF = loadCSV(_filename)
    if canvasDF.empty:
        print("Loading Canvas Grade book failed.")
        return canvasDF

    # map common assignment name to canvas name - is impractical to do this in a config
    #  file because canvas gives each assignment an id that changes every year.

    for i, assignment in enumerate(_assignments):
        _assignments[i] = canvas.locateAssignment(canvasDF, assignment)

    _assignments = [assignment for assignment in _assignments if assignment]  # remove failures from assignment list

    # drop all unused columns - so every thing but the 'never drop' list and the now mapped assignments
    for col in canvasDF.columns.values.tolist():
        if col not in CANVAS_NEVER_DROP and col not in _assignments:
            canvasDF = canvasDF.drop(columns=col)

    print(_assignments)
    print(canvasDF.columns.values.tolist())

    return canvasDF


'''
This function loads the special cases file, drops all rows whose 'assignment' column does not correspond 
to the selected assignment.
'''


def loadSpecialCases(_filename, _assignments):
    if type(_assignments) is not list:
        raise TypeError("loadSpecialCases(_filename, _assignments) -  _assignments MUST be a list." +
                        f"Type is {type(_assignments)}")
    specialCasesDF = loadCSV(_filename)
    if specialCasesDF.empty:
        print("Loading special cases failed")
        return specialCasesDF

    # Narrows down special cases to only include the assignments that we are posting
    specialCasesDF = specialCasesDF.loc[specialCasesDF['assignment'].isin(_assignments)]

    # Get multipass from email
    for i, row in specialCasesDF.iterrows():
        specialCasesDF.at[i, 'email'] = row['email'].split("@")[0]

    # Change column name to accurately reflect what is in it
    specialCasesDF.rename(columns={'email': 'multipass'}, inplace=True)

    print(f"Loaded {len(specialCasesDF['multipass'])} special cases for assignment(s) {_assignments}")
    # account for stats error if no special cases exist
    if len(specialCasesDF['multipass']) > 0:
        print(f"Average extension is {mean(specialCasesDF['extension_days'])} day(s)")

    return specialCasesDF

'''
This function loads the page flagging file, drops all rows whose assignment column does not correspond to the 
selected assignment
'''


def loadPageFlagging(_filename, _assignment):
    pass
