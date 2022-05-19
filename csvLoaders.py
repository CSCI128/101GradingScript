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
        print(f"\t...Checking \'{directory}\'...", end="")
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
        return False

    loadedData = pd.read_csv(_filename)

    print(f"...Loaded successfully from {_filename}")
    # maybe print stats about file here? idk.
    return loadedData


'''
This function loads the selected gradescope CSV file, drops all unnecessary columns, 
and modifies the existing columns to be more easily merged when the resulting CSV
'''


def loadGradescope(_filename):
    gradescope = loadCSV(_filename)
    gradescope.rename(columns={'Lateness (H:M:S)': 'Lateness'}, inplace=True)
    for col in gradescope.columns.values.tolist():
        # for gradescope, because we only care about the 'never drop' columns
        # we can drop all but those
        if col not in GRADESCOPE_NEVER_DROP:
            gradescope = gradescope.drop(columns=col)

    # print(gradescope.columns.values.tolist())
    # Process and apply grace period. Add days counter.
    for i, row in gradescope.iterrows():
        # todo check more gradescope files to see how lateness is actually stored
        #  currently I think it is stored by day
        # In the gradescope CSV, lateness is store as H:M:S (Hours, Minutes, Seconds).
        # hours, minutes, seconds = gradescope.at[i, 'Lateness'].split(':')
        # converting everything to minutes to make this once step easier
        # lateness = (float(hours) * 60) + float(minutes) + (float(seconds) / 60)
        lateness = gradescope.at[i, 'Lateness'] * 24 * 60
        if lateness <= GRADESCOPE_GRACE_PERIOD:
            gradescope.at[i, 'Lateness'] = 0
        else:
            pass
            # we are now adding days to make later stuff easier when we have to compare timestamps
            # of when special cases need to be applied and what late penitently should be applied.
            # days = hours % 24
            # hours -= days * 24
            # gradescope.at[i, 'Lateness'] = f"{days}:{hours}:{minutes}:{seconds}"

    # Get multipass from email
    for i, row in gradescope.iterrows():
        gradescope.at[i, 'Email'] = gradescope.at[i, 'Email'].split('@')[0]  # get multipass out of email
        # this approach doesn't work as great if students aren't in gradescope with their correct emails, but I digress
    # change name to what canvas uses for slightly easier joining - all SIS id are guaranteed to be unique by ITS
    gradescope.rename(columns={'Email': 'SIS Login ID'}, inplace=True)

    print(gradescope.columns.values.tolist())
    print(gradescope.head().values.tolist())
    return gradescope


'''
This function loads the selected canvas grade book, drops all assignments that are not selected,
drops all unnecessary columns, and modifies the existing columns to be more easily merged.   
'''


def loadCanvas(_filename, _assignment):
    pass


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
