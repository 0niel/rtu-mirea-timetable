import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Teacher(Base):
    __tablename__ = "schedule_teacher"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    lessons = relationship(
        "Lesson",
        cascade="delete",
        back_populates="teachers",
        secondary="schedule_lessons_to_teachers",
    )
