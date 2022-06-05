import requests
import json
import pandas as pd


class Canvas:

    def __init__(self, _API_KEY="", _USER_ID="", _COURSE_ID="", _ENDPOINT=""):
        self.API_KEY = _API_KEY
        self.USER_ID = _USER_ID
        self.COURSE_ID = _COURSE_ID
        self.ENDPOINT = _ENDPOINT
        self.m_students = []
        self.m_assignments = []

    '''
    This function checks to see if we have everything we need to make API calls to canvas.
    RETURNS:
        False - if something is invalid
        True - if everything is defined correctly and *looks* like it should work
    '''

    def __validate__(self):
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

    '''
    This function retrieves data from canvas, accounting for how canvas will split data into pages of ten
    objects to minimise the cost of each request. (So our 100mb pull of assignments is split into smaller chunks)
    Returns a list of dictionaries. This also is only used for *GET* requests 
    PARAMS:
        _url - the endpoint to query
        _headers - the headers to send with each request - typically only has the API key
    '''

    @staticmethod
    def __getPaginatedResponse__(_url, _headers, flags=""):
        _url += f"?{flags}"
        result = requests.get(_url, headers=_headers)

        if result.status_code != 200:
            print(f"An error occurred. HTML code {result.status_code}")
            return

        results = []
        pageResponse = result.json()

        for pResponse in pageResponse:
            results.append(pResponse)

        while result.links['current']['url'] != result.links['last']['url']:
            result = requests.get(result.links['next']['url'], headers=_headers)
            pageResponse = result.json()

            for pResponse in pageResponse:
                results.append(pResponse)

        return results

    '''
    This function gets the common name from the assignment in canvas.
    I am defining the common name as the short hand abbreviation for the assignment, so like
    for Homework 7 - it should be HW7 but currently this is a quick and dirty implementation so it would read this as 
    H7.
    This is a problem bc if we have Homework 14 and Homework 1 they would both be H1 which isn't right. 
    PARAMS:
        _assignmentName - the canvas assignment name 
    '''

    @staticmethod
    def __getCommonName__(_assignmentName):
        commonName = ""

        for ch in _assignmentName:
            if str.isupper(ch):
                commonName += ch
            if str.isdigit(ch):
                commonName += ch
                break
            if len(commonName) > 4:
                break

        return commonName

    def loadSettings(self, _configFile):
        if type(_configFile) is not dict:
            raise TypeError("Invalid config file")

        # if not _configFile["assignments"] or len(_configFile["assignments"]) == 0:
        #     print("No assignments found")
        #     return
        if not _configFile['course_id'] or not _configFile['API_key'] or not _configFile['user_id'] or not _configFile[
            'endpoint']:
            print("Invalid config file")
            return

        self.API_KEY = _configFile['API_key']
        self.USER_ID = _configFile['user_id']
        self.COURSE_ID = _configFile['course_id']
        self.ENDPOINT = _configFile['endpoint']

        if self.__validate__():
            print(f"Loaded class: {_configFile['class']}")

    '''
    This function gets the assignment groups from canvas, then formats them such that we only have the 
    group name and the group id.
    This allows us to not have to pull all 118 assignments from canvas when we will only need a few and know the groups.
    EXAMPLE:
        Pull from CSCI 101 SPR22
        {
        'Quizzes (6%)': 56566, 
        'Gradescope': 55687, 
        'Python Labs (6%)': 56567,
        ...
        }
        where the first col is the group name and the second col is the canvas id
    '''

    def getAssignmentGroupsFromCanvas(self):
        # /api/v1/courses/:course_id/assignment_groups - gets all assignment groups
        if not self.__validate__():
            return None

        url = f"{self.ENDPOINT}/api/v1/courses/{self.COURSE_ID}/assignment_groups"
        header = {"Authorization": f"Bearer {self.API_KEY}"}
        result = self.__getPaginatedResponse__(url, header)

        print(f"Returned {len(result)} assignment groups")

        assignmentGroups = dict()

        for assignmentGroup in result:
            assignmentGroups[assignmentGroup['name']] = assignmentGroup['id']

        return assignmentGroups

    def getAssignmentsFromCanvas(self, _assignmentGroups):
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

    def getAssignmentsFromConfig(self, _configFile):
        if type(_configFile) is not dict:
            raise TypeError("Invalid config file")
        if not _configFile["assignments"] or len(_configFile["assignments"]) == 0:
            print("No assignments found")
            return None

        self.m_assignments = _configFile["assignments"]
        print(f"Loaded {len(self.m_assignments)} assignments")

    def getStudents(self):
        # /api/v1/courses/:course_id/users - get users for a course
        pass

    def getCourseList(self):
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
            if len(course) == 2:  # if there is an error message it will only be two long
                continue

            # filter out all student courses
            if course['enrollments'][0]['type'] not in validEnrollments:
                continue

            parsedCourseData = dict()
            parsedCourseData['name'] = course['course_code']  # this includes the semester as set by the registrar
            parsedCourseData['id'] = course['id']
            parsedCourseData['enrollment_type'] = course['enrollments'][0]['type']
            validCourses.append(parsedCourseData)

        print(f"Found {len(validCourses)} valid courses")

        return validCourses



    def postAssignments(self):
        pass
