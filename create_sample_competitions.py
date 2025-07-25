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
        
        # Sample competitions data for 9 OSN competitions
        competitions_data = [
            {
                'nama_kompetisi': 'Basket',
                'deskripsi': 'Basketball tournament for junior high school teams with elimination system.',
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
                'nama_kompetisi': 'Math Olympiad',
                'deskripsi': 'Mathematics competition for junior high school students with challenging problems testing logic and problem-solving skills.',
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
                'nama_kompetisi': 'Science Olympiad',
                'deskripsi': 'Science competition covering physics, chemistry, and biology for junior high school students.',
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
                'nama_kompetisi': 'Logic Olympiad',
                'deskripsi': 'Logic and problem-solving competition for junior high school students.',
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
                'nama_kompetisi': 'Scientific Writing',
                'deskripsi': 'Scientific writing competition for junior high school students with environmental and technology themes.',
                'kategori': 'individual',
                'jenis': 'creative',
                'harga_early_bird': 60000,
                'harga_reguler': 85000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=35),
                'tanggal_kompetisi': datetime.now() + timedelta(days=50),
                'min_kelas': 7,
                'max_kelas': 9
            },
            {
                'nama_kompetisi': 'Speech',
                'deskripsi': 'English speech competition with the theme "Future Leaders".',
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
                'nama_kompetisi': 'E-Sports',
                'deskripsi': 'Mobile Legends e-sports tournament for junior high school teams.',
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
            },
            {
                'nama_kompetisi': 'Solo Vocal',
                'deskripsi': 'Solo vocal competition for junior high school students with various music genres.',
                'kategori': 'individual',
                'jenis': 'performance',
                'harga_early_bird': 40000,
                'harga_reguler': 60000,
                'tanggal_mulai_early_bird': datetime.now(),
                'tanggal_akhir_early_bird': datetime.now() + timedelta(days=7),
                'deadline_registrasi': datetime.now() + timedelta(days=25),
                'tanggal_kompetisi': datetime.now() + timedelta(days=40),
                'min_kelas': 7,
                'max_kelas': 9
            },
            {
                'nama_kompetisi': 'Digital Poster',
                'deskripsi': 'Creative competition in making digital posters with environmental themes.',
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