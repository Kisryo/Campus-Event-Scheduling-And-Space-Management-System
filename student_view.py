from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user
from models import db, Student, Event, Registration, Category, Organizer, Lecturer, Feedback,Announcements, Admin
from datetime import datetime

student_view = Blueprint('student_view', __name__)

# ========================================================
# 1. HOME PAGE 
# ========================================================
@student_view.route('/home')
@login_required
def home():
    if not isinstance(current_user, (Student, Organizer, Lecturer)):
        return redirect(url_for('auth.login'))

    current_dt = datetime.now()
    categories = Category.query.all()

    # --- QUERY 1: UPCOMING (Soonest Date First) ---
    upcoming_events = Event.query.filter(
        Event.start_datetime >= current_dt,
        Event.event_status == 'Upcoming'
    ).order_by(Event.start_datetime.asc()).limit(3).all()

    # --- QUERY 2: NEW ARRIVALS (Highest ID First) ---
    new_events = Event.query.filter(
        Event.start_datetime >= current_dt,
        Event.event_status == 'Upcoming'
    ).order_by(Event.event_id.desc()).limit(3).all()

    return render_template('student/home.html', 
                           user=current_user, 
                           categories_nav=categories, 
                           upcoming_events=upcoming_events,
                           new_events=new_events)


# ========================================================
# 2. BROWSE EVENTS (Past/Upcoming Filter)
# ========================================================
@student_view.route('/events')
@login_required
def events():
    if not isinstance(current_user, (Student, Organizer, Lecturer)):
        return redirect(url_for('auth.login'))

    # Get Parameters
    category_id = request.args.get('category')
    search_query = request.args.get('search', '').strip()
    sort = request.args.get('sort', '')
    
    # NEW: Timeframe Filter ('upcoming' is default)
    timeframe = request.args.get('timeframe', 'upcoming') 

    current_dt = datetime.now()
    categories = Category.query.all()

    # Base Query
    query = Event.query

    # 1. Timeframe Logic
    if timeframe == 'past':
        # Show events that have already ended
        query = query.filter(Event.end_datetime < current_dt)
    else:
        # Show events starting in the future OR currently ongoing
        query = query.filter(Event.end_datetime >= current_dt)
        # Ensure we only show Approved/Upcoming status for students
        query = query.filter(Event.event_status == 'Upcoming')

    # 2. Category Filter
    if category_id:
        query = query.filter(Event.category_id == category_id)

    # 3. Search Filter
    if search_query:
        query = query.filter(Event.title.ilike(f'%{search_query}%'))

# 4. Sorting
    if sort == 'newest':
        # Newest to Oldest (Latest date first)
        query = query.order_by(Event.start_datetime.desc())
        
    elif sort == 'oldest':
        # Oldest to Newest (Earliest date first)
        query = query.order_by(Event.start_datetime.asc())
        
    else:
        # Default Logic (Smart Sort)
        # If looking at Past events -> Show most recent first (Newest)
        # If looking at Upcoming events -> Show soonest first (Oldest/Earliest)
        if timeframe == 'past':
            query = query.order_by(Event.start_datetime.desc())
        else:
            query = query.order_by(Event.start_datetime.asc())

    page = request.args.get('page', 1, type=int)
    events_paginated = query.paginate(page=page, per_page=6)

    return render_template('student/events.html', 
                           user=current_user,
                           events=events_paginated, 
                           categories_nav=categories,
                           search_query=search_query,
                           current_category=category_id,
                           current_sort=sort,
                           current_timeframe=timeframe)


# ========================================================
# 3. EVENT DETAILS (View Single Event)
# ========================================================
@student_view.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    # ALLOW: Student, Organizer, OR Lecturer
    if not isinstance(current_user, (Student, Organizer, Lecturer)):
        return redirect(url_for('auth.login'))

    event = Event.query.get_or_404(event_id)
    
    # Calculate spots left
    confirmed_count = Registration.query.filter_by(event_id=event_id, status='Confirmed').count()
    spots_left = event.capacity - confirmed_count

    # Check if THIS specific user is already registered (Only if they are a student)
    is_registered = False
    if isinstance(current_user, Student):
        check_reg = Registration.query.filter_by(student_id=current_user.student_id, event_id=event_id).first()
        if check_reg:
            is_registered = True

    return render_template('student/event_details.html', 
                           user=current_user, 
                           event=event, 
                           spots_left=spots_left, 
                           is_registered=is_registered)


# ========================================================
# 4. REGISTER (Students Only)
# ========================================================
@student_view.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    # RESTRICT: Only Students can register
    if not isinstance(current_user, Student):
        flash('Only students can register for events.', 'warning')
        return redirect(url_for('student_view.event_details', event_id=event_id))

    event = Event.query.get_or_404(event_id)

    # 1. Check Duplicate
    existing = Registration.query.filter_by(student_id=current_user.student_id, event_id=event_id).first()
    if existing:
        flash('You are already registered.', 'info')
        return redirect(url_for('student_view.event_details', event_id=event_id))

    # 2. Check Capacity
    count = Registration.query.filter_by(event_id=event_id, status='Confirmed').count()
    if count >= event.capacity:
        flash('Registration closed.Event Fully Booked', 'danger')
        return redirect(url_for('student_view.event_details', event_id=event_id))

    # 3. Create Registration
    new_reg = Registration(
        student_id=current_user.student_id,
        event_id=event_id,
        status='Confirmed',
        registration_date=datetime.now()
    )
    db.session.add(new_reg)
    db.session.commit()

    flash('Successfully registered!.', 'success')
    return redirect(url_for('student_view.my_registrations'))


# ========================================================
# 5. MY REGISTRATIONS (Dashboard)
# ========================================================
@student_view.route('/my-registrations')
@login_required
def my_registrations():
    # RESTRICT: Only Students
    if not isinstance(current_user, Student):
        return redirect(url_for('student_view.home'))

    registrations = Registration.query.filter_by(student_id=current_user.student_id).all()
    
    # Get list of events user has already reviewed
    feedback_list = Feedback.query.filter_by(student_id=current_user.student_id).all()
    feedback_event_ids = [f.event_id for f in feedback_list]

    return render_template('student/my_registrations.html', 
                           user=current_user, 
                           registrations=registrations,
                           feedback_event_ids=feedback_event_ids,
                           now=datetime.now())


# ========================================================
# 6. CANCEL REGISTRATION
# ========================================================
@student_view.route('/cancel-registration/<int:event_id>', methods=['POST'])
@login_required
def cancel_registration(event_id):
    if not isinstance(current_user, Student):
        return redirect(url_for('student_view.home'))

    event = Event.query.get_or_404(event_id)
    
    # Validation: Cannot cancel if started
    if event.start_datetime < datetime.now():
        flash('Cancellation is no longer allowed.The event has already started.', 'danger')
        return redirect(url_for('student_view.my_registrations'))

    reg = Registration.query.filter_by(student_id=current_user.student_id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash('Registration cancelled successfully.', 'success')
    
    return redirect(url_for('student_view.my_registrations'))


# ========================================================
# 7. SUBMIT FEEDBACK
# ========================================================
@student_view.route('/feedback/<int:event_id>', methods=['POST'])
@login_required
def submit_feedback(event_id):
    if not isinstance(current_user, Student):
        return redirect(url_for('student_view.home'))

    # 1. Save
    rating = request.form.get('rating')
    comments = request.form.get('comments')

    new_feedback = Feedback(
        student_id=current_user.student_id,
        event_id=event_id,
        rating=rating,
        comments=comments,
        submitted_at=datetime.now()
    )
    db.session.add(new_feedback)
    db.session.commit()

    flash('Feedback submitted!', 'success')
    return redirect(url_for('student_view.my_registrations'))


# ========================================================
# 8. ORGANIZERS LIST 
# ========================================================
@student_view.route('/organizers')
@login_required
def organizers():
    # ALLOW: Student, Organizer, OR Lecturer
    if not isinstance(current_user, (Student, Organizer, Lecturer)):
        return redirect(url_for('auth.login'))
    
    # 1. Get current page number (defaults to 1)
    page = request.args.get('page', 1, type=int)
        
    # 2. Base Query (Active Organizers only)
    query = Organizer.query.filter_by(organizer_account_status='Active')

    # 3. Apply Pagination (6 items per page)
    # error_out=False prevents 404 errors if the page number is out of range
    organizers_paginated = query.paginate(page=page, per_page=6, error_out=False)

    return render_template('student/organizers_list.html', organizers=organizers_paginated)

# ========================================================
# 9. VIEW SPECIFIC ORGANIZER'S EVENTS (Dedicated Page)
# ========================================================
@student_view.route('/club/<string:organizer_id>')
@login_required
def view_club_events(organizer_id):
    # ALLOW: Student, Organizer, OR Lecturer
    if not isinstance(current_user, (Student, Organizer, Lecturer)):
        return redirect(url_for('auth.login'))

    # Get the specific organizer
    org = Organizer.query.filter_by(organizer_id=organizer_id).first_or_404()

    # Get ONLY their upcoming events
    current_dt = datetime.now()
    club_events = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.event_status == 'Upcoming',
        Event.start_datetime >= current_dt
    ).order_by(Event.start_datetime.asc()).all()

    return render_template('student/club_events.html', organizer=org, events=club_events)


# ========================================================
# 10. Receive Announcements
# ========================================================
@student_view.route('/announcements')
@login_required
def announcements():
    try:
        # UPDATED: Added current_user.student_id to the filter list
        all_announcements = Announcements.query.filter(
            Announcements.target_audience.in_(['All', 'Student', current_user.student_id])
        ).order_by(Announcements.sent_at.desc()).all()
        
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        all_announcements = []
    
    return render_template('student/announcements.html', 
                           user=current_user, 
                           announcements=all_announcements)

@student_view.context_processor
def inject_announcement_ids():
    if current_user.is_authenticated:
        # UPDATED: Added current_user.student_id here too for the notification badge
        recent_anns = Announcements.query.filter(
            Announcements.target_audience.in_(['All', 'Student', current_user.student_id])
        ).order_by(Announcements.sent_at.desc()).all()
        
        # Pass the list of IDs to all templates
        return dict(recent_announcement_ids=[a.announcement_id for a in recent_anns])
    
    return dict(recent_announcement_ids=[])

