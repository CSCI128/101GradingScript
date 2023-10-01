from Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class AssignmentsProblemsMap(Base):
    __tablename__ = "assignments_problems"

    assignment_id: Mapped[int] = mapped_column(index=True)
    problem_id: Mapped[int] = mapped_column(index=True)
