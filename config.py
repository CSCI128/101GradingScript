import json
import os
from Canvas import Canvas
from sys import exit

from UI import uiHelpers


# This file needs some work, esp with handling user input.

def locateConfigFiles():
    """
    This function reads the config files from the './config/' directory.
    It filters out any non files and any files that don't end in .json
    Returns the number of found files and a list of the files
    """

    configFileName = [f"./config/{f}" for f in os.listdir("./config/") if
                      os.path.isfile(f"./config/{f}") and f[len(f) - 4:] == "json"]
    return len(configFileName), configFileName


def readConfig(_configFileName):
    """
    This function reads the config from the disk and converts it to a python dictionary.
    PARAMS:
        _configFileName - The file name to load
    """
    with open(_configFileName, "r") as jsonDataFile:
        configFile = json.load(jsonDataFile)

    return configFile


def createNewConfig():
    """
    Creates a new config file.
    Config file must contain an api key,
    the course ID, the user ID, and the canvas endpoint.
    It also must contain the assignment list.
    This function walks the user through the creation, and builds a new config file to be saved and loaded.
    """
    apiKey = str(input("Enter your Canvas api key: "))
    userId = str(input("Enter your Canvas user id: "))
    endpoint = str(input("Enter your Canvas endpoint: "))
    canvas = Canvas(_API_KEY=apiKey, _USER_ID=userId, _ENDPOINT=endpoint)

    
    tenantId = str(intput("Enter your Azure AD Tenant Id: "))
    
    
    print("Retrieving eligible courses...", end="\n\t")
    courses = canvas.getCourseList()
    print("...Done")

    print("Please select your course")
    for i, course in enumerate(courses):
        print(f"{i + 1}: {course['name']}\t{course['enrollment_type']}\t{course['id']}")

    usrIn = int(input(f"(1 - {len(courses)}): "))
    selectedCourse = courses[usrIn - 1]

    canvas.COURSE_ID = str(selectedCourse['id'])
    print("Retrieving assignment groups...", end="\n\t")
    assignmentGroups = list(canvas.getAssignmentGroupsFromCanvas().items())
    print("...Done")

    print("Enter the assignment groups that you would like to include")

    for i, element in enumerate(assignmentGroups):
        print(f"{i + 1}: {element[0]}\t{element[1]}")

    print("When done entering values, type \'done\'")

    usrIn = ""
    groupsToUse = []
    while type(usrIn) is int or usrIn.lower() != "done":
        usrIn = str(input(f"(done or 1 - {len(assignmentGroups)}): "))
        if not usrIn.isdigit():
            continue
        usrIn = int(usrIn)
        groupsToUse.append(assignmentGroups[usrIn - 1][1])

    print(f"Downloading assignments from {len(groupsToUse)} assignment groups...", end="\n\t")
    assignments = canvas.getAssignmentsFromCanvas(groupsToUse)
    print("...Done")

    print("Enter Common Name for status assignments (they must be already downloaded).")
    selectedAssignment: str = ""
    statusAssignment: dict = {}
    statusAssignments: list[dict] = []
    while selectedAssignment.lower() != "done":
        selectedAssignment = input("(Common name or done): ")
        if selectedAssignment.lower() != "done":
            # The way that this is currently being done means that if there are multiple matches then we will be unable
            #  to actually select it.
            for i in range(len(assignments)):
                if assignments[i]['common_name'] == selectedAssignment:
                    statusAssignment = assignments[i]
                    break
            if not statusAssignment:
                print(f"Unable to identify assignment with common name {selectedAssignment}")
                continue
            print(f"Identified {statusAssignment['name']}")
            print("Is this correct?")
            usrYN = str(input("(y/n): "))
            if usrYN.lower() == 'y':
                # The trigger is the word in extension type that will trigger a status assignment update for a student
                statusAssignment['trigger'] = str(input("Enter trigger: "))
                statusAssignment.pop('points')
                statusAssignments.append(statusAssignment)

            statusAssignment = {}
            selectedAssignment = ""

    latePenalties: list[float] = []

    correct = False
    while not correct:
        print("Enter how many days for the late penalty: ")
        lateDays = uiHelpers.getUserInput(allowedLowerRange=1, allowedUpperRange=7)

        for i in range(lateDays):
            print(f"Enter max percentage for {i + 1} days late: ")
            percentage: int = uiHelpers.getUserInput(allowedLowerRange=0, allowedUpperRange=100)

            latePenalties.append(percentage / 100)

        print("Is the following information correct?")
        print("Late penalties per day: ", latePenalties)
        userYN = uiHelpers.getUserInput(allowedUserInput="y/n")
        if userYN.lower() == "y":
            correct = True

    latePenalties.insert(0, 1)
    latePenalties.append(0)

    input("Press any key to write the config file...")

    output = dict()

    print("Writing...")
    print("\tWriting course metadate...", end='')
    output['class'] = str(selectedCourse['name'])
    output['course_id'] = str(selectedCourse['id'])
    output['API_key'] = apiKey
    output['user_id'] = userId
    output['endpoint'] = endpoint
    output['tenant_id'] = tenantId
    output['late_penalties'] = latePenalties
    print("Done.")
    print("\tWriting assignments...", end='')
    output['assignments'] = assignments
    output['status_assignments'] = statusAssignments
    print("Done.")
    print("\tWriting to file...", end='')
    # TODO Move to a file handler call
    with open(f"./config/{selectedCourse['name'].replace(' ', '-')}-config.json", 'w') as jsonOutput:
        json.dump(output, jsonOutput)
        print("Done.")
    print("...Done")

    return output


def loadConfig():
    """
    This function gets the list of available config files and prompts the user to create a new file if none exist
    or choose file to open from a list. If only one file exists then it will load that file by default.
    Returns the loaded config file. (unless one isn't created, in which case it exits the program)
    """
    configFileCount, configFiles = locateConfigFiles()
    if configFileCount == 1:
        return readConfig(configFiles[0])
    if configFileCount == 0:
        print("No config files exist! Would you like to create one? (y/n): ", end="")
        usrIn = str(input(""))
        if usrIn.lower() == 'y':
            return createNewConfig()
        else:
            exit()

    print("Multiple config files found. Please select the one you'd like to load")
    for i, el in enumerate(configFiles):
        print(f"{i + 1}: {el}")

    # todo validate this input
    usrIn = int(input(f"(1 - {configFileCount}): "))

    return readConfig(configFiles[usrIn - 1])
