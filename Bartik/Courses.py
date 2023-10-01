from typing import Optional

from sqlalchemy import BigInteger, DateTime
from Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Courses(Base):
    __tablename__ = "courses"

    id: Mapped[BigInteger] = mapped_column(primary_key=True, index=True)
    course_id: Optional[Mapped[str]]
    name: Optional[Mapped[str]]
    term: Optional[Mapped[str]]
    active: Optional[Mapped[bool]]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
