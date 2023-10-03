from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime
from Bartik.Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    hover_description: Mapped[str]
    tests_json: Mapped[str]
    spec: Mapped[str]
    hidden_tests: Mapped[str]
    function_name: Mapped[str]
    in_type: Mapped[str]
    out_type: Mapped[str]
    programming_language: Mapped[str]
    header: Mapped[str]
    input_conversion_functions: Mapped[str]
    output_conversion_function: Mapped[str]
    text_files: Mapped[str]
    input_or_output: Mapped[str]
    text_filename: Mapped[str]
    input_method: Mapped[str]
    output_method: Mapped[str]
    input_filename: Mapped[str]
    output_filename: Mapped[str]

