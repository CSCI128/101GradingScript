from datetime import datetime

from Bartik.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Assignments(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Technically this is nullable, but there are no instances in the DB where it is null
    name: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    due_date: Mapped[datetime]
    hidden: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str]
    course_id: Mapped[int] = mapped_column(index=True)

    
