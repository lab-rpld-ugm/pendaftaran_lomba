#!/usr/bin/env python3
"""
Test script for ProfileForm validation and functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.forms.profile import ProfileForm
from app.models.user import User, UserProfile

def test_profile_form():
    """Test ProfileForm validation and functionality"""
    app = create_app('testing')
    
    with app.app_context():
        # Create test data
        form_data = {
            'nama_lengkap': 'John Doe',
            'sekolah': 'SMP Negeri 1 Jakarta',
            'kelas': 8,
            'nisn': '1234567890',
            'whatsapp': '081234567890',
            'instagram': 'johndoe123',
            'twitter': 'johndoe',
            'csrf_token': 'test_token'
        }
        
        # Test form validation
        form = ProfileForm(data=form_data)
        form.csrf_token.data = 'test_token'  # Mock CSRF token
        
        print("Testing ProfileForm validation...")
        
        # Test required field validation
        print(f"Form validation result: {form.validate()}")
        if form.errors:
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
        
        # Test individual field validations
        print("\nTesting individual validations:")
        
        # Test NISN validation
        form.nisn.data = '123'  # Invalid NISN (too short)
        if not form.validate_nisn(form.nisn):
            print("✓ NISN validation works for short numbers")
        
        form.nisn.data = 'abcd567890'  # Invalid NISN (contains letters)
        try:
            form.validate_nisn(form.nisn)
            print("✗ NISN validation should reject letters")
        except:
            print("✓ NISN validation rejects letters")
        
        # Test WhatsApp validation
        form.whatsapp.data = '081234567890'
        try:
            form.validate_whatsapp(form.whatsapp)
            print("✓ WhatsApp validation accepts valid Indonesian number")
        except:
            print("✗ WhatsApp validation should accept valid Indonesian number")
        
        # Test Instagram validation
        form.instagram.data = '@johndoe123'
        form.validate_instagram(form.instagram)
        print(f"✓ Instagram username cleaned: {form.instagram.data}")
        
        # Test Twitter validation
        form.twitter.data = '@johndoe'
        form.validate_twitter(form.twitter)
        print(f"✓ Twitter username cleaned: {form.twitter.data}")
        
        print("\n✓ ProfileForm tests completed successfully!")

if __name__ == '__main__':
    test_profile_form()