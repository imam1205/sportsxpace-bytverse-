from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import User, Toko, Lapangan, Pemesanan, Pembayaran
from forms import LapanganForm
from datetime import datetime, timedelta
from sqlalchemy import func
from utils import owner_required

owner_bp = Blueprint('owner', __name__, url_prefix='/owner')

@owner_bp.route('/dashboard')
@login_required
@owner_required
def dashboard():
    # Check if user has a registered toko
    toko = Toko.query.filter_by(user_id=current_user.id).first()
    if not toko:
        flash('Anda perlu mendaftarkan toko terlebih dahulu.', 'warning')
        return redirect(url_for('owner.register_toko'))
    
    # Get all fields owned by the toko
    lapangans = Lapangan.query.filter_by(toko_id=toko.id).all()
    
    # Get recent bookings
    recent_bookings = db.session.query(Pemesanan, Lapangan, User)\
        .join(Lapangan, Pemesanan.lapangan_id == Lapangan.id)\
        .join(User, Pemesanan.user_id == User.id)\
        .filter(Lapangan.toko_id == toko.id)\
        .order_by(Pemesanan.created_at.desc())\
        .limit(5).all()
    
    # Get booking statistics for the current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    bookings_this_month = db.session.query(func.count(Pemesanan.id))\
        .join(Lapangan, Pemesanan.lapangan_id == Lapangan.id)\
        .filter(Lapangan.toko_id == toko.id,
                func.extract('month', Pemesanan.created_at) == current_month,
                func.extract('year', Pemesanan.created_at) == current_year)\
        .scalar()
    
    # Get revenue statistics
    revenue = db.session.query(func.sum(Pembayaran.jumlah))\
        .join(Pemesanan, Pembayaran.pemesanan_id == Pemesanan.id)\
        .join(Lapangan, Pemesanan.lapangan_id == Lapangan.id)\
        .filter(Lapangan.toko_id == toko.id,
                Pembayaran.status == 'Success')\
        .scalar() or 0
    
    return render_template('owner/dashboard.html', 
                           title='Owner Dashboard',
                           toko=toko,
                           lapangans=lapangans,
                           recent_bookings=recent_bookings,
                           bookings_this_month=bookings_this_month,
                           revenue=revenue)

@owner_bp.route('/lapangan')
@login_required
@owner_required
def lapangans():
    toko = Toko.query.filter_by(user_id=current_user.id).first()
    if not toko:
        flash('Anda perlu mendaftarkan toko terlebih dahulu.', 'warning')
        return redirect(url_for('owner.register_toko'))
    
    lapangan_list = Lapangan.query.filter_by(toko_id=toko.id).all()
    return render_template('owner/lapangans.html', 
                           title='Kelola Lapangan',
                           toko=toko,
                           lapangans=lapangan_list)

@owner_bp.route('/lapangan/add', methods=['GET', 'POST'])
@login_required
@owner_required
def add_lapangan():
    toko = Toko.query.filter_by(user_id=current_user.id).first()
    if not toko:
        flash('Anda perlu mendaftarkan toko terlebih dahulu.', 'warning')
        return redirect(url_for('owner.register_toko'))
    
    form = LapanganForm()
    
    if form.validate_on_submit():
        lapangan = Lapangan(
            toko_id=toko.id,
            nama_lapangan=form.nama_lapangan.data,
            jenis_olahraga=form.jenis_olahraga.data,
            harga=form.harga.data,
            jam_operasional_buka=form.jam_operasional_buka.data,
            jam_operasional_tutup=form.jam_operasional_tutup.data,
            gambar_url=form.gambar_url.data
        )
        
        db.session.add(lapangan)
        db.session.commit()
        
        flash('Lapangan berhasil ditambahkan!', 'success')
        return redirect(url_for('owner.lapangans'))
    
    return render_template('owner/add_field.html', 
                           title='Tambah Lapangan',
                           form=form)

@owner_bp.route('/lapangan/edit/<int:lapangan_id>', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_lapangan(lapangan_id):
    toko = Toko.query.filter_by(user_id=current_user.id).first()
    if not toko:
        flash('Anda perlu mendaftarkan toko terlebih dahulu.', 'warning')
        return redirect(url_for('owner.register_toko'))
    
    lapangan = Lapangan.query.get_or_404(lapangan_id)
    
    # Security check: ensure the lapangan belongs to this toko
    if lapangan.toko_id != toko.id:
        abort(403)
    
    form = LapanganForm(obj=lapangan)
    
    if form.validate_on_submit():
        lapangan.nama_lapangan = form.nama_lapangan.data
        lapangan.jenis_olahraga = form.jenis_olahraga.data
        lapangan.harga = form.harga.data
        lapangan.jam_operasional_buka = form.jam_operasional_buka.data
        lapangan.jam_operasional_tutup = form.jam_operasional_tutup.data
        lapangan.gambar_url = form.gambar_url.data
        
        db.session.commit()
        
        flash('Lapangan berhasil diperbarui!', 'success')
        return redirect(url_for('owner.lapangans'))
    
    return render_template('owner/edit_field.html', 
                           title='Edit Lapangan',
                           form=form,
                           lapangan=lapangan)

@owner_bp.route('/bookings')
@login_required
@owner_required
def bookings():
    toko = Toko.query.filter_by(user_id=current_user.id).first()
    if not toko:
        flash('Anda perlu mendaftarkan toko terlebih dahulu.', 'warning')
        return redirect(url_for('owner.register_toko'))
    
    # Get all bookings for this toko's fields
    bookings_query = db.session.query(Pemesanan, Lapangan, User, Pembayaran)\
        .join(Lapangan, Pemesanan.lapangan_id == Lapangan.id)\
        .join(User, Pemesanan.user_id == User.id)\
        .outerjoin(Pembayaran, Pemesanan.id == Pembayaran.pemesanan_id)\
        .filter(Lapangan.toko_id == toko.id)\
        .order_by(Pemesanan.tanggal_booking, Pemesanan.jam_booking_mulai)
    
    # Filter by status if provided
    status_filter = request.args.get('status')
    if status_filter and status_filter != 'all':
        bookings_query = bookings_query.filter(Pemesanan.status == status_filter)
    
    bookings = bookings_query.all()
    
    return render_template('owner/bookings.html', 
                           title='Kelola Pemesanan',
                           bookings=bookings,
                           current_filter=status_filter or 'all')

@owner_bp.route('/booking/<int:booking_id>/update-status', methods=['POST'])
@login_required
@owner_required
def update_booking_status(booking_id):
    toko = Toko.query.filter_by(user_id=current_user.id).first()
    if not toko:
        abort(403)
    
    booking = Pemesanan.query.get_or_404(booking_id)
    lapangan = Lapangan.query.get_or_404(booking.lapangan_id)
    
    # Security check: ensure the booking is for a field owned by this toko
    if lapangan.toko_id != toko.id:
        abort(403)
    
    new_status = request.form.get('status')
    if new_status in ['Confirmed', 'Canceled', 'Completed']:
        booking.status = new_status
        db.session.commit()
        flash(f'Status pemesanan berhasil diperbarui menjadi {new_status}.', 'success')
    else:
        flash('Status tidak valid!', 'danger')
    
    return redirect(url_for('owner.bookings'))
