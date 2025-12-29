from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Admin, Event, Booking, Category, Rooms, Announcements, Student, Organizer, Lecturer
from datetime import datetime

admin_view = Blueprint('admin_view', __name__)

# ========================================================
# 0. DASHBOARD (The "Home" Page for Admins)
# ========================================================
@admin_view.route('/dashboard', methods=['GET', 'POST'])
@login_required
def admin_home():
    # Security Check
    if not isinstance(current_user, Admin):
        return redirect(url_for('auth.login'))

    # Update Profile Logic
    if request.method == 'POST':
        current_user.admin_name = request.form['name']
        current_user.admin_phone = request.form['phonenumber']
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('admin_view.admin_home'))

    # Statistics for the Dashboard Cards
    stats = {
        'pending_bookings': Booking.query.filter_by(status_id=1).count(),
        'total_users': Student.query.count() + Organizer.query.count() + Lecturer.query.count(),
        'upcoming_events': Event.query.filter(Event.start_datetime > datetime.now()).count()
    }

    return render_template("admin_dashboard.html", admin=current_user, stats=stats)


# ========================================================
# 1. PROCESS BOOKING REQUESTS
# ========================================================
@admin_view.route('/bookings', methods=['GET', 'POST'])
@login_required
def manage_bookings():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        status = request.form.get('status_id') # 2=Approve, 3=Reject
        
        booking = Booking.query.get(booking_id)
        
        if booking.status_id != 1: 
            flash('Action not allowed. Request already processed.', 'danger')
        else:
            booking.status_id = status
            booking.approved_by_admin_id = current_user.admin_id
            db.session.commit()
            flash(f'Booking #{booking.booking_id} updated successfully.', 'success')
            
        return redirect(url_for('admin_view.manage_bookings'))

    bookings = Booking.query.filter_by(status_id=1).all()
    return render_template("manage_bookings.html", bookings=bookings)


# ========================================================
# 2. MANAGE USER ACCOUNTS
# ========================================================
@admin_view.route('/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    search = request.args.get('search', '').strip()
    
    s_query = Student.query
    o_query = Organizer.query
    l_query = Lecturer.query
    
    if search:
        s_query = s_query.filter(Student.student_name.ilike(f'%{search}%'))
        o_query = o_query.filter(Organizer.organizer_name.ilike(f'%{search}%'))
        l_query = l_query.filter(Lecturer.lecturer_name.ilike(f'%{search}%'))

    students = s_query.all()
    organizers = o_query.all()
    lecturers = l_query.all()

    return render_template("manage_users.html", students=students, organizers=organizers, lecturers=lecturers)

@admin_view.route('/users/delete/<type>/<id>', methods=['POST'])
@login_required
def delete_user(type, id):
    if type == 'student': user = Student.query.get(id)
    elif type == 'organizer': user = Organizer.query.get(id)
    elif type == 'lecturer': user = Lecturer.query.get(id)
    
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            flash('User account deleted successfully.', 'success')
        except:
            db.session.rollback()
            flash('Cannot delete user. They may have active bookings or events.', 'danger')
    else:
        flash('User not found.', 'danger')
        
    return redirect(url_for('admin_view.manage_users'))


# ========================================================
# 3. CONFIGURE AVAILABLE SPACES
# ========================================================
@admin_view.route('/spaces', methods=['GET', 'POST'])
@login_required
def manage_rooms():
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('room_name')
        
        if not name:
            flash('Message cannot be empty (Room Name required)', 'danger')
            return redirect(url_for('admin_view.manage_rooms'))

        if action == 'add':
            new_room = Rooms(
                room_name=name,
                capacity=request.form.get('capacity'),
                location=request.form.get('location'),
                room_type=request.form.get('room_type')
            )
            db.session.add(new_room)
            db.session.commit()
            flash('Space added successfully.', 'success')

        elif action == 'edit':
            room_id = request.form.get('room_id')
            room = Rooms.query.get(room_id)
            if room:
                room.room_name = name
                room.capacity = request.form.get('capacity')
                room.location = request.form.get('location')
                room.room_type = request.form.get('room_type')
                db.session.commit()
                flash('Space updated successfully.', 'success')

        elif action == 'delete':
            room_id = request.form.get('room_id')
            room = Rooms.query.get(room_id)
            if Booking.query.filter_by(room_id=room_id).count() > 0:
                 flash('Cannot delete space. It has existing bookings.', 'danger')
            elif room:
                db.session.delete(room)
                db.session.commit()
                flash('Space deleted successfully.', 'success')

        return redirect(url_for('admin_view.manage_rooms'))

    rooms = Rooms.query.all()
    return render_template("manage_rooms.html", rooms=rooms)


# ========================================================
# 4. SEND SYSTEM ANNOUNCEMENTS
# ========================================================
@admin_view.route('/announcements', methods=['GET', 'POST'])
@login_required
def manage_announcements():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        target = request.form.get('target')

        if not message or not title:
            flash('Message cannot be empty', 'danger')
        else:
            new_announcement = Announcements(
                title=title,
                message=message,
                target_audience=target,
                admin_id=current_user.admin_id
            )
            db.session.add(new_announcement)
            db.session.commit()
            flash('Announcement sent successfully.', 'success')
            
        return redirect(url_for('admin_view.manage_announcements'))

    history = Announcements.query.filter_by(admin_id=current_user.admin_id).order_by(Announcements.sent_at.desc()).all()
    return render_template("manage_announcements.html", history=history)


# ========================================================
# 5. MONITOR ALL EVENT SCHEDULES
# ========================================================
@admin_view.route('/monitor-events')
@login_required
def monitor_events():
    events = Event.query.order_by(Event.start_datetime.desc()).all()
    return render_template("monitor_events.html", events=events)


# ========================================================
# 6. MANAGE EVENT CATEGORIES
# ========================================================
@admin_view.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('category_name')
        cat_id = request.form.get('category_id')

        if not name and action != 'delete':
            flash('Category name is missing.', 'danger')
            return redirect(url_for('admin_view.manage_categories'))

        if action == 'add':
            new_cat = Category(category_name=name, created_by_admin_id=current_user.admin_id)
            db.session.add(new_cat)
            db.session.commit()
            flash('Category added.', 'success')

        elif action == 'edit':
            cat = Category.query.get(cat_id)
            if cat:
                cat.category_name = name
                db.session.commit()
                flash('Category updated.', 'success')

        elif action == 'delete':
            events_using = Event.query.filter_by(category_id=cat_id).count()
            if events_using > 0:
                flash(f'Cannot delete. Category is in use by {events_using} event(s).', 'danger')
            else:
                cat = Category.query.get(cat_id)
                if cat:
                    db.session.delete(cat)
                    db.session.commit()
                    flash('Category deleted.', 'success')

        return redirect(url_for('admin_view.manage_categories'))

    search = request.args.get('search', '').strip()
    query = Category.query
    if search:
        query = query.filter(Category.category_name.ilike(f'%{search}%'))
    
    categories = query.all()
    return render_template("manage_categories.html", categories=categories)