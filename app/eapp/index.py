from flask import render_template

from eapp import app, login, dao

@app.route('/')
def index():
    return render_template('index.html')

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)