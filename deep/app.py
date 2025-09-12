from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import requests
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///strava.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    profile_medium = db.Column(db.String(200))
    profile = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    sex = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    activities = db.relationship('Activity', backref='athlete', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(200))
    distance = db.Column(db.Float)  # meters
    moving_time = db.Column(db.Integer)  # seconds
    elapsed_time = db.Column(db.Integer)  # seconds
    total_elevation_gain = db.Column(db.Float)  # meters
    type = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)
    start_date_local = db.Column(db.DateTime)
    timezone = db.Column(db.String(100))
    utc_offset = db.Column(db.Integer)
    achievement_count = db.Column(db.Integer)
    kudos_count = db.Column(db.Integer)
    comment_count = db.Column(db.Integer)
    athlete_count = db.Column(db.Integer)
    photo_count = db.Column(db.Integer)
    trainer = db.Column(db.Boolean)
    commute = db.Column(db.Boolean)
    manual = db.Column(db.Boolean)
    private = db.Column(db.Boolean)
    flagged = db.Column(db.Boolean)
    average_speed = db.Column(db.Float)  # m/s
    max_speed = db.Column(db.Float)  # m/s
    average_cadence = db.Column(db.Float)
    average_temp = db.Column(db.Float)
    average_watts = db.Column(db.Float)
    max_watts = db.Column(db.Float)
    weighted_average_watts = db.Column(db.Float)
    kilojoules = db.Column(db.Float)
    device_watts = db.Column(db.Boolean)
    has_heartrate = db.Column(db.Boolean)
    average_heartrate = db.Column(db.Float)
    max_heartrate = db.Column(db.Float)
    elev_high = db.Column(db.Float)
    elev_low = db.Column(db.Float)
    upload_id = db.Column(db.BigInteger)
    upload_id_str = db.Column(db.String(100))
    external_id = db.Column(db.String(100))
    from_accepted_tag = db.Column(db.Boolean)
    pr_count = db.Column(db.Integer)
    total_photo_count = db.Column(db.Integer)
    has_kudoed = db.Column(db.Boolean)
    workout_type = db.Column(db.Integer)
    description = db.Column(db.Text)
    calories = db.Column(db.Float)
    gear_id = db.Column(db.String(100))
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Streak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'))
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_days = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Strava OAuth Routes
@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    # Get today's activities
    today = datetime.now().date()
    today_activities = Activity.query.filter(
        func.date(Activity.start_date_local) == today
    ).all()

    # Calculate today's metrics
    today_metrics = {
        'count': len(today_activities),
        'distance': sum(a.distance for a in today_activities) / 1000,  # convert to km
        'elevation': sum(a.total_elevation_gain for a in today_activities),
        'time': sum(a.moving_time for a in today_activities) / 3600  # convert to hours
    }

    # Get streak info
    streak = Streak.query.filter_by(athlete_id=session.get('athlete_id')).first()

    # Get weekly data
    week_ago = today - timedelta(days=7)
    weekly_activities = Activity.query.filter(
        Activity.start_date_local >= week_ago
    ).all()

    weekly_metrics = {
        'count': len(weekly_activities),
        'distance': sum(a.distance for a in weekly_activities) / 1000,
        'elevation': sum(a.total_elevation_gain for a in weekly_activities),
        'time': sum(a.moving_time for a in weekly_activities) / 3600
    }

    # Get monthly data
    month_ago = today - timedelta(days=30)
    monthly_activities = Activity.query.filter(
        Activity.start_date_local >= month_ago
    ).all()

    monthly_metrics = {
        'count': len(monthly_activities),
        'distance': sum(a.distance for a in monthly_activities) / 1000,
        'elevation': sum(a.total_elevation_gain for a in monthly_activities),
        'time': sum(a.moving_time for a in monthly_activities) / 3600
    }

    return render_template(
        'index.html',
        today=today_metrics,
        weekly=weekly_metrics,
        monthly=monthly_metrics,
        streak=streak
    )

@app.route('/login')
def login():
    # Redirect to Strava authorization page
    client_id = os.getenv('STRAVA_CLIENT_ID')
    redirect_uri = url_for('authorized', _external=True)
    strava_auth_url = (
        f"<https://www.strava.com/oauth/authorize?">
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=activity:read_all"
    )
    return redirect(strava_auth_url)

@app.route('/authorized')
def authorized():
    # Exchange authorization code for access token
    code = request.args.get('code')
    if not code:
        return "Authorization failed", 400

    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')

    response = requests.post(
        '<https://www.strava.com/oauth/token>',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )

    if response.status_code != 200:
        return "Token exchange failed", 400

    token_data = response.json()
    session['access_token'] = token_data['access_token']
    session['refresh_token'] = token_data['refresh_token']
    session['athlete_info'] = token_data['athlete']
    session['athlete_id'] = token_data['athlete']['id']

    # Store or update athlete in database
    athlete = Athlete.query.get(token_data['athlete']['id'])
    if not athlete:
        athlete = Athlete(id=token_data['athlete']['id'])
        db.session.add(athlete)

    athlete.username = token_data['athlete'].get('username')
    athlete.firstname = token_data['athlete'].get('firstname')
    athlete.lastname = token_data['athlete'].get('lastname')
    athlete.profile_medium = token_data['athlete'].get('profile_medium')
    athlete.profile = token_data['athlete'].get('profile')
    athlete.city = token_data['athlete'].get('city')
    athlete.state = token_data['athlete'].get('state')
    athlete.country = token_data['athlete'].get('country')
    athlete.sex = token_data['athlete'].get('sex')

    db.session.commit()

    # Fetch initial activities
    fetch_activities()

    return redirect(url_for('index'))

def fetch_activities():
    # Fetch activities from Strava API
    access_token = session.get('access_token')
    if not access_token:
        return

    headers = {'Authorization': f'Bearer {access_token}'}
    page = 1
    per_page = 100

    while True:
        response = requests.get(
            '<https://www.strava.com/api/v3/athlete/activities>',
            headers=headers,
            params={'page': page, 'per_page': per_page}
        )

        if response.status_code != 200:
            break

        activities = response.json()
        if not activities:
            break

        for activity_data in activities:
            # Check if activity already exists
            activity = Activity.query.filter_by(strava_id=activity_data['id']).first()
            if not activity:
                activity = Activity(strava_id=activity_data['id'])
                db.session.add(activity)

            # Update activity data
            activity.name = activity_data.get('name')
            activity.distance = activity_data.get('distance')
            activity.moving_time = activity_data.get('moving_time')
            activity.elapsed_time = activity_data.get('elapsed_time')
            activity.total_elevation_gain = activity_data.get('total_elevation_gain')
            activity.type = activity_data.get('type')
            activity.start_date = datetime.fromisoformat(activity_data['start_date'].replace('Z', '+00:00'))
            activity.start_date_local = datetime.fromisoformat(activity_data['start_date_local'].replace('Z', '+00:00'))
            activity.timezone = activity_data.get('timezone')
            activity.utc_offset = activity_data.get('utc_offset')
            activity.achievement_count = activity_data.get('achievement_count')
            activity.kudos_count = activity_data.get('kudos_count')
            activity.comment_count = activity_data.get('comment_count')
            activity.athlete_count = activity_data.get('athlete_count')
            activity.photo_count = activity_data.get('photo_count')
            activity.trainer = activity_data.get('trainer')
            activity.commute = activity_data.get('commute')
            activity.manual = activity_data.get('manual')
            activity.private = activity_data.get('private')
            activity.flagged = activity_data.get('flagged')
            activity.average_speed = activity_data.get('average_speed')
            activity.max_speed = activity_data.get('max_speed')
            activity.average_cadence = activity_data.get('average_cadence')
            activity.average_temp = activity_data.get('average_temp')
            activity.average_watts = activity_data.get('average_watts')
            activity.max_watts = activity_data.get('max_watts')
            activity.weighted_average_watts = activity_data.get('weighted_average_watts')
            activity.kilojoules = activity_data.get('kilojoules')
            activity.device_watts = activity_data.get('device_watts')
            activity.has_heartrate = activity_data.get('has_heartrate')
            activity.average_heartrate = activity_data.get('average_heartrate')
            activity.max_heartrate = activity_data.get('max_heartrate')
            activity.elev_high = activity_data.get('elev_high')
            activity.elev_low = activity_data.get('elev_low')
            activity.upload_id = activity_data.get('upload_id')
            activity.upload_id_str = activity_data.get('upload_id_str')
            activity.external_id = activity_data.get('external_id')
            activity.from_accepted_tag = activity_data.get('from_accepted_tag')
            activity.pr_count = activity_data.get('pr_count')
            activity.total_photo_count = activity_data.get('total_photo_count')
            activity.has_kudoed = activity_data.get('has_kudoed')
            activity.workout_type = activity_data.get('workout_type')
            activity.description = activity_data.get('description')
            activity.calories = activity_data.get('calories')
            activity.gear_id = activity_data.get('gear_id')
            activity.athlete_id = session.get('athlete_id')

        page += 1

    db.session.commit()
    update_streak()

def update_streak():
    athlete_id = session.get('athlete_id')
    if not athlete_id:
        return

    # Get all activity dates
    activity_dates = db.session.query(
        func.date(Activity.start_date_local).label('activity_date')
    ).filter(
        Activity.athlete_id == athlete_id
    ).distinct().all()

    activity_dates = [d[0] for d in activity_dates]
    activity_dates.sort()

    if not activity_dates:
        return

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    last_date = None

    for date in activity_dates:
        if last_date is None:
            temp_streak = 1
        else:
            days_diff = (date - last_date).days
            if days_diff == 1:
                temp_streak += 1
            elif days_diff > 1:
                temp_streak = 1

        if temp_streak > longest_streak:
            longest_streak = temp_streak

        last_date = date

    # Check if today or yesterday was an activity for current streak
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    if today in activity_dates:
        current_streak = temp_streak
    elif yesterday in activity_dates:
        current_streak = temp_streak
    else:
        current_streak = 0

    # Update or create streak record
    streak = Streak.query.filter_by(athlete_id=athlete_id).first()
    if not streak:
        streak = Streak(athlete_id=athlete_id)
        db.session.add(streak)

    streak.current_streak = current_streak
    streak.longest_streak = longest_streak
    streak.total_days = len(activity_dates)
    streak.last_activity_date = last_date

    db.session.commit()

@app.route('/activities')
def activities():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 20
    activity_type = request.args.get('type', '')

    query = Activity.query.filter_by(athlete_id=session.get('athlete_id'))

    if activity_type:
        query = query.filter_by(type=activity_type.capitalize())

    activities = query.order_by(desc(Activity.start_date)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Get unique activity types for filter
    activity_types = db.session.query(
        Activity.type
    ).filter_by(
        athlete_id=session.get('athlete_id')
    ).distinct().all()

    activity_types = [t[0] for t in activity_types]

    return render_template(
        'activities.html',
        activities=activities,
        activity_types=activity_types,
        selected_type=activity_type
    )

@app.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))

    activity = Activity.query.get_or_404(activity_id)

    # Check if activity belongs to the authenticated athlete
    if activity.athlete_id != session.get('athlete_id'):
        return "Access denied", 403

    # Find similar activities from previous years for comparison
    similar_activities = Activity.query.filter(
        Activity.athlete_id == session.get('athlete_id'),
        Activity.type == activity.type,
        func.strftime('%m-%d', Activity.start_date_local) == func.strftime('%m-%d', activity.start_date_local),
        Activity.id != activity.id
    ).all()

    return render_template(
        'activity_detail.html',
        activity=activity,
        similar_activities=similar_activities
    )

@app.route('/weekly')
def weekly_view():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    # Get activities from the last 12 weeks
    weeks_ago = datetime.now() - timedelta(weeks=12)
    activities = Activity.query.filter(
        Activity.athlete_id == session.get('athlete_id'),
        Activity.start_date_local >= weeks_ago
    ).all()

    # Group activities by week
    weekly_data = defaultdict(lambda: {
        'count': 0,
        'distance': 0,
        'elevation': 0,
        'time': 0
    })

    for activity in activities:
        week_start = activity.start_date_local - timedelta(days=activity.start_date_local.weekday())
        week_key = week_start.strftime('%Y-%U')

        weekly_data[week_key]['count'] += 1
        weekly_data[week_key]['distance'] += activity.distance / 1000  # convert to km
        weekly_data[week_key]['elevation'] += activity.total_elevation_gain
        weekly_data[week_key]['time'] += activity.moving_time / 3600  # convert to hours

    # Convert to list and sort by week
    weekly_data = [{
        'week': week,
        'data': weekly_data[week]
    } for week in sorted(weekly_data.keys(), reverse=True)]

    return render_template('weekly.html', weekly_data=weekly_data)

@app.route('/monthly')
def monthly_view():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    # Get activities from the last 12 months
    months_ago = datetime.now() - timedelta(days=365)
    activities = Activity.query.filter(
        Activity.athlete_id == session.get('athlete_id'),
        Activity.start_date_local >= months_ago
    ).all()

    # Group activities by month
    monthly_data = defaultdict(lambda: {
        'count': 0,
        'distance': 0,
        'elevation': 0,
        'time': 0
    })

    for activity in activities:
        month_key = activity.start_date_local.strftime('%Y-%m')

        monthly_data[month_key]['count'] += 1
        monthly_data[month_key]['distance'] += activity.distance / 1000  # convert to km
        monthly_data[month_key]['elevation'] += activity.total_elevation_gain
        monthly_data[month_key]['time'] += activity.moving_time / 3600  # convert to hours

    # Convert to list and sort by month
    monthly_data = [{
        'month': month,
        'data': monthly_data[month]
    } for month in sorted(monthly_data.keys(), reverse=True)]

    return render_template('monthly.html', monthly_data=monthly_data)

@app.route('/refresh')
def refresh_activities():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    fetch_activities()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)