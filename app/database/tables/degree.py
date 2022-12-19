import sqlalchemy as db
from app.database.connection import Base
from sqlalchemy.orm import relationship


class ScheduleDegree(Base):
    __tablename__ = "schedule_degree"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    groups = relationship(
        "Group",
        cascade="delete",
        back_populates="degree",
    )
