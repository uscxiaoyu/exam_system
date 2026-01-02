from sqlalchemy import Column, Integer, String
from backend.db.base import Base

class School(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
