from typing import Optional

from sqlalchemy import BigInteger, DateTime
from Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Grades(Base):
    __tablename__ = "grades"

    id: Mapped[BigInteger] = mapped_column(primary_key=True, index=True)
    score: Optional[Mapped[int]]
    user_id: Optional[Mapped[int]] = mapped_column(index=True) 
    problem_id: Optional[Mapped[int]] = mapped_column(index=True)
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    assignment_id: Optional[Mapped[int]]
    course_id: Optional[Mapped[int]]

