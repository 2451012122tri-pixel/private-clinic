import random
from datetime import date
from eapp import app, db
from eapp.models import (init_sample_data, QuyDinh, BenhNhan, Thuoc,
                         DanhSachKham, ThongTinKham, PhieuKham, SoLuongThuoc, HoaDon)


def seed_thong_ke_3_nam():
    # Đảm bảo bảng, tài khoản mẫu, quy định, thuốc và bệnh nhân nền đã tồn tại
    init_sample_data()

    random.seed(42)
    bns = BenhNhan.query.all()
    thuocs = Thuoc.query.all()
    qd = QuyDinh.query.first()
    tien_kham_mac_dinh = qd.tien_kham if qd else 100000

    if not bns or not thuocs:
        print("Chưa có dữ liệu bệnh nhân hoặc thuốc để sinh đơn khám!")
        return

    benh_an_mau = [
        ('Sốt nhẹ, đau họng', 'Viêm họng cấp', 'Uống sau khi ăn sáng và tối'),
        ('Ho khan, sổ mũi', 'Cảm cúm thông thường', 'Uống ngày 2 lần sáng - chiều'),
        ('Đau bụng, rối loạn tiêu hóa', 'Rối loạn tiêu hóa', 'Uống trước bữa ăn 30 phút'),
        ('Mệt mỏi, chán ăn, suy nhược', 'Suy nhược cơ thể', 'Uống 1 lần vào buổi sáng'),
        ('Đau đầu, chóng mặt nhẹ', 'Rối loạn tiền đình nhẹ', 'Uống khi có triệu chứng, sau ăn'),
    ]

    cac_moc_thoi_gian = [
        (2024, range(1, 13), [6, 18, 26]),
        (2025, range(1, 13), [4, 14, 24]),
        (2026, range(1, 12), [5, 15]),
    ]

    so_ngay_them = 0
    for nam, ds_thang, ds_ngay in cac_moc_thoi_gian:
        for thang in ds_thang:
            for ngay in ds_ngay:
                ngay_kham = date(nam, thang, ngay)
                if ngay_kham > date.today():
                    continue
                if DanhSachKham.query.filter_by(ngay_kham=ngay_kham).first():
                    continue

                ds_kham = DanhSachKham(ngay_kham=ngay_kham)
                db.session.add(ds_kham)
                db.session.flush()
                so_ngay_them += 1

                so_ca = random.randint(1, 2)
                bn_trong_ngay = random.sample(bns, k=so_ca)

                for stt, bn in enumerate(bn_trong_ngay, start=1):
                    trieu_chung, loai_benh, cach_dung = random.choice(benh_an_mau)
                    ttk = ThongTinKham(
                        id_benh_nhan=bn.id,
                        id_ds_kham=ds_kham.id,
                        so_thu_tu=stt,
                        trang_thai_kham=1,
                        trang_thai_duyet=1
                    )
                    db.session.add(ttk)
                    db.session.flush()

                    pk = PhieuKham(
                        id_thong_tin_kham=ttk.id,
                        trieu_chung=trieu_chung,
                        loai_benh_du_doan=loai_benh
                    )
                    db.session.add(pk)
                    db.session.flush()

                    thuoc_ke = random.sample(thuocs, k=random.randint(1, 3))
                    tien_thuoc = 0
                    for t in thuoc_ke:
                        sl = random.randint(2, 10)
                        tien_thuoc += t.don_gia * sl
                        db.session.add(SoLuongThuoc(
                            id_thuoc=t.id,
                            id_phieu_kham=pk.id,
                            so_luong=sl,
                            cach_dung=cach_dung
                        ))

                    db.session.add(HoaDon(
                        id_phieu_kham=pk.id,
                        ngay_lap=ngay_kham,
                        tien_kham=tien_kham_mac_dinh,
                        tien_thuoc=tien_thuoc,
                        tong_tien=tien_kham_mac_dinh + tien_thuoc
                    ))

    db.session.commit()
    print(f"Đã nạp thành công dữ liệu test cho {so_ngay_them} ngày khám (giai đoạn 2024 - 2026)!")


if __name__ == '__main__':
    with app.app_context():
        seed_thong_ke_3_nam()