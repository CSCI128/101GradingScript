from typing import Optional

from sqlalchemy import BigInteger, DateTime
from Base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Users(Base):
    __tablename__ = "users"

    id: Mapped[BigInteger] = mapped_column(primary_key=True, index=True)
    description: Optional[Mapped[str]]
    name: Optional[Mapped[str]]
    created_at: Mapped[DateTime]
    updated_at: Mapped[DateTime]
    hover_description: Optional[Mapped[str]]
    tests_json: Optional[Mapped[str]]
    spec: Optional[Mapped[str]]
    hidden_tests: Optional[Mapped[str]]
    function_name: Optional[Mapped[str]]
    in_type: Optional[Mapped[str]]
    out_type: Optional[Mapped[str]]
    programming_language: Optional[Mapped[str]]
    header: Optional[Mapped[str]]
    input_conversion_functions: Optional[Mapped[str]]
    output_conversion_function: Optional[Mapped[str]]
    text_files: Optional[Mapped[str]]
    input_or_output: Optional[Mapped[str]]
    text_filename: Optional[Mapped[str]]
    input_method: Optional[Mapped[str]]
    output_method: Optional[Mapped[str]]
    input_filename: Optional[Mapped[str]]
    output_filename: Optional[Mapped[str]]

