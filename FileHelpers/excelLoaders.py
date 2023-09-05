import pandas as pd
import FileHelpers.fileHelper as fileHelper

DEFAULT_SPECIAL_CASES_SEARCH_PATH = "special_cases/special_cases.xlsx"
SPECIAL_CASES_REQUIRED_COLUMNS = ["handled", "full_name", "assignment", "extension_type",
                                  "student_comment", "extension_days", "approved_by",
                                  "handled", "grader_notes"]


def loadExcel(_filename, promptIfError: bool = False, directoriesToCheck: list[str] = None):
    """
    :Description:

    This function validates that an Excel file with the name `_filename` exists
    If it does, it loads it in to a Pandas dataframe to be returned. In the event of an error,
    an empty pandas dataframe is returned

    Calls ``fileHelper.findFile`` internally

    :param directoriesToCheck: ``fileHelper.findFile``
    :param promptIfError: ``fileHelper.findFile``
    :param _filename: the Excel filename to load
    :return: the dataframe from the Excel file or an empty dataframe if loaded failed
    """
    print(f"Attempting to load {_filename}...")

    _filename = fileHelper.findFile(_filename, promptIfError, directoriesToCheck)
    if not _filename:
        print("...Error")
        return pd.DataFrame()

    loadedData = pd.read_excel(_filename, engine="openpyxl")

    print(f"...Loaded successfully from {_filename}")
    # maybe print stats about file here? idk.
    return loadedData


def createEmptySpecialCasesSheet() -> pd.DataFrame:
    specialCasesDF: pd.DataFrame = pd.DataFrame()
    # create all column names so that we dont get errors
    for col in SPECIAL_CASES_REQUIRED_COLUMNS:
        specialCasesDF[col] = ""
    specialCasesDF['ignore'] = ""

    return specialCasesDF


def loadSpecialCases():
    """
    :Description:

    This function loads the special cases file.

    This function attempts to automatically load special cases from "./special_cases/special_cases.xlsx" or prompts the
    user to enter a path if it cant be found

    :return: the special cases dataframe
    """
    specialCasesDF = loadExcel(DEFAULT_SPECIAL_CASES_SEARCH_PATH, promptIfError=False, directoriesToCheck=["./"])

    if specialCasesDF.empty:
        print("Failed to automatically load special cases file. Please enter file name")
        usrIn = str(input("(./path/to/special_cases.xlsx): "))
        specialCasesDF = loadExcel(usrIn, promptIfError=True)
    if specialCasesDF.empty:
        print("Loading special cases failed")
        return createEmptySpecialCasesSheet()

    print("Processing special cases...", end='')
    # if for some reason excel makes these into bools - convert back to strings
    for i, row in specialCasesDF.iterrows():
        if row['handled'] == True:
            specialCasesDF.at[i, 'handled'] = "TRUE"
        elif row['handled'] == False:
            specialCasesDF.at[i, 'handled'] = "FALSE"

    # weird edge case with Excel - it parses the spaces in names as unicode \xa0 - which is a pain - changing to a _
    specialCasesDF.columns = specialCasesDF.columns.str.replace('\xa0', '_')
    specialCasesDF.columns = specialCasesDF.columns.str.replace(' ', '_')

    for col in SPECIAL_CASES_REQUIRED_COLUMNS:
        if col not in specialCasesDF.columns.values.tolist():
            print("Failed.")
            print(f"Missing required column: {col}")
            print("Special cases are being ignored.")
            return createEmptySpecialCasesSheet()

    # We want to non-destructively get the multipass so that it is easier to use the spreadsheet later
    specialCasesDF['multipass'] = ""

    # Get multipass from email
    for i, row in specialCasesDF.iterrows():
        specialCasesDF.at[i, 'multipass'] = row['CWID']

    # Set the date to be a date
    specialCasesDF['new_due_date'] = pd.to_datetime(specialCasesDF['new_due_date'])

    # set the extension days to be an int
    specialCasesDF['extension_days'] = specialCasesDF['extension_days'].apply(pd.to_numeric)

    # fill the NaNs in the approved by col with empty strings
    specialCasesDF['approved_by'] = specialCasesDF['approved_by'].fillna('')

    # fill the NaNs in the handled col with empty strings
    specialCasesDF['handled'] = specialCasesDF['handled'].fillna('')

    # fill the NaNs in the grader notes col with empty strings
    specialCasesDF['grader_notes'] = specialCasesDF['grader_notes'].fillna('')

    print("Done.")
    return specialCasesDF


def loadPassFailAssignment(_filename, multipassSearches=None) -> pd.DataFrame:
    if multipassSearches is None:
        multipassSearches = ["email", "email_address", "multipass", "mines_email", "mines_email_address"]

    passFailAssignmentDF: pd.DataFrame = loadExcel(_filename, promptIfError=False, directoriesToCheck=["./"])

    if passFailAssignmentDF.empty:
        print(f"Failed to load pass/fail assignment from {_filename}.")
        usrIn = str(input("(./path/to/assignment.xlsx): "))
        passFailAssignmentDF = loadExcel(usrIn, promptIfError=True, directoriesToCheck=["./"])

    if passFailAssignmentDF.empty:
        print("Failed to load pass/fail assignment.")
        return passFailAssignmentDF

    print("Processing pass/fail assignment...", end='')

    # weird edge case with Excel - it parses the spaces in names as unicode \xa0 - which is a pain - changing to a _
    passFailAssignmentDF.columns = passFailAssignmentDF.columns.str.replace('\xa0', '_')
    passFailAssignmentDF.columns = passFailAssignmentDF.columns.str.replace(' ', '_')

    # make all the columns lower to make my life slightly better
    passFailAssignmentDF.columns = passFailAssignmentDF.columns.str.lower()

    # We need to find the multipass in the spreadsheet, it can either be from an email or from the student entering it
    #  directly, either way, we need to find it and map to a known value. In this case we are mapping it 'multipass'
    foundMultipass: bool = False
    for curSearch in multipassSearches:
        if curSearch in passFailAssignmentDF.columns.values.tolist():
            foundMultipass = True

            passFailAssignmentDF.rename(columns={curSearch: 'multipass'}, inplace=True)

            # check to see if the column we found is an email column.
            if '@' in passFailAssignmentDF.at[0, 'multipass']:
                for i, row in passFailAssignmentDF.iterrows():
                    passFailAssignmentDF.at[i, 'multipass'] = row['multipass'].split("@")[0]

    if not foundMultipass:
        print("Failed.")
        print(f"Failed to identify student multipass in assignment. "
              f"Found: {passFailAssignmentDF.columns.values.tolist()}")
        return pd.DataFrame()

    # now we need to fill all the NaNs with spaces, so we correctly evaluate the proof of attendance

    for col in passFailAssignmentDF.columns.values.tolist():
        passFailAssignmentDF[col] = passFailAssignmentDF[col].fillna('')

    print("Done.")
    return passFailAssignmentDF
