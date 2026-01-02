from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey
from backend.db.base import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="teacher") # teacher, admin, school_admin

    # Linked to School
    school_id = Column(Integer, ForeignKey("school.id"), nullable=True)

    is_active = Column(Boolean, default=True)
