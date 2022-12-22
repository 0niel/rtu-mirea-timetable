import sqlalchemy as db
from app.database.connection import Base
from sqlalchemy.orm import relationship


class ScheduleDiscipline(Base):
    __tablename__ = "schedule_discipline"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    lessons = relationship(
        "Lesson",
        cascade="delete",
        back_populates="discipline",
    )
