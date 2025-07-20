#!/usr/bin/env python3
"""
Main application entry point for PDC 2025 Competition System
"""
import os
from app import create_app
from app.config import config

# Get configuration from environment variable
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config[config_name])

if __name__ == '__main__':
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8818)),
        debug=app.config.get('DEBUG', False)
    )