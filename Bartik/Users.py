from datetime import datetime
from typing import Optional
from Bartik.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    multipass_id: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    email: Mapped[str] = mapped_column(default="", unique=True, index=True) 
    provider: Mapped[str]
    uid: Mapped[str]
    name: Mapped[str]
    role: Mapped[str]
    theme: Mapped[str] = mapped_column(default="chrome")
    keybind: Mapped[str] = mapped_column(default="ace")
    current_course_id: Mapped[int]
    successColor: Mapped[str] = mapped_column(default="#5cb85c")
    dangerColor: Mapped[str] = mapped_column(default="#d9534f")
    infoColor: Mapped[str] = mapped_column(default="#5bc0de")
    warningColor: Mapped[str] = mapped_column(default="#f0ad4e")
    incorrectBar: Mapped[bool] = mapped_column(default=False)



