from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, Booking, Category, Rooms, Lecturer

lecturer_view = Blueprint('lecturer_view', __name__)

@lecturer_view.route('/dashboard')
@login_required
def dashboard():
    # Security check
    if not isinstance(current_user, Lecturer):
        return redirect(url_for('auth.login'))

    # Stats for this Lecturer
    my_events_count = Event.query.filter_by(lecturer_id=current_user.lecturer_id).count()
    
    my_bookings_count = db.session.query(Booking).join(Event).filter(
        Event.lecturer_id == current_user.lecturer_id
    ).count()

    return render_template('lecturer/dashboard.html', 
                           user=current_user,
                           events_count=my_events_count,
                           bookings_count=my_bookings_count)

@lecturer_view.route('/create-seminar', methods=['GET', 'POST'])
@login_required
def create_event():
    categories = Category.query.all()
    rooms = Rooms.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        venue_id = request.form.get('venue')
        category_id = request.form.get('category')
        capacity = request.form.get('capacity')

        try:
            new_event = Event(
                title=title,
                description=description,
                start_datetime=start_date,
                end_datetime=end_date,
                event_status='Upcoming',
                venue_location=venue_id,
                capacity=capacity,
                category_id=category_id,
                lecturer_id=current_user.lecturer_id, # Link to THIS lecturer
                organizer_id=None
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Seminar created successfully!', 'success')
            return redirect(url_for('lecturer_view.my_events'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating seminar.', 'danger')

    return render_template('lecturer/create_event.html', user=current_user, categories=categories, rooms=rooms)

@lecturer_view.route('/my-events')
@login_required
def my_events():
    # Only show events created by this lecturer
    events = Event.query.filter_by(lecturer_id=current_user.lecturer_id).all()
    return render_template('lecturer/my_events.html', user=current_user, events=events)