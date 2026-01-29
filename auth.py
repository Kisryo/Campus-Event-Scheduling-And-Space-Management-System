from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import Student, Admin, Organizer, Lecturer, db
from flask_login import login_user, login_required, logout_user, current_user
from markupsafe import Markup # Required for adding links in Flash messages

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET'])
def index():
    return render_template("index.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user_found = None
        user_type = None
        target_route = 'student_view.home'

        # --- 1. LOCATE USER BY EMAIL ---
        
        # Check Student
        student = Student.query.filter_by(student_email=email).first()
        if student:
            user_found = student
            user_type = 'student'
            target_route = 'student_view.home'
            
        # Check Organizer
        if not user_found:
            organizer = Organizer.query.filter_by(organizer_email=email).first()
            if organizer:
                user_found = organizer
                user_type = 'organizer'
                target_route = 'organizer_view.dashboard'

        # Check Lecturer
        if not user_found:
            lecturer = Lecturer.query.filter_by(lecturer_email=email).first()
            if lecturer:
                user_found = lecturer
                user_type = 'lecturer'
                target_route = 'lecturer_view.dashboard'

        # Check Admin
        if not user_found:
            admin = Admin.query.filter_by(admin_email=email).first()
            if admin:
                user_found = admin
                user_type = 'admin'
                target_route = 'admin_view.admin_home'

        # --- 2. VALIDATE USER ---
        if user_found:
            # Get specific password and status fields dynamically
            db_password = getattr(user_found, f"{user_type}_password")
            
            # Check Password
            if db_password == password:
                login_user(user_found, remember=True)
                return redirect(url_for(target_route))
            
            # SCENARIO 1(a): Wrong Password
            else:
                link = url_for('auth.forgot_password')
                message = Markup(f'Incorrect password. <a href="{link}" class="alert-link">Forgot Password?</a>')
                flash(message, 'danger')
        
        else:
            flash('No account found', 'danger')

    return render_template("login.html", user=current_user)


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # 1. Get email directly from the form
        email = request.form.get('email', '').strip().lower()
        
        # 2. Check Database (Manual Check)
        user = (
            Student.query.filter_by(student_email=email).first() or
            Organizer.query.filter_by(organizer_email=email).first() or
            Lecturer.query.filter_by(lecturer_email=email).first() or
            Admin.query.filter_by(admin_email=email).first()
        )

        if user:
            # 3. Store email in session (CRITICAL for next step)
            session['reset_email'] = email
            flash('Email verified. Please set your new password.', 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('No account found with that email.', 'danger')

    return render_template('forgot_password.html')


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # 1. Security Check: Ensure they came from Step 1
    if 'reset_email' not in session:
        flash('Please verify your email first.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        # 2. Get passwords manually
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')

        if new_pwd != confirm_pwd:
            flash('Passwords do not match.', 'danger')
        else:
            email = session['reset_email']
            
            # 3. Find user again to update
            student = Student.query.filter_by(student_email=email).first()
            organizer = Organizer.query.filter_by(organizer_email=email).first()
            lecturer = Lecturer.query.filter_by(lecturer_email=email).first()
            admin = Admin.query.filter_by(admin_email=email).first()

            try:
                if student:
                    student.student_password = new_pwd
                elif organizer:
                    organizer.organizer_password = new_pwd
                elif lecturer:
                    lecturer.lecturer_password = new_pwd
                elif admin:
                    admin.admin_password = new_pwd
                
                db.session.commit()
                
                # 4. Success: Clear session & Redirect
                session.pop('reset_email', None)
                flash('Password reset successful! You can now login.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                flash('Error updating password.', 'danger')

    return render_template('reset_password.html')

@auth.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('You have been logged out successfully.', 'info')
    except Exception:
        flash('Logout error. Please refresh and retry', 'danger')

    return redirect(url_for('auth.index'))
