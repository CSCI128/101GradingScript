from typing import List, Optional
from sqlalchemy import create_engine, Engine, select, where
from sqlalchemy.orm import Session, sessionmaker
from Bartik.Assignments import Assignments
from Bartik.AssignmentsProblemsMap import AssignmentsProblemsMap
from Base import Base


class Bartik():

    def __init__(self, _url: str, _userName: str, _password: str) -> None:
        CONNECTION_STRING: str = f"postgres://{_userName}:{_password}@{_url}/autograder"

        self.engine: Engine = create_engine(CONNECTION_STRING)

        self.BoundSession = sessionmaker(bind=self.engine)

        self.session: Optional[Session] = None

        Base.metadata.create_all(self.engine)
   

    def openSession(self):
        if self.session is not None:
            return

        self.session = self.BoundSession()

    def closeSession(self):
        if self.session is None:
            return

        self.session.close()


    def getScoreForAssignment(self, _email: str, _assessment: str) -> int:
        if self.session is None:
            raise Exception("Session must be started")

        assessmentIdAssessment = self.session.query(Assignments).where(Assignments.name.in_(_assessment)))
        assessmentId: int = assessmentIdAssessment.id
        problemsIdQuery = self.session.query(AssignmentsProblemsMap).where(AssignmentsProblemsMap.assignment_id == assessmentId))
        problemIds: List[int] = problemsQuery.all()









