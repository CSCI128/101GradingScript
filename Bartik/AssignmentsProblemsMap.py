from Bartik.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class AssignmentsProblemsMap(Base):
    __tablename__ = "assignments_problems"

    # Composite keys have to both be marked as the primary
    #  ffs this took like 2 hours of debugging
    assignment_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    problem_id: Mapped[int] = mapped_column(primary_key=True, index=True)
