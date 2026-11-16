import hashlib
from datetime import datetime, date, timedelta
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Date, UniqueConstraint
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
    THU_NGAN = 5


class QuyDinh(BaseModel):
    __tablename__ = 'quy_dinh'

    so_benh_nhan_toi_da = Column(Integer, default=40)
    tien_kham = Column(Float, default=100000)


class GioiTinh(UserEnum):
    NAM = 1
    NU = 2

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
    gioi_tinh = Column(Enum(GioiTinh), nullable=False)
    nam_sinh = Column(Integer, nullable=False)
    dia_chi = Column(String(255), nullable=False)
    so_dien_thoai = Column(String(10), nullable=False, unique=True)
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


def init_sample_data():
    db.create_all()

    # 1. Quy định khám mặc định
    if QuyDinh.query.count() == 0:
        db.session.add(QuyDinh(so_benh_nhan_toi_da=40, tien_kham=100000))
        db.session.commit()

    # 2. Tài khoản kiểm thử cho đầy đủ 5 vai trò (mật khẩu chung: 123456)
    if User.query.count() == 0:
        pw_default = hashlib.md5('123456'.encode('utf-8')).hexdigest()
        users = [
            User(name='Trần Đức Tài (Admin)', username='admin', password=pw_default, user_role=UserRoleEnum.QUAN_TRI),
            User(name='BS. Nguyễn Minh Khang', username='bacsi', password=pw_default, user_role=UserRoleEnum.BAC_SI),
            User(name='YT. Lê Thị Thu Hà', username='yta', password=pw_default, user_role=UserRoleEnum.Y_TA),
            User(name='TN. Phạm Hoàng Nam', username='thungan', password=pw_default, user_role=UserRoleEnum.THU_NGAN),
            User(name='Khách hàng mẫu', username='benhnhan', password=pw_default, user_role=UserRoleEnum.NGUOI_DUNG),
        ]
        db.session.add_all(users)
        db.session.commit()

    # 3. Đơn vị thuốc & Danh mục thuốc
    if DonViThuoc.query.count() == 0:
        dv_vien = DonViThuoc(ten_don_vi='Viên')
        dv_vi = DonViThuoc(ten_don_vi='Vỉ')
        dv_chai = DonViThuoc(ten_don_vi='Chai')
        dv_goi = DonViThuoc(ten_don_vi='Gói')
        db.session.add_all([dv_vien, dv_vi, dv_chai, dv_goi])
        db.session.commit()

        thuocs = [
            Thuoc(ten_thuoc='Paracetamol 500mg', id_don_vi=dv_vien.id, don_gia=2000),
            Thuoc(ten_thuoc='Amoxicillin 500mg', id_don_vi=dv_vi.id, don_gia=15000),
            Thuoc(ten_thuoc='Vitamin C 500mg', id_don_vi=dv_vien.id, don_gia=1500),
            Thuoc(ten_thuoc='Siro ho Bảo Thanh', id_don_vi=dv_chai.id, don_gia=55000),
            Thuoc(ten_thuoc='Oresol bù điện giải', id_don_vi=dv_goi.id, don_gia=5000),
            Thuoc(ten_thuoc='Berberin 100mg', id_don_vi=dv_chai.id, don_gia=25000),
        ]
        db.session.add_all(thuocs)
        db.session.commit()

    # 4. Bệnh nhân mẫu
    if BenhNhan.query.count() == 0:
        bns = [
            BenhNhan(ho_ten='Nguyễn Văn An', gioi_tinh=GioiTinh.NU, nam_sinh=1995, dia_chi='Quận 1, TP.HCM', so_dien_thoai='0901111111'),
            BenhNhan(ho_ten='Trần Thị Bình', gioi_tinh=GioiTinh.NAM, nam_sinh=1998, dia_chi='Quận 3, TP.HCM', so_dien_thoai='0902222222'),
            BenhNhan(ho_ten='Lê Hoàng Cường', gioi_tinh=GioiTinh.NU, nam_sinh=1988, dia_chi='Gò Vấp, TP.HCM', so_dien_thoai='0903333333'),
            BenhNhan(ho_ten='Phạm Mỹ Dung', gioi_tinh=GioiTinh.NAM, nam_sinh=2001, dia_chi='Bình Thạnh, TP.HCM', so_dien_thoai='0904444444'),
            BenhNhan(ho_ten='Võ Quốc Đại', gioi_tinh=GioiTinh.NU, nam_sinh=1992, dia_chi='Thủ Đức, TP.HCM', so_dien_thoai='0905555555'),
        ]
        db.session.add_all(bns)
        db.session.commit()

    # 5. Dữ liệu khám bệnh, đơn thuốc và hóa đơn để test thống kê & quy trình khám
    if DanhSachKham.query.count() == 0:
        today = date.today()
        day_1 = today.replace(day=1)
        prev_month = day_1 - timedelta(days=5)

        ds_prev = DanhSachKham(ngay_kham=prev_month)
        ds_day1 = DanhSachKham(ngay_kham=day_1)
        ds_today = DanhSachKham(ngay_kham=today) if today != day_1 else ds_day1
        db.session.add_all(list({ds_prev, ds_day1, ds_today}))
        db.session.commit()

        bns = BenhNhan.query.all()
        thuocs = Thuoc.query.all()

        # Ca khám đã hoàn tất & thanh toán ở tháng trước
        ttk1 = ThongTinKham(id_benh_nhan=bns[0].id, id_ds_kham=ds_prev.id, so_thu_tu=1, trang_thai_kham=1, trang_thai_duyet=1)
        db.session.add(ttk1)
        db.session.commit()
        pk1 = PhieuKham(id_thong_tin_kham=ttk1.id, trieu_chung='Sốt nhẹ, đau họng', loai_benh_du_doan='Viêm họng cấp')
        db.session.add(pk1)
        db.session.commit()
        db.session.add_all([
            SoLuongThuoc(id_thuoc=thuocs[0].id, id_phieu_kham=pk1.id, so_luong=10, cach_dung='Sáng 1 viên, chiều 1 viên sau ăn'),
            SoLuongThuoc(id_thuoc=thuocs[3].id, id_phieu_kham=pk1.id, so_luong=1, cach_dung='Uống 10ml x 3 lần/ngày'),
        ])
        db.session.add(HoaDon(id_phieu_kham=pk1.id, ngay_lap=prev_month, tien_kham=100000, tien_thuoc=75000, tong_tien=175000))

        # Ca khám 1 đã hoàn tất & thanh toán trong tháng hiện tại (ngày mùng 1)
        ttk2 = ThongTinKham(id_benh_nhan=bns[1].id, id_ds_kham=ds_day1.id, so_thu_tu=1, trang_thai_kham=1, trang_thai_duyet=1)
        db.session.add(ttk2)
        db.session.commit()
        pk2 = PhieuKham(id_thong_tin_kham=ttk2.id, trieu_chung='Ho khan, sổ mũi', loai_benh_du_doan='Cảm cúm thông thường')
        db.session.add(pk2)
        db.session.commit()
        db.session.add_all([
            SoLuongThuoc(id_thuoc=thuocs[0].id, id_phieu_kham=pk2.id, so_luong=6, cach_dung='Uống khi sốt trên 38.5 độ'),
            SoLuongThuoc(id_thuoc=thuocs[2].id, id_phieu_kham=pk2.id, so_luong=10, cach_dung='Sáng 1 viên sau ăn'),
        ])
        db.session.add(HoaDon(id_phieu_kham=pk2.id, ngay_lap=day_1, tien_kham=100000, tien_thuoc=27000, tong_tien=127000))

        # Ca khám 2 đã hoàn tất & thanh toán trong tháng hiện tại (ngày hôm nay)
        stt_today = 2 if ds_today.id == ds_day1.id else 1
        ttk3 = ThongTinKham(id_benh_nhan=bns[2].id, id_ds_kham=ds_today.id, so_thu_tu=stt_today, trang_thai_kham=1, trang_thai_duyet=1)
        db.session.add(ttk3)
        db.session.commit()
        pk3 = PhieuKham(id_thong_tin_kham=ttk3.id, trieu_chung='Đau bụng, rối loạn tiêu hóa', loai_benh_du_doan='Rối loạn tiêu hóa')
        db.session.add(pk3)
        db.session.commit()
        db.session.add_all([
            SoLuongThuoc(id_thuoc=thuocs[5].id, id_phieu_kham=pk3.id, so_luong=2, cach_dung='Uống 4 viên/lần, ngày 2 lần'),
            SoLuongThuoc(id_thuoc=thuocs[4].id, id_phieu_kham=pk3.id, so_luong=4, cach_dung='Pha 1 gói với 200ml nước sôi để nguội'),
        ])
        db.session.add(HoaDon(id_phieu_kham=pk3.id, ngay_lap=today, tien_kham=100000, tien_thuoc=70000, tong_tien=170000))

        # Ca khám đang chờ bác sĩ khám hôm nay (để Y tá / Bác sĩ test giao diện)
        ttk4 = ThongTinKham(id_benh_nhan=bns[3].id, id_ds_kham=ds_today.id, so_thu_tu=stt_today + 1, trang_thai_kham=0, trang_thai_duyet=1)
        ttk5 = ThongTinKham(id_benh_nhan=bns[4].id, id_ds_kham=ds_today.id, so_thu_tu=stt_today + 2, trang_thai_kham=0, trang_thai_duyet=1)
        db.session.add_all([ttk4, ttk5])
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_sample_data()
        print("Khởi tạo bảng và dữ liệu kiểm thử thành công!")