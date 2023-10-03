from datetime import datetime
from Bartik.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Courses(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[str]
    name: Mapped[str]
    term: Mapped[str]
    active: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
