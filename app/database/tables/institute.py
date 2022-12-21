import sqlalchemy as db
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Institute(Base):
    __tablename__ = "schedule_institute"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    short_name = db.Column(db.String(256), nullable=False)
    groups = relationship(
        "Group",
        cascade="delete",
        back_populates="institute",
    )
