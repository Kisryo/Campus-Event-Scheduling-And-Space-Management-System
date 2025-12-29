from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from models import db
import stripe
import os

# Initialize Flask app
app = Flask(__name__)

# ========================================================
# CONFIGURATION
# ========================================================
# Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Evon%40123@localhost/event_space_management'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}

# Security & Uploads
app.config['SECRET_KEY'] = '\xfcQz\x82\x00\xb5\xee\x14\x15\x8b\x8c\xbd\x1cSbP\xaa\x04k\x92\x9e\x15\xdf\xa6'

# Get the absolute path to the static/images folder to avoid errors
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/images')

# ========================================================
# INITIALIZE EXTENSIONS
# ========================================================
db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Stripe configuration
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51PMWarFeLdpgIRLCcD1YhpdSwJESnWBcMmxvtFXvlx9aEfh11QwoCY3eaSMi43B7Ho1BBIld9qMDAaCRIsVbUZpw00lInyAKH0'
stripe.api_key = app.config['STRIPE_SECRET_KEY']

# ========================================================
#  USER LOADER (Checks all 4 Tables)
# ========================================================
@login_manager.user_loader
def load_user(user_id):
    # Import models inside function to avoid circular imports
    from models import Student, Lecturer, Organizer, Admin
    
    # 1. Check Student
    user = Student.query.get(user_id)
    if user: return user
        
    # 2. Check Lecturer
    user = Lecturer.query.get(user_id)
    if user: return user

    # 3. Check Organizer
    user = Organizer.query.get(user_id)
    if user: return user

    # 4. Check Admin
    return Admin.query.get(user_id)

# ========================================================
#  BLUEPRINTS REGISTRATION
# ========================================================
from auth import auth
from admin_view import admin_view
from organizer_view import organizer_view
from lecturer_view import lecturer_view
from user_view import user_view 

app.register_blueprint(auth, url_prefix='/')

# Registering views with specific prefixes
app.register_blueprint(admin_view, url_prefix='/admin')         # e.g., /admin/dashboard
app.register_blueprint(organizer_view, url_prefix='/organizer') # e.g., /organizer/dashboard
app.register_blueprint(lecturer_view, url_prefix='/lecturer')   # e.g., /lecturer/dashboard
app.register_blueprint(user_view, url_prefix='/student')        # e.g., /student/home

# Run the app
if __name__ == "__main__":
    app.run(debug=True)