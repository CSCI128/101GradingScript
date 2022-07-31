
def standardGrading(_canvas: Canvas):

    print("Enter path to Gradescope grades")
    gradescopePath: str = getUserInput(allowedUserInput="./path/to/gradescope_grades.csv")
    specialCasesPath: str = getUserInput(allowedUserInput="./path/to/special_cases.cvs")
    gradescopeDF: pd.DataFrame = csvLoaders.loadGradescope(gradescopePath)
    if gradescopeDF.empty:
        print(f"Fatal: Failed to load Gradescope grades from {gradescopePath}")
        return False
    specialCasesDF: pd.DataFrame = csvLoaders.loadSpecialCases(specialCasesPath)
    if specialCasesDF.empty:
        print(f"Fatal: Failed to load Special Cases from {specialCasesPath}")
        return False

    print("\n===\tGenerating Grades\t===\n")
    scaleFactor, standardPoints, maxPoints, xcScaleFactor = setupScaling(selectedAssignment['points'].values[0])
    gradescopeDF = grade.scaleScores(gradescopeDF, scaleFactor, standardPoints, maxPoints, xcScaleFactor)
    missingScore, exceptions = setupMissingAssignments()
    gradescopeDF = grade.scoreMissingAssignments(gradescopeDF, score=missingScore, exceptions=exceptions)

    gradescopeDF, specialCasesDF = grade.calculateLatePenalty(gradescopeDF,
                                                              specialCasesDF,
                                                              selectedAssignment['common_name'].values[0])

    print("\nGrades have been generated. Would you like to continue?")
    usrYN = getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tGenerating Canvas Scores\t===\n")
    gradescopeAssignments = {selectedAssignment['common_name'].values[0]: gradescopeDF}
    studentScores = score.createCanvasScoresForAssignments(
        gradescopeAssignments,
        specialCasesDF,
        _canvas,
        selectedAssignment['common_name'].values.tolist()
    )

    print("Scores have been generated. Would you like to continue?")
    usrYN = getUserInput("y/n")
    if usrYN.lower() != 'y':
        return False

    print("\n===\tPosting Scores\t===\n")
    if post.writeGrades(gradescopeAssignments) \
        and post.updateSpecialCases(specialCasesDF) \
            and post.postToCanvas(_canvas, studentScores):
        return True

    return False
