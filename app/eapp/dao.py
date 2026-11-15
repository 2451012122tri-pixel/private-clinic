from models import User, QuyDinh, DanhSachKham

from eapp import db

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_benh_nhan_toi_da():
    return QuyDinh.BENH_NHAN_TOI_DA

def get_danh_sach_kham(ngay_kham):
    ds_kham = DanhSachKham.query.where(DanhSachKham.ngay_kham == int(ngay_kham)).first()

    if not ds_kham:
        ds_kham = DanhSachKham(ngay_kham=ngay_kham)
        db.session.add(ds_kham)

    return ds_kham