import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Lecturer, Event, Booking, Rooms, Equipments, Equipment_request, Feedback, Registration, Student, Category, Announcements, RequestStatus

lecturer_view = Blueprint('lecturer_view', __name__)

# Helper for Image Upload
def save_event_image(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

# ========================================================
# 1. DASHBOARD (View Campus Events)
# ========================================================
@lecturer_view.route('/dashboard')
@login_required
def dashboard():
    # ---------------------------------------------------------
    # 1. AUTO-EXPIRE LOGIC (Global Check)
    # ---------------------------------------------------------
    current_dt = datetime.now()

    # Find all events that are marked 'Upcoming' but have already ended
    expired_events = Event.query.filter(
        Event.end_datetime < current_dt, 
        Event.event_status == 'Upcoming'
    ).all()

    # Update them to 'Expired'
    if expired_events:
        for event in expired_events:
            event.event_status = 'Expired'
        db.session.commit()
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # 2. GET FILTER PARAMETERS
    # ---------------------------------------------------------
    category_id = request.args.get('category')
    search_query = request.args.get('search', '').strip()
    sort = request.args.get('sort', '')
    timeframe = request.args.get('timeframe', 'upcoming') # Default to 'upcoming'
    page = request.args.get('page', 1, type=int)

    # Load categories for the filter dropdown
    categories = Category.query.all()

    # ---------------------------------------------------------
    # 3. BUILD QUERY
    # ---------------------------------------------------------

    query = Event.query

    # A. Timeframe Filter
    if timeframe == 'past':
        # Show events that ended before now
        query = query.filter(Event.end_datetime < current_dt)
        # Note: We do NOT filter by status here, so we can see 'Expired'
    else:
        # Show events currently ongoing or in the future
        query = query.filter(Event.end_datetime >= current_dt)
        
        # --- MOVED THIS INSIDE THE ELSE BLOCK ---
        # Only restrict to 'Upcoming' (active) status when looking at the future
        query = query.filter(Event.event_status == 'Upcoming') 
        
    # B. Category Filter
    if category_id:
        query = query.filter(Event.category_id == category_id)

    # C. Search Filter
    if search_query:
        query = query.filter(Event.title.ilike(f'%{search_query}%'))

    # D. Sorting Logic
    if sort == 'newest':
        query = query.order_by(Event.start_datetime.desc())
    elif sort == 'oldest':
        query = query.order_by(Event.start_datetime.asc())
    else:
        if timeframe == 'past':
            query = query.order_by(Event.start_datetime.desc())
        else:
            query = query.order_by(Event.start_datetime.asc())

    # ---------------------------------------------------------
    # 4. PAGINATION & RENDER
    # ---------------------------------------------------------
    events_paginated = query.paginate(page=page, per_page=9, error_out=False)

    return render_template('lecturer/dashboard.html', 
                           user=current_user,
                           events=events_paginated,
                           categories_nav=categories,
                           search_query=search_query,
                           current_category=category_id,
                           current_sort=sort,
                           current_timeframe=timeframe)



# ========================================================
# 2. MY EVENTS (Manage Lecturer's Events)
# ========================================================
@lecturer_view.route('/lecturer/my-events')
@login_required
def my_events():
    page = request.args.get('page', 1, type=int)
    
    # Filter by lecturer_id
    my_events_paginated = Event.query.filter_by(lecturer_id=current_user.lecturer_id)\
        .order_by(Event.start_datetime.desc())\
        .paginate(page=page, per_page=9, error_out=False)
    
    return render_template('lecturer/my_events.html', 
                           events=my_events_paginated, 
                           now=datetime.now())


# ========================================================
# 3. CREATE WORKSHOP/SEMINAR
# ========================================================
@lecturer_view.route('/lecturer/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        action = request.form.get('action')
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        start_str = request.form.get('start_datetime')
        end_str = request.form.get('end_datetime')
        capacity = request.form.get('capacity')
        image_file = request.files.get('event_img')

        # Basic Validation
        if not title or not start_str or not end_str or not capacity or not category_id:
            flash('Please fill all required fields.', 'danger')
            categories = Category.query.all()
            return render_template('lecturer/create_event.html', user=current_user, categories=categories)

        # Date Validation
        try:
            start_dt = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
            if end_dt <= start_dt:
                flash('End time must be after start time.', 'warning')
                categories = Category.query.all()
                return render_template('lecturer/create_event.html', user=current_user, categories=categories)
        except ValueError:
            flash('Invalid date format.', 'danger')
            categories = Category.query.all()
            return render_template('lecturer/create_event.html', user=current_user, categories=categories)

        # Capacity Validation
        try:
            capacity_int = int(capacity)
            if capacity_int <= 0:
                flash('Capacity must be a positive number.', 'danger')
                categories = Category.query.all()
                return render_template('lecturer/create_event.html', user=current_user, categories=categories)
        except ValueError:
            flash('Invalid capacity number.', 'danger')
            categories = Category.query.all()
            return render_template('lecturer/create_event.html', user=current_user, categories=categories)

        img_filename = save_event_image(image_file)
        status = 'Upcoming' if action == 'publish' else 'Pending'

        new_event = Event(
            title=title, 
            description=description, 
            start_datetime=start_dt, 
            end_datetime=end_dt,
            event_status=status, 
            capacity=capacity, 
            event_img=img_filename,
            lecturer_id=current_user.lecturer_id, # Using lecturer_id
            category_id=category_id
        )

        try:
            db.session.add(new_event)
            db.session.commit()
            if status == 'Upcoming':
                flash('Event Published! It is now visible to students.', 'success')
            else:
                flash('Event saved as Draft. You can edit and publish it later.', 'info')
            return redirect(url_for('lecturer_view.manage_event', event_id=new_event.event_id))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving.', 'danger')
            print(e)

    categories = Category.query.all()
    return render_template('lecturer/create_event.html', user=current_user, categories=categories)


# ========================================================
# 4. MANAGE EVENT
# ========================================================
@lecturer_view.route('/lecturer/event/<int:event_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.lecturer_id != current_user.lecturer_id:
        return redirect(url_for('lecturer_view.dashboard'))

    rooms = Rooms.query.filter_by(is_active=True).all()
    equipments = Equipments.query.all()
    current_booking = Booking.query.filter_by(event_id=event_id)\
                                   .order_by(Booking.booking_id.desc())\
                                   .first()
    current_equipment_reqs = Equipment_request.query.filter_by(event_id=event_id).all()
    
    rooms = Rooms.query.all()
    
    # Participant Tracking
    search_q = request.args.get('search_q', '').strip()
    status_filter = request.args.get('status_filter', '')
    query = Registration.query.filter_by(event_id=event_id)
    if search_q:
        query = query.join(Student).filter(Student.student_name.ilike(f'%{search_q}%'))
    if status_filter:
        query = query.filter(Registration.status == status_filter)
    participants = query.order_by(Registration.registration_date.desc()).all()

    return render_template('lecturer/manage_event.html', 
                           event=event, 
                           rooms=rooms, 
                           equipments=equipments,
                           participants=participants,
                           current_booking=current_booking,
                           current_equipment_reqs=current_equipment_reqs,
                           search_q=search_q, 
                           status_filter=status_filter)


# ========================================================
# 5. EDIT EVENT DETAILS
# ========================================================
@lecturer_view.route('/lecturer/event/<int:event_id>/edit', methods=['POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.lecturer_id != current_user.lecturer_id: return redirect(url_for('auth.index'))
    
    if event.event_status != 'Pending':
        flash('Cannot edit a published event.', 'danger')
        return redirect(url_for('lecturer_view.manage_event', event_id=event_id))
    
    # INPUT VALIDATION 
    title = request.form.get('title')
    description = request.form.get('description')
    capacity = request.form.get('capacity')

    # A. Check for missing fields
    if not title or not description or not capacity:
        flash('Error: Title, Description, and Capacity are required.', 'warning')
        return redirect(url_for('lecturer_view.manage_event', event_id=event_id))

    # B. Check for invalid capacity (must be a positive number)
    if not capacity.isdigit() or int(capacity) <= 0:
        flash('Error: Capacity must be a valid positive number.', 'warning')
        return redirect(url_for('lecturer_view.manage_event', event_id=event_id))

    event.title = request.form.get('title')
    event.description = request.form.get('description')
    event.capacity = request.form.get('capacity')
    
    image_file = request.files.get('event_img')
    if image_file:
        new_filename = save_event_image(image_file)
        if new_filename:
            event.event_img = new_filename

    action = request.form.get('action')
    if action == 'publish':
        event.event_status = 'Upcoming'
        flash('Event Published Successfully!', 'success')
    else:
        flash('Draft updated successfully.', 'success')

    db.session.commit()
    return redirect(url_for('lecturer_view.manage_event', event_id=event_id))


# ========================================================
# 6. BOOK VENUE (Request Venue Booking)
# ========================================================
@lecturer_view.route('/event/<int:event_id>/book-venue', methods=['POST'])
@login_required
def book_venue(event_id):
    event = Event.query.get_or_404(event_id)
    room_id = request.form.get('room_id')

    # 1. Check for Conflicts
    # Ensure we exclude 'Rejected' (id=3) or 'Cancelled' (id=4) bookings from the conflict check
    overlap = Booking.query.filter(
        Booking.room_id == room_id, 
        Booking.status_id.notin_([3, 4]),
        Booking.req_start_datetime < event.end_datetime, 
        Booking.req_end_datetime > event.start_datetime
    ).first()

    if overlap:
        flash('Booking Conflict: This room is already booked for that time.', 'danger')
        return redirect(url_for('lecturer_view.manage_event', event_id=event_id))

    # 2. Create New Booking Request
    new_booking = Booking(
        booking_date=datetime.now(), 
        req_start_datetime=event.start_datetime, 
        req_end_datetime=event.end_datetime, 
        status_id=1, # 1 = Pending
        room_id=room_id, 
        event_id=event_id, 
        req_lecturer_id=current_user.lecturer_id
    )

    # 3. SET LOCATION TO PENDING (Do not set the actual room name yet)
    event.venue_location = "Pending Approval"

    db.session.add(new_booking)
    db.session.commit()
    
    flash('Venue requested successfully. Waiting for Admin approval.', 'success')
    return redirect(url_for('lecturer_view.manage_event', event_id=event_id))


# ========================================================
# 7. REQUEST EQUIPMENT
# ========================================================
@lecturer_view.route('/lecturer/event/<int:event_id>/request-equipment', methods=['POST'])
@login_required
def request_equipment(event_id):
    equipment_id = request.form.get('equipment_id')
    quantity = int(request.form.get('quantity'))
    
    item = Equipments.query.get_or_404(equipment_id)
    
    if quantity > item.total_stock:
        flash(f'Error: Only {item.total_stock} units available.', 'danger')
        return redirect(url_for('lecturer_view.manage_event', event_id=event_id))
    
    new_req = Equipment_request(
        quantity=quantity, 
        status_id=1, 
        event_id=event_id, 
        equipment_id=equipment_id
    )
    db.session.add(new_req)
    db.session.commit()
    
    flash('Equipment requested.', 'success')
    return redirect(url_for('lecturer_view.manage_event', event_id=event_id))


# ========================================================
# 8. VIEW FEEDBACK
# ========================================================
@lecturer_view.route('/lecturer/feedbacks')
@login_required
def view_feedback():
    # 1. Get Filter Parameters
    filter_event_id = request.args.get('event_id')
    filter_rating = request.args.get('rating')
    filter_sort = request.args.get('sort', 'newest')

    # 2. Base Query: Get only this lecturer's events
    my_events = Event.query.filter_by(lecturer_id=current_user.lecturer_id).all()
    my_event_ids = [e.event_id for e in my_events]
    
    # Start query on Feedback for those events
    query = Feedback.query.filter(Feedback.event_id.in_(my_event_ids))

    # 3. Apply Filters
    if filter_event_id:
        query = query.filter(Feedback.event_id == filter_event_id)
    
    if filter_rating:
        query = query.filter(Feedback.rating == filter_rating)

    # 4. Apply Sorting
    if filter_sort == 'oldest':
        query = query.order_by(Feedback.submitted_at.asc())
    else:
        query = query.order_by(Feedback.submitted_at.desc())

    feedbacks = query.all()

    return render_template('lecturer/feedback_list.html', 
                           feedbacks=feedbacks, 
                           events=my_events,
                           current_event=filter_event_id,
                           current_rating=filter_rating,
                           current_sort=filter_sort)


# ========================================================
# 9. BOOKING HISTORY
# ========================================================
@lecturer_view.route('/lecturer/bookings')
@login_required
def booking_history():
    search_q = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    sort_order = request.args.get('sort', '')

    # Base Query
    query = Booking.query.join(Event).filter(Booking.req_lecturer_id == current_user.lecturer_id)

    # Search (Event Title)
    if search_q:
        query = query.filter(Event.title.ilike(f'%{search_q}%'))

    # Status Filter
    if status_filter:
        query = query.filter(Booking.status_id == status_filter)

    bookings = query.all()
    statuses = RequestStatus.query.all()

    return render_template('lecturer/booking_history.html', 
                           bookings=bookings, 
                           statuses=statuses)


# ========================================================
# 10. VIEW EVENT DETAILS (General View)
# ========================================================
@lecturer_view.route('/lecturer/event/<int:event_id>/details')
@login_required
def view_event_details(event_id):
    event = Event.query.get_or_404(event_id)
    confirmed_count = Registration.query.filter_by(event_id=event_id, status='Confirmed').count()
    spots_left = event.capacity - confirmed_count

    return render_template('lecturer/event_details.html', 
                           user=current_user, 
                           event=event, 
                           spots_left=spots_left)
    

# ========================================================
# 11. Receive Announcements
# ========================================================
@lecturer_view.route('/announcements')
@login_required
def announcements():
    try:
        all_announcements = Announcements.query.filter(
            Announcements.target_audience.in_(['All', 'Lecturer'])
        ).order_by(Announcements.sent_at.desc()).all()
        
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        all_announcements = []
    
    return render_template('lecturer/announcements.html', 
                           user=current_user, 
                           announcements=all_announcements)
