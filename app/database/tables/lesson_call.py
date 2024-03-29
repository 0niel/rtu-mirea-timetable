import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class LessonCall(Base):
    __tablename__ = "schedule_lesson_call"

    id = db.Column(db.BigInteger, primary_key=True)
    num = db.Column(db.Integer, nullable=False, index=True)
    time_start = db.Column(db.Time, nullable=False, index=True)
    time_end = db.Column(db.Time, nullable=False, index=True)
    lesson = relationship(
        "Lesson",
        cascade="delete",
        back_populates="calls",
    )
