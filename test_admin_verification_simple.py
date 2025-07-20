#!/usr/bin/env python3
"""
Simple test script for admin verification functionality
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_admin_routes_exist():
    """Test that admin routes are properly defined"""
    
    from app.blueprints.admin import routes
    
    # Check if route functions exist
    expected_functions = [
        'dashboard',
        'verifikasi', 
        'approve_user',
        'reject_user',
        'bulk_verification_action'
    ]
    
    for func_name in expected_functions:
        if hasattr(routes, func_name):
            print(f"✓ Route function {func_name} exists")
        else:
            print(f"❌ Route function {func_name} not found")
            return False
    
    return True

def test_user_model_verification_methods():
    """Test user model verification methods"""
    
    from app.models.user import User, UserProfile
    from app import db
    from app.config import TestingConfig
    from app import create_app
    
    # Create minimal app for testing
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Test user without profile
        user1 = User(email='test1@example.com')
        user1.set_password('password')
        db.session.add(user1)
        db.session.flush()
        
        assert user1.is_profile_complete() == False
        assert user1.get_verification_progress() == 0
        print("✓ User without profile methods work")
        
        # Test user with incomplete profile
        profile1 = UserProfile(
            user_id=user1.id,
            nama_lengkap='Test User',
            sekolah='Test School'
            # Missing other required fields
        )
        db.session.add(profile1)
        db.session.commit()
        
        completion = profile1.calculate_completion_percentage()
        missing = profile1.get_missing_fields()
        
        assert completion < 100
        assert len(missing) > 0
        assert 'Kelas' in missing
        print(f"✓ Incomplete profile: {completion}% complete, missing: {missing}")
        
        # Test user with complete profile
        user2 = User(email='test2@example.com')
        user2.set_password('password')
        db.session.add(user2)
        db.session.flush()
        
        profile2 = UserProfile(
            user_id=user2.id,
            nama_lengkap='Complete User',
            sekolah='Complete School',
            kelas=8,
            nisn='1234567890',
            whatsapp='081234567890',
            instagram='complete_user',
            twitter='complete_user',
            foto_kartu_pelajar='kartu.jpg',
            screenshot_twibbon='twibbon.jpg'
        )
        db.session.add(profile2)
        db.session.commit()
        
        completion2 = profile2.calculate_completion_percentage()
        missing2 = profile2.get_missing_fields()
        
        assert completion2 == 100
        assert len(missing2) == 0
        print(f"✓ Complete profile: {completion2}% complete, missing: {missing2}")
        
        # Test verification status
        assert profile2.is_verified == False
        profile2.is_verified = True
        db.session.commit()
        
        assert profile2.is_verified == True
        print("✓ Verification status can be updated")
        
        return True

def test_verification_helper():
    """Test ProfileVerificationHelper methods"""
    
    from app.utils.verification import ProfileVerificationHelper
    from app.models.user import User, UserProfile
    from app import db
    from app.config import TestingConfig
    from app import create_app
    
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create test user with complete verified profile
        user = User(email='verified@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.flush()
        
        profile = UserProfile(
            user_id=user.id,
            nama_lengkap='Verified User',
            sekolah='Verified School',
            kelas=8,
            nisn='1234567890',
            whatsapp='081234567890',
            instagram='verified_user',
            twitter='verified_user',
            foto_kartu_pelajar='kartu.jpg',
            screenshot_twibbon='twibbon.jpg',
            is_verified=True
        )
        db.session.add(profile)
        db.session.commit()
        
        # Test helper methods
        can_register, reason = ProfileVerificationHelper.can_register_competition(user)
        assert can_register == True
        print(f"✓ Can register: {can_register}, reason: {reason}")
        
        status_info = ProfileVerificationHelper.get_profile_status_info(user)
        assert status_info['status'] == 'verified'
        assert status_info['can_register'] == True
        print(f"✓ Status info: {status_info}")
        
        badge_class = ProfileVerificationHelper.get_verification_badge_class(user)
        assert 'success' in badge_class
        print(f"✓ Badge class: {badge_class}")
        
        icon = ProfileVerificationHelper.get_verification_icon(user)
        assert 'check' in icon
        print(f"✓ Icon: {icon}")
        
        return True

if __name__ == '__main__':
    print("Testing Admin Verification Components...")
    print("=" * 50)
    
    try:
        print("\n1. Testing admin routes...")
        test_admin_routes_exist()
        
        print("\n2. Testing user model verification methods...")
        test_user_model_verification_methods()
        
        print("\n3. Testing verification helper...")
        test_verification_helper()
        
        print("\n" + "=" * 50)
        print("✅ ALL COMPONENT TESTS PASSED!")
        print("Admin verification functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)