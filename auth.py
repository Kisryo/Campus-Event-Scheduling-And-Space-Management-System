from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Organizer, Student

auth = Blueprint('auth', __name__)

# -----------------------------
# Organizer Signup
# -----------------------------
@auth.route('/signup/organizer', methods=['GET', 'POST'])
def signup_organizer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup_organizer'))

        if Organizer.query.filter_by(organizer_email=email).first():
            flash('Organizer email already registered.', 'danger')
            return redirect(url_for('auth.signup_organizer'))

        new_org = Organizer(
            organizer_id=f"O{Organizer.query.count()+1:03}",
            organizer_name=name,
            organizer_email=email,
            organizer_password=generate_password_hash(password),
            organizer_account_status="Active"
        )
        db.session.add(new_org)
        db.session.commit()

        flash('Organizer account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup_organizer.html')


# -----------------------------
# Student Signup
# -----------------------------
@auth.route('/signup/student', methods=['GET', 'POST'])
def signup_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup_student'))

        if Student.query.filter_by(student_email=email).first():
            flash('Student email already registered.', 'danger')
            return redirect(url_for('auth.signup_student'))

        new_student = Student(
            student_id=student_id,
            student_name=name,
            student_email=email,
            student_password=generate_password_hash(password),
            student_phone=phone,
            student_account_status="Active"
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Student account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup_student.html')


# -----------------------------
# Login
# -----------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = None
        role = None
        stored_password = None

        organizer = Organizer.query.filter_by(organizer_email=email).first()
        if organizer:
            user = organizer
            role = 'organizer'
            stored_password = organizer.organizer_password
        else:
            student = Student.query.filter_by(student_email=email).first()
            if student:
                user = student
                role = 'student'
                stored_password = student.student_password

        if not user:
            flash('Account not found.', 'danger')
            return redirect(url_for('auth.login'))

        if check_password_hash(stored_password, password):
            login_user(user)
            flash('Login successful!', 'success')

            if role == 'organizer':
                return redirect(url_for('organizer_dashboard'))
            elif role == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            flash('Incorrect password, try again.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# -----------------------------
# Logout
# -----------------------------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
