import sqlalchemy as db
from app.database.connection import Base
from sqlalchemy.orm import relationship


class Room(Base):
    __tablename__ = "schedule_room"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    campus_id = db.Column(db.BigInteger, db.ForeignKey("schedule_campus.id"), nullable=True)
    lessons = relationship(
        "Lesson",
        cascade="delete",
        back_populates="room",
        lazy="subquery",
    )
    campus = relationship(
        "ScheduleCampus",
        back_populates="rooms",
        lazy="subquery",
    )
