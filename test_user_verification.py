#!/usr/bin/env python3
"""
Test script for user verification interface functionality
"""

import os
import sys
import tempfile
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models.user import User, UserProfile

def test_user_verification_interface():
    """Test the user verification interface"""
    
    # Import config
    from app.config import TestingConfig
    
    # Create test app with testing configuration
    app = create_app(TestingConfig)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created")
        
        # Create admin user
        admin_user = User(email='admin@pdc.com', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create test users with different verification states
        test_users = [
            {
                'email': 'complete_unverified@test.com',
                'profile_data': {
                    'nama_lengkap': 'Siswa Lengkap',
                    'sekolah': 'SMP Negeri 1',
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
                    'nama_lengkap': 'Siswa Terverifikasi',
                    'sekolah': 'SMP Negeri 2',
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
                    'nama_lengkap': 'Siswa Belum Lengkap',
                    'sekolah': 'SMP Negeri 3',
                    'kelas': 7,
                    # Missing some required fields
                },
                'is_verified': False
            }
        ]
        
        created_users = []
        for user_data in test_users:
            user = User(email=user_data['email'])
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            profile = UserProfile(user_id=user.id, **user_data['profile_data'])
            profile.is_verified = user_data['is_verified']
            db.session.add(profile)
            
            created_users.append(user)
        
        db.session.commit()
        print(f"✓ Created {len(created_users)} test users")
        
        # Test client
        client = app.test_client()
        
        # Test admin login
        login_response = client.post('/masuk', data={
            'email': 'admin@pdc.com',
            'password': 'admin123'
        }, follow_redirects=True)
        
        assert login_response.status_code == 200
        print("✓ Admin login successful")
        
        # Test verification page access
        verification_response = client.get('/admin/verifikasi')
        assert verification_response.status_code == 200
        assert b'Verifikasi Pengguna' in verification_response.data
        print("✓ Verification page accessible")
        
        # Test statistics display
        assert b'Total Pengguna' in verification_response.data
        assert b'Terverifikasi' in verification_response.data
        assert b'Profil Lengkap' in verification_response.data
        assert b'Menunggu Verifikasi' in verification_response.data
        print("✓ Statistics displayed correctly")
        
        # Test user cards display
        assert b'Siswa Lengkap' in verification_response.data
        assert b'Siswa Terverifikasi' in verification_response.data
        assert b'Siswa Belum Lengkap' in verification_response.data
        print("✓ User cards displayed correctly")
        
        # Test filter functionality
        filter_response = client.get('/admin/verifikasi?status=verified')
        assert filter_response.status_code == 200
        assert b'Siswa Terverifikasi' in filter_response.data
        print("✓ Status filter working")
        
        # Test search functionality
        search_response = client.get('/admin/verifikasi?search=Lengkap')
        assert search_response.status_code == 200
        assert b'Siswa Lengkap' in search_response.data
        print("✓ Search functionality working")
        
        # Test user approval
        complete_user = User.query.filter_by(email='complete_unverified@test.com').first()
        approve_response = client.post(f'/admin/verifikasi/approve/{complete_user.id}', 
                                     follow_redirects=True)
        assert approve_response.status_code == 200
        
        # Check if user is now verified
        db.session.refresh(complete_user)
        assert complete_user.profile.is_verified == True
        print("✓ User approval working")
        
        # Test user rejection
        reject_response = client.post(f'/admin/verifikasi/reject/{complete_user.id}', 
                                    follow_redirects=True)
        assert reject_response.status_code == 200
        
        # Check if user is now unverified
        db.session.refresh(complete_user)
        assert complete_user.profile.is_verified == False
        print("✓ User rejection working")
        
        # Test bulk actions
        user_ids = [str(user.id) for user in created_users[:2]]
        bulk_response = client.post('/admin/verifikasi/bulk-action', data={
            'action': 'approve',
            'user_ids': user_ids
        }, follow_redirects=True)
        assert bulk_response.status_code == 200
        print("✓ Bulk actions working")
        
        # Test profile completion calculation
        for user in created_users:
            completion = user.profile.calculate_completion_percentage()
            missing_fields = user.profile.get_missing_fields()
            print(f"  - {user.email}: {completion}% complete, missing: {missing_fields}")
        
        print("✓ Profile completion calculation working")
        
        # Test non-admin access restriction
        client.get('/keluar')  # Logout admin
        
        # Create regular user and login
        regular_user = User(email='regular@test.com')
        regular_user.set_password('password123')
        db.session.add(regular_user)
        db.session.commit()
        
        client.post('/masuk', data={
            'email': 'regular@test.com',
            'password': 'password123'
        })
        
        # Try to access admin verification page
        restricted_response = client.get('/admin/verifikasi', follow_redirects=True)
        assert b'Akses ditolak' in restricted_response.data or restricted_response.status_code == 403
        print("✓ Non-admin access restriction working")
        
        print("\n🎉 All user verification interface tests passed!")
        
        return True

def test_profile_completion_edge_cases():
    """Test edge cases for profile completion"""
    
    # Import config
    from app.config import TestingConfig
    
    # Create test app with testing configuration
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Test user without profile
        user_no_profile = User(email='noprofile@test.com')
        user_no_profile.set_password('password123')
        db.session.add(user_no_profile)
        db.session.commit()
        
        assert user_no_profile.is_profile_complete() == False
        assert user_no_profile.get_verification_progress() == 0
        print("✓ User without profile handled correctly")
        
        # Test profile with empty strings
        user_empty = User(email='empty@test.com')
        user_empty.set_password('password123')
        db.session.add(user_empty)
        db.session.flush()
        
        profile_empty = UserProfile(
            user_id=user_empty.id,
            nama_lengkap='',  # Empty string
            sekolah=None,     # None value
            kelas=8,
            nisn='   ',       # Whitespace only
        )
        db.session.add(profile_empty)
        db.session.commit()
        
        completion = profile_empty.calculate_completion_percentage()
        missing = profile_empty.get_missing_fields()
        
        assert completion < 100
        assert 'Nama Lengkap' in missing
        assert 'Sekolah' in missing
        assert 'NISN' in missing
        print("✓ Empty/whitespace fields handled correctly")
        
        print("\n🎉 All edge case tests passed!")
        
        return True

if __name__ == '__main__':
    print("Testing User Verification Interface...")
    print("=" * 50)
    
    try:
        test_user_verification_interface()
        test_profile_completion_edge_cases()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("User verification interface is working correctly.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)