import sqlalchemy as db
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.database.connection import Base

lessons_to_teachers = db.Table(
    "schedule_lessons_to_teachers",
    Base.metadata,
    db.Column("id", db.BigInteger, primary_key=True),
    db.Column("lesson_id", db.BigInteger, db.ForeignKey("schedule_lesson.id"), index=True),
    db.Column("teacher_id", db.BigInteger, db.ForeignKey("schedule_teacher.id"), index=True),
)


class Lesson(Base):
    __tablename__ = "schedule_lesson"

    id = db.Column(db.BigInteger, primary_key=True)
    group_id = db.Column(db.BigInteger, db.ForeignKey("schedule_group.id"), nullable=False, index=True)
    call_id = db.Column(db.BigInteger, db.ForeignKey("schedule_lesson_call.id"), nullable=False, index=True)
    discipline_id = db.Column(db.BigInteger, db.ForeignKey("schedule_discipline.id"), nullable=False, index=True)
    weekday = db.Column(db.Integer, nullable=False, index=True)
    room_id = db.Column(db.BigInteger, db.ForeignKey("schedule_room.id"), nullable=True, index=True)
    lesson_type_id = db.Column(db.BigInteger, db.ForeignKey("schedule_lesson_type.id"), nullable=True, index=True)
    teachers = relationship(
        "Teacher",
        secondary="schedule_lessons_to_teachers",
        back_populates="lessons",
        lazy="joined",
    )
    subgroup = db.Column(db.Integer, nullable=True)
    weeks = db.Column(pg.ARRAY(db.Integer, dimensions=1), nullable=False, index=True)
    calls = relationship(
        "LessonCall",
        cascade="delete",
        back_populates="lesson",
        lazy="joined",
    )
    discipline = relationship(
        "ScheduleDiscipline",
        cascade="delete",
        back_populates="lessons",
        lazy="joined",
    )
    room = relationship(
        "Room",
        cascade="delete",
        back_populates="lessons",
        lazy="joined",
    )
    lesson_type = relationship(
        "LessonType",
        cascade="delete",
        back_populates="lessons",
        lazy="joined",
    )
    group = relationship(
        "Group",
        cascade="delete",
        back_populates="lessons",
        lazy="joined",
    )
