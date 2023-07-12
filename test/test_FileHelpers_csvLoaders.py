from Factories import Factories
import os
import shutil
from FileHelpers import csvLoaders
import pandas as pd
from pandas import testing
import unittest
from unittest import mock


class TestCsvLoaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster = Factories.generateStudentRoster(10)
        cls.gradesheetLocation = "gradescope/Homework_1_test_scores.csv"

        # TODO probably a better way to accomplish this here, we could separate the test classes
        # cls.runestoneRoster = Factories.generateStudentRoster(10)
        cls.runestoneGradesheetLocation = "runestone/Week_1_Readings_test_scores.csv"

    def setUp(self):
        Factories.generateStudentGradescopeGradesForAssignment(self.roster, "Homework 1", 10)
        self.assertTrue(os.path.exists(self.gradesheetLocation))
        self.assertTrue(os.path.isfile(self.gradesheetLocation))

        # Must verify that all manually mocked things are not mocked at top of test
        self.assertNotIsInstance(csvLoaders.loadCSV, mock.MagicMock)

        self.loadCSVSaved = csvLoaders.loadCSV

        # Runestone gen:
        Factories.generateStudentRunestoneGradesForAssignment(self.roster, "Week 1 Readings", 10)
        self.assertTrue(os.path.exists(self.runestoneGradesheetLocation))
        self.assertTrue(os.path.isfile(self.runestoneGradesheetLocation))

    def tearDown(self):
        shutil.rmtree("./gradescope")
        self.assertFalse(os.path.exists(self.gradesheetLocation))

        # Reset manual mocks
        csvLoaders.loadCSV = self.loadCSVSaved

    def test_loadCSV(self):
        """
        Basic CSV Loading
        """
        loadedData: pd.DataFrame = csvLoaders.loadCSV(self.gradesheetLocation)

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertFalse(loadedData.empty)

        self.assertEqual(10, len(loadedData))

    def test_loadCSVFail(self):
        """
        Basic CSV Failure - File Does Not Exist
        """
        loadedData: pd.DataFrame = csvLoaders.loadCSV("./gradescope/does_not_exist.csv", promptIfError=False)

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertTrue(loadedData.empty)

    @mock.patch("builtins.input", side_effect=["./gradescope/Homework_1_test_scores.csv"])
    def test_loadCSVReprompt(self, _):
        """
        Basic CSV Loading - File does not exist - Reprompt
        """
        loadedData: pd.DataFrame = csvLoaders.loadCSV("./gradescope/does_not_exist.csv", promptIfError=True)

        self.assertEqual(10, len(loadedData))

    def test_loadGradescope(self):
        """
        Basic Gradescope Gradesheet Loading
        """

        loadedData: pd.DataFrame = csvLoaders.loadGradescope(self.gradesheetLocation)

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertFalse(loadedData.empty)

        validCols = ["multipass", "Total Score", "Status", "hours_late"]

        self.assertSequenceEqual(validCols, loadedData.columns.to_list())

        multipasses: list[str] = loadedData['multipass'].to_list()
        for el in multipasses:
            self.assertNotIn(el, "@")

        lateness: list[float] = loadedData['hours_late'].to_list()

        for el in lateness:
            self.assertIsNotNone(el)
            self.assertIsInstance(el, float)

    def test_loadGradescopeUngraded(self):
        """
        Basic Gradescope Failure - Ungraded Assignments
        """

        mockedData: pd.DataFrame = csvLoaders.loadCSV(self.gradesheetLocation)
        mockedData.at[0, 'Total Score'] = None
        mockedData.at[0, 'Lateness (H:M:S)'] = None
        mockedData.at[0, 'Status'] = "Ungraded"

        csvLoaders.loadCSV = mock.MagicMock(return_value=mockedData)

        loadedData: pd.DataFrame = csvLoaders.loadGradescope(self.gradesheetLocation)

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertTrue(loadedData.empty)

    def test_loadGradescopeGracePeriod(self):
        """
        Verify That Grade Period Is Being Applied.
        """
        mockedData: pd.DataFrame = csvLoaders.loadCSV(self.gradesheetLocation)
        mockedData.at[0, 'Total Score'] = 10
        mockedData.at[0, 'Lateness (H:M:S)'] = "00:15:00"
        mockedData.at[0, 'Status'] = "Graded"

        mockedData.at[1, 'Total Score'] = 10
        mockedData.at[1, 'Lateness (H:M:S)'] = "24:15:00"
        mockedData.at[1, 'Status'] = "Graded"

        csvLoaders.loadCSV = mock.MagicMock(return_value=mockedData)

        loadedData: pd.DataFrame = csvLoaders.loadGradescope(self.gradesheetLocation)

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertFalse(loadedData.empty)

        self.assertEqual(0, loadedData.at[0, "hours_late"])
        self.assertEqual(24, loadedData.at[1, "hours_late"])

    def test_loadGradescopeInvalidGradesheet(self):
        """
        Verify Invalid Gradesheet - Misnamed Columns
        """
        mockedData: pd.DataFrame = csvLoaders.loadCSV(self.gradesheetLocation)
        mockedData.rename(columns={'Email': 'Missing Email'}, inplace=True)
        csvLoaders.loadCSV = mock.MagicMock(return_value=mockedData)

        loadedData: pd.DataFrame = csvLoaders.loadGradescope(self.gradesheetLocation)

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertTrue(loadedData.empty)

    def test_loadGradescopeFileNotFound(self):
        """
        Verify Gradescope Loading Error - File Does Not Exist
        """
        loadedData: pd.DataFrame = csvLoaders.loadGradescope("./gradescope/does_not_exist.csv")

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertTrue(loadedData.empty)

    def test_loadRunestone(self):
        """
        Basic Runestone Gradesheet Loading
        """

        loadedData: pd.DataFrame = csvLoaders.loadRunestone(self.runestoneGradesheetLocation, "Week 1 Readings")

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertFalse(loadedData.empty)

        validCols = ["multipass", "Total Score", 'lateness_comment', 'Status']

        self.assertSequenceEqual(validCols, loadedData.columns.to_list())

        multipasses: list[str] = loadedData['multipass'].to_list()
        for el in multipasses:
            self.assertNotIn(el, "@")

        score: list[float] = loadedData['Total Score'].to_list()

        for el in score:
            self.assertIsNotNone(el)
            self.assertIsInstance(el, float)

    def test_loadRunestoneFileNotFound(self):
        """
        Verify Runestone Loading Error - File Does Not Exist
        """
        loadedData: pd.DataFrame = csvLoaders.loadRunestone("./runestone/does_not_exist.csv", "Week 1 Readings")

        self.assertIsInstance(loadedData, pd.DataFrame)
        self.assertTrue(loadedData.empty)
