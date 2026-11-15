from eapp.models import User, QuyDinh, DanhSachKham, ThongTinKham, BenhNhan

from eapp import db

from datetime import date

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_benh_nhan_toi_da():
    return QuyDinh.BENH_NHAN_TOI_DA

def get_danh_sach_kham(ngay_kham):
    ds_kham = DanhSachKham.query.where(DanhSachKham.ngay_kham == ngay_kham).first()

    if not ds_kham and date.fromisoformat(ngay_kham) > date.today():
        ds_kham = DanhSachKham(ngay_kham=ngay_kham)
        db.session.add(ds_kham)
        db.session.commit()

    return ds_kham

def get_danh_sach_benh_nhan(ngay_kham):
    ds_kham = get_danh_sach_kham(ngay_kham)

    if not ds_kham:
        return []

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

def create_benh_nhan(ho_ten, gioi_tinh, nam_sinh, dia_chi, so_dien_thoai):
    bn = BenhNhan(ho_ten=ho_ten,
                  gioi_tinh=gioi_tinh,
                  nam_sinh=nam_sinh,
                  dia_chi=dia_chi,
                  so_dien_thoai=so_dien_thoai)

    db.session.add(bn)
    db.session.commit()

    return bn

def add_benh_nhan_to_ds_kham(bn, ngay_kham):
    ds_kham = get_danh_sach_kham(ngay_kham)

    ttk = ThongTinKham(trang_thai_kham=1,
                       benh_nhan_id=bn.id,
                       danh_sach_kham_id=ds_kham.id)

    db.session.add(ttk)
    db.session.commit()

    return ttk