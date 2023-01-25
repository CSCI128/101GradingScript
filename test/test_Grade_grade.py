import os
import shutil

import pandas as pd

from Factories import Factories
from MockRequests import mock_requestsGet

import unittest
from unittest import mock

from FileHelpers.csvLoaders import loadGradescope
from Grade import grade


class TestGrade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        roster = Factories.generateStudentRoster(1)
        cls.gradesheetLocation = "gradescope/Homework_1_test_scores.csv"
        Factories.generateStudentGradescopeGradesForAssignment(roster, "Homework 1", 10)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("./gradescope")

    def setUp(self):
        self.assertTrue(os.path.exists(self.gradesheetLocation))
        self.assertTrue(os.path.isfile(self.gradesheetLocation))

        self.gradesheet: pd.DataFrame = loadGradescope(self.gradesheetLocation)

        # assert mocks are reset

        # save mocked objects

    def tearDown(self):
        pass
        # restore mocks

    def test_scaleScoresNormalScaling(self):
        """
        Basic Test - Verify Normal Scaling, No extra credit
        """
        self.gradesheet.at[0, 'Total Score'] = 200

        self.gradesheet = grade.scaleScores(self.gradesheet, .10, assignmentPoints=10, maxScore=10)

        self.assertEqual(10, self.gradesheet.at[0, 'Total Score'])

    def test_scaleScoresNormalScalingWithExtraCredit(self):
        """
        Basic Test - Verify Normal Scaling, With no scaling extra credit
        """
        self.gradesheet.at[0, 'Total Score'] = 200

        self.gradesheet = grade.scaleScores(self.gradesheet, .10, assignmentPoints=10)

        self.assertEqual(20, self.gradesheet.at[0, 'Total Score'])

    def test_scaleScoresExtraCredit(self):
        """
        Basic Test - Verify Extra Credit Scaling
        """
        self.gradesheet.at[0, 'Total Score'] = 100

        self.gradesheet = grade.scaleScores(self.gradesheet, 1, assignmentPoints=0, XCScaleFactor=.1)

        self.assertEqual(10, self.gradesheet.at[0, 'Total Score'])

    def test_scaleScoresNormalScalingExtraCreditScaling(self):
        """
        Basic Test - Verify Normal Scaling, With extra credit scaling
        """
        self.gradesheet.at[0, 'Total Score'] = 200

        self.gradesheet = grade.scaleScores(self.gradesheet, .25, assignmentPoints=10, XCScaleFactor=.1)
        # Important to note, extra credit is scaled off the original points
        self.assertEqual(26, self.gradesheet.at[0, 'Total Score'])

    def test_scaleScoresExceptions(self):
        """
        Exception Tests for Scale Scores - Verify that correct exceptions are raised
        """
        with self.assertRaises(TypeError):
            grade.scaleScores({}, 0)

    def test_scoreMissingAssignments(self):
        """
        Basic Test - Verify score missing assignments
        """
        self.gradesheet.at[0, 'Status'] = "Missing"
        self.gradesheet.at[0, 'Total Score'] = None

        self.gradesheet = grade.scoreMissingAssignments(self.gradesheet, score=10)

        self.assertIsNotNone(self.gradesheet.at[0, 'Total Score'])
        self.assertEqual(10, self.gradesheet.at[0, 'Total Score'])

    def test_scoreMissingAssignmentsExceptions(self):
        """
        Exception Tests for Score Missing Assignment - Verify that correct exceptions are raised
        """
        with self.assertRaises(TypeError):
            grade.scoreMissingAssignments({}, 0)

        with self.assertRaises(AttributeError):
            grade.scoreMissingAssignments(self.gradesheet, exceptions={})

