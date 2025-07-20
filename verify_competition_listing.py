#!/usr/bin/env python3
"""
Verification script for competition listing implementation
"""
import os
import sys

def verify_implementation():
    """Verify that all required components are implemented"""
    print("Verifying Competition Listing Implementation...")
    print("=" * 60)
    
    checks = []
    
    # Check 1: Route implementation
    route_file = "app/blueprints/competition/routes.py"
    if os.path.exists(route_file):
        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "@bp.route('/')" in content and "def index():" in content:
                checks.append("✅ Route /kompetisi implemented")
            else:
                checks.append("❌ Route /kompetisi missing")
            
            if "participant-count" in content:
                checks.append("✅ Real-time participant count API endpoint implemented")
            else:
                checks.append("❌ Real-time participant count API endpoint missing")
    else:
        checks.append("❌ Competition routes file missing")
    
    # Check 2: Template implementation
    template_file = "app/templates/competition/index.html"
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "competition-card" in content:
                checks.append("✅ Bootstrap cards template implemented")
            else:
                checks.append("❌ Bootstrap cards template missing")
            
            if "data-competition-id" in content:
                checks.append("✅ Competition ID data attributes for real-time updates")
            else:
                checks.append("❌ Competition ID data attributes missing")
            
            if "participant-count" in content:
                checks.append("✅ Participant count display implemented")
            else:
                checks.append("❌ Participant count display missing")
            
            if "kategori" in content and "jenis" in content:
                checks.append("✅ Filtering by category and type implemented")
            else:
                checks.append("❌ Filtering functionality missing")
    else:
        checks.append("❌ Competition index template missing")
    
    # Check 3: JavaScript implementation
    js_file = "app/static/js/app.js"
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "initializeParticipantCounters" in content:
                checks.append("✅ Real-time participant counter JavaScript implemented")
            else:
                checks.append("❌ Real-time participant counter JavaScript missing")
            
            if "updateParticipantCounts" in content:
                checks.append("✅ Participant count update functionality implemented")
            else:
                checks.append("❌ Participant count update functionality missing")
    else:
        checks.append("❌ JavaScript file missing")
    
    # Check 4: Model implementation
    model_file = "app/models/competition.py"
    if os.path.exists(model_file):
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "get_participant_count" in content:
                checks.append("✅ Participant count model method implemented")
            else:
                checks.append("❌ Participant count model method missing")
            
            if "is_user_eligible" in content:
                checks.append("✅ User eligibility checking implemented")
            else:
                checks.append("❌ User eligibility checking missing")
    else:
        checks.append("❌ Competition model missing")
    
    # Print results
    for check in checks:
        print(check)
    
    # Summary
    passed = len([c for c in checks if c.startswith("✅")])
    total = len(checks)
    
    print("\n" + "=" * 60)
    print(f"Implementation Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All required features are implemented!")
        return True
    else:
        print("⚠ Some features need attention")
        return False

if __name__ == '__main__':
    verify_implementation()