from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-for-chess-school'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ===================== MODELS =====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='trainer')  # admin or trainer

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    group_name = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='planned')  # planned, started, finished

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100))

# Create DB
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route('/dashboard')
@login_required
def dashboard():
    lessons = Lesson.query.all()
    students_count = Student.query.count()
    return render_template('dashboard.html', lessons=lessons, students_count=students_count)

@app.route('/lessons')
@login_required
def lessons():
    lessons = Lesson.query.all()
    return render_template('lessons.html', lessons=lessons)

@app.route('/api/start_lesson/<int:lesson_id>', methods=['POST'])
@login_required
def start_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if lesson:
        lesson.status = 'started'
        db.session.commit()
        return jsonify({"success": True, "message": f"Урок '{lesson.title}' розпочато! Повідомлення надіслано."})
    return jsonify({"success": False})

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@app.route('/students')
@login_required
def students():
    students_list = Student.query.all()
    return render_template('students.html', students=students_list)

@app.route('/groups')
@login_required
def groups():
    return render_template('groups.html')

@app.route('/teachers')
@login_required
def teachers():
    return render_template('teachers.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)