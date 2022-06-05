import csvLoaders as ld
import grade

from Canvas import Canvas
import config

hw2Grades = None
specialCases = None


# def run():
#     global hw2Grades, specialCases
#     hw2Grades = ld.loadGradescope("sample_files/HW2_sample_scores.csv")
#     specialCases = ld.loadSpecialCases("sample_files/special_cases.csv", ["HW2"])
#     hw2Grades = grade.scoreMissingAssignments(hw2Grades)
#     hw2Grades = grade.scaleScores(hw2Grades, .1, maxScore=7)
#
#     hw2Grades, specialCases = grade.calculateLatePenalty(hw2Grades, specialCases)


def run():
    configFile = config.readConfig("sample_files/config.json")

    canvas = Canvas()

    canvas.loadSettings(configFile)
    assignmentGroups = canvas.getAssignmentGroupsFromCanvas()
    assignments = canvas.getAssignmentsFromCanvas(["56569", "56570"])

    print(assignments)
