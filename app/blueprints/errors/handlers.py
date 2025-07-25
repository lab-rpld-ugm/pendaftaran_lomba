from flask import render_template, flash, redirect, url_for
from flask_wtf.csrf import CSRFError
from app import db
from app.blueprints.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    """Handle CSRF errors"""
    flash('Sesi keamanan telah berakhir. Silakan coba lagi.', 'warning')
    return redirect(url_for('auth.masuk'))