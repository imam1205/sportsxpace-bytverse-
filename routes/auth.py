from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from models import User, Toko
from forms import LoginForm, RegisterForm, RegisterTokoForm
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.role == 'Toko':
                return redirect(next_page or url_for('owner.dashboard'))
            else:
                return redirect(next_page or url_for('customer.fields'))
        else:
            flash('Login gagal. Periksa email dan password.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    toko_form = RegisterTokoForm()
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            name=form.nama.data,
            email=form.email.data,
            password=hashed_password,
            role=form.role.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        # If user is a Toko (field owner), continue with toko registration
        if form.role.data == 'Toko':
            return redirect(url_for('auth.register_toko', user_id=user.id))
        
        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Register')

@auth_bp.route('/register/toko/<int:user_id>', methods=['GET', 'POST'])
def register_toko(user_id):
    user = User.query.get_or_404(user_id)
    
    # Security check: only allow toko registration for new Toko users
    if user.role != 'Toko' or Toko.query.filter_by(user_id=user.id).first():
        flash('Pendaftaran tidak valid.', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegisterTokoForm()
    
    if form.validate_on_submit():
        toko = Toko(
            user_id=user.id,
            nama_toko=form.nama_toko.data,
            lokasi=form.lokasi.data,
            deskripsi=form.deskripsi.data
        )
        
        db.session.add(toko)
        db.session.commit()
        
        flash('Toko berhasil didaftarkan! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_toko.html', form=form, title='Register Toko')
