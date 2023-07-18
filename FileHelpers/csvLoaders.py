import pandas as pd
from FileHelpers import fileHelper

# When dropping all the unnecessary rows, drop all but these guys ALWAYS.
# Exceptions (like for canvas we want to drop all but the assignment we are posting) exist,
# and are handled in each function
GRADESCOPE_NEVER_DROP = ['Email', 'Total Score', 'Status', 'Lateness']
# Grace Period of 15 minutes
GRADESCOPE_GRACE_PERIOD = 15


def loadCSV(_filename: str, promptIfError: bool = False, directoriesToCheck: list[str] = None):
    """
    :Description:

    This function validates that a CSV file with the name '_filename' exists
    If it does, it loads it in to a Pandas dataframe to be returned. In the event of an error,
    an empty pandas dataframe is returned

    :param directoriesToCheck: See fileHelper.findFile
    :param promptIfError: See fileHelper.findFile
    :param _filename: the csv filename to load

    :return: the dataframe from the csv or an empty dataframe if loaded failed
    """
    print(f"Attempting to load {_filename}...")

    _filename = fileHelper.findFile(_filename, promptIfError, directoriesToCheck)
    if not _filename:
        print("...Error")
        return pd.DataFrame()

    loadedData = pd.read_csv(_filename)

    print(f"...Loaded successfully from {_filename}")
    # maybe print stats about file here? idk.
    return loadedData


def loadGradescope(_filename):
    """
    :Description:

    This function loads the selected gradescope CSV file, drops all unnecessary columns,
    and converts the columns to the format that will be used later.

    Remaps Lateness (H:M:S) -> Lateness -> (converts to hours) -> hours_late
    Remaps Email -> (converts to multipass) -> multipass

    :param _filename: the filename of the assignment to be graded

    :return: the loaded gradescope dataframe
    """
    gradescopeDF = loadCSV(_filename, directoriesToCheck=["./", "./gradescope/"])

    if gradescopeDF.empty:
        print("Loading Gradescope CSV failed.")
        return gradescopeDF

    gradescopeDF.rename(columns={'Lateness (H:M:S)': 'Lateness'}, inplace=True)

    for col in gradescopeDF.columns.values.tolist():
        # for gradescope, because we only care about the 'never drop' columns
        # we can drop all but those
        if col not in GRADESCOPE_NEVER_DROP:
            gradescopeDF = gradescopeDF.drop(columns=col)

    print("Processing Gradesheet...", end='')
    missingCols: list[str] = [el for el in GRADESCOPE_NEVER_DROP if el not in gradescopeDF.columns.to_list()]

    if missingCols:
        print("Failed.")
        print("Unrecognised format for Gradescope gradesheet")
        return pd.DataFrame()

    ungradedStudents: int = 0
    # Process and apply grace period. Add days counter. And validate that all students are graded
    for i, row in gradescopeDF.iterrows():
        if row['Status'] == "Ungraded":
            ungradedStudents += 1
            continue
        # Handles edge case where student has not submitted. Lateness will NaN rather than 0:0:0.
        if type(row['Lateness']) is not str:
            gradescopeDF.at[i, 'Lateness'] = "0"
            continue

        # In the gradescope CSV, lateness is store as H:M:S (Hours, Minutes, Seconds).
        hours, minutes, seconds = row['Lateness'].split(':')
        # converting everything to minutes to make this once step easier
        lateness = (float(hours) * 60) + float(minutes) + (float(seconds) / 60)

        # Apply grade period to all submission
        lateness -= GRADESCOPE_GRACE_PERIOD

        if lateness <= 0:
            lateness = 0

        lateness /= 60  # convert back to hours, so we don't have to do the conversion later
        gradescopeDF.at[i, 'Lateness'] = f"{lateness}"

    if ungradedStudents != 0:
        print("Failed.")
        print(f"There are currently {ungradedStudents} ungraded students. Grading can not continue.")
        return pd.DataFrame()

    gradescopeDF.rename(columns={'Lateness': 'hours_late'}, inplace=True)
    # All NaN values should be handled at this point
    gradescopeDF = gradescopeDF.astype({'hours_late': "float"}, copy=False)

    # Get multipass from email
    for i, row in gradescopeDF.iterrows():
        gradescopeDF.at[i, 'Email'] = row['Email'].split('@')[0]
        # this approach doesn't work as great if students aren't in gradescope with their correct emails, but I digress

    gradescopeDF.rename(columns={'Email': 'multipass'}, inplace=True)
    print("Done.")
    return gradescopeDF


def loadRunestone(_filename, assignment: str):
    """
    :Description:

    This function loads the selected runestone CSV file, drops all unnecessary columns,
    and converts the columns to the format that will be used later.

    :param _filename: the filename of the assignment to be graded
    :param assignment: the name of the assignment to be graded
    
    :return: the loaded gradescope dataframe
    """
    runestoneDF = loadCSV(_filename, directoriesToCheck=["./", "./runestone/"])

    if runestoneDF.empty:
        print("Loading Runestone CSV failed.")
        return runestoneDF

    # get the points out first; row 1 has the total point value
    column = runestoneDF.columns.get_loc(assignment)
    totalPoints = int(runestoneDF.iloc[1][column])

    # drop due date, points, and class average rows (we just want user data)
    runestoneDF = runestoneDF.drop([0, 1, 2])

    RUNESTONE_NEVER_DROP = ["E-mail", assignment]

    # drop columns we don't care about 
    for col in runestoneDF.columns.values.tolist():
        if col not in RUNESTONE_NEVER_DROP:
            runestoneDF = runestoneDF.drop(columns=col)

    print("Processing Gradesheet...", end='')

    missingCols: list[str] = [el for el in RUNESTONE_NEVER_DROP if el not in runestoneDF.columns.to_list()]

    if missingCols:
        print("Failed.")
        print("Unrecognised format for Runestone gradesheet")
        return pd.DataFrame()

    # Get multipass from email
    for i, row in runestoneDF.iterrows():
        runestoneDF.at[i, 'E-mail'] = row['E-mail'].split('@')[0]

        # derive actual score from total points and score percentage
        score = (totalPoints / 100) * float(row[assignment].split("%")[0])
        runestoneDF.at[i, assignment] = score

        # add phony columns for gradesheet format
        runestoneDF.at[i, 'lateness_comment'] = ''
        runestoneDF.at[i, 'Status'] = ''

    runestoneDF.rename(columns={'E-mail': 'multipass'}, inplace=True)
    runestoneDF.rename(columns={assignment: 'Total Score'}, inplace=True)

    print("Done.")
    return runestoneDF

