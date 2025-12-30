from flask import Flask, flash, redirect, url_for
from flask_wtf.csrf import CSRFProtect, CSRFError # Imported CSRFError here
from flask_login import LoginManager
from models import db
import os

# Initialize Flask app
app = Flask(__name__)

# ========================================================
# CONFIGURATION
# ========================================================
# Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Evon%40123@localhost/event_space_management'

# Security
app.config['SECRET_KEY'] = '\xfcQz\x82\x00\xb5\xee\x14\x15\x8b\x8c\xbd\x1cSbP\xaa\x04k\x92\x9e\x15\xdf\xa6'

# Upload Folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/images')

# ========================================================
# INITIALIZE EXTENSIONS
# ========================================================
db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# ========================================================
# ERROR HANDLERS (Paste your code here)
# ========================================================
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Session expired or form tampered. Please try again.', 'danger')
    # CHANGED: 'auth.login' is safer because 'index' is inside a blueprint
    return redirect(url_for('auth.login')) 

# ========================================================
#  USER LOADER
# ========================================================
@login_manager.user_loader
def load_user(user_id):
    from models import Student, Lecturer, Organizer, Admin
    
    user = Student.query.get(user_id)
    if user: return user
        
    user = Lecturer.query.get(user_id)
    if user: return user

    user = Organizer.query.get(user_id)
    if user: return user

    return Admin.query.get(user_id)

# ========================================================
#  BLUEPRINTS REGISTRATION
# ========================================================
from auth import auth
from admin_view import admin_view
from organizer_view import organizer_view
from lecturer_view import lecturer_view
from student_view import student_view 

app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(admin_view, url_prefix='/admin')
app.register_blueprint(organizer_view, url_prefix='/organizer')
app.register_blueprint(lecturer_view, url_prefix='/lecturer')
app.register_blueprint(student_view, url_prefix='/student')

if __name__ == "__main__":
    app.run(debug=True)
