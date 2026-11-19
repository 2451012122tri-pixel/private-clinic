import hashlib
from sqlalchemy import func, extract
from sqlalchemy.orm import joinedload
from eapp import db
from eapp.models import (User, QuyDinh, DonViThuoc, Thuoc,
                         SoLuongThuoc, PhieuKham, ThongTinKham, DanhSachKham, HoaDon, BenhNhan, GioiTinh, UserRoleEnum)
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


def count_thuoc_by_don_vi():
    return (db.session.query(
                DonViThuoc.id,
                DonViThuoc.ten_don_vi,
                func.count(Thuoc.id)
            )
            .join(Thuoc, Thuoc.id_don_vi.__eq__(DonViThuoc.id), isouter=True)
            .group_by(DonViThuoc.id, DonViThuoc.ten_don_vi)
            .order_by(DonViThuoc.id).all())

def get_thuoc_list_query():
    # Truy vấn danh sách thuốc kèm JOIN sang bảng DonViThuoc để lấy tên đơn vị tính
    return db.session.query(Thuoc).options(joinedload(Thuoc.don_vi_thuoc))


def get_all_ten_thuoc():
    rows = (db.session.query(Thuoc.ten_thuoc)
            .distinct()
            .order_by(Thuoc.ten_thuoc.asc())
            .all())
    return [r.ten_thuoc for r in rows if r.ten_thuoc]


def get_all_ten_don_vi():
    rows = (db.session.query(DonViThuoc.ten_don_vi)
            .distinct()
            .order_by(DonViThuoc.ten_don_vi.asc())
            .all())
    return [r.ten_don_vi for r in rows if r.ten_don_vi]


def check_thuoc_exists(ten_thuoc, exclude_id=None):
    query = Thuoc.query.filter(func.lower(Thuoc.ten_thuoc).__eq__(ten_thuoc.strip().lower()))
    if exclude_id:
        query = query.filter(Thuoc.id != int(exclude_id))
    return query.first() is not None


def check_don_vi_exists(ten_don_vi, exclude_id=None):
    query = DonViThuoc.query.filter(func.lower(DonViThuoc.ten_don_vi).__eq__(ten_don_vi.strip().lower()))
    if exclude_id:
        query = query.filter(DonViThuoc.id != int(exclude_id))
    return query.first() is not None


def get_thuoc_usage_stats(id_thuoc):
    # JOIN 4 bảng Thuoc -> SoLuongThuoc -> PhieuKham -> HoaDon để thống kê tình hình sử dụng của từng thuốc
    row = (db.session.query(
                func.coalesce(func.sum(SoLuongThuoc.so_luong), 0).label('tong_so_luong'),
                func.count(func.distinct(PhieuKham.id)).label('so_phieu_kham'),
                func.coalesce(func.sum(SoLuongThuoc.so_luong * Thuoc.don_gia), 0).label('tong_doanh_thu')
            )
            .join(SoLuongThuoc, Thuoc.id.__eq__(SoLuongThuoc.id_thuoc))
            .join(PhieuKham, SoLuongThuoc.id_phieu_kham.__eq__(PhieuKham.id))
            .join(HoaDon, PhieuKham.id.__eq__(HoaDon.id_phieu_kham), isouter=True)
            .filter(Thuoc.id.__eq__(int(id_thuoc)))
            .first())
    return {
        'tong_so_luong': int(row.tong_so_luong or 0) if row else 0,
        'so_phieu_kham': int(row.so_phieu_kham or 0) if row else 0,
        'tong_doanh_thu': float(row.tong_doanh_thu or 0) if row else 0
    }

def get_available_years():
    rows = (db.session.query(extract('year', HoaDon.ngay_lap).label('nam'))
            .join(PhieuKham, HoaDon.id_phieu_kham.__eq__(PhieuKham.id))
            .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
            .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id))
            .distinct()
            .order_by(extract('year', HoaDon.ngay_lap).desc())
            .all())
    return [int(r.nam) for r in rows if r.nam is not None]


def get_available_months(year):
    if not year:
        return []
    rows = (db.session.query(extract('month', HoaDon.ngay_lap).label('thang'))
            .join(PhieuKham, HoaDon.id_phieu_kham.__eq__(PhieuKham.id))
            .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
            .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id))
            .filter(extract('year', HoaDon.ngay_lap).__eq__(int(year)))
            .distinct()
            .order_by(extract('month', HoaDon.ngay_lap).asc())
            .all())
    return [int(r.thang) for r in rows if r.thang is not None]

def get_available_thuoc(thang=None, nam=None):
    query = (db.session.query(Thuoc.id, Thuoc.ten_thuoc)
             .join(SoLuongThuoc, Thuoc.id.__eq__(SoLuongThuoc.id_thuoc))
             .join(PhieuKham, SoLuongThuoc.id_phieu_kham.__eq__(PhieuKham.id))
             .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
             .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id)))

    if thang:
        query = query.filter(extract('month', DanhSachKham.ngay_kham).__eq__(int(thang)))
    if nam:
        query = query.filter(extract('year', DanhSachKham.ngay_kham).__eq__(int(nam)))

    return query.distinct().order_by(Thuoc.ten_thuoc.asc()).all()

def stats_doanh_thu_theo_thoi_gian(year, time='month'):
    if time not in ('month', 'quarter'):
        time = 'month'

    thoi_gian_col = extract(time, HoaDon.ngay_lap)
    query = (db.session.query(
                thoi_gian_col.label('thoi_gian'),
                func.count(func.distinct(BenhNhan.id)).label('so_benh_nhan'),
                func.count(HoaDon.id).label('so_luot_kham'),
                func.sum(HoaDon.tong_tien).label('doanh_thu')
            )
            .join(PhieuKham, HoaDon.id_phieu_kham.__eq__(PhieuKham.id))
            .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
            .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id))
            .join(BenhNhan, ThongTinKham.id_benh_nhan.__eq__(BenhNhan.id))
            .filter(extract('year', HoaDon.ngay_lap).__eq__(int(year)))
            .group_by(thoi_gian_col)
            .order_by(thoi_gian_col).all())

    tong_doanh_thu = sum(float(r.doanh_thu or 0) for r in query)
    ket_qua = []
    for r in query:
        dt = float(r.doanh_thu or 0)
        ty_le = (dt / tong_doanh_thu * 100) if tong_doanh_thu > 0 else 0
        ket_qua.append({
            'thoi_gian': int(r.thoi_gian),
            'so_benh_nhan': int(r.so_benh_nhan),
            'so_luot_kham': int(r.so_luot_kham),
            'doanh_thu': dt,
            'ty_le': round(ty_le, 2)
        })

    return ket_qua, tong_doanh_thu


def stats_doanh_thu_thang(thang, nam):
    ngay_col = extract('day', HoaDon.ngay_lap)
    query = (db.session.query(
                ngay_col.label('ngay'),
                func.count(func.distinct(BenhNhan.id)).label('so_benh_nhan'),
                func.sum(HoaDon.tong_tien).label('doanh_thu')
            )
            .join(PhieuKham, HoaDon.id_phieu_kham.__eq__(PhieuKham.id))
            .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
            .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id))
            .join(BenhNhan, ThongTinKham.id_benh_nhan.__eq__(BenhNhan.id))
            .filter(extract('month', HoaDon.ngay_lap).__eq__(int(thang)),
                    extract('year', HoaDon.ngay_lap).__eq__(int(nam)))
            .group_by(ngay_col)
            .order_by(ngay_col).all())

    tong_doanh_thu = sum(float(r.doanh_thu or 0) for r in query) if query else 0
    ket_qua = []
    for r in query:
        dt = float(r.doanh_thu or 0)
        ty_le = (dt / tong_doanh_thu * 100) if tong_doanh_thu > 0 else 0
        ket_qua.append({
            'ngay': int(r.ngay),
            'so_benh_nhan': int(r.so_benh_nhan),
            'doanh_thu': dt,
            'ty_le': round(ty_le, 2)
        })

    return ket_qua, float(tong_doanh_thu)


def stats_su_dung_thuoc_thang(thang, nam, kw=None):
    query = (db.session.query(
                Thuoc.id,
                Thuoc.ten_thuoc,
                DonViThuoc.ten_don_vi,
                func.sum(SoLuongThuoc.so_luong).label('so_luong'),
                func.count(func.distinct(PhieuKham.id)).label('so_lan_dung'),
                func.sum(SoLuongThuoc.so_luong * Thuoc.don_gia).label('doanh_thu')
            )
            .join(DonViThuoc, Thuoc.id_don_vi.__eq__(DonViThuoc.id))
            .join(SoLuongThuoc, Thuoc.id.__eq__(SoLuongThuoc.id_thuoc))
            .join(PhieuKham, SoLuongThuoc.id_phieu_kham.__eq__(PhieuKham.id))
            .join(ThongTinKham, PhieuKham.id_thong_tin_kham.__eq__(ThongTinKham.id))
            .join(DanhSachKham, ThongTinKham.id_ds_kham.__eq__(DanhSachKham.id))
            .filter(extract('month', DanhSachKham.ngay_kham).__eq__(int(thang)),
                    extract('year', DanhSachKham.ngay_kham).__eq__(int(nam))))

    if kw and kw.strip():
        query = query.filter(Thuoc.ten_thuoc.contains(kw.strip()))

    return (query.group_by(Thuoc.id, Thuoc.ten_thuoc, DonViThuoc.ten_don_vi)
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
             .where(ThongTinKham.id_ds_kham == ds_kham.id)
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

def create_user(name, username, password, user_role=UserRoleEnum.NGUOI_DUNG):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
    u = User(name=name.strip(), username=username.strip(), password=password, user_role=user_role)

    db.session.add(u)
    db.session.commit()