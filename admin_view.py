from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import jsonify
from models import db, Admin, Event, Booking, Category, Rooms, Announcements, Student, Organizer, Lecturer, Equipment_request, Registration
from datetime import datetime
from sqlalchemy import func, extract
import json

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

    # Update Profile
    if request.method == 'POST':
        current_user.admin_name = request.form['name']
        current_user.admin_phone = request.form['phonenumber']
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('admin_view.admin_home'))

    # Statistics
    # 1. VENUE BOOKINGS (Breakdown)
    # IDs: 1=Pending, 2=Approved, 3=Rejected
    venue_pending = Booking.query.filter_by(status_id=1).count()
    venue_approved = Booking.query.filter_by(status_id=2).count()
    venue_rejected = Booking.query.filter_by(status_id=3).count()

    # 2. EQUIPMENT REQUESTS (Breakdown - NEW)
    equip_pending = Equipment_request.query.filter_by(status_id=1).count()
    equip_approved = Equipment_request.query.filter_by(status_id=2).count()
    equip_rejected = Equipment_request.query.filter_by(status_id=3).count()

    # 3. USER COUNTS
    student_count = Student.query.count()
    lecturer_count = Lecturer.query.count()
    organizer_count = Organizer.query.count()

    stats = {
        # Card Totals
        'pending_bookings': venue_pending + equip_pending,
        'total_users': student_count + lecturer_count + organizer_count,
        'upcoming_events': Event.query.filter(Event.start_datetime > datetime.now(), Event.event_status == 'Upcoming').count(),

        # Chart 1: User Demographics
        'chart_users': {
            'Students': student_count,
            'Lecturers': lecturer_count,
            'Organizers': organizer_count
        },

        # Chart 2: Venue vs Equipment (Split Data)
        'chart_venue': [venue_approved, venue_pending, venue_rejected],
        'chart_equip': [equip_approved, equip_pending, equip_rejected]
    }

    return render_template("admin/admin_dashboard.html", admin=current_user, stats=stats)


# ========================================================
# 1. VIEW ALL REQUESTS (Venue & Equipment)
# ========================================================
@admin_view.route('/process-requests')
@login_required
def process_requests():
    # Fetch Pending Venue Bookings (Status ID 1 = Pending)
    venue_requests = Booking.query.filter_by(status_id=1).order_by(Booking.booking_date.asc()).all()
    
    # Fetch Pending Equipment Requests (Status ID 1 = Pending)
    equipment_requests = Equipment_request.query.filter_by(status_id=1).all()
    
    return render_template('admin/process_requests.html', 
                           venue_requests=venue_requests, 
                           equipment_requests=equipment_requests)


# ========================================================
# 2. APPROVE/REJECT VENUE BOOKING (With Status Check)
# ========================================================
@admin_view.route('/booking/<int:booking_id>/action/<string:action>')
@login_required
def booking_action(booking_id, action):
    booking = Booking.query.get_or_404(booking_id)
    # 1. Fetch the Event associated with this booking
    event = Event.query.get(booking.event_id)
    
    # --- CHECK: PREVENT DUPLICATE ACTIONS ---
    if booking.status_id != 1:  # If not Pending
        flash('Action not allowed. This request has already been processed.', 'warning')
        return redirect(url_for('admin_view.process_requests'))

    if action == 'approve':
        booking.status_id = 2  # Approved
        booking.approved_by_admin_id = current_user.admin_id
        
        # --- CRITICAL FIX: UPDATE THE EVENT LOCATION TEXT ---
        event.venue_location = booking.room.room_name 
        
        flash(f'Venue booking approved. Event location set to {booking.room.room_name}.', 'success')

    elif action == 'reject':
        booking.status_id = 3  # Rejected
        booking.approved_by_admin_id = current_user.admin_id
        
        # --- CRITICAL FIX: RESET EVENT LOCATION TEXT ---
        # Reset to "Not Booked" so the Organizer sees they need to try again
        event.venue_location = "Not Booked"
        
        flash(f'Venue booking for {booking.room.room_name} rejected.', 'danger')
    
    db.session.commit()
    return redirect(url_for('admin_view.process_requests'))


# ========================================================
# 3. APPROVE/REJECT EQUIPMENT REQUEST (With Status Check)
# ========================================================
@admin_view.route('/equipment_action/<int:req_id>/<action>', methods=['GET', 'POST'])
@login_required
def equipment_action(req_id, action):
    if not isinstance(current_user, Admin):
        return redirect(url_for('auth.login'))

    # 1. Fetch the Request
    req = Equipment_request.query.get_or_404(req_id)
    equipment_item = req.equipment # Access the related Equipment object

    # 2. Handle Approval
    if action == 'approve':
        # CHECK: Is there enough stock?
        if equipment_item.total_stock >= req.quantity:
            # A. Deduct Stock
            equipment_item.total_stock -= req.quantity
            
            # B. Update Status to Approved (ID 2 = Approved)
            req.status_id = 2 
            
            flash(f'Request approved. {req.quantity} {equipment_item.item_name}(s) deducted from stock.', 'success')
        else:
            # Not enough stock
            flash(f'Cannot approve: Insufficient stock. Only {equipment_item.total_stock} left.', 'danger')
            return redirect(url_for('admin_view.process_requests'))

    # 3. Handle Rejection
    elif action == 'reject':
        # If we are rejecting a request that was PREVIOUSLY approved, we must return the stock
        if req.status_id == 2: # 2 = Approved
             equipment_item.total_stock += req.quantity

        req.status_id = 3 # 3 = Rejected
        flash('Equipment request rejected.', 'warning')

    db.session.commit()
    return redirect(url_for('admin_view.process_requests'))

# ========================================================
# 4. MANAGE USER ACCOUNTS
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

    return render_template("admin/manage_users.html", students=students, organizers=organizers, lecturers=lecturers)

@admin_view.route('/users/delete/<type>/<id>', methods=['POST'])
@login_required
def delete_user(type, id):
    user = None
    has_published_events = False

    # 1. Fetch User & Check for Published Events
    if type == 'student': 
        user = Student.query.get(id)
        
    elif type == 'organizer': 
        user = Organizer.query.get(id)
        # Check if they have any 'Upcoming' events
        if user and any(event.event_status == 'Upcoming' for event in user.events):
            has_published_events = True
            
    elif type == 'lecturer': 
        user = Lecturer.query.get(id)
        # Check if they have any 'Upcoming' events
        if user and any(event.event_status == 'Upcoming' for event in user.events):
            has_published_events = True
    
    # 2. Perform Action
    if user:
        if has_published_events:
            # Custom message for published events
            flash('Cannot delete user. They have published (Upcoming) events. Please remove the events first.', 'danger')
        else:
            try:
                db.session.delete(user)
                db.session.commit()
                flash('User account deleted successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                # Fallback for other database constraints (like existing bookings)
                flash('Cannot delete user. They may have active bookings or history records.', 'danger')
    else:
        flash('User not found.', 'danger')
        
    return redirect(url_for('admin_view.manage_users'))


# ========================================================
# 5. CREATE USER ACCOUNT (Admin Only)
# ========================================================
@admin_view.route('/users/create', methods=['POST'])
@login_required
def create_user():
    if not isinstance(current_user, Admin):
        return redirect(url_for('auth.login'))

    # 1. Get Form Data
    user_type = request.form.get('user_type')
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')

    try:
        # --- CHECK IF EMAIL ALREADY EXISTS ---
        # We check all 3 tables to ensure email uniqueness across the system
        email_exists = (
            Student.query.filter_by(student_email=email).first() or
            Organizer.query.filter_by(organizer_email=email).first() or
            Lecturer.query.filter_by(lecturer_email=email).first()
        )

        if email_exists:
            flash(f'Error: The email "{email}" is already in use by another account.', 'danger')
            return redirect(url_for('admin_view.manage_users'))
        # ------------------------------------------

        new_user = None

        # 2. Create Object based on Type
        if user_type == 'student':
            if Student.query.get(user_id):
                raise Exception(f'Student ID {user_id} already exists.')
            
            new_user = Student(
                student_id=user_id,
                student_name=name,
                student_email=email,
                student_phone=phone,
                student_password=password 
            )

        elif user_type == 'organizer':
            if Organizer.query.get(user_id):
                raise Exception(f'Organizer ID {user_id} already exists.')

            new_user = Organizer(
                organizer_id=user_id,
                organizer_name=name,
                organizer_email=email,
                organizer_phone=phone,
                organizer_password=password
            )

        elif user_type == 'lecturer':
            if Lecturer.query.get(user_id):
                raise Exception(f'Lecturer ID {user_id} already exists.')

            new_user = Lecturer(
                lecturer_id=user_id,
                lecturer_name=name,
                lecturer_email=email,
                lecturer_phone=phone,
                lecturer_password=password
            )
        
        else:
            flash('Invalid user type selected.', 'danger')
            return redirect(url_for('admin_view.manage_users'))

        # 3. Save to Database
        db.session.add(new_user)
        db.session.commit()
        flash(f'New {user_type.capitalize()} account ({name}) created successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating account: {str(e)}', 'danger')

    return redirect(url_for('admin_view.manage_users'))


# ========================================================
# 6. CONFIGURE AVAILABLE SPACES
# ========================================================
@admin_view.route('/spaces', methods=['GET', 'POST'])
@login_required
def manage_rooms():
    if request.method == 'POST':
        action = request.form.get('action')
        
        # 1. Handle DELETE separately (Only needs room_id)
        if action == 'delete':
            room_id = request.form.get('room_id')
            room = Rooms.query.get(room_id)
            if Booking.query.filter_by(room_id=room_id).count() > 0:
                 flash('Cannot delete space. It has existing bookings.', 'danger')
            elif room:
                db.session.delete(room)
                db.session.commit()
                flash('Space deleted successfully.', 'success')
            return redirect(url_for('admin_view.manage_rooms'))

        # 2. Extract Data for ADD/EDIT
        name = request.form.get('room_name')
        capacity = request.form.get('capacity')
        location = request.form.get('location')
        room_type = request.form.get('room_type')

        # 3. Handle ADD
        if action == 'add':
            new_room = Rooms(
                room_name=name,
                capacity=capacity,
                location=location,
                room_type=room_type
            )
            db.session.add(new_room)
            db.session.commit()
            flash('Space added successfully.', 'success')

        # 4. Handle EDIT
        elif action == 'edit':
            room_id = request.form.get('room_id')
            room = Rooms.query.get(room_id)
            if room:
                room.room_name = name
                room.capacity = capacity
                room.location = location
                room.room_type = room_type
                db.session.commit()
                flash('Space updated successfully.', 'success')

        return redirect(url_for('admin_view.manage_rooms'))

    rooms = Rooms.query.all()
    return render_template("admin/manage_rooms.html", rooms=rooms)


# ========================================================
# 7. SEND SYSTEM ANNOUNCEMENTS
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
    return render_template("admin/manage_announcements.html", history=history)


# ========================================================
# 8. MONITOR ALL EVENT SCHEDULES
# ========================================================
@admin_view.route('/monitor-events')
@login_required
def monitor_events():
    return render_template("admin/monitor_events.html")

@admin_view.route('/api/calendar-events')
@login_required
def get_calendar_events():
    # Filter: Show everything EXCEPT 'Pending' (matching your original logic)
    events = Event.query.filter(Event.event_status != 'Pending').all()
    
    events_list = []
    for e in events:
        # Define color based on Status
        color = '#4e73df' # Default Blue
        if e.event_status == 'Upcoming':
            color = '#1cc88a' # Green
        elif e.event_status == 'Expired':
            color = '#858796' # Gray
        elif e.event_status == 'Cancelled':
            color = '#e74a3b' # Red

        events_list.append({
            'id': e.event_id,
            'title': e.title,
            'start': e.start_datetime.isoformat(), # ISO format is required for JS
            'end': e.end_datetime.isoformat(),
            # Generate the URL for the event details page
            'url': url_for('admin_view.view_event', event_id=e.event_id), 
            'backgroundColor': color,
            'borderColor': color,
            # Add extra data for tooltips
            'extendedProps': {
                'venue': e.venue_location or 'TBD',
                'status': e.event_status
            }
        })
    
    return jsonify(events_list)


# ========================================================
# 9. VIEW EVENT DETAILS (The Route for Single Event)
# ========================================================
@admin_view.route('/event/<int:event_id>/details')
@login_required
def view_event(event_id):
    # 1. Fetch the specific event by ID
    event = Event.query.get_or_404(event_id)
    
    # 2. Calculate confirmed participants (Optional, useful for Admin)
    confirmed_count = Registration.query.filter_by(event_id=event_id, status='Confirmed').count()
    
    # 3. Calculate spots left
    # (Ensure capacity is not None to avoid errors)
    capacity = event.capacity if event.capacity else 0
    spots_left = capacity - confirmed_count

    return render_template('admin/event_details.html', 
                           event=event, 
                           confirmed_count=confirmed_count,
                           spots_left=spots_left)
    
    
# ========================================================
# 10. MANAGE EVENT CATEGORIES
# ========================================================
@admin_view.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        action = request.form.get('action')
        # Use .strip() to remove accidental whitespace around the name
        name = request.form.get('category_name', '').strip()
        cat_id = request.form.get('category_id')

        # Basic Validation
        if not name and action != 'delete':
            flash('Category name is missing.', 'danger')
            return redirect(url_for('admin_view.manage_categories'))

        # ======================================================
        # ACTION: ADD
        # ======================================================
        if action == 'add':
            # 1. Check if name already exists (Case-insensitive)
            existing_cat = Category.query.filter(Category.category_name.ilike(name)).first()
            
            if existing_cat:
                # Changed to 'danger' so it appears RED
                flash(f'Category "{name}" already exists.', 'danger')
            else:
                new_cat = Category(category_name=name, created_by_admin_id=current_user.admin_id)
                db.session.add(new_cat)
                db.session.commit()
                flash('Category added successfully.', 'success')

        # ======================================================
        # ACTION: EDIT
        # ======================================================
        elif action == 'edit':
            cat = Category.query.get(cat_id)
            if cat:
                # 1. Check if NEW name exists (excluding the current category itself)
                duplicate_check = Category.query.filter(
                    Category.category_name.ilike(name), 
                    Category.category_id != cat_id
                ).first()

                if duplicate_check:
                    # Changed to 'danger' so it appears RED
                    flash(f'Category name "{name}" is already in use.', 'danger')
                else:
                    cat.category_name = name
                    db.session.commit()
                    flash('Category updated successfully.', 'success')

        # ======================================================
        # ACTION: DELETE
        # ======================================================
        elif action == 'delete':
            # Check if any events are currently using this category
            events_using = Event.query.filter_by(category_id=cat_id).count()
            
            if events_using > 0:
                flash(f'Cannot delete. Category is in use by {events_using} event(s).', 'danger')
            else:
                cat = Category.query.get(cat_id)
                if cat:
                    db.session.delete(cat)
                    db.session.commit()
                    flash('Category deleted successfully.', 'success')

        return redirect(url_for('admin_view.manage_categories'))

    # ======================================================
    # GET REQUEST (View/Search)
    # ======================================================
    search = request.args.get('search', '').strip()
    query = Category.query
    if search:
        query = query.filter(Category.category_name.ilike(f'%{search}%'))
    
    categories = query.all()
    return render_template("admin/manage_categories.html", categories=categories)

# ========================================================
# 9. DELETE EVENT (Admin Action)
# ========================================================
@admin_view.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('auth.login'))

    event = Event.query.get_or_404(event_id)
    event_title = event.title

    try:
        # 1. Delete Related Venue Bookings
        Booking.query.filter_by(event_id=event_id).delete()

        # 2. Delete Related Equipment Requests
        Equipment_request.query.filter_by(event_id=event_id).delete()

        # 3. Delete Participant Registrations
        Registration.query.filter_by(event_id=event_id).delete()

        # 4. Finally, Delete the Event itself
        db.session.delete(event)
        db.session.commit()

        flash(f'Event "{event_title}" and all associated records have been permanently deleted.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting event: {str(e)}', 'danger')

    return redirect(url_for('admin_view.monitor_events'))
