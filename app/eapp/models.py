from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from enum import Enum as UserEnum
from datetime import datetime
from eapp import db


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRoleEnum(UserEnum):
    QUAN_TRI = 1
    BAC_SI = 2
    Y_TA = 3
    NGUOI_DUNG = 4
    THU_NGAN = 5


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.NGUOI_DUNG)

    def __str__(self):
        return self.name


class BenhNhan(BaseModel):
    __tablename__ = 'benh_nhan'

    ho_ten = Column(String(100), nullable=False)
    gioi_tinh = Column(Integer, nullable=False)  # 1: Nam, 0: Nữ
    nam_sinh = Column(Integer, nullable=False)
    dia_chi = Column(String(255), nullable=True)
    so_dien_thoai = Column(String(15), nullable=False, unique=True)

    thong_tin_khams = relationship('ThongTinKham', backref='benh_nhan', lazy=True)


class DanhSachKham(BaseModel):
    __tablename__ = 'danh_sach_kham'

    ngay_kham = Column(Date, nullable=False, unique=True)
    thong_tin_khams = relationship('ThongTinKham', backref='danh_sach_kham', lazy=True)


class ThongTinKham(BaseModel):
    __tablename__ = 'thong_tin_kham'
    __table_args__ = (
        UniqueConstraint('id_benh_nhan', 'id_ds_kham', name='uix_benhnhan_dskham'),
        UniqueConstraint('id_ds_kham', 'so_thu_tu', name='uix_dskham_sothutu'),
    )

    id_benh_nhan = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    id_ds_kham = Column(Integer, ForeignKey(DanhSachKham.id), nullable=False)
    so_thu_tu = Column(Integer, nullable=True)
    trang_thai_kham = Column(Integer, default=0)
    trang_thai_duyet = Column(Integer, default=1)
    trang_thai_sms = Column(Integer, default=0)

    phieu_kham = relationship('PhieuKham', backref='thong_tin_kham', uselist=False)


class DonViThuoc(BaseModel):
    __tablename__ = 'don_vi_thuoc'

    ten_don_vi = Column(String(50), nullable=False, unique=True)
    thuocs = relationship('Thuoc', backref='don_vi_thuoc', lazy=True)

    def __str__(self):
        return self.ten_don_vi


class Thuoc(BaseModel):
    __tablename__ = 'thuoc'

    ten_thuoc = Column(String(100), nullable=False, unique=True)
    id_don_vi = Column(Integer, ForeignKey(DonViThuoc.id), nullable=False)
    don_gia = Column(Float, default=0)
    hinh_anh = Column(String(200),
                      default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1646729533/zuur9gzztcekmyfenkfr.jpg')

    so_luong_thuocs = relationship('SoLuongThuoc', backref='thuoc', lazy=True)

    def __str__(self):
        return self.ten_thuoc


class PhieuKham(BaseModel):
    __tablename__ = 'phieu_kham'

    id_thong_tin_kham = Column(Integer, ForeignKey(ThongTinKham.id), nullable=False, unique=True)
    trieu_chung = Column(String(255), nullable=False)
    loai_benh_du_doan = Column(String(255), nullable=False)

    so_luong_thuocs = relationship('SoLuongThuoc', backref='phieu_kham', lazy=True)
    hoa_don = relationship('HoaDon', backref='phieu_kham', uselist=False)


class SoLuongThuoc(BaseModel):
    __tablename__ = 'so_luong_thuoc'

    id_thuoc = Column(Integer, ForeignKey(Thuoc.id), nullable=False)
    id_phieu_kham = Column(Integer, ForeignKey(PhieuKham.id), nullable=False)
    so_luong = Column(Integer, nullable=False)
    cach_dung = Column(String(255), nullable=False)


class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'

    id_phieu_kham = Column(Integer, ForeignKey(PhieuKham.id), nullable=False, unique=True)
    ngay_lap = Column(Date, default=datetime.now)
    tien_kham = Column(Float, nullable=False)
    tien_thuoc = Column(Float, nullable=False)
    tong_tien = Column(Float, nullable=False)


class QuyDinh(BaseModel):
    __tablename__ = 'quy_dinh'

    so_benh_nhan_toi_da = Column(Integer, default=40)
    tien_kham = Column(Float, default=100000)