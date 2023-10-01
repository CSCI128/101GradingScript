from typing import Optional

from sqlalchemy import BigInteger, DateTime
from Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Assignments(Base):
    __tablename__ = "assignments"

    id: Mapped[BigInteger] = mapped_column(primary_key=True, index=True)
    name: Optional[Mapped[str]]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    due_date: Mapped[DateTime]
    hidden: Mapped[bool] = mapped_column(default=False)
    description: Optional[Mapped[str]]
    course_id: Optional[Mapped[int]] = mapped_column(index=True)

    
