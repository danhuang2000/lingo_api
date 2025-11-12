from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class InstructionLanguage(SQLModel, table=True):
    __tablename__ = "instruction_language"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    code: str = Field(index=True, unique=True)

 