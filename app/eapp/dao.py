import hashlib
from sqlalchemy import func, extract
from eapp import db
from eapp.models import (User, QuyDinh, DonViThuoc, Thuoc,
                         SoLuongThuoc, PhieuKham, ThongTinKham, DanhSachKham, HoaDon, BenhNhan, GioiTinh)
from datetime import date


def authenticate_user(username, password):
    if username and password:
        pw_hash = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
        return User.query.filter(
            User.username.__eq__(username.strip()),
            User.password.__eq__(pw_hash)
        ).first()
    return None


def get_quy_dinh():
    qd = QuyDinh.query.first()
    if not qd:
        qd = QuyDinh(so_benh_nhan_toi_da=40, tien_kham=100000)
        db.session.add(qd)
        db.session.commit()
    return qd


def count_thuoc():
    return Thuoc.query.count()


def is_don_vi_used(id_don_vi):
    return Thuoc.query.filter(Thuoc.id_don_vi.__eq__(int(id_don_vi))).count() > 0


def is_thuoc_used(id_thuoc):
    return SoLuongThuoc.query.filter(SoLuongThuoc.id_thuoc.__eq__(int(id_thuoc))).count() > 0


def stats_doanh_thu_thang(thang, nam):
    query = (db.session.query(
                extract('day', HoaDon.ngay_lap).label('ngay'),
                func.count(HoaDon.id).label('so_benh_nhan'),
                func.sum(HoaDon.tong_tien).label('doanh_thu')
            )
            .filter(extract('month', HoaDon.ngay_lap).__eq__(int(thang)),
                    extract('year', HoaDon.ngay_lap).__eq__(int(nam)))
            .group_by(extract('day', HoaDon.ngay_lap))
            .order_by(extract('day', HoaDon.ngay_lap)).all())

    tong_doanh_thu = sum(r.doanh_thu for r in query) if query else 0
    ket_qua = []
    for r in query:
        ty_le = (r.doanh_thu / tong_doanh_thu * 100) if tong_doanh_thu > 0 else 0
        ket_qua.append({
            'ngay': int(r.ngay),
            'so_benh_nhan': int(r.so_benh_nhan),
            'doanh_thu': float(r.doanh_thu),
            'ty_le': round(ty_le, 2)
        })

    return ket_qua, float(tong_doanh_thu)


def stats_su_dung_thuoc_thang(thang, nam):
    return (db.session.query(
                Thuoc.id,
                Thuoc.ten_thuoc,
                DonViThuoc.ten_don_vi,
                func.sum(SoLuongThuoc.so_luong).label('so_luong'),
                func.count(SoLuongThuoc.id).label('so_lan_dung')
            )
            .join(DonViThuoc, Thuoc.id_don_vi.__eq__(DonViThuoc.id))
            .join(SoLuongThuoc, Thuoc.id.__eq__(SoLuongThuoc.id_thuoc))
            .join(PhieuKham, SoLuongThuoc.id_phieu_kham.__eq__(PhieuKham.id))
            .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
            .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id))
            .filter(extract('month', DanhSachKham.ngay_kham).__eq__(int(thang)),
                    extract('year', DanhSachKham.ngay_kham).__eq__(int(nam)))
            .group_by(Thuoc.id, Thuoc.ten_thuoc, DonViThuoc.ten_don_vi)
            .order_by(func.sum(SoLuongThuoc.so_luong).desc()).all())


def get_user_by_id(user_id):
    return User.query.get(int(user_id))

def get_benh_nhan_toi_da():
    return get_quy_dinh().so_benh_nhan_toi_da

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

    query = (db.session.query(ThongTinKham.id, ThongTinKham.id_benh_nhan)
             .where(ThongTinKham.id_ds_kham==ds_kham.id)
             .all())

    ds_benh_nhan = []

    for value in query:
        bn = get_benh_nhan(value[1])
        ds_benh_nhan.append(bn)

    return ds_benh_nhan

def get_benh_nhan(id_benh_nhan):
    return BenhNhan.query.get(id_benh_nhan)

def get_benh_nhan_by_stt(so_dien_thoai):
    return BenhNhan.query.where(BenhNhan.so_dien_thoai == so_dien_thoai).first()

def create_benh_nhan(ho_ten, gioi_tinh, nam_sinh, dia_chi, so_dien_thoai):
    if not ho_ten or not gioi_tinh or not nam_sinh or not dia_chi or not so_dien_thoai:
        return None

    bn_trung_sdt = get_benh_nhan_by_stt(so_dien_thoai)

    if bn_trung_sdt:
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

    ds_ttk = ThongTinKham.query.where(ThongTinKham.id_ds_kham == ds_kham.id).all()
    
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
                       id_benh_nhan=bn.id,
                       id_ds_kham=ds_kham.id)

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
