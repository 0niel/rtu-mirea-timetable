import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Group(Base):
    __tablename__ = "schedule_group"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    period_id = db.Column(db.BigInteger, db.ForeignKey("schedule_period.id"))
    period = relationship(
        "SchedulePeriod",
        back_populates="groups",
        lazy="subquery",
    )
    degree_id = db.Column(db.BigInteger, db.ForeignKey("schedule_degree.id"))
    institute_id = db.Column(db.BigInteger, db.ForeignKey("schedule_institute.id"))
    institute = relationship(
        "Institute",
        back_populates="groups",
        lazy="subquery",
    )
    degree = relationship(
        "ScheduleDegree",
        cascade="delete",
        back_populates="groups",
        lazy="subquery",
    )
    lessons = relationship(
        "Lesson",
        cascade="delete",
        back_populates="group",
        lazy="subquery",
    )
