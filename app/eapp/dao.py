from eapp.models import User, QuyDinh, DanhSachKham, ThongTinKham, BenhNhan

from eapp import db

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_benh_nhan_toi_da():
    return QuyDinh.BENH_NHAN_TOI_DA

def get_danh_sach_kham(ngay_kham):
    ds_kham = DanhSachKham.query.where(DanhSachKham.ngay_kham == ngay_kham).first()

    if not ds_kham:
        ds_kham = DanhSachKham(ngay_kham=ngay_kham)
        db.session.add(ds_kham)

    return ds_kham

def get_danh_sach_benh_nhan(ngay_kham):
    ds_kham = get_danh_sach_kham(ngay_kham)

    query = (db.session.query(ThongTinKham.id, ThongTinKham.benh_nhan_id)
             .where(ThongTinKham.danh_sach_kham_id==ds_kham.id)
             .all())

    ds_benh_nhan = []

    for value in query:
        bn = get_benh_nhan(value[1])
        ds_benh_nhan.append(bn)

    return ds_benh_nhan

def get_benh_nhan(benh_nhan_id):
    return BenhNhan.query.get(benh_nhan_id)