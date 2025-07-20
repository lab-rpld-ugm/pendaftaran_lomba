#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.user import User, UserProfile
from app.models.competition import Competition
from app.models.registration import IndividualRegistration
from app.models.payment import Payment
from datetime import datetime

def create_sample_payment():
    """Create sample registration and payment for testing"""
    print("=== Creating Sample Payment ===\n")
    
    app = create_app()
    
    with app.app_context():
        # Get first user and competition
        user = User.query.first()
        competition = Competition.query.filter_by(kategori='individual').first()
        
        if not user:
            print("❌ No user found")
            return
        
        if not competition:
            print("❌ No individual competition found")
            return
        
        print(f"✓ Found user: {user.email}")
        print(f"✓ Found competition: {competition.nama_kompetisi}")
        
        # Check if registration already exists
        existing_reg = IndividualRegistration.query.filter_by(
            user_id=user.id,
            competition_id=competition.id
        ).first()
        
        if existing_reg:
            print(f"✓ Registration already exists: {existing_reg.id}")
            payment = Payment.query.filter_by(registration_id=existing_reg.id).first()
            if payment:
                print(f"✓ Payment already exists: {payment.id}")
                return
        else:
            # Create registration
            registration = IndividualRegistration(
                user_id=user.id,
                competition_id=competition.id,
                harga_terkunci=competition.get_current_price(),
                status='pending'
            )
            db.session.add(registration)
            db.session.flush()
            print(f"✓ Created registration: {registration.id}")
            
            # Create payment
            payment = Payment(
                registration_id=registration.id,
                jumlah=registration.harga_terkunci,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            print(f"✓ Created payment: {payment.id}")
        
        print("\n=== Sample Payment Created Successfully ===")

if __name__ == '__main__':
    create_sample_payment()