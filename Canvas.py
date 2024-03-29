import warnings

import pandas as pd
import requests


class Canvas:
    """
    :Description:

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
        self.m_statusAssignments: pd.DataFrame = pd.DataFrame()
        self.m_statusAssignmentsScores: pd.DataFrame = pd.DataFrame()
        self.m_assignmentsToGrade: (pd.DataFrame, None) = None

    def __validate__(self):
        """
        :Description:

        This function checks to see if we have everything we need to make api calls to canvas.

        :returns: True if everything is defined correctly and *looks* like it should work, false if not
        """
        if not self.API_KEY:
            print("api key is invalid")
            return False
        if not self.USER_ID or not (self.USER_ID.isdigit() or self.USER_ID == "self"):
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
        :Description:

        This function retrieves data from canvas, accounting for how canvas will split data into pages of ten
        objects to minimise the cost of each request. (So our 100mb pull of assignments is split into smaller chunks)
        Returns a list of dictionaries. This also is only used for *GET* requests

        :param _url: the endpoint to query
        :param _headers: the headers to send with each request - typically only has the api key
        :param flags: Any extra flags to pass to Canvas. Completely optional.

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
    def __postRequest__(_url, _headers, _data) -> dict[any, any]:
        """
        :Description:

        This function makes a post request to the server.
        This function returns a URL to get the success-ness of the request as
        canvas post requests are async and the server responds with a URL to see what the status of
        the request is. Getting that data is anonymous, and as such, does not require an auth token to get.
        This function does **not** currently support paginated responses as most returns with post requests are small
        and our usage only gets status responses back indicating if we have a successful request or not

        :param _url: the endpoint to send the request to
        :param _headers: the headers to send (like the authorization token)
        :param _data: the data to send with the post request. Is passed as a -D in curl. Currently, only form data is
        supported as that it what canvas uses.

        :return: The URL of the status OR the response from the server.
        """
        result = requests.post(_url, headers=_headers, data=_data)
        if result.status_code != 200:
            print(f"An error occurred while making request. HTTP code is {result.status_code}")
            return {}

        return result.json()

    @staticmethod
    def __getCommonName__(_assignmentName: str) -> str:
        """
        :Description:

        This function gets the common name from the assignment in canvas.
        I am defining the common name as the shorthand abbreviation for the assignment,
        so HW 1 would read as HW1, Lab 14 would read as L14.
        Also supports the 102 OL way of doing lab names IE Python Assessment 1B = PA1B
        If this function can't derive a common name it returns UKN + the current unknown counter.
        UKN stands for UnKowN.

        :param _assignmentName: the canvas assignment name

        :return: the common format name
        """
        commonNameNumbers: str = "".join([ch for ch in _assignmentName if str(ch).isdigit()])
        commonNameLabLetter: str = ""
        # Find the lab letter for cases like L1B or Python Assessment 1B - there might be a better way to do this
        for i in range(1, len(_assignmentName)):
            if str.isdigit(_assignmentName[i - 1]) and _assignmentName[i] != " " and str.isupper(_assignmentName[i]):
                commonNameLabLetter = _assignmentName[i]
                break

        commonName = ""
        for ch in _assignmentName:
            if str.isupper(ch):
                commonName += ch
            if str.isdigit(ch):
                commonName += commonNameNumbers
                commonName += commonNameLabLetter
                break
            if len(commonName) >= 4:
                break

        if not commonName:
            Canvas.s_unknownAssignments += 1
            commonName = "UKN" + str(Canvas.s_unknownAssignments)

        return commonName

    def loadSettings(self, _configFile):
        """
        :Description:

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
        :Description:

        This function reads in the assignments from the config file and updates the internal members.
        First it validates that there is at least one assignment.

        :param _configFile: the config file containing the assignments to be loaded
        """
        if type(_configFile) is not dict:
            raise TypeError("Invalid config file")
        if not _configFile["assignments"] or len(_configFile["assignments"]) == 0:
            print("No assignments found")
            return None

        if 'status_assignments' not in _configFile.keys() or \
                not _configFile['status_assignments'] or len(_configFile["assignments"]) == 0:
            print("No status assignments found")

        else:
            self.m_statusAssignments = \
                pd.DataFrame(_configFile['status_assignments']) if _configFile['status_assignments'] else pd.DataFrame()

            print(f"Loaded {len(self.m_statusAssignments)} status assignments")

        self.m_assignments = pd.DataFrame(_configFile["assignments"])
        print(f"Loaded {len(self.m_assignments)} assignments")

    def getAssignmentGroupsFromCanvas(self):
        """
        :Description:

        This function gets the assignment groups from canvas, then formats them such that we only have the
        group name and the group id.
        This allows us to not have to pull all 118 assignments from canvas when we will only need a few and know the groups.

        :Example:

        Pulled from CSCI 101 SPR22

        .. code-block:: json

            {
            'Quizzes (6%)': 56566,
            'Gradescope': 55687,
            'Python Labs (6%)': 56567,
            ...
            }

        the first col is the group name and the second col is the canvas id

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

    def getAssignmentsFromCanvas(self, _assignmentGroups) -> list:
        """
        :Description:

        This function pulls assignments from canvas that it finds in the groups passed as parameters. It strips out
        the unnecessary fields provided by the canvas api.
        :Example:

        .. code-block:: json

            {
                common_name: "HW8",
                name: "HW8 - Hardware and Software',
                id: "56383",
                points: 6.0
            },

        :param _assignmentGroups: The list of ids of the desired groups to pull from.

        :return: formatted assignments
        """
        # /api/v1/courses/:course_id/assignments - gets list of assignments in a course
        # /api/v1/courses/:course_id/assignment_groups/:assignment_group_id/assignments
        #  - gets list of assignments in a group

        if not self.__validate__():
            return []

        if type(_assignmentGroups) is not list:
            raise TypeError("Assignment groups must be a list")

        header = {"Authorization": f"Bearer {self.API_KEY}"}

        canvasAssignments: list = []
        for assignmentGroup in _assignmentGroups:
            url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/assignment_groups/{assignmentGroup}/assignments"
            canvasAssignments.extend(self.__getPaginatedResponse__(url, header))

        print(f"Returned {len(canvasAssignments)} assignments")
        parsedAssignments: list = []
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
        :Description:

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

        print("Downloading updated Canvas roster....")
        print("\t(This may take a few minutes depending on the enrollment size of the course)")

        result = self.__getPaginatedResponse__(url, header, flags=flags)

        print(f"\tDownloaded {len(result)} students")

        studentList: list[dict] = []
        print("\tProcessing students...", end='')
        invalidStudents: int = 0
        for student in result:
            if 'email' not in student or 'name' not in student or 'id' not in student:
                invalidStudents += 1
                continue
            parsedStudent = dict()
            parsedStudent['name'] = student['name']
            parsedStudent['id'] = student['id']
            # Despite this sis_id - it actually is the CWID.
            # Thanks mines for phasing out multipass
            parsedStudent['sis_id'] = student['sis_user_id']
            # parsedStudent['sis_id'] = student['email'].split('@')[0]
            studentList.append(parsedStudent)

        if invalidStudents != 0:
            print("Warning")
            print(f"\t\t{invalidStudents} students were invalid")
        else:
            print("Done")
        # dataframes are a lot easier to work with
        self.m_students = pd.DataFrame(studentList)
        print("...Done")

    def updateStatusAssignmentScores(self):
        """
        :Description:

        This function pulls the scores for all the status assignments found in the config file. Stores the current
        scores in a dataframe internally
        """
        if not self.__validate__():
            return

        if self.m_statusAssignments.empty:
            print("Unable to fetch status assignments: No status assignments found")
            return

        if self.m_students.empty:
            print("Unable to fetch status assignments: No students found")
            return
        # /api/v1/courses/:course/assignments/:assignmentid/submissions

        header = {"Authorization": f"Bearer {self.API_KEY}"}
        flags = "per_page=100"
        print(f"Updating {len(self.m_statusAssignments)} status assignments...")

        self.m_statusAssignmentsScores['multipass'] = ""
        self.m_statusAssignmentsScores['student_score'] = 0.0
        self.m_statusAssignmentsScores['status_assignment_id'] = 0

        for assignment in self.m_statusAssignments['id'].values:
            assignmentName = self.m_statusAssignments.loc[self.m_statusAssignments['id'] == assignment, 'name'].values
            print(f"\tUpdating {assignmentName[0]} for {len(self.m_students)} students...", end='')

            url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/assignments/{assignment}/submissions"

            res = self.__getPaginatedResponse__(url, header, flags=flags)
            invalidScoreCounter = 0

            for score in res:
                if 'user_id' not in score.keys() or 'score' not in score.keys() or 'assignment_id' not in score.keys():
                    invalidScoreCounter += 1
                    continue

                if score['assignment_id'] != assignment:
                    invalidScoreCounter += 1
                    continue
                studentMultipass = self.m_students.loc[self.m_students['id'] == score['user_id'], 'sis_id']

                # When we pull scores, we also pull scores for students who dropped, and virtual students
                #  like the test student. So in this case, those are expected invalid students, so don't increment
                #  the counter
                if len(studentMultipass) == 0:
                    # invalidScoreCounter += 1
                    continue

                self.m_statusAssignmentsScores = \
                    pd.concat([self.m_statusAssignmentsScores, pd.DataFrame({
                                'multipass': str(studentMultipass.values[0]),
                                'student_score': float(score['score']),
                                'status_assignment_id': int(assignment)}, index=[0])],
                              ignore_index=True)

            if invalidScoreCounter != 0:
                print("Warning")
                print(f"\t\t{invalidScoreCounter} invalid scores were downloaded")
                continue
            print("Done")

    def getCourseList(self):
        """
        :Description:

        Retrieves the list of courses from canvas that the user in enrolled in, then filters out the student ones
        to ensure that they will have write access.

        :return: The list of courses with the course ID, name, and enrollment type
        """
        # we are getting the list of course IDs here, so we don't need to do a full validation
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

    def postAssignment(self, _assignment: str, _batchedAssignment: list[str]) -> bool:
        """
        :Description:

        This function post assignments to Canvas in batches of at most 50. It waits for a response from the
        api and validates to check if the posting was successful or not.

        :param _assignment: the assigment *ID* to be posted. Must be the ID and *NOT* the name
        :param _batchedAssignment: the list of assignments

        :return: True on a success False on a failure
        """
        # POST /v1/courses/{course_id}/assignments/{assignment_id}/submissions/update_grades
        # payload = f"grade_data[25685][posted_grade]=6.0&grade_data[25685][text_comment]=Nice Work!&" \
        # f"grade_data[30691][posted_grade]=0.0&grade_data[30691][text_comment]=No Submission&"

        url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/assignments/{_assignment}/submissions/update_grades"
        header = {"Authorization": f"Bearer {self.API_KEY}"}

        responses: list[dict[any, any]] = []
        for i, batch in enumerate(_batchedAssignment):
            print(f"\t\tPosting batch {i + 1} / {len(_batchedAssignment)}...", end='')
            responses.append(self.__postRequest__(url, header, batch))
            if len(responses[i]) == 0:
                print(f"Failed\n\tPosting failed on batch {i + 1} / {len(_batchedAssignment)}")
                return False
            print("Pending")
            # TODO validate the response

        return True

    def getAssignmentIDsFromCommonName(self, _assignmentList: list[str]) -> dict[str, str]:
        """
        :Description:

        This function takes in the assignment common names and generates a map of the assignment common name to its ID.
        This is to make the user interface slightly simpler for the user.

        .. deprecated:: 1.0.0
            Do not use this. Use the `assignmentToGrade` workflow instead. For an example, look at `UI.standardGrading`.
            Deprecated as part of improving assignment handling internally. See `#13 <https://github.com/TriHardStudios/101GradingScript/issues/13>`_ and `#6 <https://github.com/TriHardStudios/101GradingScript/issues/6>`_

        :param _assignmentList: A list of assignment common names.
        :return: a map mapping the assignment common names to the assignment ids.
        """

        warnings.warn(
            "Canvas.getAssignmentIDsFromCommonName is deprecated. Use the assignmentToGrade workflow instead.",
            FutureWarning,
        )
        assignmentMap: dict[str, str] = {}
        for commonName in _assignmentList:
            assignmentMap[commonName] = str(self.getAssignmentFromCommonName(commonName)['id'].values[0])

        return assignmentMap

    def getAssignmentFromID(self, _id: int) -> pd.DataFrame:
        """
        :Description:

        Maps the id to a canvas assignment in the main assignment list.

        :param _id: the id to parse

        :return: a dataframe containing the id or an empty dataframe if it was not found.
        """
        if type(_id) is not int:
            try:
                _id = int(_id)
            except ValueError:
                raise AttributeError("Unable to to parse assignment ID")

        return self.m_assignments.loc[self.m_assignments['id'] == _id]

    def getAssignmentFromCommonName(self, _assignment: str) -> (pd.DataFrame, None):
        """
        :Description:


        :param _assignment:
        :return:
        """

        filteredAssignments: pd.DataFrame = self.m_assignments.loc[self.m_assignments['common_name'] == _assignment]
        # Validate assignments and correctly map assignment.
        if len(filteredAssignments) > 1:
            print(f"Many assignments matching {_assignment} found. Please enter the id the correct one")

            for i, assignment in filteredAssignments.iterrows():
                print(f"{assignment['id']}\t{assignment['name']}\t{assignment['points']}")
            correctID = int(input("(id: 123456): "))

            return filteredAssignments.loc[filteredAssignments['id'] == correctID]

        elif len(filteredAssignments) == 0:
            print(f"Unable to map assignment automatically. {_assignment} is unknown.")
            # todo add support to manually enter assignment details
            print("Assignment is being ignored.")
            return None

        return filteredAssignments

    def validateAssignment(self, commonName: (str, None) = None, canvasID: (int, None) = None) -> bool:
        """
        :Description:

        :param commonName:
        :param canvasID:
        :return:
        """
        if commonName is not None:
            return len(self.m_assignments.loc[self.m_assignments['common_name'] == commonName]) > 0
        if canvasID is not None:
            return len(self.m_assignments.loc[self.m_assignments['id'] == canvasID]) > 0

        return False

    def selectAssignmentsToGrade(self, _assignments: list[str]):
        """
        :Description:

        This function maps the common name of the assignment to the actual assignment - this will help clean up a lot of
        the logic and make the rest of the program a lot more consistent with the way that it handles them

        :param _assignments: the list of assignment common names.
        """

        if type(_assignments) is not list or not _assignments:
            raise AttributeError("Unable to parse _assignments. Must be a list of strings.")
        if self.m_assignmentsToGrade is None:
            self.m_assignmentsToGrade = pd.DataFrame()

        for assignment in _assignments:
            mappedAssignment: (pd.DataFrame, None) = self.getAssignmentFromCommonName(assignment)
            if mappedAssignment is None:
                continue
            self.m_assignmentsToGrade = pd.concat([self.m_assignmentsToGrade, mappedAssignment], axis=0, join='outer')

    def getStudents(self):
        return self.m_students

    def getAssignments(self):
        return self.m_assignments

    def getAssignmentsToGrade(self):
        return self.m_assignmentsToGrade

    def getStatusAssignments(self):
        return self.m_statusAssignments

    def getStatusAssignmentScores(self):
        return self.m_statusAssignmentsScores
