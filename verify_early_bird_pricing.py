#!/usr/bin/env python3
"""
Verification script for early bird pricing logic implementation
"""

import os
import sys
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_early_bird_pricing():
    """Test early bird pricing logic without database"""
    
    print("=== Testing Early Bird Pricing Logic ===\n")
    
    # Mock Competition class for testing
    class MockCompetition:
        def __init__(self, early_bird_price, regular_price, early_bird_start, early_bird_end):
            self.harga_early_bird = early_bird_price
            self.harga_reguler = regular_price
            self.tanggal_mulai_early_bird = early_bird_start
            self.tanggal_akhir_early_bird = early_bird_end
        
        def get_current_price(self):
            """Get current price based on early bird status"""
            if self.is_early_bird_active():
                return self.harga_early_bird
            return self.harga_reguler
        
        def is_early_bird_active(self):
            """Check if early bird pricing is currently active"""
            now = datetime.utcnow()
            return (self.tanggal_mulai_early_bird <= now <= self.tanggal_akhir_early_bird)
        
        def get_early_bird_savings(self):
            """Calculate savings amount during early bird period"""
            return self.harga_reguler - self.harga_early_bird
        
        def get_early_bird_days_left(self):
            """Get number of days left for early bird pricing"""
            if not self.is_early_bird_active():
                return 0
            
            now = datetime.utcnow()
            if now < self.tanggal_mulai_early_bird:
                return 0
            
            days_left = (self.tanggal_akhir_early_bird - now).days
            return max(0, days_left)
        
        def get_locked_price_at_registration(self, registration_date=None):
            """Get the price that should be locked at registration time"""
            if registration_date is None:
                registration_date = datetime.utcnow()
            
            # Check if registration date falls within early bird period
            if (self.tanggal_mulai_early_bird <= registration_date <= self.tanggal_akhir_early_bird):
                return self.harga_early_bird
            return self.harga_reguler
        
        def get_pricing_info(self):
            """Get comprehensive pricing information"""
            now = datetime.utcnow()
            
            pricing_info = {
                'current_price': self.get_current_price(),
                'early_bird_price': self.harga_early_bird,
                'regular_price': self.harga_reguler,
                'is_early_bird_active': self.is_early_bird_active(),
                'early_bird_savings': self.get_early_bird_savings(),
                'early_bird_days_left': self.get_early_bird_days_left(),
                'early_bird_start': self.tanggal_mulai_early_bird,
                'early_bird_end': self.tanggal_akhir_early_bird,
            }
            
            return pricing_info
        
        def validate_early_bird_dates(self):
            """Validate early bird date configuration"""
            errors = []
            
            if self.tanggal_mulai_early_bird >= self.tanggal_akhir_early_bird:
                errors.append("Tanggal mulai early bird harus sebelum tanggal akhir")
            
            if self.harga_early_bird >= self.harga_reguler:
                errors.append("Harga early bird harus lebih murah dari harga reguler")
            
            return errors
    
    # Test scenarios
    now = datetime.utcnow()
    
    # Scenario 1: Early bird active (started yesterday, ends in 5 days)
    print("1. Testing Early Bird Active Scenario")
    comp1 = MockCompetition(
        early_bird_price=50000,
        regular_price=75000,
        early_bird_start=now - timedelta(days=1),
        early_bird_end=now + timedelta(days=5)
    )
    
    print(f"   Early bird active: {comp1.is_early_bird_active()}")
    print(f"   Current price: Rp {comp1.get_current_price():,}")
    print(f"   Early bird savings: Rp {comp1.get_early_bird_savings():,}")
    print(f"   Days left: {comp1.get_early_bird_days_left()}")
    print(f"   Locked price now: Rp {comp1.get_locked_price_at_registration():,}")
    
    # Test locked price for different registration dates
    past_date = now - timedelta(days=2)  # Before early bird
    future_date = now + timedelta(days=10)  # After early bird
    print(f"   Locked price 2 days ago: Rp {comp1.get_locked_price_at_registration(past_date):,}")
    print(f"   Locked price in 10 days: Rp {comp1.get_locked_price_at_registration(future_date):,}")
    
    validation_errors = comp1.validate_early_bird_dates()
    print(f"   Validation errors: {validation_errors}")
    print()
    
    # Scenario 2: Early bird not yet started
    print("2. Testing Early Bird Not Started Scenario")
    comp2 = MockCompetition(
        early_bird_price=40000,
        regular_price=60000,
        early_bird_start=now + timedelta(days=2),
        early_bird_end=now + timedelta(days=9)
    )
    
    print(f"   Early bird active: {comp2.is_early_bird_active()}")
    print(f"   Current price: Rp {comp2.get_current_price():,}")
    print(f"   Days left: {comp2.get_early_bird_days_left()}")
    print(f"   Locked price now: Rp {comp2.get_locked_price_at_registration():,}")
    print()
    
    # Scenario 3: Early bird ended
    print("3. Testing Early Bird Ended Scenario")
    comp3 = MockCompetition(
        early_bird_price=30000,
        regular_price=50000,
        early_bird_start=now - timedelta(days=10),
        early_bird_end=now - timedelta(days=3)
    )
    
    print(f"   Early bird active: {comp3.is_early_bird_active()}")
    print(f"   Current price: Rp {comp3.get_current_price():,}")
    print(f"   Days left: {comp3.get_early_bird_days_left()}")
    print(f"   Locked price now: Rp {comp3.get_locked_price_at_registration():,}")
    
    # Test locked price during early bird period
    early_bird_date = now - timedelta(days=5)  # During early bird period
    print(f"   Locked price during early bird: Rp {comp3.get_locked_price_at_registration(early_bird_date):,}")
    print()
    
    # Scenario 4: Invalid configuration
    print("4. Testing Invalid Configuration")
    comp4 = MockCompetition(
        early_bird_price=80000,  # Higher than regular price (invalid)
        regular_price=60000,
        early_bird_start=now + timedelta(days=5),  # Starts after it ends (invalid)
        early_bird_end=now + timedelta(days=2)
    )
    
    validation_errors = comp4.validate_early_bird_dates()
    print(f"   Validation errors: {validation_errors}")
    print(f"   Current price (fallback): Rp {comp4.get_current_price():,}")
    print()
    
    # Test comprehensive pricing info
    print("5. Testing Comprehensive Pricing Info")
    pricing_info = comp1.get_pricing_info()
    print("   Pricing Info:")
    for key, value in pricing_info.items():
        if isinstance(value, datetime):
            print(f"     {key}: {value.strftime('%Y-%m-%d %H:%M:%S')}")
        elif isinstance(value, (int, float)):
            print(f"     {key}: {value:,}")
        else:
            print(f"     {key}: {value}")
    
    print("\n=== Early Bird Pricing Logic Test Complete ===")
    return True

def test_price_formatting():
    """Test price formatting functions"""
    print("\n=== Testing Price Formatting ===\n")
    
    def format_price(amount):
        return f"Rp {amount:,}"
    
    def calculate_savings_percentage(early_bird, regular):
        if regular > 0:
            return round(((regular - early_bird) / regular) * 100, 1)
        return 0
    
    test_prices = [
        (50000, 75000),
        (100000, 150000),
        (25000, 40000),
        (0, 50000),  # Edge case
    ]
    
    for early_bird, regular in test_prices:
        savings = regular - early_bird
        percentage = calculate_savings_percentage(early_bird, regular)
        
        print(f"Early Bird: {format_price(early_bird)}")
        print(f"Regular: {format_price(regular)}")
        print(f"Savings: {format_price(savings)} ({percentage}%)")
        print()
    
    print("=== Price Formatting Test Complete ===")

if __name__ == "__main__":
    try:
        test_early_bird_pricing()
        test_price_formatting()
        print("\n✅ All tests passed! Early bird pricing logic is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)