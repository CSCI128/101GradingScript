import os
# The directories to check if the user does not set what directories to check
DEFAULT_DIRECTORIES = ["./", "./grades/", "./canvas/", "./gradescope/", "./special_cases/", "./runestone/"]


def findFile(_filename: str, promptIfError: bool = False, directoriesToCheck: list[str] = None):
    """
    :Description:

    This function attempts to automatically locate the file in a few different places:
    ./, ./grades/, ./canvas/, ./gradescope/, ./special_cases/

    :param directoriesToCheck: The directories to search
    :param promptIfError: If we should prompt the user for a file name if we fail to locate the file
    :param _filename: the file name to search for

    :return: the file name with the found directory prepended
    """
    if directoriesToCheck is None:
        directoriesToCheck = DEFAULT_DIRECTORIES

    for directory in directoriesToCheck:
        print(f"\tChecking \'{directory}\'...", end="")
        if os.path.exists(f"{directory}{_filename}"):
            print("Found.")
            return f"{directory}{_filename}"
        print("Not Found.")

    if promptIfError:
        print("\tUnable to automatically locate file. Please enter path to file or ignore")
        usrIn = ""
        while usrIn.lower() != "ignore":
            usrIn = str(input("\t(path/to/file or ignore): "))
            if os.path.exists(usrIn):
                return usrIn

    return False
