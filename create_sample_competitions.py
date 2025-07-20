#!/usr/bin/env python3
"""
Script to create sample competitions for testing
"""
from datetime import datetime, timedelta
from app import create_app, db
from app.models.competition import Competition, CompetitionCategory

def create_sample_competitions():
    """Create sample competitions for testing"""
    app = create_app()
    
    with app.app_context():
        # Create default categories first
        CompetitionCategory.create_default_categories()
        
        # Sample competitions data
        competitions_data = [
            {
                'nama_kompetisi': 'Olimpiade Matematika SMP',
                'deskripsi': 'Kompetisi matematika tingkat SMP dengan soal-soal menantang yang menguji kemampuan logika dan pemecahan masalah.',
                'kategori': 'individual',
                'jenis': 'academic',
                'harga_early_bird': 50000,
                'harga_reguler': 75000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=30),
                'tanggal_kompetisi': datetime.now() + timedelta(days=45),
                'min_kelas': 7,
                'max_kelas': 9
            },
            {
                'nama_kompetisi': 'Olimpiade Sains SMP',
                'deskripsi': 'Kompetisi sains yang mencakup fisika, kimia, dan biologi untuk siswa SMP.',
                'kategori': 'individual',
                'jenis': 'academic',
                'harga_early_bird': 55000,
                'harga_reguler': 80000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=25),
                'tanggal_kompetisi': datetime.now() + timedelta(days=40),
                'min_kelas': 7,
                'max_kelas': 9
            },
            {
                'nama_kompetisi': 'Kompetisi Poster Digital',
                'deskripsi': 'Kompetisi kreativitas dalam membuat poster digital dengan tema lingkungan.',
                'kategori': 'individual',
                'jenis': 'creative',
                'harga_early_bird': 40000,
                'harga_reguler': 60000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=35),
                'tanggal_kompetisi': datetime.now() + timedelta(days=50),
                'min_kelas': 7,
                'max_kelas': 9
            },
            {
                'nama_kompetisi': 'Kompetisi Pidato Bahasa Inggris',
                'deskripsi': 'Kompetisi pidato bahasa Inggris dengan tema "Future Leaders".',
                'kategori': 'individual',
                'jenis': 'performance',
                'harga_early_bird': 45000,
                'harga_reguler': 65000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=28),
                'tanggal_kompetisi': datetime.now() + timedelta(days=42),
                'min_kelas': 7,
                'max_kelas': 9
            },
            {
                'nama_kompetisi': 'Turnamen Basket SMP',
                'deskripsi': 'Turnamen basket antar sekolah SMP dengan sistem gugur.',
                'kategori': 'team',
                'jenis': 'basketball',
                'harga_early_bird': 200000,
                'harga_reguler': 300000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=20),
                'tanggal_kompetisi': datetime.now() + timedelta(days=35),
                'min_kelas': 7,
                'max_kelas': 9,
                'min_anggota': 5,
                'max_anggota': 8
            },
            {
                'nama_kompetisi': 'Turnamen E-Sports Mobile Legends',
                'deskripsi': 'Turnamen e-sports Mobile Legends untuk tim SMP.',
                'kategori': 'team',
                'jenis': 'esports',
                'harga_early_bird': 150000,
                'harga_reguler': 250000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=22),
                'tanggal_kompetisi': datetime.now() + timedelta(days=38),
                'min_kelas': 7,
                'max_kelas': 9,
                'min_anggota': 5,
                'max_anggota': 7
            }
        ]
        
        # Create competitions
        for comp_data in competitions_data:
            existing = Competition.query.filter_by(nama_kompetisi=comp_data['nama_kompetisi']).first()
            if not existing:
                competition = Competition(**comp_data)
                db.session.add(competition)
                print(f"Created competition: {comp_data['nama_kompetisi']}")
            else:
                print(f"Competition already exists: {comp_data['nama_kompetisi']}")
        
        db.session.commit()
        print("Sample competitions created successfully!")

if __name__ == '__main__':
    create_sample_competitions()