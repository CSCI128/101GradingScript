import json
import os
from Canvas import Canvas


def locateConfigFiles():
    configFileName = [f"./config/{f}" for f in os.listdir("./config/") if os.path.isfile(os.path.join("./config/", f))]
    return len(configFileName), configFileName


def readConfig(_configFileName):
    with open(_configFileName, "r") as jsonDataFile:
        configFile = json.load(jsonDataFile)

    return configFile


def createNewConfig():
    apiKey = str(input("Enter your Canvas API key: "))
    userId = str(input("Enter your Canvas user id: "))
    endpoint = str(input("Enter your Canvas endpoint: "))
    canvas = Canvas(_API_KEY=apiKey, _USER_ID=userId, _ENDPOINT=endpoint)

    print("Retrieving eligible courses...", end="\n\t")
    courses = canvas.getCourseList()
    print("...Done")

    print("Please select your course")
    for i, course in enumerate(courses):
        print(f"{i + 1} {course['name']}\t{course['enrollment_type']}\t{course['id']}")

    usrIn = int(input(f"(1 - {len(courses)}): "))
    selectedCourse = courses[usrIn - 1]

    canvas.COURSE_ID = str(selectedCourse['id'])
    print("Retrieving assignment groups...", end="\n\t")
    assignmentGroups = list(canvas.getAssignmentGroupsFromCanvas().items())
    print("...Done")

    print("Enter the assignment groups that you would like to include")

    for i, element in enumerate(assignmentGroups):
        print(f"{i + 1} {element[0]}\t{element[1]}")

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

    input("Press any key to write the config file...")

    output = dict()

    print("Writing...")
    print("\tWriting course metadate...", end='')
    output['class'] = str(selectedCourse['name'])
    output['course_id'] = str(selectedCourse['id'])
    output['API_key'] = str(apiKey)
    output['user_id'] = str(userId)
    output['endpoint'] = str(endpoint)
    print("Done.")
    print("\tWriting assignments...", end='')
    output['assignments'] = assignments
    print("Done.")
    print("\tWriting to file...", end='')
    with open(f"./config/{selectedCourse['name']}-config.json", 'w') as jsonOutput:
        json.dump(output, jsonOutput)
        print("Done.")
    print("...Done")

    return output


def loadConfig():
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