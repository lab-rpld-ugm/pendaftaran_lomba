from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from app.blueprints.team import bp
from app.models.competition import Competition
from app.models.registration import Team, TeamMember, TeamRegistration
from app.models.payment import Payment
from app.models.user import User
from app.forms.team import CreateTeamForm, AddMemberForm, TeamRegistrationForm
from app.utils.verification import profile_required
from datetime import datetime
from app import db


@bp.route('/buat/<int:competition_id>', methods=['GET', 'POST'])
@login_required
@profile_required
def create_team(competition_id):
    """Create a new team for a competition"""
    competition = Competition.query.get_or_404(competition_id)
    
    # Validate competition is team-based
    if competition.kategori != 'team':
        flash('Kompetisi ini bukan untuk tim.', 'error')
        return redirect(url_for('competition.detail', id=competition_id))
    
    # Check if user is eligible
    if not competition.is_user_eligible(current_user):
        flash('Anda tidak memenuhi persyaratan untuk kompetisi ini.', 'error')
        return redirect(url_for('competition.detail', id=competition_id))
    
    # Check if user is already captain of a team for this competition
    existing_team = Team.query.filter_by(
        captain_id=current_user.id,
        competition_id=competition_id
    ).first()
    
    if existing_team:
        flash('Anda sudah menjadi kapten tim untuk kompetisi ini.', 'warning')
        return redirect(url_for('team.manage', id=existing_team.id))
    
    # Check if user is already a member of another team for this competition
    existing_membership = TeamMember.query.join(Team).filter(
        Team.competition_id == competition_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if existing_membership:
        flash('Anda sudah terdaftar di tim lain untuk kompetisi ini.', 'warning')
        return redirect(url_for('team.manage', id=existing_membership.team_id))
    
    form = CreateTeamForm(competition=competition)
    
    if form.validate_on_submit():
        try:
            # Create team
            team = Team(
                nama_tim=form.nama_tim.data,
                competition_id=competition_id,
                captain_id=current_user.id
            )
            
            db.session.add(team)
            db.session.flush()  # Get team ID
            
            # Add captain as first member
            captain_member = TeamMember(
                team_id=team.id,
                user_id=current_user.id,
                posisi='Captain'
            )
            
            db.session.add(captain_member)
            db.session.commit()
            
            flash(f'Tim "{team.nama_tim}" berhasil dibuat! Anda adalah kapten tim.', 'success')
            return redirect(url_for('team.manage', id=team.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Team creation error: {str(e)}')
            flash('Terjadi kesalahan saat membuat tim. Silakan coba lagi.', 'error')
    
    return render_template('team/create.html', 
                         form=form, 
                         competition=competition)


@bp.route('/<int:id>/kelola')
@login_required
@profile_required
def manage(id):
    """Manage team (for captain)"""
    team = Team.query.get_or_404(id)
    
    # Only captain can manage team
    if team.captain_id != current_user.id:
        flash('Hanya kapten tim yang dapat mengelola tim.', 'error')
        return redirect(url_for('main.dashboard'))
    
    competition = Competition.query.get(team.competition_id)
    add_member_form = AddMemberForm(team=team)
    
    # Check if team can be registered
    can_register = team.is_complete() and competition.is_registration_open()
    
    # Check if team is already registered
    existing_registration = TeamRegistration.query.filter_by(team_id=team.id).first()
    
    return render_template('team/manage.html',
                         team=team,
                         competition=competition,
                         add_member_form=add_member_form,
                         can_register=can_register,
                         existing_registration=existing_registration)


@bp.route('/<int:id>/tambah-anggota', methods=['POST'])
@login_required
@profile_required
def add_member(id):
    """Add member to team"""
    team = Team.query.get_or_404(id)
    
    # Only captain can add members
    if team.captain_id != current_user.id:
        flash('Hanya kapten tim yang dapat menambah anggota.', 'error')
        return redirect(url_for('team.manage', id=id))
    
    form = AddMemberForm(team=team)
    
    if form.validate_on_submit():
        try:
            success, message = team.add_member(form.user, form.posisi.data)
            if success:
                flash(f'{form.user.profile.nama_lengkap} berhasil ditambahkan ke tim.', 'success')
            else:
                flash(message, 'error')
        except Exception as e:
            current_app.logger.error(f'Add member error: {str(e)}')
            flash('Terjadi kesalahan saat menambah anggota.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return redirect(url_for('team.manage', id=id))


@bp.route('/<int:id>/hapus-anggota/<int:user_id>', methods=['POST'])
@login_required
@profile_required
def remove_member(id, user_id):
    """Remove member from team"""
    team = Team.query.get_or_404(id)
    
    # Only captain can remove members
    if team.captain_id != current_user.id:
        flash('Hanya kapten tim yang dapat menghapus anggota.', 'error')
        return redirect(url_for('team.manage', id=id))
    
    try:
        success, message = team.remove_member(user_id)
        if success:
            flash('Anggota berhasil dihapus dari tim.', 'success')
        else:
            flash(message, 'error')
    except Exception as e:
        current_app.logger.error(f'Remove member error: {str(e)}')
        flash('Terjadi kesalahan saat menghapus anggota.', 'error')
    
    return redirect(url_for('team.manage', id=id))


@bp.route('/<int:id>/daftar', methods=['POST'])
@login_required
@profile_required
def register_team(id):
    """Register complete team for competition"""
    team = Team.query.get_or_404(id)
    
    # Only captain can register team
    if team.captain_id != current_user.id:
        flash('Hanya kapten tim yang dapat mendaftarkan tim.', 'error')
        return redirect(url_for('team.manage', id=id))
    
    # Check if team is already registered
    existing_registration = TeamRegistration.query.filter_by(team_id=team.id).first()
    if existing_registration:
        flash('Tim sudah terdaftar untuk kompetisi ini.', 'warning')
        return redirect(url_for('team.manage', id=id))
    
    form = TeamRegistrationForm(team=team)
    
    if form.validate_on_submit():
        try:
            competition = Competition.query.get(team.competition_id)
            
            # Calculate locked price
            locked_price = competition.get_current_price()
            
            # Create team registration
            registration = TeamRegistration(
                user_id=current_user.id,  # Captain as registrant
                competition_id=team.competition_id,
                team_id=team.id,
                harga_terkunci=locked_price,
                status='pending'
            )
            
            db.session.add(registration)
            db.session.flush()  # Get registration ID
            
            # Create payment record
            payment = Payment(
                registration_id=registration.id,
                jumlah=locked_price,
                status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            flash(f'Tim berhasil didaftarkan! Harga terkunci: Rp {locked_price:,}. Silakan upload bukti pembayaran dalam 24 jam.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Team registration error: {str(e)}')
            flash('Terjadi kesalahan saat mendaftarkan tim.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return redirect(url_for('team.manage', id=id))


@bp.route('/<int:id>/info')
@login_required
def team_info(id):
    """Get team information (AJAX endpoint)"""
    team = Team.query.get_or_404(id)
    
    # Check if user has access to this team info
    is_member = any(member.user_id == current_user.id for member in team.members)
    if not is_member and team.captain_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    competition = Competition.query.get(team.competition_id)
    
    return jsonify({
        'success': True,
        'team': {
            'id': team.id,
            'nama_tim': team.nama_tim,
            'member_count': team.get_member_count(),
            'is_complete': team.is_complete(),
            'captain': {
                'id': team.captain_id,
                'nama': team.get_captain().profile.nama_lengkap if team.get_captain().profile else 'Unknown'
            },
            'members': [
                {
                    'id': member.user.id,
                    'nama': member.user.profile.nama_lengkap if member.user.profile else 'Unknown',
                    'posisi': member.get_position_display(),
                    'sekolah': member.user.profile.sekolah if member.user.profile else 'Unknown'
                }
                for member in team.members
            ]
        },
        'competition': {
            'nama': competition.nama_kompetisi,
            'min_anggota': competition.min_anggota,
            'max_anggota': competition.max_anggota,
            'current_price': competition.get_current_price()
        }
    })


@bp.route('/cari-user')
@login_required
def search_user():
    """Search users by email (AJAX endpoint)"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 3:
        return jsonify({'users': []})
    
    users = User.query.filter(
        User.email.ilike(f'%{query}%')
    ).limit(10).all()
    
    user_list = []
    for user in users:
        if user.profile and user.is_profile_complete():
            user_list.append({
                'id': user.id,
                'email': user.email,
                'nama': user.profile.nama_lengkap,
                'sekolah': user.profile.sekolah
            })
    
    return jsonify({'users': user_list})