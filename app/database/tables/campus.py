import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ScheduleCampus(Base):
    __tablename__ = "schedule_campus"

    id = db.Column(db.BigInteger, primary_key=True)
    short_name = db.Column(db.String(256), nullable=False, unique=True, index=True)
    name = db.Column(db.String(256), nullable=False, unique=True, index=True)
    rooms = relationship(
        "Room",
        cascade="delete",
        back_populates="campus",
    )
