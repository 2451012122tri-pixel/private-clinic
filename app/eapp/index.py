from flask import render_template, session, request, redirect

from eapp import app, login, dao

from datetime import date

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/danhsachkham')
def danh_sach_kham():
    ngay_kham = request.args.get('q')

    ds_kham_id = -1
    is_date_expired = False
    is_full = False
    BENH_NHAN_TOI_DA = dao.get_benh_nhan_toi_da()

    ds_benh_nhan = []
    if ngay_kham:
        ds_benh_nhan = dao.get_danh_sach_benh_nhan(ngay_kham)

        if ds_benh_nhan:
            ds_kham_id = dao.get_danh_sach_kham(ngay_kham).id

        if date.fromisoformat(ngay_kham) <= date.today():
            is_date_expired = True

        if len(ds_benh_nhan) >= BENH_NHAN_TOI_DA:
            is_full = True

    return render_template('danh_sach_kham.html',
                           current_date=ngay_kham,
                           ds_kham_id=ds_kham_id,
                           ds_benh_nhan=enumerate(ds_benh_nhan),
                           count=len(ds_benh_nhan),
                           date_expired=is_date_expired,
                           danh_sach_full=is_full,
                           BENH_NHAN_TOI_DA=BENH_NHAN_TOI_DA)

@app.route('/danhsachkham', methods=['POST'])
def them_benh_nhan_vao_danh_sach_kham():
    ngay_kham = request.args.get('q')

    form = request.form
    bn = dao.create_benh_nhan(form.get('ho_ten'),
                         form.get('gioi_tinh'),
                         form.get('nam_sinh'),
                         form.get('dia_chi'),
                         form.get('so_dien_thoai'))

    if bn and ngay_kham:
        ttk = dao.create_thong_tin_kham(bn, ngay_kham)

        saved_ttk = session.get('saved_ttk')
        if not saved_ttk:
            saved_ttk = {}

        saved_ttk[str(ttk.id)] = {
            "benh_nhan_id": ttk.benh_nhan_id,
            "danh_sach_kham_id": ttk.danh_sach_kham_id
        }

        session['saved_ttk'] = saved_ttk

    return redirect(f'/danhsachkham?q={ngay_kham}')

@app.route('/danhsachkham/delete/<ttk_id>', methods=['DELETE'])
def xoa_benh_nhan_ra_danh_sach_kham(ttk_id):
    dao.delete_thong_tin_kham(int(ttk_id))

    session['saved_ttk'].pop(str(ttk_id), None)
    session.modified = True
    return 'Successfully delete a ttk'

@app.route('/danhsachkham', methods=['PATCH'])
def luu_danh_sach():
    session.pop('saved_ttk', None)
    return 'Successfully delete saved_ttk session'

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)