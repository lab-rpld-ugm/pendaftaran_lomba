from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.blueprints.auth import bp
from app.forms.auth import RegistrationForm, LoginForm
from app.models.user import User, UserProfile
from app import db

@bp.route('/masuk', methods=['GET', 'POST'])
def masuk():
    """Login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            # Login user with remember me option
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'Selamat datang, {user.email}!', 'success')
            return redirect(next_page)
        else:
            flash('Email atau kata sandi tidak valid.', 'danger')
    
    return render_template('auth/masuk.html', form=form)

@bp.route('/daftar', methods=['GET', 'POST'])
def daftar():
    """Registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(email=form.email.data.lower())
            user.set_password(form.password.data)
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            # Create empty user profile
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            
            flash('Registrasi berhasil! Silakan masuk dengan akun Anda.', 'success')
            return redirect(url_for('auth.masuk'))
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat registrasi. Silakan coba lagi.', 'danger')
    
    return render_template('auth/daftar.html', form=form)

@bp.route('/keluar')
def keluar():
    """Logout route"""
    logout_user()
    return redirect(url_for('main.index'))