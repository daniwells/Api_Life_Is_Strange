from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(30), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    refresh_tokens = relationship("RefreshTokenModel", back_populates="user")