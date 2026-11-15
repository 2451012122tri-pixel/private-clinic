from flask import render_template, session, request

from eapp import app, login, dao

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/danhsachkham')
def danh_sach_kham():
    date = request.args.get('q')

    ds_benh_nhan = []
    if date:
        ds_benh_nhan = dao.get_danh_sach_benh_nhan(date)

    return render_template('danh_sach_kham.html', current_date=date, ds_benh_nhan=enumerate(ds_benh_nhan))

@app.route('/danhsachkham', methods=['POST'])
def xu_ly_danh_sach_kham():
    date = request.args.get('q')

    return render_template('danh_sach_kham.html', current_date=date)

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)