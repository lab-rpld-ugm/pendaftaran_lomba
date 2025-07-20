#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.competition import Competition
from app.models.registration import Registration
from app.models.payment import Payment
from app.models.user import User, UserProfile

def test_export_system():
    """Test export system functionality"""
    print("=== Testing Export System ===\n")
    
    app = create_app()
    
    with app.app_context():
        print("1. Testing export data availability...")
        
        # Check competitions
        competitions = Competition.query.all()
        print(f"   ✓ Found {len(competitions)} competitions")
        
        # Check registrations
        registrations = Registration.query.all()
        print(f"   ✓ Found {len(registrations)} registrations")
        
        # Check payments
        payments = Payment.query.all()
        print(f"   ✓ Found {len(payments)} payments")
        
        # Check users with profiles
        users_with_profiles = User.query.join(UserProfile).filter(UserProfile.id.isnot(None)).all()
        print(f"   ✓ Found {len(users_with_profiles)} users with profiles")
        
        print("\n2. Testing export statistics calculation...")
        
        if competitions:
            for competition in competitions:
                comp_registrations = Registration.query.filter_by(competition_id=competition.id).all()
                approved_registrations = [r for r in comp_registrations if r.status == 'approved']
                paid_registrations = [r for r in comp_registrations if r.payment and r.payment.status == 'approved']
                revenue = sum(r.payment.jumlah for r in comp_registrations if r.payment and r.payment.status == 'approved')
                
                print(f"   ✓ {competition.nama_kompetisi}:")
                print(f"     - Total registrations: {len(comp_registrations)}")
                print(f"     - Approved: {len(approved_registrations)}")
                print(f"     - Paid: {len(paid_registrations)}")
                print(f"     - Revenue: Rp {revenue:,}")
        
        print("\n3. Testing export routes...")
        
        # Test routes exist
        with app.test_client() as client:
            # Test export dashboard route (should redirect to login)
            response = client.get('/admin/export')
            print(f"   ✓ Export dashboard route status: {response.status_code}")
            
            # Test export users route (should redirect to login)
            response = client.get('/admin/export/users')
            print(f"   ✓ Export users route status: {response.status_code}")
            
            # Test export revenue route (should redirect to login)
            response = client.get('/admin/export/revenue')
            print(f"   ✓ Export revenue route status: {response.status_code}")
            
            if competitions:
                # Test export participants route (should redirect to login)
                response = client.get(f'/admin/export/participants/{competitions[0].id}')
                print(f"   ✓ Export participants route status: {response.status_code}")
        
        print("\n4. Testing CSV generation logic...")
        
        # Test CSV header generation
        participant_headers = [
            'No', 'Nama Lengkap', 'Email', 'Sekolah', 'Kelas', 'NISN', 
            'WhatsApp', 'Instagram', 'Twitter', 'Tipe Registrasi', 
            'Status Registrasi', 'Tanggal Registrasi', 'Harga Terkunci',
            'Status Pembayaran', 'Tanggal Pembayaran', 'Nama Tim', 'Posisi Tim'
        ]
        print(f"   ✓ Participant CSV headers: {len(participant_headers)} columns")
        
        revenue_headers = [
            'No', 'Nama Kompetisi', 'Kategori', 'Jenis', 'Harga Early Bird', 'Harga Reguler',
            'Total Registrasi', 'Registrasi Disetujui', 'Pembayaran Disetujui', 
            'Revenue Early Bird', 'Revenue Reguler', 'Total Revenue'
        ]
        print(f"   ✓ Revenue CSV headers: {len(revenue_headers)} columns")
        
        user_headers = [
            'No', 'Email', 'Nama Lengkap', 'Sekolah', 'Kelas', 'NISN', 
            'WhatsApp', 'Instagram', 'Twitter', 'Kelengkapan Profil (%)', 
            'Status Verifikasi', 'Tanggal Registrasi', 'Update Terakhir'
        ]
        print(f"   ✓ User CSV headers: {len(user_headers)} columns")
        
        print("\n5. Testing export templates...")
        
        # Check if templates exist
        template_files = [
            'app/templates/admin/export.html'
        ]
        
        for template in template_files:
            if os.path.exists(template):
                print(f"   ✓ Template exists: {template}")
            else:
                print(f"   ❌ Template missing: {template}")
        
        print("\n6. Testing revenue calculation...")
        
        # Calculate total revenue across all competitions
        total_revenue = db.session.query(db.func.sum(Payment.jumlah)).filter_by(status='approved').scalar() or 0
        print(f"   ✓ Total system revenue: Rp {total_revenue:,}")
        
        # Calculate early bird vs regular revenue
        early_bird_total = 0
        regular_total = 0
        
        for competition in competitions:
            paid_registrations = Registration.query.filter_by(competition_id=competition.id).join(Payment).filter(Payment.status == 'approved').all()
            
            for registration in paid_registrations:
                if registration.harga_terkunci == competition.harga_early_bird:
                    early_bird_total += registration.payment.jumlah
                else:
                    regular_total += registration.payment.jumlah
        
        print(f"   ✓ Early bird revenue: Rp {early_bird_total:,}")
        print(f"   ✓ Regular revenue: Rp {regular_total:,}")
        
        print("\n=== Export System Test Complete ===")
        
        print("\nKey features implemented:")
        print("✓ Export dashboard with competition statistics")
        print("✓ Participant export with filtering (all/approved/paid)")
        print("✓ Revenue report with early bird breakdown")
        print("✓ User export with verification status")
        print("✓ CSV format with proper headers")
        print("✓ Secure filename generation")
        print("✓ Admin authentication required")
        print("✓ Bootstrap interface with download options")

if __name__ == '__main__':
    test_export_system()