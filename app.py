from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import RegisterForm, LoginForm
import datetime
import hashlib
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'awgiuhbwo9eui12982t91y59iwusnfaslkf0qwH(QUHIUHBASIFBI9h129hh)'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/users_avatars'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'jpg'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    modified_date = db.Column(db.DateTime, default=datetime.datetime.now)
    spezialize = db.Column(db.String, unique=False, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    about = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='def.jpg')

    def set_password(self, password):
        self.hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.hashed_password == hashlib.sha256(password.encode('utf-8')).hexdigest()

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False, default = 0)
    place = db.Column(db.String(100), nullable=False, default="Скрыто")
    info = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='def.jpg')

class Reviews(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer = db.Column(db.String(64), nullable=False)
    info = db.Column(db.Text, nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user1_name = db.Column(db.String(100), nullable=False)
    user2_name = db.Column(db.String(100), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


def username_exists(username):
    return db.session.query(User.id).filter_by(username=username).scalar() is not None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def email_exists(email):
    return db.session.query(User.id).filter_by(email=email).scalar() is not None

@app.route('/login',  methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main_page'))
        else:
            return render_template('login.html', form=form, error='Неправильный email или пароль')
    return render_template('login.html', form=form)


@app.errorhandler(404)
def er_404(error):
    return "Неизвестная страничка"

@app.route('/user/<username>', methods=['GET'])
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.username != username:
        av_url = 'users_avatars/' + user.image_file
        spec = ''
        about = ''
        
        if user.spezialize is not None: spec = user.spezialize
        if user.about is not None: about = user.about
        age = user.age
        return render_template('user_page.html',default_avatar_url=av_url, us=user.username, age=age, about = about, spec = spec)
    else:
        av_url = 'users_avatars/' + user.image_file
        spec = ''
        about = ''
        if user.spezialize is not None: spec = user.spezialize
        if user.about is not None: about = user.about
        age = user.age
        return render_template('my_page_change.html',default_avatar_url=av_url, us=user.username, age=age, about = about, spec = spec, url_for_edit = f'{username}/edit_profile')
    
    
@app.route('/user/<username>/announcements', methods=['GET'])
@login_required
def look_ann(username):
    user = User.query.filter_by(username=username).first_or_404()
    announcements = Announcement.query.filter_by(user_id=user.id).all()
    reviews = Reviews.query.filter_by(author_id=user.id).all()
    return render_template('my_un.html', user=user, announcements=announcements, reviews=reviews)


@app.route('/redirect_after_ok/<username>')
@login_required
def redirect_after_ok(username):
    return redirect(url_for('user_profile', username=username))


@app.route('/create_or_open_chat/<int:recipient_id>')
@login_required
def create_or_open_chat(recipient_id):
    user_id = current_user.id
    user1 = User.query.filter_by(id=current_user.id).first_or_404()
    user2 = User.query.filter_by(id = recipient_id).first_or_404()
    chat = Chat.query.filter(
        ((Chat.user1_id == user_id) & (Chat.user2_id == recipient_id)) |
        ((Chat.user1_id == recipient_id) & (Chat.user2_id == user_id))
    ).first()

    if chat:
        return redirect(url_for('chat', chat_id=chat.id))
    else:
        new_chat = Chat(user1_id=user_id, user2_id=recipient_id, user1_name = user1.username, user2_name= user2.username)
        db.session.add(new_chat)
        db.session.commit()
        return redirect(url_for('chat', chat_id=new_chat.id))
    

@app.route('/chats')
@login_required
def chats():
    chats = Chat.query.filter((Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)).all()
    return render_template('messanger.html', chats=chats)

@app.route('/chat/<int:chat_id>')
@login_required
def chat(chat_id):
    user_id = current_user.id
    chat = Chat.query.get_or_404(chat_id)
    chats = Chat.query.filter(
            ((Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id))
        ).all()

    if chat.user1_id != user_id and chat.user2_id != user_id:
        return "Unauthorized", 403

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    return render_template('messanger.html', chat=chat, chats = chats, messages=messages,selected_chat=True)


@app.route('/send_message/<int:chat_id>', methods=['POST'])
@login_required
def send_message(chat_id):
    user_id = current_user.id
    chat = Chat.query.get_or_404(chat_id)


    content = request.form['content']
    if content:
        new_message = Message(chat_id=chat_id, sender_id=user_id, sender_name=current_user.username, content=content)
        db.session.add(new_message)
        db.session.commit()
    return redirect(url_for('chat', chat_id=chat_id))

@app.route('/user/<username>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.username != username:
        return redirect(url_for('denied'))
    else:

        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = f'id{user.id}.jpg'
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    user.image_file = filename
            user.spezialize = request.form.get('spezialize')
            user.age = request.form.get('age')
            user.about = request.form.get('about')
            db.session.commit()
            flash('Профиль обновлен! Нажмите ОК, чтобы продолжить.', 'persistent')
            av_url = 'users_avatars/' + user.image_file
            spec = ''
            about = ''
            if user.spezialize is not None: spec = user.spezialize
            if user.about is not None: about = user.about
            age = user.age
            return render_template('my_page_change_conf.html', default_avatar_url=av_url, us=user.username, age=age, about = about, spec = spec, message = 'Профиль обновлен! Нажмите ОК, чтобы продолжить.')
        else:
            av_url = 'users_avatars/' + user.image_file
            spec = ''
            about = ''
            if user.spezialize is not None: spec = user.spezialize
            if user.about is not None: about = user.about
            age = user.age
            return render_template('my_page_change_conf.html',default_avatar_url=av_url, us=user.username, age=age, about = about, spec = spec)


@app.route('/user/<username>/make_ann', methods=['GET', 'POST'])
@login_required
def make_ann(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.username != username:
        return redirect(url_for('denied'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        location = request.form.get('location')
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_file1 = filename
        else:
            image_file1 = None
        
        announcement = Announcement(
            name=title,
            info=description,
            price=price,
            place=location,
            image_file=image_file1,
            user_id=user.id,
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for('user_profile', username=username))
    else:
        av_url = 'users_avatars/' + user.image_file
        return render_template('create_announcement.html', us = user.username, default_avatar_url = av_url)
    
@app.route('/announcement/<int:announcement_id>')
@login_required
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    user = User.query.filter_by(id=announcement.user_id).first_or_404()
    reviews = Reviews.query.filter_by(author_id=user.id).all()
    return render_template('announcement_other.html', user=user, announcement=announcement, reviews=reviews)
    


@app.route('/user/<username>/submit_review', methods=['POST'])
@login_required
def submit_review(username):
    user = User.query.filter_by(username=username).first_or_404()
    review_text = request.form.get('review_text')
    if current_user.username != username:
        if review_text:
            new_review = Reviews(reviewer=current_user.username, info=review_text, author_id=user.id)
            db.session.add(new_review)
            db.session.commit()
            flash('Review submitted!', 'success')
        else:
            flash('Review cannot be blank.', 'error')
    else:
        flash('Вы не можете написать отзыв сами себе')

    return redirect(url_for('user_profile', username=username))

@app.route('/main_page')
@login_required
def main_page():
    price_from = request.args.get('price_from', type=int, default=None)
    price_to = request.args.get('price_to', type=int, default=None)
    search_term = request.args.get('search_term', default=None)
    sort_by = request.args.get('sort_by', default=None) 

    query = Announcement.query

    if price_from is not None:
        query = query.filter(Announcement.price >= price_from)
    if price_to is not None:
        query = query.filter(Announcement.price <= price_to)

    if search_term:
        query = query.filter(Announcement.name.contains(search_term))

    if sort_by == 'price_asc':
        query = query.order_by(Announcement.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Announcement.price.desc())

    announcements = query.all()
    return render_template('search_page.html',
                           announcements=announcements,
                           price_from=price_from,
                           price_to=price_to,
                           search_term=search_term,
                           sort_by=sort_by)


@app.route('/denied')
def denied():
    return "Несанкционированный доступ"

@app.route('/delete_ann/<int:announcement_id>')
@login_required
def delete_ann(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    user = User.query.filter_by(id=announcement.user_id).first_or_404()
    if current_user.username == user.username:
        db.session.delete(announcement)
        db.session.commit()
        return redirect(url_for('look_ann',username = current_user.username))
    else:
        return redirect(denied)    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    db_file = os.path.abspath(os.path.dirname(__file__)) + '/site.db'
    if not os.path.exists(db_file):
        with app.app_context():
            db.create_all()
    app.run(debug=True)