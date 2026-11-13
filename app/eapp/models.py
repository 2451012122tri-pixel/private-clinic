from sqlalchemy import Column, Integer, String, Enum
from flask_login import UserMixin

from enum import Enum as UserEnum
from eapp import db

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

class UserRoleEnum(UserEnum):
    QUAN_TRI = 1
    BAC_SI = 2
    Y_TA = 3
    NGUOI_DUNG = 4

class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.NGUOI_DUNG)