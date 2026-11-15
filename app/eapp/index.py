from flask import render_template, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from eapp import app, login, dao
from eapp.models import UserRoleEnum
import eapp.admin  # noqa: F401


@app.route('/')
def index():
    return render_template('index.html')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


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


@app.route('/logout')
def logout_view():
    is_admin = current_user.is_authenticated and current_user.user_role == UserRoleEnum.QUAN_TRI
    logout_user()
    if is_admin:
        return redirect('/admin')
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)