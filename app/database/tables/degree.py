import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ScheduleDegree(Base):
    __tablename__ = "schedule_degree"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True, index=True)
    groups = relationship(
        "Group",
        cascade="delete",
        back_populates="degree",
    )
