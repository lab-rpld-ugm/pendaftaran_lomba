from flask import render_template, redirect, url_for, flash, request, session
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
            # Make session permanent for iframe compatibility
            session.permanent = True
            
            # Login user with remember me option
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'Selamat datang, {user.email}!', 'success')
            
            # Check if we're in an iframe by looking at referer header
            referer = request.headers.get('Referer', '')
            parent_domain = 'https://pdc.praditadirgantara.sch.id'
            
            # If request comes from the parent domain, we're likely in an iframe
            if parent_domain in referer:
                return f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Login Success</title>
                </head>
                <body>
                    <div style="text-align: center; padding: 50px;">
                        <h3>Login berhasil!</h3>
                        <p>Mengalihkan ke dashboard...</p>
                    </div>
                    <script type="text/javascript">
                        // Try multiple redirect methods for iframe
                        function redirectToParent() {{
                            try {{
                                // Method 1: Redirect parent window
                                if (window.parent && window.parent !== window) {{
                                    window.parent.location.href = "{next_page}";
                                    return;
                                }}
                                
                                // Method 2: Use top window
                                if (window.top && window.top !== window) {{
                                    window.top.location.href = "{next_page}";
                                    return;
                                }}
                                
                                // Method 3: Regular redirect
                                window.location.href = "{next_page}";
                            }} catch (e) {{
                                // Fallback: Regular redirect
                                window.location.href = "{next_page}";
                            }}
                        }}
                        
                        // Execute redirect immediately
                        redirectToParent();
                        
                        // Fallback after 2 seconds
                        setTimeout(function() {{
                            window.location.href = "{next_page}";
                        }}, 2000);
                    </script>
                </body>
                </html>
                '''
            
            # Regular redirect for non-iframe requests
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
            
            # Check if we're in an iframe
            is_iframe = request.headers.get('Sec-Fetch-Dest') == 'iframe' or \
                       request.headers.get('X-Requested-With') == 'iframe' or \
                       'iframe' in request.headers.get('Referer', '').lower()
            
            next_page = url_for('auth.masuk')
            
            # For iframe, use JavaScript redirect to break out of iframe context
            if is_iframe:
                return f'''
                <script type="text/javascript">
                    if (window.parent !== window) {{
                        window.parent.location.href = "{next_page}";
                    }} else {{
                        window.location.href = "{next_page}";
                    }}
                </script>
                <p>Redirecting to login...</p>
                '''
            
            return redirect(next_page)
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat registrasi. Silakan coba lagi.', 'danger')
    
    return render_template('auth/daftar.html', form=form)

@bp.route('/keluar')
def keluar():
    """Logout route"""
    logout_user()
    return redirect(url_for('main.index'))