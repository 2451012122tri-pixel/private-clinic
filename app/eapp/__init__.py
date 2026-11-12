from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = '3e57c4bead8b63763afa878612a7aa891cf0524ea283f8039404fae588d6c4d7'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/clinicdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app=app)
# login = LoginManager(app=app)