from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, Event, Booking, Category, Rooms, Organizer
from datetime import datetime

organizer_view = Blueprint('organizer_view', __name__)

@organizer_view.route('/dashboard')
@login_required
def dashboard():
    # Security check
    if not isinstance(current_user, Organizer):
        return redirect(url_for('auth.login'))

    # 1. Get stats for this specific Organizer
    my_events_count = Event.query.filter_by(organizer_id=current_user.organizer_id).count()
    
    # 2. Get total bookings for their events
    my_bookings_count = db.session.query(Booking).join(Event).filter(
        Event.organizer_id == current_user.organizer_id
    ).count()

    # 3. Get recent bookings (last 5)
    recent_bookings = db.session.query(Booking).join(Event).filter(
        Event.organizer_id == current_user.organizer_id
    ).order_by(Booking.booking_date.desc()).limit(5).all()

    return render_template('organizer/dashboard.html', 
                           user=current_user,
                           events_count=my_events_count,
                           bookings_count=my_bookings_count,
                           recent_bookings=recent_bookings)

@organizer_view.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    # Load categories and rooms for the dropdowns
    categories = Category.query.all()
    rooms = Rooms.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date') # Format: YYYY-MM-DD HH:MM:SS
        end_date = request.form.get('end_date')
        venue_id = request.form.get('venue') # This maps to room_id in your schema
        category_id = request.form.get('category')
        capacity = request.form.get('capacity')

        try:
            new_event = Event(
                title=title,
                description=description,
                start_datetime=start_date,
                end_datetime=end_date,
                event_status='Upcoming',
                venue_location=venue_id, # Or map to room name if preferred
                capacity=capacity,
                category_id=category_id,
                organizer_id=current_user.organizer_id, # Link to THIS organizer
                lecturer_id=None # Null for organizer events
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('organizer_view.my_events'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating event. Please check your inputs.', 'danger')
            print(e)

    return render_template('organizer/create_event.html', user=current_user, categories=categories, rooms=rooms)

@organizer_view.route('/my-events')
@login_required
def my_events():
    # Only show events created by this organizer
    events = Event.query.filter_by(organizer_id=current_user.organizer_id).all()
    return render_template('organizer/my_events.html', user=current_user, events=events)

@organizer_view.route('/bookings/<int:event_id>')
@login_required
def event_bookings(event_id):
    # Ensure this event belongs to the logged-in organizer
    event = Event.query.filter_by(event_id=event_id, organizer_id=current_user.organizer_id).first_or_404()
    
    bookings = Booking.query.filter_by(event_id=event.event_id).all()
    
    return render_template('organizer/event_bookings.html', user=current_user, event=event, bookings=bookings)