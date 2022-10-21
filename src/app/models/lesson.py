import sqlalchemy as db
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from app.db.base_class import Base

lessons_to_teachers = db.Table(
    "schedule_lessons_to_teachers",
    Base.metadata,
    db.Column("lesson_id", db.BigInteger, db.ForeignKey("schedule_lesson.id")),
    db.Column("teacher_id", db.BigInteger, db.ForeignKey("schedule_teacher.id")),
)


class Lesson(Base):
    __tablename__ = "schedule_lesson"

    id = db.Column(db.BigInteger, primary_key=True)
    group_id = db.Column(db.BigInteger, db.ForeignKey("schedule_group.id"))
    call_id = db.Column(
        db.BigInteger, db.ForeignKey("schedule_lesson_call.id"), nullable=False
    )
    discipline_id = db.Column(
        db.BigInteger, db.ForeignKey("schedule_discipline.id"), nullable=False
    )
    weekday = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.BigInteger, db.ForeignKey("schedule_room.id"), nullable=True)
    lesson_type_id = db.Column(
        db.BigInteger, db.ForeignKey("schedule_lesson_type.id"), nullable=True
    )
    teachers = relationship(
        "Teacher",
        secondary=lessons_to_teachers,
        back_populates="lessons",
        lazy="subquery",
    )
    subgroup = db.Column(db.Integer, nullable=True)
    weeks = db.Column(pg.ARRAY(db.Integer, dimensions=1))
    calls = relationship(
        "LessonCall",
        cascade="delete",
        back_populates="lesson",
        lazy="subquery",
    )
    discipline = relationship(
        "ScheduleDiscipline",
        cascade="delete",
        back_populates="lessons",
        lazy="subquery",
    )
    room = relationship(
        "Room",
        cascade="delete",
        back_populates="lessons",
        lazy="subquery",
    )
    lesson_type = relationship(
        "LessonType",
        cascade="delete",
        back_populates="lessons",
        lazy="subquery",
    )
    group = relationship(
        "Group",
        cascade="delete",
        back_populates="lessons",
    )
