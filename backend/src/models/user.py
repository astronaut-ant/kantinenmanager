from sqlalchemy import Column, Integer, String
from src.database import db


class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(150))
    user_group = Column(String(20))
