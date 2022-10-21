import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ScheduleCampus(Base):
    __tablename__ = "schedule_campus"

    id = db.Column(db.BigInteger, primary_key=True)
    short_name = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    rooms = relationship(
        "Room",
        cascade="delete",
        back_populates="campus",
    )
