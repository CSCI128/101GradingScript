import pandas as pd
import requests


class Canvas:
    """
    This class helps us interface directly with canvas and abstracts some weirdness away
    Importantly - this class supports paginated responses and handles them elegantly -
    regardless of the size of the response
    """
    s_unknownAssignments: int = 0

    def __init__(self, _API_KEY="", _USER_ID="", _COURSE_ID="", _ENDPOINT=""):
        self.API_KEY: str = _API_KEY
        self.USER_ID: str = _USER_ID
        self.COURSE_ID: str = _COURSE_ID
        self.ENDPOINT: str = _ENDPOINT
        self.m_students: pd.DataFrame = pd.DataFrame()
        self.m_assignments: pd.DataFrame = pd.DataFrame()

    def __validate__(self):
        """
        This function checks to see if we have everything we need to make API calls to canvas.
        RETURNS:
            False - if something is invalid
            True - if everything is defined correctly and *looks* like it should work
        """
        if not self.API_KEY:
            print("API key is invalid")
            return False
        if not self.USER_ID or not self.USER_ID.isdigit():
            print("User ID is invalid")
            return False
        if not self.COURSE_ID or not self.COURSE_ID.isdigit():
            print("Course ID is invalid")
            return False
        if not self.ENDPOINT or "https://" not in self.ENDPOINT:
            print("Endpoint is invalid")
            return False
        return True

    @staticmethod
    def __getPaginatedResponse__(_url: str, _headers: str, flags: str = "") -> list[dict[any, any]]:
        """
        This function retrieves data from canvas, accounting for how canvas will split data into pages of ten
        objects to minimise the cost of each request. (So our 100mb pull of assignments is split into smaller chunks)
        Returns a list of dictionaries. This also is only used for *GET* requests

        :param _url: the endpoint to query
        :param _headers: the headers to send with each request - typically only has the API key
        :return: the full response - merged in to a list of dicts
        """
        _url += f"?{flags}"
        result = requests.get(_url, headers=_headers)

        if result.status_code != 200:
            print(f"An error occurred. HTML code {result.status_code}")
            return []

        results = []
        pageResponse = result.json()

        for pResponse in pageResponse:
            results.append(pResponse)

        while 'last' not in result.links or result.links['current']['url'] != result.links['last']['url']:
            result = requests.get(result.links['next']['url'], headers=_headers)

            if result.status_code != 200:
                print(f"An error occurred. HTML code {result.status_code}")
                return []

            pageResponse = result.json()

            for pResponse in pageResponse:
                results.append(pResponse)

        return results

    @staticmethod
    def __postRequest__(_url, _headers, _data):
        pass

    @staticmethod
    def __getCommonName__(_assignmentName: str) -> str:
        """
        This function gets the common name from the assignment in canvas.
        I am defining the common name as the shorthand abbreviation for the assignment,
        so HW 1 would read as HW1, Lab 14 would read as L14.
        If this function can't derive a common name it returns UKN + the current unknown counter.
        UKN stands for UnKowN - clever, right?

        :param _assignmentName: the canvas assignment name
        :return: the common format name
        """
        commonNameNumbers: str = "".join([ch for ch in _assignmentName if str(ch).isdigit()])
        commonName = ""

        for ch in _assignmentName:
            if str.isupper(ch):
                commonName += ch
            if str.isdigit(ch):
                commonName += commonNameNumbers
                break
            if len(commonName) >= 4:
                break

        if not commonName:
            Canvas.s_unknownAssignments += 1
            commonName = "UKN" + str(Canvas.s_unknownAssignments)

        return commonName

    def loadSettings(self, _configFile):
        """
        This function gets the config file as a dict, validates it, then updates the internal members.

        :param _configFile: The config file we are using
        """
        if type(_configFile) is not dict:
            raise TypeError("Invalid config file")

        if not _configFile['course_id'] \
                or not _configFile['API_key'] \
                or not _configFile['user_id'] \
                or not _configFile['endpoint']:
            print("Invalid config file")
            return

        self.API_KEY = _configFile['API_key']
        self.USER_ID = _configFile['user_id']
        self.COURSE_ID = _configFile['course_id']
        self.ENDPOINT = _configFile['endpoint']

        if self.__validate__():
            print(f"Loaded class: {_configFile['class']}")

    def getAssignmentsFromConfig(self, _configFile):
        """
        This function reads in the assignments from the config file and updates the internal members.
        First it validates that there is at least one assignment.
        :param _configFile: the config file containing the assignments to be loaded
        """
        if type(_configFile) is not dict:
            raise TypeError("Invalid config file")
        if not _configFile["assignments"] or len(_configFile["assignments"]) == 0:
            print("No assignments found")
            return None

        self.m_assignments = pd.DataFrame(_configFile["assignments"])
        print(f"Loaded {len(self.m_assignments)} assignments")

    def getAssignmentGroupsFromCanvas(self):
        """
        This function gets the assignment groups from canvas, then formats them such that we only have the
        group name and the group id.
        This allows us to not have to pull all 118 assignments from canvas when we will only need a few and know the groups.
        :example:
            Pull from CSCI 101 SPR22
            {
            'Quizzes (6%)': 56566,
            'Gradescope': 55687,
            'Python Labs (6%)': 56567,
            ...
            }
            where the first col is the group name and the second col is the canvas id
        :return: the formatted assignment groups
        """
        # /api/v1/courses/:course_id/assignment_groups - gets all assignment groups
        if not self.__validate__():
            return None

        url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/assignment_groups"
        header = {"Authorization": f"Bearer {self.API_KEY}"}
        result = self.__getPaginatedResponse__(url, header)

        print(f"Retrieved {len(result)} assignment groups")

        assignmentGroups = dict()

        for assignmentGroup in result:
            assignmentGroups[assignmentGroup['name']] = assignmentGroup['id']

        return assignmentGroups

    def getAssignmentsFromCanvas(self, _assignmentGroups):
        """
        This function pulls assignments from canvas that it finds in the groups passed as parameters. It strips out
        the unnecessary fields provided by the canvas api.
        :example:
            {
                common_name: "HW8",
                name: "HW8 - Hardware and Software',
                id: "56383",
                points: 6.0
            },
            ...
        :param _assignmentGroups: The list of ids of the desired groups to pull from.
        :return: formatted assignments
        """
        # /api/v1/courses/:course_id/assignments - gets list of assignments in a course
        # /api/v1/courses/:course_id/assignment_groups/:assignment_group_id/assignments
        #  - gets list of assignments in a group

        if not self.__validate__():
            return None

        if type(_assignmentGroups) is not list:
            raise TypeError("Assignment groups must be a list")

        header = {"Authorization": f"Bearer {self.API_KEY}"}

        canvasAssignments = []
        for assignmentGroup in _assignmentGroups:
            url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/assignment_groups/{assignmentGroup}/assignments"
            canvasAssignments.extend(self.__getPaginatedResponse__(url, header))

        print(f"Returned {len(canvasAssignments)} assignments")
        parsedAssignments = []
        for assignment in canvasAssignments:
            newAssignment = dict()
            newAssignment['common_name'] = self.__getCommonName__(assignment['name'])
            newAssignment['name'] = assignment['name']
            newAssignment['id'] = assignment['id']
            newAssignment['points'] = assignment['points_possible']
            parsedAssignments.append(newAssignment)

        return parsedAssignments

    def getStudentsFromCanvas(self):
        """
        This function gets a list of users from canvas, filtering out the non-students. This will allow us to post
        grades for students without needed to download the entire gradebook. Because the list of students changes
        frequently as they add and drop classes, this is pulled before grades are posted every run. This will update
        the student list internally.
        """
        # /api/v1/courses/:course_id/users - get users for a course
        url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/users"
        header = {"Authorization": f"Bearer {self.API_KEY}"}
        # These flags increase the query size to 100 students and filters out all non students
        flags = "per_page=100&&enrollment_type[]=student"

        print("Downloading updated Canvas roaster....")
        print("\t(This may take a few minutes depending on the enrollment size of the course)")

        result = self.__getPaginatedResponse__(url, header, flags=flags)

        print(f"\tDownloaded {len(result)} students")

        studentList: list[dict] = []
        # So when the registrar adds students to a class, we don't have their CWID or multipass
        #  Naturally, this isn't documented anywhere so through trial and error i found the fields that will always
        #  be included when we pull the students.
        print("\tProcessing students...", end='')
        invalidStudents: int = 0
        for student in result:
            if 'email' not in student or 'name' not in student or 'id' not in student:
                invalidStudents += 1
                continue
            parsedStudent = dict()
            parsedStudent['name'] = student['name']
            parsedStudent['id'] = student['id']
            parsedStudent['sis_id'] = student['email'].split('@')[0]
            studentList.append(parsedStudent)

        if invalidStudents != 0:
            print("Warning")
            print(f"\t\t{invalidStudents} students were invalid")
        else:
            print("Done")
        # dataframes are a lot easier to work with
        self.m_students = pd.DataFrame(studentList)
        print("...Done")

    def getCourseList(self):
        """
        Retrieves the list of courses from canvas that the user in enrolled in, then filters out the student ones
        to ensure that they will have write access.
        :return: The list of courses with the course ID, name, and enrollment type
        """
        # we are getting the list of course IDs here so we dont need to do a full validation
        # api/v1/users/:userid/courses
        if not self.API_KEY or not self.USER_ID:
            return None

        url = f"{self.ENDPOINT}/api/v1/users/{self.USER_ID}/courses"
        header = {"Authorization": f"Bearer {self.API_KEY}"}

        result = self.__getPaginatedResponse__(url, header)

        validEnrollments = ['ta', 'teacher']
        validCourses = []

        for course in result:
            if len(course) == 2:  # if there is an error message it will only be two units long
                # this error condition, in my experience, only comes up when a teacher deletes a course
                continue

            # filter out all student courses - we only want the ta / teacher courses
            if course['enrollments'][0]['type'] not in validEnrollments:
                continue

            parsedCourseData = dict()
            parsedCourseData['name'] = course['course_code']  # this includes the semester as set by the registrar
            parsedCourseData['id'] = course['id']
            parsedCourseData['enrollment_type'] = course['enrollments'][0]['type']
            validCourses.append(parsedCourseData)

        print(f"Retrieved {len(validCourses)} valid courses")

        return validCourses

    def postAssignment(self, _assignment: str, _batchedAssignment: list[str]):
        # POST /api/v1/sections/:section_id/assignments/:assignment_id/submissions/update_grades
        # payload = f"grade_data[25685][posted_grade]=6.0&grade_data[25685][text_comment]=Nice Work!&" \
        # f"grade_data[30691][posted_grade]=0.0&grade_data[30691][text_comment]=No Submission&"
        pass

    def getAssignmentIDsFromCommonName(self, _assignmentList: list[str]):
        """
        This function takes in the assignment common names and generates a map of the assignment common name to its ID.
        This is to make the user interface slightly simpler for the user
        :param _assignmentList:
        :return:
        """
        assignmentMap: dict[str, str] = {}
        for commonName in _assignmentList:
            filteredAssignments: pd.DataFrame = self.m_assignments.loc[self.m_assignments['common_name'] == commonName]
            if len(filteredAssignments) > 1:
                print(f"Many assignments matching {commonName} found. Please enter the id the correct one")
                for i, assignment in filteredAssignments.iterrows():
                    print(f"{assignment['id']}\t{assignment['name']}\t{assignment['points']}")
                correctID = str(input("(id: 123456): "))
                assignmentMap[commonName] = correctID
                continue

            assignmentMap[commonName] = str(filteredAssignments['id'].values[0])

        return assignmentMap

    def getStudents(self):
        return self.m_students
