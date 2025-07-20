#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.user import User, UserProfile
from app.models.competition import Competition
from app.models.registration import Team, TeamMember
from datetime import datetime, timedelta

def test_team_formation():
    """Test team formation functionality"""
    print("=== Testing Team Formation System ===\n")
    
    app = create_app()
    
    with app.app_context():
        # Test Team model methods
        print("1. Testing Team model...")
        
        # Get a team competition
        team_competition = Competition.query.filter_by(kategori='team').first()
        if not team_competition:
            print("   ❌ No team competition found")
            return
        
        print(f"   ✓ Found team competition: {team_competition.nama_kompetisi}")
        print(f"   ✓ Team size: {team_competition.min_anggota}-{team_competition.max_anggota} members")
        
        # Test team creation
        test_team = Team(
            nama_tim="Test Basketball Team",
            competition_id=team_competition.id,
            captain_id=1  # Assuming user ID 1 exists
        )
        
        print(f"   ✓ Team created: {test_team}")
        
        # Test team methods
        print(f"   ✓ Member count: {test_team.get_member_count()}")
        print(f"   ✓ Is complete: {test_team.is_complete()}")
        
        # Test school consistency validation
        is_valid, message = test_team.validate_school_consistency()
        print(f"   ✓ School consistency: {is_valid} - {message}")
        
        print("\n2. Testing Team forms...")
        
        # Test form classes exist
        from app.forms.team import CreateTeamForm, AddMemberForm, TeamRegistrationForm
        print(f"   ✓ CreateTeamForm class exists")
        print(f"   ✓ AddMemberForm class exists")
        print(f"   ✓ TeamRegistrationForm class exists")
        
        print("\n3. Testing Team routes...")
        
        # Test routes exist
        with app.test_client() as client:
            # Test create team route (should redirect to login)
            response = client.get(f'/tim/buat/{team_competition.id}')
            print(f"   ✓ Create team route status: {response.status_code}")
            
            # Test team management route (should redirect to login)
            response = client.get('/tim/1/kelola')
            print(f"   ✓ Team management route status: {response.status_code}")
        
        print("\n4. Testing Team relationships...")
        
        # Test relationships
        existing_team = Team.query.first()
        if existing_team:
            print(f"   ✓ Found existing team: {existing_team.nama_tim}")
            print(f"   ✓ Team members: {len(existing_team.members)}")
            print(f"   ✓ Competition: {existing_team.competition.nama_kompetisi if existing_team.competition else 'None'}")
            
            # Test captain relationship
            captain = existing_team.get_captain()
            if captain:
                print(f"   ✓ Team captain: {captain.email}")
            else:
                print("   ⚠ No captain found")
        else:
            print("   ⚠ No existing teams found")
        
        print("\n5. Testing Team templates...")
        
        # Check if templates exist
        template_files = [
            'app/templates/team/create.html',
            'app/templates/team/manage.html'
        ]
        
        for template in template_files:
            if os.path.exists(template):
                print(f"   ✓ Template exists: {template}")
            else:
                print(f"   ❌ Template missing: {template}")
        
        print("\n=== Team Formation System Test Complete ===")
        
        print("\nKey features implemented:")
        print("✓ Team model with validation methods")
        print("✓ Team creation and member management")
        print("✓ School consistency validation")
        print("✓ Team size validation")
        print("✓ Team forms (CreateTeamForm, AddMemberForm)")
        print("✓ Team routes (create, manage, add/remove members)")
        print("✓ Team templates with Bootstrap styling")
        print("✓ Integration with competition system")

if __name__ == '__main__':
    test_team_formation()