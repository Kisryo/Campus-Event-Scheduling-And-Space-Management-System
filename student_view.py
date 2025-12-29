from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user
from models import db, Student, Event, Registration, Category, Organizer
from datetime import datetime
from forms import ResetPasswordForm 

student_view = Blueprint('student_view', __name__)

# ========================================================
# 1. HOME PAGE
# ========================================================
@student_view.route('/home')
@login_required
def home():
    # Security check: Ensure user is a Student
    if not isinstance(current_user, Student):
        return redirect(url_for('auth.login'))

    current_dt = datetime.now()
    categories = Category.query.all()

    # Upcoming Events
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
@student_view.route('/events')
@login_required
def events():
    category_id = request.args.get('category')
    search_query = request.args.get('search', '').strip()
    sort = request.args.get('sort', '')
    
    current_dt = datetime.now()
    categories = Category.query.all()

    query = Event.query.filter(Event.event_status == 'Upcoming')

    if category_id:
        query = query.filter(Event.category_id == category_id)

    if search_query:
        query = query.filter(Event.title.ilike(f'%{search_query}%'))

    query = query.filter(Event.start_datetime >= current_dt)

    if sort == 'date':
        query = query.order_by(Event.start_datetime.asc())
    elif sort == 'a-z':
        query = query.order_by(Event.title.asc())
    elif sort == 'z-a':
        query = query.order_by(Event.title.desc())
    else:
        query = query.order_by(Event.start_datetime.asc())

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
@student_view.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    is_registered = Registration.query.filter_by(
        student_id=current_user.student_id, 
        event_id=event_id
    ).first()

    registered_count = Registration.query.filter_by(event_id=event_id).count()
    spots_left = event.capacity - registered_count

    return render_template('event_details.html', 
                           user=current_user, 
                           event=event, 
                           is_registered=is_registered,
                           spots_left=spots_left)


@student_view.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    existing = Registration.query.filter_by(
        student_id=current_user.student_id, 
        event_id=event_id
    ).first()

    if existing:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('student_view.event_details', event_id=event_id))

    count = Registration.query.filter_by(event_id=event_id).count()
    if count >= event.capacity:
        flash('Sorry, this event is fully booked.', 'danger')
        return redirect(url_for('student_view.event_details', event_id=event_id))

    new_reg = Registration(
        student_id=current_user.student_id,
        event_id=event_id,
        status='Confirmed',
        registration_date=datetime.now()
    )
    db.session.add(new_reg)
    db.session.commit()

    flash('Successfully registered for event!', 'success')
    return redirect(url_for('student_view.my_registrations'))


@student_view.route('/cancel-registration/<int:event_id>', methods=['POST'])
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
    
    return redirect(url_for('student_view.my_registrations'))
