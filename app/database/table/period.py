import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class SchedulePeriod(Base):
    __tablename__ = "schedule_period"

    id = db.Column(db.BigInteger, primary_key=True)
    year_start = db.Column(db.Integer, nullable=False)
    year_end = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    groups = relationship(
        "Group",
        cascade="delete",
        back_populates="period",
    )
