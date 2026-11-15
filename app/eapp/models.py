from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
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

class QuyDinh(UserEnum):
    BENH_NHAN_TOI_DA = 40


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.NGUOI_DUNG)


class BenhNhan(BaseModel):
    ho_ten = Column(String(50), nullable=False)
    gioi_tinh = Column(String(3), nullable=False)
    nam_sinh = Column(String(4), nullable=False)
    dia_chi = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(10), nullable=False)
    thong_tin_kham = relationship('ThongTinKham', backref='thong_tin', lazy=True)

class DanhSachKham(BaseModel):
    ngay_kham = Column(String(50), nullable=False)
    thong_tin_kham = relationship('ThongTinKham', backref='thong_tin', lazy=True)

class ThongTinKham(BaseModel):
    trang_thai_kham = Column(Integer, nullable=False, default=0)
    benh_nhan_id = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    danh_sach_kham_id = Column(Integer, ForeignKey(DanhSachKham.id), nullable=False)