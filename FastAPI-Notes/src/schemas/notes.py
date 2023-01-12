from datetime import datetime

from pydantic import BaseModel, Field


class NoteModel(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=150, description="Description of the note")


class NoteUpdate(NoteModel):
    done: bool


class NoteDone(BaseModel):
    done: bool

class NoteResponse(NoteModel):
    id: int
    done: bool
    created: datetime

    class Config:
        orm_mode = True
