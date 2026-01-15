from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateTimeLocalField,
    SelectField, PasswordField, SubmitField
)
from wtforms.validators import (
    DataRequired, ValidationError,Email, EqualTo, Length
)
from models import Student, Lecturer, Organizer, Admin

# ========================================================
# 1. SIGNUP FORM (For Students Only)
# ========================================================
class SignupForm(FlaskForm):
    user_id = StringField(
        'Student ID',
        validators=[DataRequired(), Length(min=10, max=10, message="ID must be exactly 10 characters.")],
        render_kw={"placeholder": "Student ID"}
    )
    user_name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={"placeholder": "Full Name"}
    )
    user_email = StringField(
        'Email',
        validators=[DataRequired()],
        render_kw={"placeholder": "Student Email"}
    )
    user_phone = StringField(
        'Phone number',
        validators=[DataRequired(), Length(min=10, max=13)],
        render_kw={"placeholder": "Phone Number (with -)"}
    )
    user_pwd = PasswordField(
        'Password',
        validators=[DataRequired(), EqualTo('confirm_pwd', message='Passwords must match.')],
        render_kw={"placeholder": "Password"}
    )
    confirm_pwd = PasswordField(
        'Confirm Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Confirm Password"}
    )
    signup_submit = SubmitField('Register Student')

    def validate_user_id(self, user_id):
        # Check all 4 tables to ensure ID is unique across the entire system
        id_data = user_id.data.strip()
        if (Student.query.get(id_data) or 
            Lecturer.query.get(id_data) or 
            Organizer.query.get(id_data) or 
            Admin.query.get(id_data)):
            raise ValidationError("This ID already exists in the system.")

    def validate_user_email(self, user_email):
        # STRICT VALIDATION: Only allow student domain for this form
        allowed_domains = ["@student.mmu.edu.my"]
        email = user_email.data.lower().strip()

        if not any(email.endswith(domain) for domain in allowed_domains):
            raise ValidationError("Students must use a valid @student.mmu.edu.my email.")

        # Check all 4 tables to ensure Email is unique
        if (Student.query.filter_by(student_email=email).first() or
            Lecturer.query.filter_by(lecturer_email=email).first() or
            Organizer.query.filter_by(organizer_email=email).first() or
            Admin.query.filter_by(admin_email=email).first()):
            raise ValidationError("This email is already registered.")


# ========================================================
# 2. PASSWORD RESET FORM (For Profile Page)
# ========================================================
class ResetPasswordForm(FlaskForm):
    old_pwd = PasswordField(
        'Old Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter Old Password"}
    )
    new_pwd = PasswordField(
        'New Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter New Password"}
    )
    confirm_new_pwd = PasswordField(
        'Confirm New Password', 
        validators=[DataRequired(), EqualTo('new_pwd', message='Passwords must match.')],
        render_kw={"placeholder": "Confirm New Password"}
    )

    def validate_new_pwd(self, new_pwd):
        if new_pwd.data == self.old_pwd.data:
            raise ValidationError("New password cannot be the same as the old password.")


# ========================================================
# 3. FORGOT PASSWORD FORM (Request Reset Link)
# ========================================================
class ForgotPasswordForm(FlaskForm):
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your registered email"}
    )
    submit = SubmitField('Send Reset Link')

# ========================================================
# 4. SET NEW PASSWORD
# ========================================================
class SetNewPasswordForm(FlaskForm):
    new_pwd = PasswordField(
        'New Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter New Password"}
    )
    confirm_new_pwd = PasswordField(
        'Confirm New Password', 
        validators=[DataRequired(), EqualTo('new_pwd', message='Passwords must match.')],
        render_kw={"placeholder": "Confirm New Password"}
    )
