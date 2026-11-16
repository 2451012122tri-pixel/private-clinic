from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from flask_login import UserMixin

from enum import Enum as UserEnum
from eapp import app, db


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


class GioiTinh(UserEnum):
    NAM = 1
    NU = 2

class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.NGUOI_DUNG)


class BenhNhan(BaseModel):
    ho_ten = Column(String(50), nullable=False)
    gioi_tinh = Column(Enum(GioiTinh), nullable=False)
    nam_sinh = Column(Integer, nullable=False)
    dia_chi = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(10), nullable=False)
    thong_tin_kham = relationship('ThongTinKham', backref='benh_nhan', lazy=True)

class DanhSachKham(BaseModel):
    ngay_kham = Column(Date, nullable=False)
    thong_tin_kham = relationship('ThongTinKham', backref='danh_sach_kham', lazy=True)

class ThongTinKham(BaseModel):
    trang_thai_kham = Column(Integer, nullable=False, default=0)
    so_thu_tu = Column(Integer, nullable=True)
    benh_nhan_id = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    danh_sach_kham_id = Column(Integer, ForeignKey(DanhSachKham.id), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        bn1 = BenhNhan(ho_ten='AAA',
                       gioi_tinh='nam',
                       nam_sinh='2006',
                       dia_chi='95 Ngô Quang Anh Hồ Chí Minh',
                       so_dien_thoai='0987654321')
        bn2 = BenhNhan(ho_ten='BBB',
                       gioi_tinh='nữ',
                       nam_sinh='2006',
                       dia_chi='183 Ngô Quang Anh Hồ Chí Minh',
                       so_dien_thoai='1234567890')
        bn3 = BenhNhan(ho_ten='CCC',
                       gioi_tinh='nam',
                       nam_sinh='2006',
                       dia_chi='24 Ngô Quang Anh Hồ Chí Minh',
                       so_dien_thoai='6473942985')

        dsk1 = DanhSachKham(ngay_kham='2026-11-20')
        dsk2 = DanhSachKham(ngay_kham='2026-11-21')

        db.session.add_all([bn1, bn2, bn3,
                           dsk1, dsk2])
        db.session.commit()

        ttk1 = ThongTinKham(trang_thai_kham=1, benh_nhan_id=bn1.id, danh_sach_kham_id=dsk1.id)
        ttk2 = ThongTinKham(trang_thai_kham=1, benh_nhan_id=bn2.id, danh_sach_kham_id=dsk1.id)
        ttk3 = ThongTinKham(trang_thai_kham=1, benh_nhan_id=bn2.id, danh_sach_kham_id=dsk2.id)
        ttk4 = ThongTinKham(trang_thai_kham=1, benh_nhan_id=bn3.id, danh_sach_kham_id=dsk2.id)

        db.session.add_all([ttk1, ttk2, ttk3, ttk4])
        db.session.commit()