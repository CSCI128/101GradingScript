import os
import numpy.random as numpy_rand
from scipy import stats
import random
import json


def generateTruncNorm(mean: float, sd: float, lower: int, upper: int) -> stats.truncnorm:
    return stats.truncnorm(
        (lower - mean) / sd, (upper - mean) / sd, loc=mean, scale=sd)


class Factories:
    AssignmentMaxPoints: list[int] = []
    AssignmentMaxStudentPoints: int = None

    @staticmethod
    def generateStudentRoster(_numberOfStudents: int, studentEmailDomain: str = "realschool.edu",
                              studentSISID: str = "1086#####") -> list[dict]:
        """
        :Description:

        This function generates a sample roster for a Canvas class.
        Generates: Full Name, Student Email, Student SIS ID, Canvas ID

        The full names are generated from names.json as retrieved from `dominictarr/random-name <https://github.com/dominictarr/random-name>`_.
        This file is licensed under MIT.

        :param _numberOfStudents: The number of students to generate.
        :param studentEmailDomain: The school email for all students.
        :param studentSISID: The format for the students SIS_ID. The last 5 digits are used as the Canvas ID.

        :returns: The student roster as a dictionary.
        """

        random.seed(12345)

        with open("names.json", 'r') as namesJson:
            availableNames = json.load(namesJson)

        roster: list[dict] = []

        for i in range(_numberOfStudents):
            student: dict = {}
            studentFirstName: str = ""
            studentLastName: str = random.choice(availableNames['surnames'])

            # If I get an Adam Adams, I will actually cry
            if i % 2 == 0:
                studentFirstName = random.choice(availableNames['female'])
            else:
                studentFirstName = random.choice(availableNames['male'])

            sisSID: str = "".join([str(random.randint(0, 9)) if el == "#" else el for el in studentSISID])
            studentEmail: str = studentFirstName[0].lower() + studentLastName.lower() + "@" + studentEmailDomain

            student['name'] = f"{studentFirstName} {studentLastName}"
            student['email'] = studentEmail
            student["sis_sid"] = sisSID
            student["sis_id"] = studentEmail.split('@')[0]
            student["id"] = sisSID[-5:]

            roster.append(student)

        return roster

    @staticmethod
    def generateStudentSubmissionsForAssignment(_studentRoster: list[dict], _assignmentID: str) -> list[dict]:
        """
        :Description:

        This function generates a canvas submissions with scores assigned to each student

        Relays on ``Factories.AssignmentMaxPoints`` and ``Factories.AssignmentMaxStudentPoints`` for the points that
        will be assigned to students.

        Grade distribution will be assigned on a normal curve, similar to ``Factories.generateStudentGradescopeGradesForAssignment``

        :param _studentRoster: The student roster generated from ``Factories.generateStudentRoster``.
        :param _assignmentID: The assignment ID for the assignment being generated.

        :returns: The list of submissions corresponding to all the students in the roster.
        """

        gradeDist = None

        if Factories.AssignmentMaxStudentPoints is not None:
            # On average students get an 75% - 80% with a standard deviation of 12% - 15%. Using a 75% avg and a 15% sd for this
            gradeDist: stats.truncnorm = generateTruncNorm(mean=Factories.AssignmentMaxStudentPoints * .75,
                                                           sd=Factories.AssignmentMaxStudentPoints * .15,
                                                           lower=0, upper=Factories.AssignmentMaxStudentPoints)

            numpyGenerator = numpy_rand.Generator(numpy_rand.PCG64(12345))
            gradeDist.random_state = numpyGenerator

        submissions: list[dict] = []

        for student in _studentRoster:
            studentSubmission: dict = {}

            studentSubmission['user_id'] = student['id']
            studentSubmission['assignment_id'] = _assignmentID
            if gradeDist is None:
                studentSubmission['score'] = ""

            else:
                studentSubmission['score'] = f"{gradeDist.rvs():.0f}"

            submissions.append(studentSubmission)

        # Reset to base state
        Factories.AssignmentMaxStudentPoints = None

        return submissions

    @staticmethod
    def generateAssignmentGroups(_numberOfGroups: int, canvasAssignmentGroupIDFormat: str = "#####") -> list[dict]:
        """
        :Description:

        This function generates ``_numberOfGroups`` worth of assignment groups.

        :param _numberOfGroups: The number of groups to generate.
        :param canvasAssignmentGroupIDFormat: The format for the groups.
        """
        random.seed(12345)

        assignmentGroups: list[dict] = []

        for i in range(_numberOfGroups):
            assignmentGroup: dict = {}

            assignmentGroup['name'] = f"Assignment Group {i + 1}"
            assignmentGroup['id'] = "".join(
                [str(random.randint(0, 9)) if el == "#" else el for el in canvasAssignmentGroupIDFormat])

            assignmentGroups.append(assignmentGroup)

        return assignmentGroups

    @staticmethod
    def generateAssignments(_numberOfAssignments: int, canvasAssignmentIDFormat: str = "######") -> list[dict]:
        """
        :Description:

        This function generates assignments. Assignments are randomly assigned a name from HW #, Assessment #, and Lab #.
        IDs are also generated for each assignment.

        Relies on ``Factories.AssignmentMaxPoints`` for assignment points.

        .. warning::
            Because of the way that assignment IDs are implemented, if this is called more than once, all the assignments
            will have a duplicate ID. Which is bad. So, during testing, either only use one call of this function
            (ie one call of ``Canvas.getAssignmentsFromCanvas`` or only one assignment group selected in the config)

        :param _numberOfAssignments: The number of assignments to generate.
        :param canvasAssignmentIDFormat: The ID format for the generated assignments.

        :returns: The list of generated assignments.
        """

        if len(Factories.AssignmentMaxPoints) != _numberOfAssignments:
            raise Exception(f"Invalid number of assignments max points. Must have {_numberOfAssignments}.")

        random.seed(12345)

        validAssignmentNames: dict[str, int] = {
            "HW #": 0,
            "Assessment #": 0,
            "Lab #": 0,
        }

        validKeys: list = list(validAssignmentNames.keys())

        assignments: list[dict] = []

        for i in range(_numberOfAssignments):
            assignment: dict = {}

            selectedName: str = random.choice(validKeys)
            validAssignmentNames[selectedName] += 1
            selectedName.replace('#', str(validAssignmentNames[selectedName]))
            assignment['name'] = selectedName
            assignment['id'] = "".join(
                [str(random.randint(0, 9)) if el == "#" else el for el in canvasAssignmentIDFormat])
            assignment['points_possible'] = Factories.AssignmentMaxPoints[i]

            assignments.append(assignment)

        Factories.AssignmentMaxPoints = []

        return assignments

    @staticmethod
    def generateCourses(_numberOfCourses: int, canvasCourseIDFormat: str = "#####") -> list[dict]:
        """
        :Description:

        This function generates courses. Courses will have a random ID and will have the teacher enrollment type.

        :param _numberOfCourses: The number of courses to generate.
        :param canvasCourseIDFormat: The ID format for generated courses.

        :returns: The lists of generated courses.
        """

        random.seed(1234)

        courses: list[dict] = []

        for i in range(_numberOfCourses):
            course: dict = {}

            course['course_code'] = f"Course {i + 1}"
            course['id'] = "".join([str(random.randint(0, 9)) if el == "#" else el for el in canvasCourseIDFormat])
            course['enrollments'] = [{'type': "teacher"}]

            courses.append(course)

        return courses

    @staticmethod
    def generateStudentGradescopeGradesForAssignment(_studentRoster: list[dict], _assignmentName: str,
                                                     _assignmentPoints: int):
        """
        :Description:

        This function generates a gradescope gradesheet for the student roster. It will randomly generate scores, missing assignments, and lateness.

        Calls ``Factories.generateSingleStudentGradescopeGrade`` internally.
        Calls ``Factories.writeOutGradescopeGrades`` internally.

        This data will be written out to  ``./gradescope/{_assignmentName}_test_scores.csv``.

        :param _studentRoster: A student roster generated by ``Factories.generateStudentRoster``.
        :param _assignmentName: The name of the assignment that grades are being generated for.
        :param _assignmentPoints: The max number of points for this assignment
        """

        # seed random for reproducibility
        random.seed(12345)

        # Students submit assignments on average with 80% success
        availableStatus: list[str] = ["Ungraded", "Missing", "Graded"]
        statusSelProb: list[float] = [0.0, 0.2, 0.8]

        # About 5% students submit work late
        studentLate: list[str] = ["Late", "NotLate"]
        studentLateSelProb: list[float] = [.05, .95]

        # On average students get an 75% - 80% with a standard deviation of 12% - 15%.
        #  Using a 75% avg and a 15% sd for this
        gradeDist: stats.truncnorm = generateTruncNorm(mean=_assignmentPoints * .75, sd=_assignmentPoints * .15,
                                                       lower=0, upper=_assignmentPoints)

        # Seed scipy for reproducibility
        numpyGenerator = numpy_rand.Generator(numpy_rand.PCG64(12345))
        gradeDist.random_state = numpyGenerator

        gradeSheet: list[str] = []
        for student in _studentRoster:
            studentStatus: str = random.choices(population=availableStatus, weights=statusSelProb, k=1)[0]

            studentLateness: float | None
            studentScore: float | None
            if studentStatus == "Missing":
                studentLateness = None
                studentScore = None
            elif random.choices(population=studentLate, weights=studentLateSelProb, k=1)[0] == "Late":
                studentLateness = random.uniform(.25, 24.25)
                studentScore = gradeDist.rvs()
            else:
                studentLateness = 0
                studentScore = gradeDist.rvs()

            gradeSheet.append(
                Factories.generateSingleStudentGradescopeGrade(student, studentScore,
                                                               _assignmentPoints, studentStatus, studentLateness))

        Factories.writeOutGradescopeGrades(f"{_assignmentName}_test_scores.csv", gradeSheet)

    @staticmethod
    def generateSingleStudentGradescopeGrade(_studentRosterEntry: dict, _studentScore: float | None,
                                             _assignmentPoints: int, _status: str, _lateness: float | None) -> str:
        """
        :Description:

        Generates an entry for a Gradescope gradesheet for a single student. These are stored as CSVs

        returns in format ``{First Name},{Last Name},{Student ID},{Student Email},{Student Score},{Max Score},{Status},{Lateness}``

        :param _studentRosterEntry: The student to create an entry for. Should be generated by ``Factories.generateStudentRoster``
        :param _studentScore: The score the student received on their submission.
        :param _assignmentPoints: The max number of points for this assignment.
        :param _status: The status for the student's submission. Must be ``Graded``, ``Missing``, or ``Ungraded``.
        :param _lateness: How late the students submission was. Stored in hours. If ``None`` is set then ``_status`` must be ``Missing``

        :returns: A line for a CSV file representing the student's raw grade for this assignment
        """

        if not (_status == "Graded" or _status == "Missing" or _status == "Ungraded"):
            raise Exception(f"Invalid status for Gradescope: {_status}")

        if (_status == "Missing" and _lateness is not None) or (_lateness is None and _status != "Missing"):
            raise Exception(f"Parameter mismatch for Gradescope. Lateness must be \'None\' if status is \'Missing\'")

        formattedLateness: str = ""

        if _lateness is not None:
            seconds: float = _lateness * 60 * 60
            minutes: int = int(seconds // 60)
            seconds -= minutes * 60
            hours: int = int(minutes // 60)
            minutes -= hours * 60
            formattedLateness = f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"

        formattedScore: str = ""
        if _studentScore is not None:
            formattedScore = f"{_studentScore:.0f}"

        formattedEntry: str = ""

        # add all the information about the student
        # add first name
        formattedEntry += f"{_studentRosterEntry['name'].split(' ')[0]},"
        # add last name
        formattedEntry += f"{_studentRosterEntry['name'].split(' ')[1]},"
        formattedEntry += f"{_studentRosterEntry['sis_sid']},"
        formattedEntry += f"{_studentRosterEntry['email']},"

        # add submission info
        formattedEntry += f"{formattedScore},"
        formattedEntry += f"{_assignmentPoints},"
        formattedEntry += f"{_status},"
        formattedEntry += f"{formattedLateness}"

        return formattedEntry

    @staticmethod
    def writeOutGradescopeGrades(_fileName: str, _gradeSheet: list[str]):
        """
        :Description:

        This function writes out the gradescope gradesheet to ``gradescope/{_fileName}``.

        It also injects the correct header for a gradescope gradesheet.

        :param _fileName: The file name to write to.
        :param _gradeSheet: The gradesheet to write.
        """

        if not os.path.exists("./gradescope") or not os.path.isdir("./gradescope"):
            os.makedirs("./gradescope")
            os.makedirs("./gradescope/graded")

        pathToFile: str = f"./gradescope/{_fileName}".replace(" ", "_")
        gradesheetWriter = open(pathToFile, "w+")

        header: str = "First Name,Last Name,SID,Email,Total Score,Max Points,Status,Lateness (H:M:S)"
        gradesheetWriter.write(f"{header}\n")

        for line in _gradeSheet:
            if line.count(',') != header.count(','):
                raise Exception("Invalid CSV Row for Gradescope Gradesheet")
            gradesheetWriter.write(f"{line}\n")

        gradesheetWriter.close()

    @staticmethod
    def generateStudentRunestoneGradesForAssignment(_studentRoster: list[dict], _assignmentName: str,
                                                     _assignmentPoints: int):
        """
        :Description:

        This function generates a runestone gradesheet for the student roster. It will randomly generate scores.

        Calls ``Factories.writeRunestoneGrades`` internally.

        This data will be written out to  ``./runestone/{_assignmentName}_test_scores.csv``.

        :param _studentRoster: A student roster generated by ``Factories.generateStudentRoster``.
        :param _assignmentName: The name of the assignment that grades are being generated for.
        :param _assignmentPoints: The max number of points for this assignment
        """

        # On average students get an 75% - 80% with a standard deviation of 12% - 15%.
        #  Using a 75% avg and a 15% sd for this
        gradeDist: stats.truncnorm = generateTruncNorm(mean=_assignmentPoints * .75, sd=_assignmentPoints * .15,
                                                       lower=0, upper=_assignmentPoints)

        # Seed scipy for reproducibility
        numpyGenerator = numpy_rand.Generator(numpy_rand.PCG64(12345))
        gradeDist.random_state = numpyGenerator
        gradeSheet = []

        # three lines that are in the runestone format parser
        gradeSheet.append("0, 0")
        gradeSheet.append("0, 3") # total points
        gradeSheet.append("0, 0")
        for student in _studentRoster:
            studentScore = gradeDist.rvs()
            gradeSheet.append(f"{student['email']},{round(studentScore,2) * 10}%")

        Factories.writeOutRunestoneGrades(f"{_assignmentName}_test_scores.csv", gradeSheet, _assignmentName)

    @staticmethod
    def writeOutRunestoneGrades(_fileName: str, _gradeSheet: list[str], assignmentName: str):
        """
        :Description:

        This function writes out the runestone gradesheet to ``runestone/{_fileName}``.

        It also injects the correct header for a runestone gradesheet.

        :param _fileName: The file name to write to.
        :param _gradeSheet: The gradesheet to write.
        :param assignmentName: The name of the assignment to generate
        """

        if not os.path.exists("./runestone") or not os.path.isdir("./runestone"):
            os.makedirs("./runestone")
            os.makedirs("./runestone/graded")

        pathToFile: str = f"./runestone/{_fileName}".replace(" ", "_")
        gradesheetWriter = open(pathToFile, "w+")

        header: str = "E-mail," + assignmentName
        gradesheetWriter.write(f"{header}\n")

        for line in _gradeSheet:
            if line.count(',') != header.count(','):
                raise Exception("Invalid CSV Row for Runestone Gradesheet")
            gradesheetWriter.write(f"{line}\n")

        gradesheetWriter.close()
