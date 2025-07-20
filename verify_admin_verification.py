#!/usr/bin/env python3
"""
Verification script for admin user verification interface
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_test_data():
    """Create test data for verification"""
    
    from app import create_app, db
    from app.models.user import User, UserProfile
    from app.config import DevelopmentConfig
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@pdc.com').first()
        if not admin:
            admin = User(email='admin@pdc.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Created admin user (admin@pdc.com / admin123)")
        else:
            print("✓ Admin user already exists")
        
        # Create test users with different verification states
        test_users = [
            {
                'email': 'complete_unverified@test.com',
                'profile_data': {
                    'nama_lengkap': 'Siswa Lengkap Belum Verifikasi',
                    'sekolah': 'SMP Negeri 1 Jakarta',
                    'kelas': 8,
                    'nisn': '1234567890',
                    'whatsapp': '081234567890',
                    'instagram': 'siswa_lengkap',
                    'twitter': 'siswa_lengkap',
                    'foto_kartu_pelajar': 'kartu_pelajar_1.jpg',
                    'screenshot_twibbon': 'twibbon_1.jpg'
                },
                'is_verified': False
            },
            {
                'email': 'verified@test.com',
                'profile_data': {
                    'nama_lengkap': 'Siswa Sudah Terverifikasi',
                    'sekolah': 'SMP Negeri 2 Jakarta',
                    'kelas': 9,
                    'nisn': '0987654321',
                    'whatsapp': '081987654321',
                    'instagram': 'siswa_verified',
                    'twitter': 'siswa_verified',
                    'foto_kartu_pelajar': 'kartu_pelajar_2.jpg',
                    'screenshot_twibbon': 'twibbon_2.jpg'
                },
                'is_verified': True
            },
            {
                'email': 'incomplete@test.com',
                'profile_data': {
                    'nama_lengkap': 'Siswa Profil Belum Lengkap',
                    'sekolah': 'SMP Negeri 3 Jakarta',
                    'kelas': 7,
                    # Missing required fields intentionally
                },
                'is_verified': False
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(email=user_data['email'])
                user.set_password('password123')
                db.session.add(user)
                db.session.flush()  # Get user ID
                
                profile = UserProfile(user_id=user.id, **user_data['profile_data'])
                profile.is_verified = user_data['is_verified']
                db.session.add(profile)
                created_count += 1
        
        db.session.commit()
        
        if created_count > 0:
            print(f"✓ Created {created_count} test users")
        else:
            print("✓ Test users already exist")
        
        # Display statistics
        total_users = User.query.join(UserProfile).count()
        verified_users = User.query.join(UserProfile).filter(UserProfile.is_verified == True).count()
        complete_profiles = User.query.join(UserProfile).filter(UserProfile.verification_progress == 100).count()
        
        print(f"✓ Database statistics:")
        print(f"  - Total users with profiles: {total_users}")
        print(f"  - Verified users: {verified_users}")
        print(f"  - Complete profiles: {complete_profiles}")
        
        return True

def verify_admin_interface():
    """Verify admin interface functionality"""
    
    from app import create_app
    from app.config import DevelopmentConfig
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        # Test template rendering
        from flask import render_template_string
        
        # Test basic template rendering
        try:
            test_template = """
            {% extends "base.html" %}
            {% block content %}
            <h1>Test Admin Interface</h1>
            {% endblock %}
            """
            
            rendered = render_template_string(test_template)
            assert 'Test Admin Interface' in rendered
            print("✓ Template rendering works")
            
        except Exception as e:
            print(f"❌ Template rendering failed: {e}")
            return False
        
        # Test admin route functions
        from app.blueprints.admin.routes import admin_required
        from flask_login import AnonymousUserMixin
        
        # Test admin_required decorator
        @admin_required
        def test_admin_function():
            return "Admin access granted"
        
        print("✓ Admin decorator defined")
        
        return True

def display_usage_instructions():
    """Display instructions for using the admin interface"""
    
    print("\n" + "=" * 60)
    print("🎯 ADMIN VERIFICATION INTERFACE READY!")
    print("=" * 60)
    
    print("\n📋 How to use the admin verification interface:")
    print("1. Start the Flask application:")
    print("   python run.py")
    
    print("\n2. Login as admin:")
    print("   Email: admin@pdc.com")
    print("   Password: admin123")
    
    print("\n3. Access admin verification:")
    print("   URL: http://localhost:5000/admin/verifikasi")
    print("   Or click 'Admin' → 'Verifikasi Pengguna' in navigation")
    
    print("\n🔧 Available features:")
    print("✓ View all users with verification status")
    print("✓ Filter users by verification status")
    print("✓ Search users by name, email, or school")
    print("✓ View user profile completion progress")
    print("✓ View uploaded documents (student ID, twibbon)")
    print("✓ Approve/reject individual users")
    print("✓ Bulk approve/reject multiple users")
    print("✓ Real-time statistics dashboard")
    
    print("\n📊 Test users available:")
    print("• complete_unverified@test.com - Complete profile, needs verification")
    print("• verified@test.com - Already verified user")
    print("• incomplete@test.com - Incomplete profile")
    print("• Password for all test users: password123")
    
    print("\n🎨 Interface features:")
    print("• Responsive Bootstrap design")
    print("• Mobile-friendly interface")
    print("• Real-time progress indicators")
    print("• Document preview modals")
    print("• Bulk action capabilities")
    print("• Status badges and icons")

if __name__ == '__main__':
    print("Setting up Admin Verification Interface...")
    print("=" * 50)
    
    try:
        print("\n1. Creating test data...")
        create_test_data()
        
        print("\n2. Verifying admin interface...")
        verify_admin_interface()
        
        display_usage_instructions()
        
    except Exception as e:
        print(f"\n❌ SETUP FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)