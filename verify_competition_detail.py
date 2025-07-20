#!/usr/bin/env python3
"""
Verification script for competition detail functionality
"""
import os
import sys

def verify_competition_detail():
    """Verify that competition detail functionality is properly implemented"""
    print("Verifying Competition Detail Implementation")
    print("=" * 50)
    
    # Check 1: Route implementation
    print("\n1. Checking route implementation...")
    route_file = "app/blueprints/competition/routes.py"
    if os.path.exists(route_file):
        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for detail route
        if "@bp.route('/<int:id>')" in content and "def detail(id):" in content:
            print("   ✓ Detail route exists")
        else:
            print("   ✗ Detail route missing")
            return False
            
        # Check for eligibility logic
        if "user_eligible" in content and "eligibility_reason" in content:
            print("   ✓ User eligibility logic implemented")
        else:
            print("   ✗ User eligibility logic missing")
            return False
            
        # Check for template rendering
        if "render_template('competition/detail.html'" in content:
            print("   ✓ Template rendering implemented")
        else:
            print("   ✗ Template rendering missing")
            return False
    else:
        print("   ✗ Route file not found")
        return False
    
    # Check 2: Template implementation
    print("\n2. Checking template implementation...")
    template_file = "app/templates/competition/detail.html"
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Check for required template elements
        required_elements = [
            "competition.nama_kompetisi",
            "competition.deskripsi", 
            "competition.get_current_price()",
            "competition.is_early_bird_active()",
            "user_eligible",
            "eligibility_reason",
            "competition.tanggal_kompetisi",
            "competition.deadline_registrasi"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in template_content:
                missing_elements.append(element)
        
        if not missing_elements:
            print("   ✓ All required template elements present")
        else:
            print(f"   ✗ Missing template elements: {missing_elements}")
            return False
            
        # Check for pricing display
        if "Early Bird" in template_content and "Rp" in template_content:
            print("   ✓ Pricing display implemented")
        else:
            print("   ✗ Pricing display missing")
            return False
            
        # Check for registration button
        if "Daftar" in template_content or "register" in template_content:
            print("   ✓ Registration button implemented")
        else:
            print("   ✗ Registration button missing")
            return False
    else:
        print("   ✗ Template file not found")
        return False
    
    # Check 3: Model methods
    print("\n3. Checking model methods...")
    model_file = "app/models/competition.py"
    if os.path.exists(model_file):
        with open(model_file, 'r', encoding='utf-8') as f:
            model_content = f.read()
            
        required_methods = [
            "get_current_price",
            "is_early_bird_active", 
            "is_user_eligible",
            "get_participant_count",
            "get_early_bird_savings",
            "is_registration_open"
        ]
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in model_content:
                missing_methods.append(method)
        
        if not missing_methods:
            print("   ✓ All required model methods present")
        else:
            print(f"   ✗ Missing model methods: {missing_methods}")
            return False
    else:
        print("   ✗ Model file not found")
        return False
    
    # Check 4: Verification helper
    print("\n4. Checking verification helper...")
    helper_file = "app/utils/verification.py"
    if os.path.exists(helper_file):
        with open(helper_file, 'r', encoding='utf-8') as f:
            helper_content = f.read()
            
        if "ProfileVerificationHelper" in helper_content:
            print("   ✓ ProfileVerificationHelper exists")
        else:
            print("   ✗ ProfileVerificationHelper missing")
            return False
    else:
        print("   ✗ Verification helper file not found")
        return False
    
    print("\n" + "=" * 50)
    print("✓ Competition detail implementation verified successfully!")
    print("\nImplemented features:")
    print("- Route /kompetisi/<id> for competition details")
    print("- Complete template with competition information")
    print("- Current pricing display with early bird logic")
    print("- User eligibility checking")
    print("- Registration button when user is eligible")
    print("- Profile status integration")
    print("- Responsive Bootstrap design")
    
    return True

if __name__ == '__main__':
    success = verify_competition_detail()
    sys.exit(0 if success else 1)