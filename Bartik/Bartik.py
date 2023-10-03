from typing import List, Optional
from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import Session, sessionmaker
from Bartik.Assignments import Assignments
from Bartik.AssignmentsProblemsMap import AssignmentsProblemsMap
from Bartik.Courses import Courses
from Bartik.Users import Users
from Bartik.Grades import Grades
from Bartik.Base import Base


class Bartik():

    def __init__(self, _url: str, _userName: str, _password: str, courseId: Optional[int] = None) -> None:
        CONNECTION_STRING: str = f"postgresql+psycopg://{_userName}:{_password}@{_url}/autograder"

        self.engine: Engine = create_engine(CONNECTION_STRING)

        self.BoundSession = sessionmaker(bind=self.engine)

        self.session: Optional[Session] = None

        self.COURSE_ID = courseId

        Base.metadata.create_all(self.engine)
   

    def openSession(self):
        if self.session is not None:
            return

        self.session = self.BoundSession()

    def closeSession(self):
        if self.session is None:
            return

        self.session.close()

    def getCourseId(self, _courseName: str) -> int:
        if self.session is None:
            raise Exception("Session must be started")

        courseIdStm = select(Courses).where(Courses.name.like(f"%{_courseName}%"), Courses.active==True)
        courseIdCourse = self.session.scalars(courseIdStm).first()

        if courseIdCourse is None:
            raise Exception("Failed to locate course")

        return courseIdCourse.id



    def getScoreForAssignment(self, _email: str, _assessment: str, requiredProblems: int = 3, maxScore: float = 10) -> float:
        if self.session is None:
            raise Exception("Session must be started")

        assessmentIdStm = select(Assignments).where(Assignments.name.like(f"%{_assessment}%"), Assignments.course_id == self.COURSE_ID)
        assessmentIdAssessment = self.session.scalars(assessmentIdStm).first()

        if assessmentIdAssessment is None:
            raise Exception("Failed to locate assignment")

        assessmentId: int = assessmentIdAssessment.id

        problemsIdStm = select(AssignmentsProblemsMap).where(AssignmentsProblemsMap.assignment_id == assessmentId)

        problemsIdProblems = self.session.scalars(problemsIdStm).all()

        if problemsIdProblems is None or not len(problemsIdProblems):
            raise Exception("Failed to locate problems for assignment")

        problemIds: List[int] = [problemId.problem_id for problemId in problemsIdProblems if problemId is not None]

        userIdStm = select(Users).where(Users.email == _email)
        userIdUser = self.session.scalars(userIdStm).first()
        
        if userIdUser is None:
            raise Exception(f"Failed to find user with email {_email}")

        userId = userIdUser.id

        gradesStm = select(Grades).where(Grades.problem_id.in_(problemIds), Grades.user_id == userId)
        grades = self.session.scalars(gradesStm).all()
        # Rn i dont really have the motivation to parse the required problems 

        totalScore: float = 0

        for grade in grades:
            totalScore += grade.score if grade is not None else 0
        
        # bartik reports scores out of 10 per problem, scale down so they are now out of 1
        
        totalScore /= 10

        totalScore = round((totalScore / requiredProblems) * maxScore, 2)

        return totalScore if totalScore <= maxScore else maxScore
        
        

        












