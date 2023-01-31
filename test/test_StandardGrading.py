import shutil
import unittest

import pandas as pd

from FileHelpers import excelLoaders, csvLoaders

from Factories import Factories
import MockRequests

import Canvas
from Grade import grade, score, post


class TestStandardGrading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canvas: Canvas.Canvas = Canvas.Canvas("DEV", "self", "10001", "https://canvas.realschool.edu")
        cls.savedRequestsGet = Canvas.requests.get
        cls.savedRequestsPost = Canvas.requests.post
        Canvas.requests.get = MockRequests.mock_requestsGet
        Canvas.requests.post = MockRequests.mock_requestsPost

        excelLoaders.DEFAULT_SPECIAL_CASES_SEARCH_PATH = "special_cases/SC_test_working.xlsx"

        roster = Factories.generateStudentRoster(550)
        Factories.generateStudentGradescopeGradesForAssignment(roster, "HW1", 100)
        Factories.generateSpecialCases(roster, ["HW1"], extensionTypes=["Late Pass"], specialCaseRatio=.10)

    @classmethod
    def tearDownClass(cls):
        Canvas.requests.get = cls.savedRequestsGet
        Canvas.requests.post = cls.savedRequestsPost
        shutil.rmtree("./gradescope")
        shutil.rmtree("./special_cases", ignore_errors=True)

    def setUp(self):
        configFile: dict = {
            'assignments': [
                {
                    'common_name': 'HW1',
                    'name': "HW 1 - Development",
                    'id': "569011",
                    'points': 10,
                }
            ],
            'status_assignments': [
                {
                    'common_name': 'LPL',
                    'name': "Late Passes Left",
                    'id': "569012",
                    'points': 0,
                    'trigger': "Late Pass"
                }
            ]
        }

        self.canvas.getAssignmentsFromConfig(configFile)
        self.canvas.getStudentsFromCanvas()
        Factories.AssignmentMaxStudentPoints = 5
        self.canvas.updateStatusAssignmentScores()

    def test_standardGradingProcess(self):
        """
        Full integration test for standard grading process
        """

        gradesheet: pd.DataFrame = csvLoaders.loadGradescope("gradescope/HW1_test_scores.csv")
        specialCases: pd.DataFrame = excelLoaders.loadSpecialCases()

        statusAssignments: pd.DataFrame = self.canvas.getStatusAssignments()
        statusAssignmentsScores: pd.DataFrame = self.canvas.getStatusAssignmentScores()

        gradesheet = grade.scaleScores(gradesheet, .10, 10, 10, .10)

        self.assertEqual(10, gradesheet['Total Score'].max())

        gradesheet = grade.scoreMissingAssignments(gradesheet, score=0)

        self.assertEqual(118, len(gradesheet.loc[gradesheet['Status'] == "Missing"]))

        gradesheet, specialCases, statusAssignmentsScores = \
            grade.calculateLatePenalty(gradesheet, specialCases,
                                       statusAssignments, statusAssignmentsScores, "HW1")

        pass

