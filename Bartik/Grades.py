from datetime import datetime
from Bartik.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Grades(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    score: Mapped[int]
    user_id: Mapped[int] = mapped_column(index=True) 
    problem_id: Mapped[int] = mapped_column(index=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    assignment_id: Mapped[int]
    course_id: Mapped[int]

