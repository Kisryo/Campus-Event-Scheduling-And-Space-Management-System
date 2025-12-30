from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateTimeLocalField,
    SelectField, PasswordField, SubmitField
)
from wtforms.validators import (
    DataRequired, ValidationError, EqualTo, Length
)
from flask_wtf.file import FileField, FileAllowed
from models import Student, Lecturer, Organizer, Admin

# ========================================================
# 1. SIGNUP FORM (For Students)
# ========================================================
class SignupForm(FlaskForm):
    user_id = StringField(
        'Student ID',
        validators=[DataRequired(), Length(min=10, max=10, message="ID must be 10 characters long")],
        render_kw={"placeholder": "Student ID"}
    )
    user_name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={"placeholder": "Name"}
    )
    user_email = StringField(
        'Email',
        validators=[DataRequired()],
        render_kw={"placeholder": "Email"}
    )
    user_phone = StringField(
        'Phone number',
        validators=[DataRequired(), Length(min=10, max=11)],
        render_kw={"placeholder": "Phone Number (without -)"}
    )
    user_pwd = PasswordField(
        'Password',
        validators=[DataRequired(), EqualTo('confirm_pwd', message='Both passwords must match.')],
        render_kw={"placeholder": "Password"}
    )
    confirm_pwd = PasswordField(
        'Confirm Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Confirm Password"}
    )
    signup_submit = SubmitField('Sign up')

    def validate_user_id(self, user_id):
        # Check all 4 tables to ensure ID is unique
        id_data = user_id.data.strip()
        if (Student.query.get(id_data) or 
            Lecturer.query.get(id_data) or 
            Organizer.query.get(id_data) or 
            Admin.query.get(id_data)):
            raise ValidationError("This ID already exists in the system.")

    def validate_user_email(self, user_email):
        # Check allowed domains
        allowed_domains = ["@student.mmu.edu.my", "@mmu.edu.my", "@staff.mmu.edu.my"]
        email = user_email.data.lower().strip()

        if not any(email.endswith(domain) for domain in allowed_domains):
            raise ValidationError("Email must be a valid university email.")

        # Check unique email across all tables
        if (Student.query.filter_by(student_email=email).first() or
            Lecturer.query.filter_by(lecturer_email=email).first() or
            Organizer.query.filter_by(organizer_email=email).first() or
            Admin.query.filter_by(admin_email=email).first()):
            raise ValidationError("This email is already registered.")


# ========================================================
# 2. RESET PASSWORD FORM
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
# 3. EVENT FORM (Simplified & Fixed Date/Time)
# ========================================================
class EventForm(FlaskForm):
    event_name = StringField(
        'Event Title',
        validators=[DataRequired()],
        render_kw={"placeholder": "Event Title"}
    )
    
    # Dropdown for Categories (Populated in View)
    event_cat = SelectField(
        'Category',
        choices=[], 
        coerce=int,
        validators=[DataRequired()]
    )
    
    # FIXED: Combined Date & Time into one field to match Database
    event_start = DateTimeLocalField(
        'Start Date & Time', 
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M'
    )
    
    event_end = DateTimeLocalField(
        'End Date & Time', 
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M'
    )
    
    event_img = FileField(
        'Event Poster',
        validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only (jpg, png)')]
    )
    
    event_descr = TextAreaField(
        'Description',
        validators=[DataRequired()],
        render_kw={"placeholder": "Event details..."}
    )
    
    # Dropdown for Rooms (Populated in View)
    event_venue = SelectField(
        'Venue / Room',
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )
    
    # Removed complex TicketList (No Stripe)
    
    submit = SubmitField('Save Event')

    def validate_event_end(self, field):
        if field.data < self.event_start.data:
            raise ValidationError('End date cannot be earlier than start date.')
