from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime
import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import hashlib

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.hashed_password == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"<Colonist> {self.id} {self.username} {self.email}"