from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lodhi-samaj-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lodhi_samaj.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'

# ─── MODELS ─────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='member')  # member, admin, superadmin
    status = db.Column(db.String(20), default='pending')  # pending, active, suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship('Member', backref='user', uselist=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    father_name = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    village = db.Column(db.String(100))
    education = db.Column(db.String(200))
    profession = db.Column(db.String(200))
    blood_group = db.Column(db.String(5))
    photo = db.Column(db.String(200), default='default.png')
    bio = db.Column(db.Text)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.String(30))
    venue = db.Column(db.String(200))
    image = db.Column(db.String(200))
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    year = db.Column(db.String(10))
    image = db.Column(db.String(200))
    member = db.relationship('Member', backref='achievements')

class MatrimonialProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    height = db.Column(db.String(20))
    complexion = db.Column(db.String(30))
    education = db.Column(db.String(200))
    profession = db.Column(db.String(200))
    city = db.Column(db.String(100))
    about = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    member = db.relationship('Member', backref='matrimonial')

class BloodDonor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    blood_group = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(100))
    available = db.Column(db.Boolean, default=True)
    member = db.relationship('Member', backref='donor_info')

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── ROUTES ─────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    events = Event.query.order_by(Event.created_at.desc()).limit(3).all()
    achievements = Achievement.query.order_by(Achievement.id.desc()).limit(3).all()
    member_count = User.query.filter_by(status='active').count()
    event_count = Event.query.count()
    return render_template('home.html', events=events, achievements=achievements,
                           member_count=member_count, event_count=event_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile number already registered!', 'danger')
            return redirect(url_for('register'))
        user = User(name=name, email=email, mobile=mobile,
                    password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.flush()
        member = Member(
            user_id=user.id,
            father_name=request.form.get('father_name'),
            dob=request.form.get('dob'),
            gender=request.form.get('gender'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            village=request.form.get('village'),
            education=request.form.get('education'),
            profession=request.form.get('profession'),
            blood_group=request.form.get('blood_group'),
        )
        db.session.add(member)
        db.session.commit()
        flash('Registration successful! Admin approval pending.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if user.status == 'pending':
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            if user.status == 'suspended':
                flash('Your account has been suspended.', 'danger')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role in ['admin', 'superadmin']:
        return redirect(url_for('admin_dashboard'))
    member = Member.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard.html', member=member)

@app.route('/directory')
@login_required
def directory():
    search = request.args.get('search', '')
    city = request.args.get('city', '')
    profession = request.args.get('profession', '')
    blood_group = request.args.get('blood_group', '')
    page = request.args.get('page', 1, type=int)

    query = Member.query.join(User).filter(User.status == 'active')
    if search:
        query = query.filter(User.name.ilike(f'%{search}%'))
    if city:
        query = query.filter(Member.city.ilike(f'%{city}%'))
    if profession:
        query = query.filter(Member.profession.ilike(f'%{profession}%'))
    if blood_group:
        query = query.filter(Member.blood_group == blood_group)

    members = query.paginate(page=page, per_page=12, error_out=False)
    cities = db.session.query(Member.city).filter(Member.city != None).distinct().all()
    return render_template('directory.html', members=members, cities=cities,
                           search=search, city=city, profession=profession, blood_group=blood_group)

@app.route('/events')
def events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('events.html', events=events)

@app.route('/achievements')
def achievements():
    achievements = Achievement.query.order_by(Achievement.id.desc()).all()
    return render_template('achievements.html', achievements=achievements)

@app.route('/matrimonial')
@login_required
def matrimonial():
    gender_filter = request.args.get('gender', '')
    city_filter = request.args.get('city', '')
    query = MatrimonialProfile.query.filter_by(status='approved')
    if gender_filter:
        query = query.filter_by(gender=gender_filter)
    if city_filter:
        query = query.filter(MatrimonialProfile.city.ilike(f'%{city_filter}%'))
    profiles = query.all()
    return render_template('matrimonial.html', profiles=profiles,
                           gender_filter=gender_filter, city_filter=city_filter)

@app.route('/matrimonial/register', methods=['GET', 'POST'])
@login_required
def matrimonial_register():
    member = Member.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        profile = MatrimonialProfile(
            member_id=member.id,
            gender=request.form.get('gender'),
            dob=request.form.get('dob'),
            height=request.form.get('height'),
            complexion=request.form.get('complexion'),
            education=request.form.get('education'),
            profession=request.form.get('profession'),
            city=request.form.get('city'),
            about=request.form.get('about'),
        )
        db.session.add(profile)
        db.session.commit()
        flash('Matrimonial profile submitted! Admin approval pending.', 'success')
        return redirect(url_for('matrimonial'))
    return render_template('matrimonial_register.html', member=member)

@app.route('/blood-donors')
def blood_donors():
    blood_group = request.args.get('blood_group', '')
    city = request.args.get('city', '')
    query = BloodDonor.query.filter_by(available=True)
    if blood_group:
        query = query.filter_by(blood_group=blood_group)
    if city:
        query = query.join(Member).filter(Member.city.ilike(f'%{city}%'))
    donors = query.all()
    return render_template('blood_donors.html', donors=donors,
                           blood_group=blood_group, city=city)

@app.route('/gallery')
def gallery():
    category = request.args.get('category', '')
    query = Gallery.query
    if category:
        query = query.filter_by(category=category)
    photos = query.order_by(Gallery.uploaded_at.desc()).all()
    categories = db.session.query(Gallery.category).distinct().all()
    return render_template('gallery.html', photos=photos, categories=categories, category=category)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fb = Feedback(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message'),
        )
        db.session.add(fb)
        db.session.commit()
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ─── ADMIN ROUTES ────────────────────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'superadmin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_members': User.query.filter_by(role='member').count(),
        'pending': User.query.filter_by(status='pending').count(),
        'active': User.query.filter_by(status='active').count(),
        'events': Event.query.count(),
        'matrimonial_pending': MatrimonialProfile.query.filter_by(status='pending').count(),
        'messages': Feedback.query.count(),
    }
    pending_users = User.query.filter_by(status='pending').order_by(User.created_at.desc()).all()
    recent_feedback = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           pending_users=pending_users, recent_feedback=recent_feedback)

@app.route('/admin/members')
@login_required
@admin_required
def admin_members():
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        users = User.query.filter(User.role == 'member').order_by(User.created_at.desc()).all()
    else:
        users = User.query.filter_by(role='member', status=status_filter).order_by(User.created_at.desc()).all()
    return render_template('admin/members.html', users=users, status_filter=status_filter)

@app.route('/admin/approve/<int:user_id>')
@login_required
@admin_required
def approve_member(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    flash(f'{user.name} approved successfully!', 'success')
    return redirect(url_for('admin_members'))

@app.route('/admin/reject/<int:user_id>')
@login_required
@admin_required
def reject_member(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'rejected'
    db.session.commit()
    flash(f'{user.name} rejected.', 'warning')
    return redirect(url_for('admin_members'))

@app.route('/admin/suspend/<int:user_id>')
@login_required
@admin_required
def suspend_member(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'suspended'
    db.session.commit()
    flash(f'{user.name} suspended.', 'warning')
    return redirect(url_for('admin_members'))

@app.route('/admin/events', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_events():
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            event_date=request.form.get('event_date'),
            venue=request.form.get('venue'),
            posted_by=current_user.id,
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added!', 'success')
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/events/delete/<int:event_id>')
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('admin_events'))

@app.route('/admin/matrimonial')
@login_required
@admin_required
def admin_matrimonial():
    profiles = MatrimonialProfile.query.order_by(MatrimonialProfile.id.desc()).all()
    return render_template('admin/matrimonial.html', profiles=profiles)

@app.route('/admin/matrimonial/approve/<int:pid>')
@login_required
@admin_required
def approve_matrimonial(pid):
    p = MatrimonialProfile.query.get_or_404(pid)
    p.status = 'approved'
    db.session.commit()
    flash('Profile approved!', 'success')
    return redirect(url_for('admin_matrimonial'))

@app.route('/admin/matrimonial/reject/<int:pid>')
@login_required
@admin_required
def reject_matrimonial(pid):
    p = MatrimonialProfile.query.get_or_404(pid)
    p.status = 'rejected'
    db.session.commit()
    flash('Profile rejected.', 'warning')
    return redirect(url_for('admin_matrimonial'))

@app.route('/admin/gallery', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_gallery():
    if request.method == 'POST':
        photo = Gallery(
            title=request.form.get('title'),
            image_url=request.form.get('image_url'),
            category=request.form.get('category'),
        )
        db.session.add(photo)
        db.session.commit()
        flash('Photo added!', 'success')
    photos = Gallery.query.order_by(Gallery.uploaded_at.desc()).all()
    return render_template('admin/gallery.html', photos=photos)

@app.route('/admin/gallery/delete/<int:gid>')
@login_required
@admin_required
def delete_gallery(gid):
    photo = Gallery.query.get_or_404(gid)
    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted.', 'info')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/achievements', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_achievements():
    if request.method == 'POST':
        ach = Achievement(
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            year=request.form.get('year'),
        )
        db.session.add(ach)
        db.session.commit()
        flash('Achievement added!', 'success')
    achievements = Achievement.query.order_by(Achievement.id.desc()).all()
    return render_template('admin/achievements.html', achievements=achievements)

@app.route('/admin/messages')
@login_required
@admin_required
def admin_messages():
    messages = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/blood-donors', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_blood():
    if request.method == 'POST':
        donor = BloodDonor(
            blood_group=request.form.get('blood_group'),
            city=request.form.get('city'),
            available=True,
        )
        db.session.add(donor)
        db.session.commit()
        flash('Donor added!', 'success')
    donors = BloodDonor.query.all()
    return render_template('admin/blood.html', donors=donors)

# ─── SEED DATA ──────────────────────────────────────────────────────────────

def seed_data():
    if User.query.first():
        return
    # Super Admin
    admin = User(name='Super Admin', email='admin@lodhisamaj.in', mobile='9999999999',
                 password_hash=generate_password_hash('admin123'), role='superadmin', status='active')
    db.session.add(admin)
    db.session.flush()

    # Sample members
    for i, (name, city, prof, bg) in enumerate([
        ('Ramesh Lodhi', 'Lucknow', 'Teacher', 'B+'),
        ('Suresh Kumar', 'Kanpur', 'Engineer', 'O+'),
        ('Priya Lodhi', 'Agra', 'Doctor', 'A+'),
        ('Vikram Singh', 'Varanasi', 'Farmer', 'B-'),
        ('Anita Devi', 'Allahabad', 'Nurse', 'O-'),
    ]):
        u = User(name=name, email=f'member{i+1}@test.com', mobile=f'98765432{i+1:02d}',
                 password_hash=generate_password_hash('test123'), role='member', status='active')
        db.session.add(u)
        db.session.flush()
        m = Member(user_id=u.id, city=city, profession=prof, blood_group=bg,
                   gender='Male' if i % 2 == 0 else 'Female', state='Uttar Pradesh')
        db.session.add(m)
        db.session.flush()
        db.session.add(BloodDonor(member_id=m.id, blood_group=bg, city=city, available=True))

    # Sample events
    for title, desc, date_str, venue in [
        ('Samaj Mahasabha 2026', 'Varshik mahasabha mein aap sabka swagat hai.', '15 May 2026', 'Town Hall, Lucknow'),
        ('Scholarship Distribution', 'Medhavi chhatron ko scholarship vitran.', '20 June 2026', 'Community Center, Kanpur'),
        ('Blood Donation Camp', 'Rakhtdan mahadan — aayein aur jeevan bachayein.', '10 July 2026', 'Civil Hospital, Agra'),
    ]:
        db.session.add(Event(title=title, description=desc, event_date=date_str, venue=venue, posted_by=1))

    # Sample achievements
    for title, cat, year in [
        ('IAS Officer — Proud Moment', 'Education', '2025'),
        ('National Sports Award Winner', 'Sports', '2024'),
        ('Best Social Worker Award', 'Social Service', '2025'),
    ]:
        db.session.add(Achievement(title=title, category=cat, year=year,
                                   description='Community ka garv — hamare beech se aaya yeh achievement.'))

    # Sample gallery
    for title, cat, url in [
        ('Mahasabha 2025', 'Events', 'https://via.placeholder.com/400x300/1A3A6B/FFFFFF?text=Mahasabha+2025'),
        ('Scholarship Ceremony', 'Events', 'https://via.placeholder.com/400x300/C8922A/FFFFFF?text=Scholarship+2025'),
        ('Cultural Program', 'Functions', 'https://via.placeholder.com/400x300/2E5FAE/FFFFFF?text=Cultural+Program'),
        ('Blood Donation Camp', 'Events', 'https://via.placeholder.com/400x300/DC3545/FFFFFF?text=Blood+Donation'),
        ('Youth Meet 2025', 'Youth', 'https://via.placeholder.com/400x300/28A745/FFFFFF?text=Youth+Meet'),
        ('Sports Day', 'Sports', 'https://via.placeholder.com/400x300/6F42C1/FFFFFF?text=Sports+Day'),
    ]:
        db.session.add(Gallery(title=title, category=cat, image_url=url))

    db.session.commit()
    print("✓ Seed data created")

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
