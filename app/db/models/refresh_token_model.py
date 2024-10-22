from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("UserModel", back_populates="refresh_tokens")