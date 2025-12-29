from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user
from models import db, Student, Event, Registration, Category, Rooms, Organizer, Admin
from datetime import datetime
from forms import ResetPasswordForm 

user_view = Blueprint('user_view', __name__)

# ========================================================
# 1. HOME PAGE
# ========================================================
@user_view.route('/home')
@login_required
def home():
    # Security check: Ensure user is a Student
    if not isinstance(current_user, Student):
        return redirect(url_for('auth.login'))

    current_dt = datetime.now()
    categories = Category.query.all()

    # Upcoming Events (Published & Future)
    upcoming_events = Event.query.filter(
        Event.start_datetime >= current_dt,
        Event.event_status == 'Upcoming' 
    ).order_by(Event.start_datetime.asc()).limit(6).all()

    # Newest Added Events
    new_events = Event.query.filter(
        Event.start_datetime >= current_dt,
        Event.event_status == 'Upcoming'
    ).order_by(Event.event_id.desc()).limit(6).all()

    return render_template('home.html', 
                           user=current_user, 
                           categories_nav=categories, 
                           upcoming=upcoming_events, 
                           new=new_events)


# ========================================================
# 2. EVENTS LISTING & FILTERING
# ========================================================
@user_view.route('/events')
@login_required
def events():
    # Get Filters
    category_id = request.args.get('category')
    search_query = request.args.get('search', '').strip()
    sort = request.args.get('sort', '')
    
    current_dt = datetime.now()
    categories = Category.query.all()

    # Base Query
    query = Event.query.filter(Event.event_status == 'Upcoming')

    # 1. Filter by Category
    if category_id:
        query = query.filter(Event.category_id == category_id)

    # 2. Filter by Search (Title)
    if search_query:
        query = query.filter(Event.title.ilike(f'%{search_query}%'))

    # 3. Filter Expired (Default: Hide past events)
    query = query.filter(Event.start_datetime >= current_dt)

    # 4. Sorting
    if sort == 'date':
        query = query.order_by(Event.start_datetime.asc())
    elif sort == 'a-z':
        query = query.order_by(Event.title.asc())
    elif sort == 'z-a':
        query = query.order_by(Event.title.desc())
    else:
        # Default sort
        query = query.order_by(Event.start_datetime.asc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    events_paginated = query.paginate(page=page, per_page=9)

    return render_template('events.html', 
                           user=current_user,
                           events=events_paginated, 
                           categories_nav=categories,
                           search_query=search_query,
                           current_category=category_id)


# ========================================================
# 3. EVENT DETAILS & REGISTRATION
# ========================================================
@user_view.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if student is already registered
    is_registered = Registration.query.filter_by(
        student_id=current_user.student_id, 
        event_id=event_id
    ).first()

    # Check available spots
    registered_count = Registration.query.filter_by(event_id=event_id).count()
    spots_left = event.capacity - registered_count

    return render_template('event_details.html', 
                           user=current_user, 
                           event=event, 
                           is_registered=is_registered,
                           spots_left=spots_left)


@user_view.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if already registered
    existing = Registration.query.filter_by(
        student_id=current_user.student_id, 
        event_id=event_id
    ).first()

    if existing:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('user_view.event_details', event_id=event_id))

    # Check capacity
    count = Registration.query.filter_by(event_id=event_id).count()
    if count >= event.capacity:
        flash('Sorry, this event is fully booked.', 'danger')
        return redirect(url_for('user_view.event_details', event_id=event_id))

    # Register Student
    new_reg = Registration(
        student_id=current_user.student_id,
        event_id=event_id,
        status='Confirmed',
        registration_date=datetime.now()
    )
    db.session.add(new_reg)
    db.session.commit()

    flash('Successfully registered for event!', 'success')
    return redirect(url_for('user_view.my_registrations'))


@user_view.route('/cancel-registration/<int:event_id>', methods=['POST'])
@login_required
def cancel_registration(event_id):
    reg = Registration.query.filter_by(
        student_id=current_user.student_id, 
        event_id=event_id
    ).first()

    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash('Registration cancelled.', 'info')
    
    return redirect(url_for('user_view.my_registrations'))


# ========================================================
# 4. STUDENT DASHBOARD / PROFILE
# ========================================================
@user_view.route('/my-registrations')
@login_required
def my_registrations():
    # Get all events this student has registered for
    registrations = Registration.query.filter_by(student_id=current_user.student_id).all()
    return render_template('my_registrations.html', user=current_user, registrations=registrations)


@user_view.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ResetPasswordForm() 

    if request.method == 'POST':
        if form.validate_on_submit():
            # UPDATED: Use plain text comparison instead of bcrypt
            if current_user.student_password == form.old_pwd.data:
                # UPDATED: Save plain text password
                current_user.student_password = form.new_pwd.data
                db.session.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Incorrect old password.', 'danger')
        
    return render_template('profile.html', user=current_user, form=form)


# ========================================================
# 5. ORGANIZERS LIST
# ========================================================
@user_view.route('/organizers')
@login_required
def organizers():
    # List all Organizers so students can browse them
    organizers = Organizer.query.filter_by(organizer_account_status='Active').all()
    return render_template('organizers_list.html', user=current_user, organizers=organizers)

@user_view.route('/organizer/<string:organizer_id>')
@login_required
def organizer_details(organizer_id):
    organizer = Organizer.query.get_or_404(organizer_id)
    # Show events by this organizer
    events = Event.query.filter_by(organizer_id=organizer_id, event_status='Upcoming').all()
    return render_template('organizer_public_profile.html', user=current_user, organizer=organizer, events=events)