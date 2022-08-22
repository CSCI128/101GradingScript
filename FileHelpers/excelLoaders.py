import pandas as pd
import FileHelpers.fileHelper as fileHelper

DEFAULT_SPECIAL_CASES_SEARCH_PATH = "special_cases/special_cases.xlsx"


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
        usrIn = str(input("(./path/to/special_cases.xlxs): "))
        specialCasesDF = loadExcel(usrIn, promptIfError=True)
    if specialCasesDF.empty:
        print("Loading special cases failed")
        return specialCasesDF

    # if for some reason excel makes these into bools - convert back to strings
    for i, row in specialCasesDF.iterrows():
        if row['handled'] == True:
            specialCasesDF.at[i, 'handled'] = "TRUE"
        elif row['handled'] == False:
            specialCasesDF.at[i, 'handled'] = "FALSE"

    # weird edge case with Excel - it parses the spaces in names as unicode \xa0 - which is a pain - changing to a _
    specialCasesDF.columns = specialCasesDF.columns.str.replace('\xa0', '_')
    specialCasesDF.columns = specialCasesDF.columns.str.replace(' ', '_')

    # We want to non-destructively get the multipass so that it is easier to use the spreadsheet later
    specialCasesDF['multipass'] = ""

    # Get multipass from email
    for i, row in specialCasesDF.iterrows():
        specialCasesDF.at[i, 'multipass'] = row['email'].split("@")[0]

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

    return specialCasesDF
