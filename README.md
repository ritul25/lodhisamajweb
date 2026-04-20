# Lodhi Rajpoot Samaj — Community Website
## Flask (Python) + Bootstrap + SQLite

---

## Setup Instructions (Kaise Chalayein)

### Step 1 — Python Install Karein
Python 3.8+ aapke system mein hona chahiye.

### Step 2 — Project Folder Kholen
```
cd lodhi_samaj
```

### Step 3 — Virtual Environment Banayein (Recommended)
```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 4 — Dependencies Install Karein
```
pip install -r requirements.txt
```

### Step 5 — Website Chalayein
```
python app.py
```

### Step 6 — Browser Mein Kholein
```
http://localhost:5000
```

---

## Default Login Credentials

| Role        | Email                    | Password  |
|-------------|--------------------------|-----------|
| Super Admin | admin@lodhisamaj.in      | admin123  |
| Member      | member1@test.com         | test123   |

---

## Website Pages

| Page          | URL                   |
|---------------|-----------------------|
| Home          | /                     |
| Register      | /register             |
| Login         | /login                |
| Dashboard     | /dashboard            |
| Directory     | /directory            |
| Events        | /events               |
| Achievements  | /achievements         |
| Matrimonial   | /matrimonial          |
| Blood Donors  | /blood-donors         |
| Gallery       | /gallery              |
| Contact       | /contact              |
| Admin Panel   | /admin                |

---

## Project Structure

```
lodhi_samaj/
├── app.py                   # Main Flask app + routes + models
├── requirements.txt         # Python dependencies
├── instance/
│   └── lodhi_samaj.db       # SQLite database (auto-created)
├── templates/
│   ├── base.html            # Base layout with navbar + footer
│   ├── home.html            # Homepage
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html       # Member dashboard
│   ├── directory.html       # Member directory
│   ├── events.html          # Events page
│   ├── achievements.html    # Achievements page
│   ├── matrimonial.html     # Matrimonial listings
│   ├── matrimonial_register.html
│   ├── blood_donors.html    # Blood donor search
│   ├── gallery.html         # Photo gallery
│   ├── contact.html         # Contact form
│   └── admin/
│       ├── base_admin.html  # Admin layout with sidebar
│       ├── dashboard.html   # Admin dashboard
│       ├── members.html     # Member management
│       ├── events.html      # Events management
│       ├── matrimonial.html # Matrimonial approval
│       ├── gallery.html     # Gallery management
│       ├── achievements.html
│       ├── blood.html       # Blood donor management
│       └── messages.html    # Contact messages
└── static/
    ├── css/                 # Custom CSS files
    ├── js/                  # Custom JS files
    └── images/              # Uploaded images
```

---

## Production Deployment (Server pe Lagaana)

### cPanel / Shared Hosting:
1. Upload karein sab files
2. Python App setup karein cPanel mein
3. `app.py` ko entry point banayein
4. Database ko MySQL mein convert karein (SQLite se)

### VPS (Linux):
```bash
pip install gunicorn
gunicorn -w 4 app:app --bind 0.0.0.0:5000
```

### MySQL Use Karna Chahte Hain:
`app.py` mein yeh line change karein:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/lodhi_samaj'
```
Aur install karein: `pip install pymysql`

---

## Features Included

- ✅ Member Registration + Admin Approval
- ✅ Login / Logout
- ✅ Member Directory with Search & Pagination
- ✅ Events Management
- ✅ Achievements Section
- ✅ Matrimonial Profiles (with Admin Approval)
- ✅ Blood Donor Registry
- ✅ Photo Gallery
- ✅ Contact / Feedback Form
- ✅ Admin Dashboard with Stats
- ✅ Member Approve / Reject / Suspend
- ✅ Role-based Access (Member / Admin / Super Admin)
- ✅ Responsive Design (Mobile + Desktop)
- ✅ Hindi + English Bilingual UI

---

**Developed for Lodhi Rajpoot Samaj Community — 2026**
