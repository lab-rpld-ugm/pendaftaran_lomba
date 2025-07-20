#!/usr/bin/env python3
"""
Test script for competition detail functionality
"""
from app import create_app, db
from app.models.competition import Competition
from app.models.user import User, UserProfile

def test_competition_detail():
    """Test competition detail page functionality"""
    app = create_app()
    
    with app.app_context():
        print("Testing Competition Detail Functionality")
        print("=" * 50)
        
        # Test 1: Check if competitions exist
        competitions = Competition.query.all()
        print(f"\n1. Found {len(competitions)} competitions in database")
        
        if competitions:
            for comp in competitions:
                print(f"   - {comp.nama_kompetisi} (ID: {comp.id})")
                print(f"     Category: {comp.kategori}, Type: {comp.jenis}")
                print(f"     Early bird: Rp {comp.harga_early_bird:,} -> Regular: Rp {comp.harga_reguler:,}")
                print(f"     Early bird active: {comp.is_early_bird_active()}")
                print(f"     Registration open: {comp.is_registration_open()}")
                print(f"     Participant count: {comp.get_participant_count()}")
                print()
        
        # Test 2: Test competition detail route functionality
        if competitions:
            test_comp = competitions[0]
            print(f"2. Testing detail functionality for: {test_comp.nama_kompetisi}")
            
            # Test pricing info
            pricing_info = test_comp.get_pricing_info()
            print(f"   Current price: Rp {pricing_info['current_price']:,}")
            print(f"   Early bird active: {pricing_info['is_early_bird_active']}")
            print(f"   Early bird savings: Rp {pricing_info['early_bird_savings']:,}")
            print(f"   Registration days left: {pricing_info['registration_days_left']}")
            
            # Test user eligibility (without user)
            print(f"   User eligible (no user): {test_comp.is_user_eligible(None)}")
            
            # Test with a sample user
            user = User.query.first()
            if user:
                print(f"   User eligible (with user): {test_comp.is_user_eligible(user)}")
                if user.profile:
                    print(f"   User profile complete: {user.is_profile_complete()}")
                    print(f"   User grade: {user.profile.kelas}")
                else:
                    print("   User has no profile")
            else:
                print("   No users found in database")
        
        # Test 3: Test template context requirements
        print("\n3. Testing template context requirements")
        
        # Check if ProfileVerificationHelper is available
        try:
            from app.utils.verification import ProfileVerificationHelper
            print("   ✓ ProfileVerificationHelper imported successfully")
            
            if competitions and User.query.first():
                user = User.query.first()
                status_info = ProfileVerificationHelper.get_profile_status_info(user)
                print(f"   ✓ Profile status info: {status_info}")
                
                badge_class = ProfileVerificationHelper.get_verification_badge_class(user)
                print(f"   ✓ Badge class: {badge_class}")
                
                icon = ProfileVerificationHelper.get_verification_icon(user)
                print(f"   ✓ Icon: {icon}")
            
        except ImportError as e:
            print(f"   ✗ Error importing ProfileVerificationHelper: {e}")
        
        print("\n" + "=" * 50)
        print("Competition detail test completed!")

if __name__ == '__main__':
    test_competition_detail()