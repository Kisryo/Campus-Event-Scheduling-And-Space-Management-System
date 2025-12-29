from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# ==========================================
# 1. Lookup Table (Request Status)
# ==========================================
class RequestStatus(db.Model):
    __tablename__ = 'RequestStatus'
    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(20), nullable=False)

    # Relationships (Optional: to see items with this status)
    bookings = db.relationship('Booking', backref='status', lazy=True)
    equipment_requests = db.relationship('Equipment_request', backref='status', lazy=True)


# ==========================================
# 2. Actor Models (Admin, Organizer, Lecturer, Student)
# ==========================================
class Admin(db.Model, UserMixin):
    __tablename__ = 'Admin'
    admin_id = db.Column(db.String(20), primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    admin_email = db.Column(db.String(100), unique=True, nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    admin_phone = db.Column(db.String(20))
    admin_img = db.Column(db.String(255), nullable=True)
    admin_account_status = db.Column(db.String(20), default='Active')

    # Relationships
    categories_created = db.relationship('Category', backref='created_by', lazy=True)
    bookings_approved = db.relationship('Booking', backref='approver', lazy=True)
    equipment_approved = db.relationship('Equipment_request', backref='approver', lazy=True)
    announcements = db.relationship('Announcements', backref='author', lazy=True)

    def get_id(self):
        return self.admin_id


class Organizer(db.Model, UserMixin):
    __tablename__ = 'Organizer'
    organizer_id = db.Column(db.String(20), primary_key=True)
    organizer_name = db.Column(db.String(100), nullable=False)
    organizer_email = db.Column(db.String(100), unique=True, nullable=False)
    organizer_password = db.Column(db.String(255), nullable=False)
    organizer_phone = db.Column(db.String(20))
    organizer_img = db.Column(db.String(255), nullable=True)
    organizer_account_status = db.Column(db.String(20), default='Active')

    # Relationships
    events = db.relationship('Event', backref='organizer', lazy=True)
    bookings = db.relationship('Booking', backref='organizer_requester', lazy=True)

    def get_id(self):
        return self.organizer_id


class Lecturer(db.Model, UserMixin):
    __tablename__ = 'Lecturer'
    lecturer_id = db.Column(db.String(20), primary_key=True)
    lecturer_name = db.Column(db.String(100), nullable=False)
    lecturer_email = db.Column(db.String(100), unique=True, nullable=False)
    lecturer_password = db.Column(db.String(255), nullable=False)
    lecturer_phone = db.Column(db.String(20))
    lecturer_img = db.Column(db.String(255), nullable=True)
    lecturer_account_status = db.Column(db.String(20), default='Active')

    # Relationships
    events = db.relationship('Event', backref='lecturer', lazy=True)
    bookings = db.relationship('Booking', backref='lecturer_requester', lazy=True)

    def get_id(self):
        return self.lecturer_id


class Student(db.Model, UserMixin):
    __tablename__ = 'Student'
    student_id = db.Column(db.String(20), primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), unique=True, nullable=False)
    student_password = db.Column(db.String(255), nullable=False)
    student_phone = db.Column(db.String(20))
    student_account_status = db.Column(db.String(20), default='Active')

    # Relationships
    registrations = db.relationship('Registration', backref='student', lazy=True)
    feedbacks = db.relationship('Feedback', backref='student', lazy=True)

    def get_id(self):
        return self.student_id


# ==========================================
# 3. Resource Models
# ==========================================
class Rooms(db.Model):
    __tablename__ = 'Rooms'
    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer)
    location = db.Column(db.String(100))
    room_type = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    bookings = db.relationship('Booking', backref='room', lazy=True)


class Equipments(db.Model):
    __tablename__ = 'Equipments'
    equipment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(100), nullable=False)
    total_stock = db.Column(db.Integer, default=0)

    # Relationships
    requests = db.relationship('Equipment_request', backref='equipment', lazy=True)


class Category(db.Model):
    __tablename__ = 'Category'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), nullable=False)
    created_by_admin_id = db.Column(db.String(20), db.ForeignKey('Admin.admin_id'))


# ==========================================
# 4. Transaction Models (Events, Bookings, etc)
# ==========================================
class Event(db.Model):
    __tablename__ = 'Event'
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    event_status = db.Column(db.String(20))
    venue_location = db.Column(db.String(100)) # Simple text, or link to Rooms if preferred
    capacity = db.Column(db.Integer)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('Category.category_id'))
    organizer_id = db.Column(db.String(20), db.ForeignKey('Organizer.organizer_id'), nullable=True)
    lecturer_id = db.Column(db.String(20), db.ForeignKey('Lecturer.lecturer_id'), nullable=True)

    # Relationships
    bookings = db.relationship('Booking', backref='event', lazy=True)
    equipment_requests = db.relationship('Equipment_request', backref='event', lazy=True)
    registrations = db.relationship('Registration', backref='event', lazy=True)
    feedbacks = db.relationship('Feedback', backref='event', lazy=True)
    category = db.relationship('Category', backref='events')


class Booking(db.Model):
    __tablename__ = 'Booking'
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_date = db.Column(db.DateTime, default=datetime.now)
    req_start_datetime = db.Column(db.DateTime)
    req_end_datetime = db.Column(db.DateTime)
    
    # Foreign Keys
    status_id = db.Column(db.Integer, db.ForeignKey('RequestStatus.status_id'), default=1)
    room_id = db.Column(db.Integer, db.ForeignKey('Rooms.room_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('Event.event_id'))
    
    # Requestors (Nullable because only one makes the request)
    req_organizer_id = db.Column(db.String(20), db.ForeignKey('Organizer.organizer_id'), nullable=True)
    req_lecturer_id = db.Column(db.String(20), db.ForeignKey('Lecturer.lecturer_id'), nullable=True)
    
    # Approver
    approved_by_admin_id = db.Column(db.String(20), db.ForeignKey('Admin.admin_id'), nullable=True)


class Equipment_request(db.Model):
    __tablename__ = 'Equipment_request'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer)
    
    # Foreign Keys
    status_id = db.Column(db.Integer, db.ForeignKey('RequestStatus.status_id'), default=1)
    event_id = db.Column(db.Integer, db.ForeignKey('Event.event_id'))
    equipment_id = db.Column(db.Integer, db.ForeignKey('Equipments.equipment_id'))
    approved_by_admin_id = db.Column(db.String(20), db.ForeignKey('Admin.admin_id'), nullable=True)


class Registration(db.Model):
    __tablename__ = 'Registration'
    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='Confirmed')
    
    student_id = db.Column(db.String(20), db.ForeignKey('Student.student_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('Event.event_id'), nullable=False)


class Announcements(db.Model):
    __tablename__ = 'Announcements'
    announcement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.now)
    target_audience = db.Column(db.String(50))
    
    admin_id = db.Column(db.String(20), db.ForeignKey('Admin.admin_id'))


class Feedback(db.Model):
    __tablename__ = 'Feedback'
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    
    student_id = db.Column(db.String(20), db.ForeignKey('Student.student_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('Event.event_id'))