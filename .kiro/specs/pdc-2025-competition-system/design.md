# Dokumen Desain - Sistem Manajemen Kompetisi PDC 2025

## Overview

Sistem Manajemen Kompetisi PDC 2025 akan dibangun menggunakan Flask Python dengan arsitektur modular yang mendukung skalabilitas dan maintainability. Sistem ini menggunakan pola MVC (Model-View-Controller) dengan Blueprint untuk organisasi kode yang bersih, SQLAlchemy untuk ORM, dan Flask-Login untuk manajemen sesi pengguna.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   Database      │
│   (Jinja2 +    │◄──►│   (Python)      │◄──►│   (SQLite/      │
│   Bootstrap)    │    │                 │    │   PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   File Storage  │
                       │   (Local/Cloud) │
                       └─────────────────┘
```

### Technology Stack

- **Backend Framework:** Flask 2.3+
- **Database ORM:** SQLAlchemy with Flask-SQLAlchemy
- **Authentication:** Flask-Login + Werkzeug password hashing
- **Forms:** Flask-WTF with WTForms validation
- **File Upload:** Flask-Upload with secure filename handling
- **Database:** SQLite (development) / PostgreSQL (production)
- **Frontend:** Jinja2 templates + Bootstrap 5 (untuk UI yang konsisten dan menarik) + JavaScript
- **UI Framework:** Bootstrap 5 dengan komponen cards, forms, modals, dan navigation yang responsif
- **Language:** Bahasa Indonesia untuk semua UI text, labels, messages, dan content
- **Localization:** Semua template HTML menggunakan Bahasa Indonesia karena peserta dari Indonesia

### Application Structure

```
app/
├── __init__.py                 # Flask app factory
├── config.py                   # Configuration settings
├── models/                     # Database models
│   ├── __init__.py
│   ├── user.py                # User and profile models
│   ├── competition.py         # Competition models
│   ├── registration.py        # Registration models
│   └── payment.py             # Payment models
├── blueprints/                # Flask blueprints
│   ├── __init__.py
│   ├── auth/                  # Authentication routes
│   ├── main/                  # Main application routes
│   ├── admin/                 # Admin panel routes
│   ├── competition/           # Competition management
│   └── api/                   # API endpoints
├── forms/                     # WTForms form classes
├── templates/                 # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── dashboard/
│   ├── competition/
│   └── admin/
├── static/                    # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── bootstrap.min.css  # Bootstrap 5 CSS
│   │   └── custom.css         # Custom styling
│   ├── js/
│   │   ├── bootstrap.min.js   # Bootstrap 5 JS
│   │   └── app.js            # Custom JavaScript
│   └── images/               # Logo, icons, etc.
└── utils/                     # Utility functions
```

## Bootstrap UI Design

### Key Bootstrap Components

**Navigation:**
- Bootstrap Navbar dengan brand logo dan responsive menu
- Breadcrumb navigation untuk halaman dalam
- Sidebar navigation untuk admin panel

**Cards & Layout:**
- Competition cards dengan gambar, deskripsi, dan pricing
- User profile cards dengan progress indicators
- Dashboard cards untuk statistik dan quick actions
- Team member cards dengan role badges

**Forms:**
- Bootstrap form styling dengan floating labels
- Input groups untuk field yang terkait
- Form validation dengan custom error messages
- File upload dengan drag-and-drop styling

**Interactive Elements:**
- Modal dialogs untuk konfirmasi actions
- Toast notifications untuk feedback
- Progress bars untuk verification status
- Badges untuk status indicators (verified, pending, approved)

**Responsive Design:**
- Mobile-first approach dengan Bootstrap grid system
- Responsive tables dengan horizontal scroll
- Collapsible sections untuk mobile optimization

### UI Color Scheme
- Primary: Bootstrap blue (#0d6efd) untuk actions utama
- Success: Green (#198754) untuk status approved/verified
- Warning: Orange (#fd7e14) untuk pending status
- Danger: Red (#dc3545) untuk errors dan rejections
- Info: Light blue (#0dcaf0) untuk informational content

## Components and Interfaces

### 1. User Management Component

**Models:**
- `User`: Core user authentication and basic info
- `UserProfile`: Extended profile information
- `UserVerification`: Verification status and documents

**Key Methods:**
```python
class User(UserMixin, db.Model):
    def check_password(self, password)
    def is_profile_complete(self)
    def get_verification_progress(self)
    
class UserProfile(db.Model):
    def calculate_completion_percentage(self)
    def get_missing_fields(self)
```

**Routes (Bahasa Indonesia):**
- `/masuk` - Login ("Masuk" = Login)
- `/daftar` - Registration ("Daftar" = Register)
- `/profil` - Profile management ("Profil" = Profile)
- `/verifikasi` - Verification status ("Verifikasi" = Verification)

**Template Labels (Bahasa Indonesia):**
- "Nama Lengkap" (Full Name)
- "Kata Sandi" (Password)
- "Sekolah" (School)
- "Kelas" (Grade)
- "Nomor WhatsApp" (WhatsApp Number)
- "Foto Kartu Pelajar" (Student ID Photo)
- "Screenshot Twibbon" (Twibbon Screenshot)

### 2. Competition Management Component

**Models:**
- `Competition`: Competition details and settings
- `CompetitionCategory`: Academic, Creative, Performance categories
- `CompetitionPricing`: Early bird and regular pricing

**Key Methods:**
```python
class Competition(db.Model):
    def get_current_price(self)
    def is_early_bird_active(self)
    def get_participant_count(self)
    def is_user_eligible(self, user)
```

**Routes:**
- `/kompetisi` - Competition listing
- `/kompetisi/<id>` - Competition details
- `/kompetisi/<id>/daftar` - Registration

### 3. Registration Component

**Models:**
- `IndividualRegistration`: Individual competition entries
- `TeamRegistration`: Team competition entries
- `Team`: Team information and members
- `TeamMember`: Team member details and roles

**Key Methods:**
```python
class Team(db.Model):
    def add_member(self, user, position)
    def validate_school_consistency(self)
    def calculate_total_cost(self)
    
class Registration(db.Model):
    def get_status_display(self)
    def can_submit_files(self)
```

### 4. Payment Processing Component

**Models:**
- `Payment`: Payment records and proofs
- `PaymentStatus`: Payment approval workflow

**Key Methods:**
```python
class Payment(db.Model):
    def calculate_amount(self)
    def is_within_deadline(self)
    def approve_payment(self, admin_user)
```

### 5. Admin Panel Component

**Features:**
- User verification dashboard
- Payment approval interface
- Competition management
- Export functionality

**Routes:**
- `/admin/dashboard` - Admin overview
- `/admin/verifikasi` - User verification
- `/admin/pembayaran` - Payment management
- `/admin/kompetisi` - Competition settings

## Data Models

### Core Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE
);

-- User profiles table
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    nama_lengkap VARCHAR(100),
    sekolah VARCHAR(100),
    kelas INTEGER,
    nisn VARCHAR(20),
    whatsapp VARCHAR(20),
    instagram VARCHAR(50),
    twitter VARCHAR(50),
    foto_kartu_pelajar VARCHAR(200),
    screenshot_twibbon VARCHAR(200),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_progress INTEGER DEFAULT 0
);

-- Competitions table
CREATE TABLE competitions (
    id INTEGER PRIMARY KEY,
    nama_kompetisi VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    kategori VARCHAR(50), -- 'individual' or 'team'
    jenis VARCHAR(50), -- 'academic', 'creative', 'performance', 'basketball', 'esports'
    harga_early_bird INTEGER,
    harga_reguler INTEGER,
    tanggal_mulai_early_bird TIMESTAMP,
    tanggal_akhir_early_bird TIMESTAMP,
    deadline_registrasi TIMESTAMP,
    tanggal_kompetisi TIMESTAMP,
    min_kelas INTEGER DEFAULT 7,
    max_kelas INTEGER DEFAULT 9,
    min_anggota INTEGER,
    max_anggota INTEGER
);

-- Registrations table
CREATE TABLE registrations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    competition_id INTEGER REFERENCES competitions(id),
    team_id INTEGER REFERENCES teams(id) NULL,
    status VARCHAR(20) DEFAULT 'pending',
    harga_terkunci INTEGER,
    tanggal_registrasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_submission VARCHAR(200),
    google_drive_link VARCHAR(500)
);

-- Teams table
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    nama_tim VARCHAR(100) NOT NULL,
    competition_id INTEGER REFERENCES competitions(id),
    captain_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team members table
CREATE TABLE team_members (
    id INTEGER PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    user_id INTEGER REFERENCES users(id),
    posisi VARCHAR(20), -- 'Captain', 'Player', 'Reserve'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments table
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    registration_id INTEGER REFERENCES registrations(id),
    jumlah INTEGER NOT NULL,
    bukti_pembayaran VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    tanggal_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tanggal_approval TIMESTAMP,
    approved_by INTEGER REFERENCES users(id)
);
```

### Model Relationships

```python
# User relationships
user.profile = relationship("UserProfile", backref="user", uselist=False)
user.registrations = relationship("Registration", backref="user")
user.teams_as_captain = relationship("Team", backref="captain")
user.team_memberships = relationship("TeamMember", backref="user")

# Competition relationships
competition.registrations = relationship("Registration", backref="competition")
competition.teams = relationship("Team", backref="competition")

# Team relationships
team.members = relationship("TeamMember", backref="team")
team.registration = relationship("Registration", backref="team", uselist=False)

# Registration relationships
registration.payment = relationship("Payment", backref="registration", uselist=False)
```

## Error Handling

### Exception Handling Strategy

```python
# Custom exceptions
class CompetitionError(Exception):
    pass

class RegistrationError(Exception):
    pass

class PaymentError(Exception):
    pass

class VerificationError(Exception):
    pass

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
```

### Validation Rules

```python
# Form validation
class RegistrationForm(FlaskForm):
    def validate_eligibility(self, field):
        if not current_user.profile.is_verified:
            raise ValidationError('Profil harus terverifikasi untuk mendaftar')
    
    def validate_deadline(self, field):
        if datetime.now() > self.competition.deadline_registrasi:
            raise ValidationError('Pendaftaran sudah ditutup')

# Business logic validation
def validate_team_formation(team, competition):
    # Check school consistency
    schools = set(member.user.profile.sekolah for member in team.members)
    if len(schools) > 1:
        raise RegistrationError('Semua anggota tim harus dari sekolah yang sama')
    
    # Check member count
    if not (competition.min_anggota <= len(team.members) <= competition.max_anggota):
        raise RegistrationError(f'Jumlah anggota tim harus {competition.min_anggota}-{competition.max_anggota}')
```

## Testing Strategy

### Unit Testing

```python
# Test structure
tests/
├── test_models.py          # Model testing
├── test_auth.py           # Authentication testing
├── test_registration.py   # Registration flow testing
├── test_payment.py        # Payment processing testing
└── test_admin.py          # Admin functionality testing

# Example test case
class TestUserModel(unittest.TestCase):
    def test_password_hashing(self):
        user = User(email='test@example.com')
        user.set_password('testpassword')
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertTrue(user.check_password('testpassword'))
    
    def test_profile_completion(self):
        user = User(email='test@example.com')
        profile = UserProfile(user=user)
        self.assertEqual(profile.calculate_completion_percentage(), 0)
```

### Integration Testing

```python
# Test registration flow
class TestRegistrationFlow(unittest.TestCase):
    def test_individual_registration_flow(self):
        # Create verified user
        # Create competition
        # Test registration process
        # Verify payment requirement
        # Test admin approval
        pass
    
    def test_team_registration_flow(self):
        # Create team captain
        # Create team members
        # Test team formation
        # Test payment by captain
        pass
```

### Performance Testing

- Load testing with 1000+ concurrent users
- Database query optimization
- File upload performance testing
- Mobile responsiveness testing

## Security Considerations

### Authentication & Authorization

```python
# Password security
from werkzeug.security import generate_password_hash, check_password_hash

# File upload security
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# SQL injection prevention (SQLAlchemy ORM)
# XSS prevention (Jinja2 auto-escaping)
```

### Data Protection

- Secure file storage with proper permissions
- Input validation and sanitization
- Rate limiting for API endpoints
- Secure session management
- HTTPS enforcement in production

## Deployment Architecture

### Development Environment

```python
# config.py
class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pdc_dev.db'
    SECRET_KEY = 'dev-secret-key'
    UPLOAD_FOLDER = 'uploads'
```

### Production Environment

```python
class ProductionConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = '/var/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
```

### Scalability Considerations

- Database connection pooling
- File storage optimization (local vs cloud)
- Caching strategy for competition data
- Background task processing for notifications
- Load balancing for high traffic periods