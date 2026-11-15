from flask import render_template, session, request, redirect

from eapp import app, login, dao

from datetime import date

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/danhsachkham')
def danh_sach_kham():
    ngay_kham = request.args.get('q')

    is_date_expired = False
    is_full = False

    ds_benh_nhan = []
    if ngay_kham:
        ds_benh_nhan = dao.get_danh_sach_benh_nhan(ngay_kham)

        if date.fromisoformat(ngay_kham) <= date.today():
            is_date_expired = True

        if len(ds_benh_nhan) >= dao.get_benh_nhan_toi_da():
            is_full = True

    return render_template('danh_sach_kham.html',
                           current_date=ngay_kham,
                           ds_benh_nhan=enumerate(ds_benh_nhan),
                           count=len(ds_benh_nhan),
                           date_expired=is_date_expired,
                           danh_sach_full=is_full)

@app.route('/danhsachkham', methods=['POST'])
def them_benh_nhan_vao_danh_sach_kham():
    ngay_kham = request.args.get('q')

    form = request.form
    bn = dao.create_benh_nhan(form.get('ho_ten'),
                         form.get('gioi_tinh'),
                         form.get('nam_sinh'),
                         form.get('dia_chi'),
                         form.get('so_dien_thoai'))

    dao.add_benh_nhan_to_ds_kham(bn, ngay_kham)

    return redirect(f'/danhsachkham?q={ngay_kham}')

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)