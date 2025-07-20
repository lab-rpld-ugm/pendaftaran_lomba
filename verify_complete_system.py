#!/usr/bin/env python3
"""
Comprehensive verification script for PDC 2025 Competition System
"""

import os
import sys
from app import create_app
from app.models.user import User
from app.models.competition import Competition
from app.models.registration import Registration
from app.models.payment import Payment

def verify_system():
    print("=== PDC 2025 Competition System Verification ===\n")
    
    app = create_app()
    with app.app_context():
        # Check database models
        print("1. Database Models:")
        print(f"   ✓ Users: {User.query.count()}")
        print(f"   ✓ Competitions: {Competition.query.count()}")
        print(f"   ✓ Registrations: {Registration.query.count()}")
        print(f"   ✓ Payments: {Payment.query.count()}")
        
        # Check routes
        print("\n2. Available Routes:")
        routes = []
        for rule in app.url_map.iter_rules():
            if not rule.rule.startswith('/static'):
                routes.append(f"   {list(rule.methods)} {rule.rule}")
        
        for route in sorted(routes):
            print(route)
        
        # Check templates
        print(f"\n3. Template Files:")
        template_dir = "app/templates"
        template_count = 0
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    template_count += 1
                    rel_path = os.path.relpath(os.path.join(root, file), template_dir)
                    print(f"   ✓ {rel_path}")
        
        print(f"\n   Total templates: {template_count}")
        
        # Check forms
        print(f"\n4. Form Files:")
        forms_dir = "app/forms"
        if os.path.exists(forms_dir):
            for file in os.listdir(forms_dir):
                if file.endswith('.py') and file != '__init__.py':
                    print(f"   ✓ {file}")
        
        # Check blueprints
        print(f"\n5. Blueprint Files:")
        blueprints_dir = "app/blueprints"
        if os.path.exists(blueprints_dir):
            for blueprint in os.listdir(blueprints_dir):
                blueprint_path = os.path.join(blueprints_dir, blueprint)
                if os.path.isdir(blueprint_path):
                    routes_file = os.path.join(blueprint_path, "routes.py")
                    if os.path.exists(routes_file):
                        print(f"   ✓ {blueprint}/routes.py")
        
        # Check static files
        print(f"\n6. Static Files:")
        static_dir = "app/static"
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), static_dir)
                    print(f"   ✓ {rel_path}")

if __name__ == "__main__":
    verify_system()