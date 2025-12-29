from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from models import db, Admin, Organizer, Lecturer, Student
import stripe
import os

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")

# -----------------------------
# Configuration
# -----------------------------
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://Jaclyn:Ying%40123@localhost:3306/event_management_system"
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=os.getenv("SECRET_KEY", "replace-this-with-a-secure-key"),
    UPLOAD_FOLDER="static/images/",
    STRIPE_SECRET_KEY=os.getenv(
        "STRIPE_SECRET_KEY",
        "sk_test_51PMWarFeLdpgIRLCcD1YhpdSwJESnWBcMmxvtFXvlx9aEfh11QwoCY3eaSMi43B7Ho1BBIld9qMDAaCRIsVbUZpw00lInyAKH0"
    ),
)

# -----------------------------
# Initialize extensions
# -----------------------------
db.init_app(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

stripe.api_key = app.config["STRIPE_SECRET_KEY"]

# -----------------------------
# User loader for Flask-Login
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login requires a user loader.
    We check across all role tables: Admin, Organizer, Lecturer, Student.
    """
    return (
        Admin.query.get(user_id)
        or Organizer.query.get(user_id)
        or Lecturer.query.get(user_id)
        or Student.query.get(user_id)
    )

# -----------------------------
# Landing page route
# -----------------------------
@app.route("/")
def index():
    # Render CESMS landing page (index.html)
    return render_template("index.html")

# -----------------------------
# Import and register blueprints
# -----------------------------
from auth import auth
from user_view import user_view
from student_view import student_view
from admin_view import admin_view
from organizer_view import organizer_view
from lecturer_view import lecturer_view

app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(user_view, url_prefix="/user")
app.register_blueprint(student_view, url_prefix="/student")
app.register_blueprint(admin_view, url_prefix="/admin")
app.register_blueprint(organizer_view, url_prefix="/organizer")
app.register_blueprint(lecturer_view, url_prefix="/lecturer")

from flask_wtf.csrf import CSRFError

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Session expired or form tampered. Please try again.', 'danger')
    return redirect(url_for('index'))

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
