from statistics import mean

import pandas as pd
import os

# When dropping all the unnecessary rows, drop all but these guys ALWAYS.
# Exceptions (like for canvas we want to drop all but the assignment we are posting) exist,
# and are handled in each function
GRADESCOPE_NEVER_DROP = ['Name', 'Email', 'Total Score', 'Status', 'Lateness']
# Grace Period of 15 minutes
GRADESCOPE_GRACE_PERIOD = 15 * 60


def findFile(_filename):
    """
    This function attempts to locate the file in a few different places:
    ./, ./grades/, ./canvas/, ./gradescope/

    :param _filename: the file name to search for
    :return: the file name with the found directory prepended
    """
    directoriesToCheck = ["./", "./grades/", "./canvas/", "./gradescope/"]

    for directory in directoriesToCheck:
        print(f"\tChecking \'{directory}\'...", end="")
        if os.path.exists(f"{directory}{_filename}"):
            print("Found.")
            return f"{directory}{_filename}"
        print("Not Found.")

    return False


def loadCSV(_filename):
    """
    This function validates that a CSV file with the name '_filename' exists
    If it does, it loads it in to a Pandas dataframe to be returned. In the event of an error,
    an empty pandas dataframe is returned
    :param _filename: the csv filename to load
    :return: the dataframe from the csv or an empty dataframe if loaded failed
    """
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


def loadGradescope(_filename):
    """
    This function loads the selected gradescope CSV file, drops all unnecessary columns,
    and modifies the existing columns to be more easily merged when the resulting CSV
    :param _filename: the filename of the assignment to be graded
    :return: the loaded gradescope dataframe
    """
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
            gradescopeDF.at[i, 'Lateness'] = f"0:0:0"

    # Get multipass from email
    for i, row in gradescopeDF.iterrows():
        gradescopeDF.at[i, 'Email'] = row['Email'].split('@')[0]
        # this approach doesn't work as great if students aren't in gradescope with their correct emails, but I digress
    # change name to what canvas uses for slightly easier joining - all SIS id are guaranteed to be unique by ITS
    gradescopeDF.rename(columns={'Email': 'sis_id'}, inplace=True)
    return gradescopeDF


def loadSpecialCases(_filename):
    """
    This function loads the special cases file, drops all rows whose 'assignment' column does not correspond
    to the selected assignment.
    :param _filename: The file name of the special cases file
    :return: the filtered special cases dataframe
    """
    specialCasesDF = loadCSV(_filename)
    if specialCasesDF.empty:
        print("Loading special cases failed")
        return specialCasesDF

    # Get multipass from email
    for i, row in specialCasesDF.iterrows():
        specialCasesDF.at[i, 'email'] = row['email'].split("@")[0]

    # Change column name to accurately reflect what is in it
    specialCasesDF.rename(columns={'email': 'multipass'}, inplace=True)

    # account for stats error if no special cases exist
    if len(specialCasesDF['multipass']) > 0:
        print(f"Average extension is {mean(specialCasesDF['extension_days'])} day(s)")

    return specialCasesDF


def loadPageFlagging(_filename, _assignment):
    """
    This function loads the page flagging file, drops all rows whose assignment column does not correspond to the
    selected assignment
    :param _filename:
    :param _assignment:
    :return:
    """
    raise NotImplementedError("Page flagging is not yet implemented")
