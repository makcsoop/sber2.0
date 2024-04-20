import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user
from data import db_session
from flask_wtf import FlaskForm
from data.db_session import global_init, SqlAlchemyBase
from data.users import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
import urllib
import random
import sqlite3
import smtplib
from email.mime.text import MIMEText
import json

app = Flask(__name__)
frame_r = 0
login = ''
password = ''
role = ''
all_info = {}
current_menu_static = {}
current_menu = list()
user_info = []
submit_info = []
current_info_menu = []
all_info_ticket = None

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

class LoginForm(FlaskForm):
    login = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    surname = StringField('surname', validators=[DataRequired()])
    patronymic = StringField('patronymic')
    login = StringField('login', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('password_repeat', validators=[DataRequired()])
    rules = BooleanField('rules')
    submit = SubmitField('Submit')

########################BEGIN
class Orders(SqlAlchemyBase):
    tablename = 'orders'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    quality = sqlalchemy.Column(
        sqlalchemy.Integer)  # кол - во заказов    status = sqlalchemy.Column(sqlalchemy.Integer) #(По умолчанию)Новые 0, подтвержденные 1, отмененные 2    created_date = sqlalchemy.Column(sqlalchemy.DateTime,                                      default=datetime.datetime.now)


class Products(SqlAlchemyBase):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    quality = sqlalchemy.Column(
        sqlalchemy.Integer)  # количесвто, < наличие    nal = sqlalchemy.Column(sqlalchemy.Integer) # наличие    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    # админ class Orders(SqlAlchemyBase):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    status = sqlalchemy.Column(
        sqlalchemy.Integer)  # (По умолчанию)Новые 0, подтвержденные 1, отмененные 2    time = sqlalchemy.Column(sqlalchemy.Integer) # время заказа    userName = sqlalchemy.Column(sqlalchemy.Integer) # фио заказчика

###########################END
def send_email(message, getters):
    sender = "maroz15official@gmail.com"
    getter = 'znv10324@omeie.com'
    password = "apirvlcgklmdkmkh"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "Ваша регистрация"
        server.sendmail(sender, getters, msg.as_string())

        # server.sendmail(sender, sender, f"Subject: CLICK ME PLEASE!\n{message}")

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


def open_data():
    global all_info
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    sub = cursor.execute(f"""SELECT * FROM user""").fetchall()
    for i in range(len(sub)):
        all_info[f'{sub[i][0]}'] = [sub[i][2], sub[i][3], sub[i][4], sub[i][5], sub[i][1]]


def open_ticket():
    global all_info_ticket
    connect = sqlite3.connect('ticket_base.db')
    cursor = connect.cursor()
    all_info_ticket = cursor.execute(f"""SELECT * FROM ticket""").fetchall()


def open_menu():
    global all_info_menu, all_food
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    all_info = cursor.execute(f"""SELECT * FROM menu_dish ORDER BY category""").fetchall()
    all_info_menu = []
    for i in all_info:
        if int(i[-1]) == 1:
            all_info_menu.append([i[0], i[1], i[2], i[3], i[4], 'Завтрак'])
        elif int(i[-1]) == 2:
            all_info_menu.append([i[0], i[1], i[2], i[3], i[4], 'Первые блюда'])
        elif int(i[-1]) == 3:
            all_info_menu.append([i[0], i[1], i[2], i[3], i[4], 'Основные блюда'])
        elif int(i[-1]) == 4:
            all_info_menu.append([i[0], i[1], i[2], i[3], i[4], 'Закуски и салаты'])
        elif int(i[-1]) == 5:
            all_info_menu.append([i[0], i[1], i[2], i[3], i[4], 'Завтрак'])
    all_food = []
    for i in all_info_menu:
        all_food.append(i[1])
    all_info_menu = all_info_menu[:6]

def open_current_menu():
    global current_menu, current_menu_static
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    current_menu = cursor.execute(f"""SELECT * FROM current_menu ORDER BY time""").fetchall()
    for i in current_menu:
        i = list(i)
    current_menu = cursor.execute(f"""SELECT name, time, value, price, count FROM current_menu ORDER BY time""").fetchall()


open_current_menu()
open_data()
open_ticket()
open_menu()


with open('static/data.json', 'w', encoding='utf-8') as file:
    json.dump(all_info, file)
    file.close()


def generator_log():
    alp = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    random.shuffle(alp)
    vowels = set('bcdfghjklmnpqrstvwxz')
    flag = True
    while flag:
        for i in range(4):
            if alp[i] in vowels and set(alp[i:i + 2]) <= vowels:
                random.shuffle(alp)
                flag = True
                break
            else:
                flag = False
    return ''.join(alp[:6])


# @app.route('/')
# def index():
#     return render_template('index.html', obj=all_info)
db_session.global_init('main.db')
db_sess = db_session.create_session()
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        login_cur = db_sess.query(User).filter(User.login == form.login.data).first()
        if not login_cur:
            return render_template('index.html', title='Авторизация',
                                   form=form,
                                   message="Такого пользователя не существует")
        elif login_cur.password != form.password.data:
            return render_template('index.html', title='Авторизация',
                                   form=form,
                                   message="Неверный пароль")
    return render_template('register_new.html', title='Авторизация', form=form)

@app.route('/table-edit', methods=['GET', 'POST'])
def table_edit():
    name = str(request.args.get('name'))
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute(
        f"""DELETE from current_menu WHERE name = {name}""")
    for i in current_menu_static:
        for j in i:
            if name == j:
                del current_menu_static[current_menu.index(i)]
    connect.commit()
    connect.close()
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/new', methods=['GET', 'POST'])
def new():
    name = str(request.args.get('name'))
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    current = cursor.execute(f"""SELECT name, time, value, price, count FROM current_menu WHERE name = '{name}'""").fetchall()
    current.append("10")
    #curent_menu_static.append(current)
    for i in all_food:
        if i == name:
            print(i)
            break
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/reg', methods=['POST', 'GET'])
def reg():
    fullname = str(request.args.get('FIO'))
    email = str(request.args.get('email'))
    password1 = str(request.args.get('password1'))
    password2 = str(request.args.get('password2'))
    login = generator_log()
    send_email(message=f'Здравствуйте! Высылаем вам ваш логин для входа в систему: {login}', getters=[email])
    print(fullname, email, password1, password2)
    if password1 == password2:
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute(
            f"""INSERT INTO user (name, email, login, password, role) VALUES ('{fullname}', '{email}', '{login}', '{password1}', 'user')""")
        connect.commit()
        connect.close()
        open_data()
    return '', 200, {'Content-Type': 'text/plain'}


@app.route('/user')
def user():
    global all_info_menu
    user_info.clear()
    fullname = str(request.args.get('FIO'))
    email = str(request.args.get('email'))
    user_info.append(fullname)
    user_info.append(email)
    return render_template('menu_user.html', all_info=all_info_menu, current_menu=current_menu, name=fullname,
                           email=email)


@app.route('/subm', methods=['POST'])
def sub():
    global submit_info
    if request.method == 'POST':
        submit_info.clear()
        submit_info.append(str(request.args.get('name')))
        submit_info.append(str(request.args.get('fullname')))
        submit_info.append(str(request.args.get('email')))
        submit_info.append(str(request.args.get('text')))
        connect = sqlite3.connect('ticket_base.db')
        cursor = connect.cursor()
        cursor.execute(
            f"""INSERT INTO ticket (topic, name, email, description, status) VALUES ('{submit_info[0]}', '{submit_info[1]}', '{submit_info[2]}', '{submit_info[3]}', 'active')""")
        connect.commit()
        connect.close()
        return '', 200, {'Content-Type': 'text/plain'}


@app.route('/admin/profile')
def profile():
    global user_info
    print(user_info)
    return render_template('profile.html')


@app.route('/ticket')
def ticket():
    return render_template('ticket.html')


@app.route('/admin/profile/graph')
def graph():
    return render_template('graph.html')


@app.route('/admin/profile/analitic')
def analitic():
    return render_template('analitic.html')


@app.route('/user/basket')
def basket():
    return render_template('basket.html')


@app.route('/admin/profile/menu')
def menu():
    return render_template('menu.html', lst=current_info_menu)


@app.route('/admin/profile/menu/table')
def table():
    return render_template('table.html', lst=current_menu)


@app.route('/app1')
def app1():
    return jsonify(all_info)

@app.route('/api')
def api():
    return jsonify(current_menu_static)

@app.route('/api2')
def api2():
    return jsonify(all_food)

@app.route('/user/order')
def order():
    return render_template('order.html')


if __name__ == '__main__':
    app.debug = True
    db_session.global_init("db/user.db")
    app.run(host="localhost", port=5050)
