import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Organizer, Event, Booking, Rooms, Equipments, Equipment_request, Feedback, Registration, Student, Category, Announcements, RequestStatus

organizer_view = Blueprint('organizer_view', __name__)

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
# 1. DASHBOARD (Public View of All Upcoming Events)
# ========================================================
@organizer_view.route('/dashboard')
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
    events_paginated = query.paginate(page=page, per_page=6, error_out=False)

    return render_template('organizer/organizer_dashboard.html', 
                           user=current_user,
                           events=events_paginated,
                           categories_nav=categories,
                           search_query=search_query,
                           current_category=category_id,
                           current_sort=sort,
                           current_timeframe=timeframe)


# ========================================================
# 2. MANAGE MY EVENTS (List of Organizer's Events)
# ========================================================
@organizer_view.route('/my-events')
@login_required
def my_events():
    # Admin/Organizer check removed as requested
    
    page = request.args.get('page', 1, type=int)
    my_events_paginated = Event.query.filter_by(organizer_id=current_user.organizer_id)\
        .order_by(Event.start_datetime.desc())\
        .paginate(page=page, per_page=6, error_out=False)
    
    # PASS 'now' variable
    return render_template('organizer/my_events.html', 
                           events=my_events_paginated, 
                           now=datetime.now())


# ========================================================
# 3. CREATE EVENT (With Capacity Validation)
# ========================================================
@organizer_view.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    # Admin/Organizer check removed as requested

    if request.method == 'POST':
        action = request.form.get('action') # 'save' or 'publish'
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        start_str = request.form.get('start_datetime')
        end_str = request.form.get('end_datetime')
        capacity = request.form.get('capacity')
        image_file = request.files.get('event_img')

        # 1. Basic Validation
        if not title or not start_str or not end_str or not capacity or not category_id:
            flash('Please fill all required fields.', 'danger')
            categories = Category.query.all()
            return render_template('organizer/create_event.html', user=current_user, categories=categories)

        # 2. Date Validation
        try:
            start_dt = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')

            if end_dt <= start_dt:
                flash('End time must be after start time.', 'warning')
                categories = Category.query.all()
                return render_template('organizer/create_event.html', user=current_user, categories=categories)
        except ValueError:
            flash('Invalid date format.', 'danger')
            categories = Category.query.all()
            return render_template('organizer/create_event.html', user=current_user, categories=categories)

        # 3. Capacity Validation (Prevent Negative Numbers)
        try:
            capacity_int = int(capacity)
            if capacity_int <= 0:
                flash('Capacity must be a positive number (at least 1).', 'danger')
                categories = Category.query.all()
                return render_template('organizer/create_event.html', user=current_user, categories=categories)
        except ValueError:
            flash('Invalid capacity number.', 'danger')
            categories = Category.query.all()
            return render_template('organizer/create_event.html', user=current_user, categories=categories)


        # 4. Handle Image
        img_filename = save_event_image(image_file)

        # 5. Determine Status
        # Publish -> 'Upcoming', Save -> 'Pending' (Draft)
        status = 'Upcoming' if action == 'publish' else 'Pending'

        new_event = Event(
            title=title, 
            description=description, 
            start_datetime=start_dt, 
            end_datetime=end_dt,
            event_status=status, 
            capacity=capacity, 
            event_img=img_filename,
            organizer_id=current_user.organizer_id,
            category_id=category_id
        )

        try:
            db.session.add(new_event)
            db.session.commit()
            
            if status == 'Upcoming':
                flash('Event Published! It is now visible to students.', 'success')
            else:
                flash('Event saved as Draft. You can edit and publish it later.', 'info')
                
            return redirect(url_for('organizer_view.manage_event', event_id=new_event.event_id))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving the event.', 'danger')
            print(e)

    # GET Request
    categories = Category.query.all()
    return render_template('organizer/create_event.html', user=current_user, categories=categories)


# ========================================================
# 4. MANAGE EVENT HUB
# ========================================================
@organizer_view.route('/event/<int:event_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_event(event_id):
    # Admin/Organizer check removed as requested
    
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.organizer_id:
        return redirect(url_for('organizer_view.dashboard'))

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

    return render_template('organizer/manage_event.html', 
                           event=event, 
                           rooms=rooms, 
                           equipments=equipments,
                           participants=participants,
                           current_booking=current_booking,
                           current_equipment_reqs=current_equipment_reqs,
                           search_q=search_q, 
                           status_filter=status_filter)


# ========================================================
# 5. EDIT EVENT (Only 'Pending' events can be edited)
# ========================================================
@organizer_view.route('/event/<int:event_id>/edit', methods=['POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.organizer_id: return redirect(url_for('auth.index'))
    
    if event.event_status != 'Pending':
        flash('Cannot edit a published event.', 'danger')
        return redirect(url_for('organizer_view.manage_event', event_id=event_id))
    
    # 1. Capture Inputs
    title = request.form.get('title')
    description = request.form.get('description')
    capacity = request.form.get('capacity')
    start_str = request.form.get('start_datetime') # New
    end_str = request.form.get('end_datetime')     # New

    # 2. Validation
    if not title or not description or not capacity or not start_str or not end_str:
        flash('Error: All fields are required.', 'warning')
        return redirect(url_for('organizer_view.manage_event', event_id=event_id))

    if not capacity.isdigit() or int(capacity) <= 0:
        flash('Error: Capacity must be a valid positive number.', 'warning')
        return redirect(url_for('organizer_view.manage_event', event_id=event_id))

    # 3. Convert Date Strings -> Datetime Objects
    try:
        # HTML datetime-local format: '2025-12-31T23:59'
        new_start = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
        new_end = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')

        # Logic Check: End must be after Start
        if new_end <= new_start:
            flash('Error: End time must be after start time.', 'danger')
            return redirect(url_for('organizer_view.manage_event', event_id=event_id))
            
    except ValueError:
        flash('Error: Invalid date format.', 'danger')
        return redirect(url_for('organizer_view.manage_event', event_id=event_id))

    # 4. Update Event Fields
    event.title = title
    event.description = description
    event.capacity = capacity
    event.start_datetime = new_start # Update DB
    event.end_datetime = new_end     # Update DB
    
    image_file = request.files.get('event_img')
    if image_file:
        new_filename = save_event_image(image_file)
        if new_filename:
            event.event_img = new_filename

    # 5. Handle Publish/Save
    action = request.form.get('action')
    if action == 'publish':
        event.event_status = 'Upcoming'
        flash('Event Published Successfully!', 'success')
    else:
        flash('Event details updated successfully.', 'success')

    db.session.commit()
    return redirect(url_for('organizer_view.manage_event', event_id=event_id))

# ========================================================
# 6. BOOK VENUE
# ========================================================
@organizer_view.route('/event/<int:event_id>/book-venue', methods=['POST'])
@login_required
def book_venue(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Convert room_id to Integer immediately
    try:
        room_id = int(request.form.get('room_id'))
    except (ValueError, TypeError):
        flash('Invalid room selected.', 'danger')
        return redirect(url_for('organizer_view.manage_event', event_id=event_id))

    # Robust Conflict Check
    # We check for ANY overlap in time for the SAME room
    # Logic: (StartA < EndB) and (EndA > StartB)
    overlap = Booking.query.filter(
        Booking.room_id == room_id, 
        Booking.status_id.notin_([3]), # Ignore Rejected(3)
        Booking.req_start_datetime < event.end_datetime, 
        Booking.req_end_datetime > event.start_datetime
    ).first()

    if overlap:
        flash(f'Booking Conflict: This room is already taken during {overlap.req_start_datetime} - {overlap.req_end_datetime}.', 'danger')
        return redirect(url_for('organizer_view.manage_event', event_id=event_id))

    # 1. Create New Booking Request
    new_booking = Booking(
        booking_date=datetime.now(), 
        req_start_datetime=event.start_datetime, 
        req_end_datetime=event.end_datetime, 
        status_id=1, # 1 = Pending
        room_id=room_id, 
        event_id=event_id, 
        req_organizer_id=current_user.organizer_id
    )

    event.venue_location = "Pending Approval"

    db.session.add(new_booking)
    db.session.commit()
    
    flash('Venue requested successfully. Waiting for Admin approval.', 'success')
    return redirect(url_for('organizer_view.manage_event', event_id=event_id))


# ========================================================
# 7. REQUEST EQUIPMENT
# ========================================================
@organizer_view.route('/event/<int:event_id>/request-equipment', methods=['POST'])
@login_required
def request_equipment(event_id):
    equipment_id = request.form.get('equipment_id')
    quantity = int(request.form.get('quantity'))
    
    # 1. Proceed if valid
    new_req = Equipment_request(
        quantity=quantity, 
        status_id=1, # Pending
        event_id=event_id, 
        equipment_id=equipment_id
    )
    db.session.add(new_req)
    db.session.commit()
    
    flash('Equipment requested successfully.', 'success')
    return redirect(url_for('organizer_view.manage_event', event_id=event_id))


# ========================================================
# 8. VIEW FEEDBACK
# ========================================================
@organizer_view.route('/feedbacks')
@login_required
def view_feedback():
    # 1. Get Filter Parameters from URL
    filter_event_id = request.args.get('event_id')
    filter_rating = request.args.get('rating')
    filter_sort = request.args.get('sort', 'newest') # Default to Newest

    # 2. Base Query: Only feedback for this organizer's events
    my_events = Event.query.filter_by(organizer_id=current_user.organizer_id).all()
    my_event_ids = [e.event_id for e in my_events]
    
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

    # Pass 'my_events' to populate the dropdown list
    return render_template('organizer/feedback_list.html', 
                           feedbacks=feedbacks, 
                           events=my_events,
                           current_event=filter_event_id,
                           current_rating=filter_rating,
                           current_sort=filter_sort)

# ========================================================
# 9. BOOKING HISTORY
# ========================================================
@organizer_view.route('/organizer/bookings')
@login_required
def booking_history():
    search_q = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    sort_order = request.args.get('sort', '')

    # Base Query
    query = Booking.query.join(Event).filter(Booking.req_organizer_id == current_user.organizer_id)

    # Search (Event Title)
    if search_q:
        query = query.filter(Event.title.ilike(f'%{search_q}%'))

    # Status Filter
    if status_filter:
        query = query.filter(Booking.status_id == status_filter)

    bookings = query.all()
    statuses = RequestStatus.query.all()

    return render_template('organizer/booking_history.html', 
                           bookings=bookings, 
                           statuses=statuses)

# ========================================================
# 10. VIEW EVENT DETAILS 
# ========================================================
@organizer_view.route('/event/<int:event_id>/details')
@login_required
def view_event_details(event_id):
    # Admin/Organizer check removed as requested
    
    event = Event.query.get_or_404(event_id)
    
    # Calculate spots left
    confirmed_count = Registration.query.filter_by(event_id=event_id, status='Confirmed').count()
    spots_left = event.capacity - confirmed_count

    return render_template('organizer/event_details.html', 
                           user=current_user, 
                           event=event, 
                           spots_left=spots_left)
    

# ========================================================
# 11. Receive Announcements
# ========================================================
@organizer_view.route('/announcements')
@login_required
def announcements():
    try:
        # UPDATED: Added current_user.organizer_id to the filter list
        all_announcements = Announcements.query.filter(
            Announcements.target_audience.in_(['All', 'Organizer', current_user.organizer_id])
        ).order_by(Announcements.sent_at.desc()).all()
        
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        all_announcements = []
    
    return render_template('organizer/announcements.html', 
                           user=current_user, 
                           announcements=all_announcements)
    
@organizer_view.context_processor
def inject_announcement_ids():
    if current_user.is_authenticated:
        # UPDATED: Added current_user.organizer_id to the filter list here too
        recent_anns = Announcements.query.filter(
            Announcements.target_audience.in_(['All', 'Organizer', current_user.organizer_id])
        ).order_by(Announcements.sent_at.desc()).all()
        
        # Pass the list of IDs to all templates
        return dict(recent_announcement_ids=[a.announcement_id for a in recent_anns])
    
    return dict(recent_announcement_ids=[])

# ========================================================
# 12. DELETE EVENT (Drafts Only)
# ========================================================
@organizer_view.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # 1. Security Check: Ensure the current user owns this event
    if event.organizer_id != current_user.organizer_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('organizer_view.my_events'))

    # 2. Status Check: Only allow deletion of 'Pending' (Draft) events
    # We prevent deleting 'Upcoming' events because students might have already registered.
    if event.event_status != 'Pending':
        flash('Cannot delete a published or expired event.', 'warning')
        return redirect(url_for('organizer_view.my_events'))

    try:
        # -------------------------------------------------------------
        # 3. MANUAL CASCADE DELETE
        # Delete children records first to prevent Foreign Key errors
        # -------------------------------------------------------------
        
        # A. Delete Equipment Requests linked to this event
        Equipment_request.query.filter_by(event_id=event_id).delete()
        
        # B. Delete Venue Bookings linked to this event
        Booking.query.filter_by(event_id=event_id).delete()
        
        # 4. Delete the Event itself
        db.session.delete(event)
        db.session.commit()
        
        flash('Draft event and its booking requests were deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the event.', 'danger')
        print(f"Delete Error: {e}")

    return redirect(url_for('organizer_view.my_events'))
