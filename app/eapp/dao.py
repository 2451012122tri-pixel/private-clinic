from pickletools import dis

from eapp.models import User, QuyDinh, DanhSachKham, ThongTinKham, BenhNhan, GioiTinh

from eapp import db

from datetime import date

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_benh_nhan_toi_da():
    return QuyDinh.BENH_NHAN_TOI_DA.value

def create_danh_sach_kham(ngay_kham):
    ds_kham = DanhSachKham(ngay_kham=ngay_kham)
    db.session.add(ds_kham)
    db.session.commit()

    return ds_kham


def get_danh_sach_kham(ngay_kham):
    ds_kham = DanhSachKham.query.where(DanhSachKham.ngay_kham == ngay_kham).first()

    if not ds_kham and date.fromisoformat(ngay_kham) > date.today():
        create_danh_sach_kham(ngay_kham)

    return ds_kham

def get_danh_sach_benh_nhan(ds_kham):
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
    if not ho_ten or not gioi_tinh or not nam_sinh or not dia_chi or not so_dien_thoai:
        return None

    bn = BenhNhan(ho_ten=ho_ten,
                  gioi_tinh=gioi_tinh,
                  nam_sinh=nam_sinh,
                  dia_chi=dia_chi,
                  so_dien_thoai=so_dien_thoai)

    db.session.add(bn)
    db.session.commit()

    return bn

def get_next_so_thu_tu(ds_kham):
    if not ds_kham:
        return None

    ds_ttk = ThongTinKham.query.where(ThongTinKham.danh_sach_kham_id == ds_kham.id).all()
    
    if ds_ttk:
        so_thu_tu_cuoi = ds_ttk[-1].so_thu_tu

        if so_thu_tu_cuoi:
            return so_thu_tu_cuoi + 1
        else:
            return None

    return 1

def create_thong_tin_kham(bn, ds_kham, so_thu_tu=None):
    ttk = ThongTinKham(trang_thai_kham=1,
                       so_thu_tu=so_thu_tu,
                       benh_nhan_id=bn.id,
                       danh_sach_kham_id=ds_kham.id)

    db.session.add(ttk)
    db.session.commit()

    return ttk

def delete_thong_tin_kham(ttk_id):
    ttk = ThongTinKham.query.where(ThongTinKham.id == ttk_id).first()

    db.session.delete(ttk)
    db.session.commit()

    return True

def get_Gioi_Tinh():
    return GioiTinh

def gui_Twilio():
    pass