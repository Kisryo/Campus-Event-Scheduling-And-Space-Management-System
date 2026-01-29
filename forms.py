from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, 
)

# ========================================================
# 1. FORGOT PASSWORD FORM (Request Reset Link)
# ========================================================
class ForgotPasswordForm(FlaskForm):
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your registered email"}
    )
    submit = SubmitField('Send Reset Link')


# ========================================================
# 2. SET NEW PASSWORD
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
