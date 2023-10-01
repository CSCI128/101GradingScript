from typing import Optional

from sqlalchemy import BigInteger, DateTime
from Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Users(Base):
    __tablename__ = "users"

    id: Mapped[BigInteger] = mapped_column(primary_key=True, index=True)
    multipass_id: Optional[Mapped[str]]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    email: Mapped[str] = mapped_column(default="", unique=True, index=True) 
    provider: Optional[Mapped[str]]
    uid: Optional[Mapped[str]]
    name: Optional[Mapped[str]]
    role: Optional[Mapped[str]]
    theme: Mapped[str] = mapped_column(default="chrome")
    keybind: Mapped[str] = mapped_column(default="ace")
    current_course_id: Optional[Mapped[int]]
    successColor: Optional[Mapped[str]] = mapped_column(default="#5cb85c")
    dangerColor: Optional[Mapped[str]] = mapped_column(default="#d9534f")
    infoColor: Optional[Mapped[str]] = mapped_column(default="#5bc0de")
    warningColor: Optional[Mapped[str]] = mapped_column(default="#f0ad4e")
    incorrectBar: Optional[Mapped[bool]] = mapped_column(default=False)



