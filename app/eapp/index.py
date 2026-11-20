from flask import render_template, session, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from eapp import app, db, login, dao, utils
from eapp.models import UserRoleEnum, GioiTinh
import eapp.admin  # noqa: F401


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
        ds_kham = dao.get_danh_sach_kham(ngay_kham)

        if ds_kham:
            ds_kham_id = ds_kham.id

        ds_benh_nhan = dao.get_danh_sach_benh_nhan(ds_kham)

        if date.fromisoformat(ngay_kham) <= date.today():
            is_date_expired = True
            flash('Ngày khám cũ hơn hôm nay, chọn ngày khám khác để đăng ký khám', 'warning')

        if len(ds_benh_nhan) >= BENH_NHAN_TOI_DA:
            is_full = True
        print(session)
    return render_template('danh_sach_kham.html',
                           page_return='danhsachkham',
                           current_date=ngay_kham,
                           ds_kham_id=ds_kham_id,
                           ds_benh_nhan=enumerate(ds_benh_nhan),
                           count=len(ds_benh_nhan),
                           date_expired=is_date_expired,
                           danh_sach_full=is_full,
                           GIOI_TINH=dao.get_Gioi_Tinh(),
                           BENH_NHAN_TOI_DA=BENH_NHAN_TOI_DA)

@app.route('/danhsachkham', methods=['POST'])
def them_benh_nhan_vao_danh_sach_kham():
    ngay_kham = request.args.get('q')

    form = request.form

    str_gioi_tinh = form.get('gioi_tinh')
    gioi_tinh = utils.gioi_tinh_str_to_enum(str_gioi_tinh)

    bn = dao.create_benh_nhan(form.get('ho_ten'),
                         gioi_tinh,
                         form.get('nam_sinh'),
                         form.get('dia_chi'),
                         form.get('so_dien_thoai'))

    if bn and ngay_kham:
        ds_kham = dao.get_danh_sach_kham(ngay_kham)
        so_thu_tu = dao.get_next_so_thu_tu(ds_kham)

        ttk = dao.create_thong_tin_kham(bn, ds_kham, so_thu_tu)

        saved_ttk = session.get('saved_ttk')
        if not saved_ttk:
            saved_ttk = {}

        bn_session = {
            'id': bn.id,
            'so_thu_tu': so_thu_tu,
            'ho_ten': form.get('ho_ten'),
            'gioi_tinh': gioi_tinh.value,
            'nam_sinh': form.get('nam_sinh'),
            'dia_chi': form.get('dia_chi'),
            'so_dien_thoai': form.get('so_dien_thoai')
        }

        ds_kham_session = {
            'id': ds_kham.id,
            'ngay_kham': ngay_kham
        }

        saved_ttk[str(ttk.id)] = {
            "benh_nhan": bn_session,
            "ds_kham": ds_kham_session
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

    flash('Gửi danh sách lên hệ thống thành công, kiểm tra thông tin trong tin nhắn SMS trên Twilio hay trong tài khoản đăng nhập', 'success')
    return 'Successfully delete saved_ttk session'


@app.route('/admin-login', methods=['post'])
def admin_login_view():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    user = dao.authenticate_user(username=username, password=password)
    if not user:
        flash('Tên đăng nhập hoặc mật khẩu quản trị không chính xác!', 'danger')
    elif user.user_role != UserRoleEnum.QUAN_TRI:
        flash('Tài khoản này không có quyền truy cập cổng Quản trị!', 'danger')
    else:
        login_user(user=user)

    return redirect('/admin')


@app.route('/login')
def login_view():
    page_return = request.args.get('q')

    return render_template('login.html', page_return=page_return)

@app.route('/login', methods=['POST'])
def login_process():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    page_return = request.args.get('q')
    if not page_return:
        page_return = ''

    user = dao.authenticate_user(username=username, password=password)
    if not user:
        flash('Tên đăng nhập hoặc mật khẩu quản trị không chính xác!', 'danger')
    elif user.user_role == UserRoleEnum.QUAN_TRI:
        flash('Tài khoản này là của quản trị viên, nên đăng nhập ở trang admin', 'danger')
    else:
        login_user(user=user)
        return redirect(f'/{page_return}')

    return redirect('/login')


@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_process():
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    err_msg = None
    if not password or not confirm or password != confirm:
        err_msg = 'Mật khẩu không khớp!'
    else:
        data = request.form.copy()
        del data['confirm']

        try:
            dao.create_user(**data)
        except:
            err_msg = 'Tài khoản đã tồn tại!'

    if not err_msg:
        return redirect('/')

    return render_template('register.html', err_msg=err_msg)


@app.route('/logout')
def logout_view():
    is_admin = current_user.is_authenticated and current_user.user_role == UserRoleEnum.QUAN_TRI
    logout_user()
    if is_admin:
        return redirect('/admin')
    return redirect('/')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)