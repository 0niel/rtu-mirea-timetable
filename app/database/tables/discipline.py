import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ScheduleDiscipline(Base):
    __tablename__ = "schedule_discipline"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True, index=True)
    lessons = relationship(
        "Lesson",
        cascade="delete",
        back_populates="discipline",
    )
