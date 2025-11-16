from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base
from pydantic import BaseModel
from typing import List, Dict

class QuizRecord(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String, index=True)
    date_generated = Column(DateTime(timezone=True), server_default=func.now())
    scraped_content = Column(Text)
    raw_html = Column(Text, nullable=True)
    full_quiz_data = Column(Text)

# Pydantic schemas used for validation (LLM parsing)
class QuestionSchema(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str
    difficulty: str

class QuizOutput(BaseModel):
    title: str
    summary: str
    key_entities: Dict[str, List[str]]
    sections: List[str]
    quiz: List[QuestionSchema]
    related_topics: List[str]
