import csvLoaders as ld
from Grade import grade, score, post
from Canvas import Canvas
import config

hw2Grades = None
specialCases = None
assignmentsToPost = None


def run():
    global hw2Grades, specialCases, assignmentsToPost
    hw2Grades = ld.loadGradescope("sample_files/HW2_Scavenger_Hunt_scores.csv")
    specialCases = ld.loadSpecialCases("sample_files/special_cases.csv")
    hw2Grades = grade.scoreMissingAssignments(hw2Grades)
    hw2Grades = grade.scaleScores(hw2Grades, .1, maxScore=7)

    hw2Grades, specialCases = grade.calculateLatePenalty(hw2Grades, specialCases, "HW2")
    configFile = config.loadConfig()

    canvas = Canvas()

    canvas.loadSettings(configFile)
    canvas.getAssignmentsFromConfig(configFile)
    canvas.getStudentsFromCanvas()

    assignmentsToPost = score.createCanvasScoresForAssignments({"HW2": hw2Grades}, specialCases, canvas, ["HW2"])


if __name__ == "__main__":
    run()
