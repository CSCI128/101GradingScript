from Factories import Factories
import re


class MockResponse:
    def __init__(self, _jsonData, _statusCode):
        self.json_data = _jsonData
        self.status_code = _statusCode
        self.links = {
            'current': {
                'url': "last"
            },
            'last': {
                'url': "last"
            }

        }

    def json(self):
        return self.json_data


def mock_requestsGet(*args, **kwargs) -> MockResponse:
    # /api/v1/courses/:course_id/assignment_groups
    if re.match(r"https://(\w+\.?)+\.\w{3}/api/v[0-9]/courses/[0-9]{5}/assignment_groups", args[0]) is not None:
        # For safety, only returning one assignment group. See warning for Factories.generateAssignments
        return MockResponse(Factories.generateAssignmentGroups(1), 200)

    # /api/v1/courses/:course_id/assignment_groups/:assignment_group_id/assignments
    if re.match(r"https://(\w+\.?)+\.\w{3}/api/v[0-9]/courses/[0-9]{5}/assignment_groups/[0-9]{5}/assignments",
                args[0]) is not None:
        return MockResponse(Factories.generateAssignments(10), 200)

    # /api/v1/courses/:course_id/users for students only
    if re.match(r"https://(\w+\.?)+\.\w{3}/api/v[0-9]/courses/[0-9]{5}/users\?.*&&enrollment_type\[]=student",
                args[0]) is not None:
        return MockResponse(Factories.generateStudentRoster(550), 200)

    # /api/v1/courses/:course/assignments/:assignmentid/submissions
    if re.match(r"https://(\w+\.?)+\.\w{3}/api/v[0-9]/courses/[0-9]{5}/assignments/[0-9]{6}/submissions",
                args[0]) is not None:
        startingIndex: int = args[0].index("/assignments/") + len("/assignments/")
        assignmentID: str = args[0][startingIndex: startingIndex + 6]

        return MockResponse(Factories.generateStudentSubmissionsForAssignment(
            Factories.generateStudentRoster(550), assignmentID), 200)

    # /api/v1/users/:userid/courses
    if re.match(r"https://(\w+\.?)+\.\w{3}/api/v[0-9]/users/self/courses", args[0]) is not None:
        return MockResponse(Factories.generateCourses(7), 200)

    return MockResponse({'Error': "Failed to resolve mocked GET request."}, 404)


def mock_requestsPost(*args, **kwargs) -> MockResponse:
    # POST /api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/update_grades
    # payload = f"grade_data[25685][posted_grade]=6.0&grade_data[25685][text_comment]=Nice Work!&" \
    # f"grade_data[30691][posted_grade]=0.0&grade_data[30691][text_comment]=No Submission&"

    if re.match(r"https://(\w+\.?)+\.\w{3}/api/v[0-9]/courses/[0-9]{5}/assignments/[0-9]{6}/submissions/update_grades",
                args[0]) is not None:
        return MockResponse({'Status': "Success"}, 200)

    return MockResponse({'Error': "Failed to resolve mocked POST request."}, 404)
