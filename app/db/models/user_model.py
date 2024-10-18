from sqlalchemy import Column, Integer, String
from db.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(100))
    username = Column(String(30))
    password = Column(String(30))