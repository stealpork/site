# Repirok

Приложения для поиска репетиторов и работы с ними

## Введение

Сайт Repirok создан для удобного поиска репетиторов, предлагая пользователям интуитивно понятный интерфейс, который позволяет быстро подобрать преподавателя по нужному предмету и уровню подготовки.

В функционал приложения входит возможность создания профиля репетитора с указанием личных данных, что помогает пользователям находить наиболее подходящих специалистов. Кроме того, Repirok предлагает инструменты для оценки качества услуг репетиторов и связи, обеспечивая прозрачность и удобство сервиса.

На текущем этапе реализации:
- **Не реализована полноценная админ-панель.**
- **Ошибки валидируются на сервере, но не выводятся пользователю на сайте.**


## Основные моменты:
1. На чем базируется приложение
2. Изначальный концепт дизайна
3. Главные функции
4. Основы кода




## Изначальный концепт дизайна

Исходный дизайн проекта доступен по ссылке:  
[Макет в Figma](https://www.figma.com/design/prHZnF96kZz5j3mBG7TvBL/Untitled?node-id=0-1&t=tcJ9ZRDsfKu0CZ2f-1)

Основной визуальный стиль основан на сочетании **тёмных фонов** с **небольшими жёлтыми акцентами**. Это придаёт интерфейсу современный и минималистичный вид, а также помогает выделять важные элементы, такие как кнопки действий и ключевые метки.  

Дизайн был задуман как лаконичный и простой, чтобы не перегружать внимание пользователя и обеспечить быструю навигацию.



# Главные функции

## Регистрация и вход

Пользователи могут создать учётную запись с указанием e-mail, логина и пароля. После регистрации они получают доступ ко всем функциям платформы. Авторизация осуществляется через безопасную проверку данных, с использованием Flask-Login.

## Профиль пользователя

Каждый пользователь может:

* редактировать личные данные (возраст, описание, специализация);
* загружать фотографию;
* управлять своими объявлениями;
* просматривать свои чаты и историю переписок.

## Объявления

Репетиторы могут размещать объявления с указанием:

* предмета и описания;
* стоимости занятий;
* местоположения и изображения;
* уникального заголовка.

Каждое объявление сохраняется в базе и отображается в профиле.

## Чаты

Система личных сообщений позволяет:

* автоматически создавать чат при обращении к репетитору;
* просматривать и продолжать уже начатую переписку;
* централизовать общение между пользователями.


## Основы кода

Веб-приложение, реализованно с использованием Flask. Ниже приведены основные моменты кода, с кратким описанием логики и вставками.

---

## 1. Регистрация пользователя

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    ...
    if form.validate_on_submit():
        ...
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
```

Регистрация новых пользователей через форму. Пароль хэшируется методом `set_password`, затем пользователь сохраняется в базу. Валидация формы и проверка на уникальность логина/email выполняются вручную.

---

## 2. Авторизация пользователя

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main_page'))
    return render_template('login.html', form=form)
```

Используется `Flask-Login` для авторизации. После успешной проверки логина и пароля пользователь аутентифицируется и перенаправляется на главную страницу.

---

## 3. Редактирование профиля

```python
@app.route('/user/<username>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    ...
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = f'id{user.id}.jpg'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.image_file = filename
        user.spezialize = request.form.get('spezialize')
        user.age = request.form.get('age')
        user.about = request.form.get('about')
        db.session.commit()
```

Позволяет пользователю редактировать свою информацию и загружать новый аватар. Данные сохраняются в базу, а аватар сохраняется на сервере. Проверка прав доступа также встроена.

---

## 4. Создание объявления

```python
@app.route('/user/<username>/make_ann', methods=['GET', 'POST'])
@login_required
def make_ann(username):
    ...
    if request.method == 'POST':
        ...
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
        return redirect(url_for('user_profile', username=username))
```

Пользователи могут публиковать объявления, прикрепляя к ним изображение. Все данные сохраняются в таблицу `Announcement`, включая цену, описание и локацию.

---

## 5. Создание/открытие чата

```python
@app.route('/create_or_open_chat/<int:recipient_id>')
@login_required
def create_or_open_chat(recipient_id):
    ...
    chat = Chat.query.filter(
        ((Chat.user1_id == user_id) & (Chat.user2_id == recipient_id)) |
        ((Chat.user1_id == recipient_id) & (Chat.user2_id == user_id))
    ).first()

    if chat:
        return redirect(url_for('chat', chat_id=chat.id))
    else:
        new_chat = Chat(user1_id=user_id, user2_id=recipient_id, ...)
        db.session.add(new_chat)
        db.session.commit()
        return redirect(url_for('chat', chat_id=new_chat.id))
```

Позволяет пользователям начать переписку. Если чат уже существует, он открывается. Иначе создаётся новая запись. Это обеспечивает единственный канал общения между каждой парой пользователей.
