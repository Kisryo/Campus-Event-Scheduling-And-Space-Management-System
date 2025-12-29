from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateField, TimeField, DateTimeLocalField,
    SelectField, PasswordField, FieldList, FormField, DecimalField,
    IntegerField, SubmitField
)
from wtforms.validators import (
    DataRequired, ValidationError, EqualTo, Length,
    NumberRange, InputRequired
)
from flask_wtf.file import FileField, FileAllowed
# IMPORTS UPDATED: Import all 4 actor models to check for duplicates
from models import Student, Lecturer, Organizer, Admin

class SignupForm(FlaskForm):
    user_id = StringField(
        'Student ID',
        validators=[DataRequired(), Length(min=10, max=10)],
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
        # Check all 4 tables to ensure ID is unique across the system
        id_data = user_id.data.strip()
        if (Student.query.filter_by(student_id=id_data).first() or
            Lecturer.query.filter_by(lecturer_id=id_data).first() or
            Organizer.query.filter_by(organizer_id=id_data).first() or
            Admin.query.filter_by(admin_id=id_data).first()):
            raise ValidationError("This ID already exists in the system.")

    def validate_user_email(self, user_email):
        # Allowed university domains
        allowed_domains = [
            "@student.mmu.edu.my",
            "@mmu.edu.my",
            "@staff.mmu.edu.my"
        ]
        email = user_email.data.lower().strip()

        # Check domain validity
        if not any(email.endswith(domain) for domain in allowed_domains):
            raise ValidationError(
                "Email must be a valid university email (student, lecturer, or staff)."
            )

        # Check all 4 tables to ensure Email is unique
        if (Student.query.filter_by(student_email=email).first() or
            Lecturer.query.filter_by(lecturer_email=email).first() or
            Organizer.query.filter_by(organizer_email=email).first() or
            Admin.query.filter_by(admin_email=email).first()):
            raise ValidationError("This email is already registered.")


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

class TicketForm(FlaskForm):
    ticket_type = StringField(
        'Ticket Type',
        validators=[DataRequired()],
        render_kw={"placeholder": "Ticket type*"}
    )
    price = DecimalField(
        'Normal Price',
        validators=[InputRequired(), NumberRange(min=0)],
        render_kw={"placeholder": "Normal price*"}
    )
    member_discount = DecimalField(
        'Member Price',
        validators=[InputRequired(), NumberRange(min=0)],
        render_kw={"placeholder": "Member price*"}
    )
    max_quantity = IntegerField(
        'Quantity',
        validators=[DataRequired()],
        render_kw={"placeholder": "Quantity*"}
    )
    start_sale = DateTimeLocalField(
        'Start Sale',
        validators=[DataRequired()],
        format="%Y-%m-%dT%H:%M"
    )
    end_sale = DateTimeLocalField(
        'End Sale',
        validators=[DataRequired()],
        format="%Y-%m-%dT%H:%M"
    )

    def validate_end_sale(self, field):
        if field.data <= self.start_sale.data:
            raise ValidationError('Tickets end sale date should be later than start sale date')


class EventForm(FlaskForm):
    event_name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={"placeholder": "Event name*"}
    )
    
    # Updated: Choices are empty [] and will be filled in the View (views.py)
    # coerce=int ensures the value returned is an Integer (Category ID)
    event_cat = SelectField(
        'Category',
        choices=[], 
        coerce=int,
        validators=[DataRequired()]
    )
    
    event_start = DateField('Start Date', validators=[DataRequired()])
    event_end = DateField('End Date', validators=[DataRequired()])
    event_time = TimeField('Start Time', validators=[DataRequired()])
    
    duration = StringField(
        'Duration',
        validators=[DataRequired()],
        render_kw={"placeholder": "days / hours / minutes *"}
    )
    
    event_img = FileField(
        'Poster',
        validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Image format only accepts jpeg, jpg or png')]
    )
    
    event_descr = TextAreaField(
        'Description',
        validators=[DataRequired()],
        render_kw={"placeholder": "Event details*"}
    )
    
    # Updated: Choices are empty [] and will be filled in the View
    # coerce=int assuming you will pass Room IDs
    event_venue = SelectField(
        'Location/Room',
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )
    
    location_detail = StringField(
        'Location Details',
        validators=[DataRequired()],
        render_kw={"placeholder": "Specific details (e.g. Building A, Zoom Link)*"}
    )
    
    tickets = FieldList(FormField(TicketForm))
    publish_status = StringField('Publish Status')

    def validate_event_end(self, field):
        if field.data < self.event_start.data:
            raise ValidationError('Event end date should not be earlier than start date')