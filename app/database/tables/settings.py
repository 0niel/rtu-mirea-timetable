import sqlalchemy as db

from app.database.connection import Base


class Settings(Base):
    __tablename__ = "schedule_settings"

    id = db.Column(db.BigInteger, index=True, primary_key=True)
    max_week = db.Column(db.Integer, nullable=False, index=True)
