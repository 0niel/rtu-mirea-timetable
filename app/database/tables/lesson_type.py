import sqlalchemy as db
from app.database.connection import Base
from sqlalchemy.orm import relationship


class LessonType(Base):
    __tablename__ = "schedule_lesson_type"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    lessons = relationship(
        "Lesson",
        cascade="delete",
        back_populates="lesson_type",
    )
