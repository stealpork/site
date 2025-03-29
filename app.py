from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from forms import RegisterForm
from classes import User, Base
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very_secret_key_for_secret_man'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



@app.route('/')
def index():
    return render_template('starter.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    username_error = ''
    email_error = ''
    if form.validate_on_submit():
        if username_exists(form.username.data):
            username_error = 'Пользователь с таким логином уже существует.'
        if email_exists(form.email.data):
            email_error = 'Пользователь с таким email уже существует.'
        if username_error or email_error:
            return render_template('register.html', form=form, username_error=username_error, email_error=email_error)
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('register.html', form=form)


def username_exists(username):
    return db.session.query(User.id).filter_by(username=username).scalar() is not None


def email_exists(email):
    return db.session.query(User.id).filter_by(email=email).scalar() is not None


@app.route('/success')
def success():
    return "Регистрация прошла успешно!"

if __name__ == '__main__':
    db_file = os.path.abspath(os.path.dirname(__file__)) + '/site.db'
    if not os.path.exists(db_file):
        with app.app_context():
            Base.metadata.create_all(db.engine)
    app.run(debug=True)