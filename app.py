from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chessfm-super-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chessfm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ===================== MODELS =====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='trainer')   # trainer or admin

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    group_name = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='planned')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

# ===================== INIT =====================
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===================== ADMIN PASSCODES =====================
ADMIN_PASSCODE = "7101"
SUPER_PASSCODE = "6479"

# ===================== ROUTES =====================
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Невірний логін або пароль')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Заповніть усі поля", "error")
        elif User.query.filter_by(username=username).first():
            flash("Ім'я користувача вже зайняте", "error")
        else:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Реєстрація успішна! Увійдіть.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    lessons = Lesson.query.order_by(Lesson.date.desc()).limit(6).all()
    students_count = Student.query.count()
    return render_template('dashboard.html', lessons=lessons, students_count=students_count)

# ===================== ADMIN PANEL =====================
@app.route('/admin')
@login_required
def admin():
    if not session.get('admin_access'):
        return redirect(url_for('admin_passcode'))
    return render_template('admin.html')

@app.route('/admin/passcode', methods=['GET', 'POST'])
def admin_passcode():
    if request.method == 'POST':
        code = request.form.get('passcode')
        if code == ADMIN_PASSCODE:
            session['admin_access'] = True
            flash("Доступ до адмін-панелі надано", "success")
            return redirect(url_for('admin'))
        else:
            flash("Невірний код доступу", "error")
    return render_template('admin_passcode.html')

@app.route('/admin/super', methods=['GET', 'POST'])
def admin_super():
    if not session.get('admin_access'):
        return redirect(url_for('admin_passcode'))
    if request.method == 'POST':
        code = request.form.get('supercode')
        if code == SUPER_PASSCODE:
            session['super_access'] = True
            flash("Супер-доступ відкрито", "success")
            return redirect(url_for('admin_super_panel'))
        else:
            flash("Невірний супер-код", "error")
    return render_template('admin_super_passcode.html')

@app.route('/admin/super/panel')
@login_required
def admin_super_panel():
    if not session.get('super_access'):
        return redirect(url_for('admin'))
    users = User.query.all()
    return render_template('admin_super_panel.html', users=users)

# ===================== MANAGEMENT ROUTES =====================
@app.route('/admin/add_lesson', methods=['POST'])
@login_required
def add_lesson():
    if not session.get('admin_access'):
        return jsonify({"success": False})
    title = request.form.get('title')
    group_name = request.form.get('group_name')
    if title:
        lesson = Lesson(title=title, group_name=group_name)
        db.session.add(lesson)
        db.session.commit()
        flash("Урок успішно додано", "success")
    return redirect(url_for('admin'))

# Similar routes for students and groups will be added next

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
