from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Student, Admin, Organizer, Lecturer, db
from flask_login import login_user, login_required, logout_user, current_user
from forms import SignupForm

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET'])
def index():
    return render_template("index.html", user=current_user)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        new_student = Student(
            student_id=form.user_id.data.strip(),
            student_name=form.user_name.data.strip(),
            student_email=form.user_email.data.lower().strip(),
            student_phone=form.user_phone.data.strip(),
            student_password=form.user_pwd.data, 
            student_account_status='Active'
        )
        
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. ID or Email may already exist.', 'danger')
            print(e)

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form.get('id').strip()
        password = request.form.get('password')

        # Check all 4 tables to find who is logging in
        student = Student.query.get(id)
        organizer = Organizer.query.get(id)
        lecturer = Lecturer.query.get(id)
        admin = Admin.query.get(id)

        user_to_login = None
        target_route = 'user_view.home' # Default fallback

        # ---  PASSWORD CHECKS ---
        
        # 1. Check Student
        if student and student.student_password == password:
            user_to_login = student
            target_route = 'student_view.home' 
            
        # 2. Check Organizer
        elif organizer and organizer.organizer_password == password:
            user_to_login = organizer
            target_route = 'organizer_view.dashboard'
            
        # 3. Check Lecturer
        elif lecturer and lecturer.lecturer_password == password:
            user_to_login = lecturer
            target_route = 'lecturer_view.dashboard'
            
        # 4. Check Admin
        elif admin and admin.admin_password == password:
            user_to_login = admin
            target_route = 'admin_view.admin_home'

        # Perform the actual login if a user was found and password matched
        if user_to_login:
            login_user(user_to_login, remember=True)
            return redirect(url_for(target_route))
        else:
            flash('Login failed. Check your ID and password.', 'danger')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.index'))
