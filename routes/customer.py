from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from models import Lapangan, Toko, Pemesanan, Pembayaran, Rating, User
from forms import BookingForm, PaymentForm, RatingForm
from datetime import datetime, timedelta
from utils import customer_required
from sqlalchemy import func, and_, or_

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

@customer_bp.route('/fields')
def fields():
    # Get search/filter parameters
    search = request.args.get('search', '')
    sport_type = request.args.get('sport_type', '')
    location = request.args.get('location', '')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    
    # Base query
    query = db.session.query(Lapangan, Toko)\
        .join(Toko, Lapangan.toko_id == Toko.id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Lapangan.nama_lapangan.ilike(f'%{search}%'),
                Toko.nama_toko.ilike(f'%{search}%'),
                Lapangan.jenis_olahraga.ilike(f'%{search}%')
            )
        )
    
    if sport_type:
        query = query.filter(Lapangan.jenis_olahraga == sport_type)
    
    if location:
        query = query.filter(Toko.lokasi.ilike(f'%{location}%'))
    
    if price_min and price_min.isdigit():
        query = query.filter(Lapangan.harga >= int(price_min))
    
    if price_max and price_max.isdigit():
        query = query.filter(Lapangan.harga <= int(price_max))
    
    # Execute query
    results = query.all()
    
    # Get unique sport types for filter dropdown
    sport_types = db.session.query(Lapangan.jenis_olahraga)\
        .distinct().order_by(Lapangan.jenis_olahraga).all()
    
    # Get unique locations for filter dropdown
    locations = db.session.query(Toko.lokasi)\
        .distinct().order_by(Toko.lokasi).all()
    
    return render_template('customer/fields.html',
                           title='Cari Lapangan',
                           results=results,
                           sport_types=sport_types,
                           locations=locations,
                           search=search,
                           sport_type=sport_type,
                           location=location,
                           price_min=price_min,
                           price_max=price_max)

@customer_bp.route('/field/<int:field_id>')
def field_detail(field_id):
    lapangan = Lapangan.query.get_or_404(field_id)
    toko = Toko.query.get(lapangan.toko_id)
    
    # Get ratings for this field
    ratings = db.session.query(Rating, User)\
        .join(User, Rating.user_id == User.id)\
        .filter(Rating.lapangan_id == field_id)\
        .order_by(Rating.created_at.desc())\
        .all()
    
    # Check if user has booked and can leave a rating
    can_rate = False
    user_rating = None
    
    if current_user.is_authenticated and current_user.role == 'Pembeli':
        # Check if user has completed bookings for this field
        completed_bookings = Pemesanan.query.filter(
            Pemesanan.user_id == current_user.id,
            Pemesanan.lapangan_id == field_id,
            Pemesanan.status == 'Completed'
        ).count()
        
        can_rate = completed_bookings > 0
        
        # Check if user already rated
        user_rating = Rating.query.filter_by(
            user_id=current_user.id,
            lapangan_id=field_id
        ).first()
    
    return render_template('customer/field_detail.html', 
        title=lapangan.nama_lapangan, 
        lapangan=lapangan, 
        toko=toko, 
        ratings=ratings, 
        can_rate=can_rate, 
        user_rating=user_rating
    )

@customer_bp.route('/field/<int:field_id>/check-availability', methods=['GET'])
def check_availability(field_id):
    date_str = request.args.get('date')
    print(field_id)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400
    
    lapangan = Lapangan.query.get_or_404(field_id)
    
    # Get all bookings for this field on the selected date
    bookings = Pemesanan.query.filter(
        Pemesanan.lapangan_id == field_id,
        Pemesanan.tanggal_booking == selected_date,
        Pemesanan.status.in_(['Pending', 'Confirmed'])
    ).all()
    
    # Create a list of booked timeslots
    booked_slots = []
    for booking in bookings:
        booked_slots.append({
            'start': booking.jam_booking_mulai.strftime('%H:%M'),
            'end': booking.jam_booking_selesai.strftime('%H:%M')
        })
    
    # Generate all available timeslots based on operating hours
    open_time = lapangan.jam_operasional_buka
    close_time = lapangan.jam_operasional_tutup
    
    return jsonify({
        'field_id': field_id,
        'date': date_str,
        'operating_hours': {
            'open': open_time.strftime('%H:%M'),
            'close': close_time.strftime('%H:%M')
        },
        'booked_slots': booked_slots
    })

@customer_bp.route('/field/<int:field_id>/book', methods=['GET', 'POST'])
@login_required
@customer_required
def book_field(field_id):
    lapangan = Lapangan.query.get_or_404(field_id)
    toko = Toko.query.get(lapangan.toko_id)
    
    form = BookingForm()
    
    if form.validate_on_submit():
        # Parse the date and time from form data
        booking_date = form.tanggal_booking.data
        start_time = form.jam_booking_mulai.data
        end_time = form.jam_booking_selesai.data
        
        # Check if the timeslot is already booked
        existing_booking = Pemesanan.query.filter(
            Pemesanan.lapangan_id == field_id,
            Pemesanan.tanggal_booking == booking_date,
            Pemesanan.status.in_(['Pending', 'Confirmed']),
            or_(
                and_(
                    Pemesanan.jam_booking_mulai <= start_time,
                    Pemesanan.jam_booking_selesai > start_time
                ),
                and_(
                    Pemesanan.jam_booking_mulai < end_time,
                    Pemesanan.jam_booking_selesai >= end_time
                ),
                and_(
                    Pemesanan.jam_booking_mulai >= start_time,
                    Pemesanan.jam_booking_selesai <= end_time
                )
            )
        ).first()
        
        if existing_booking:
            flash('Maaf, jadwal ini sudah dipesan. Silakan pilih waktu lain.', 'danger')
            return redirect(url_for('customer.book_field', field_id=field_id))
        
        # Create the booking
        booking = Pemesanan(
            user_id=current_user.id,
            lapangan_id=field_id,
            tanggal_booking=booking_date,
            jam_booking_mulai=start_time,
            jam_booking_selesai=end_time,
            status='Pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking berhasil dibuat! Silakan lanjutkan ke pembayaran.', 'success')
        return redirect(url_for('customer.payment', booking_id=booking.id))
    
    return render_template('customer/booking.html',
                           title='Booking Lapangan',
                           lapangan=lapangan,
                           toko=toko,
                           form=form)

@customer_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def payment(booking_id):
    booking = Pemesanan.query.get_or_404(booking_id)
    
    # Security check: ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        abort(403)
    
    lapangan = Lapangan.query.get(booking.lapangan_id)
    
    # Calculate booking duration in hours
    start_time = booking.jam_booking_mulai
    end_time = booking.jam_booking_selesai
    duration_minutes = (end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute)
    duration_hours = duration_minutes / 60
    
    # Calculate total amount
    total_amount = int(lapangan.harga * duration_hours)
    
    form = PaymentForm()
    
    if form.validate_on_submit():
        payment = Pembayaran(
            pemesanan_id=booking.id,
            metode=form.metode.data,
            jumlah=total_amount,
            status='Success'  # In a real app, this would be pending until payment is confirmed
        )
        
        # Update booking status
        booking.status = 'Confirmed'
        
        db.session.add(payment)
        db.session.commit()
        
        flash('Pembayaran berhasil! Booking Anda telah dikonfirmasi.', 'success')
        return redirect(url_for('customer.my_bookings'))
    
    return render_template('customer/payment.html',
                           title='Pembayaran',
                           booking=booking,
                           lapangan=lapangan,
                           total_amount=total_amount,
                           duration_hours=duration_hours,
                           form=form)

@customer_bp.route('/my-bookings')
@login_required
@customer_required
def my_bookings():
    # Get all bookings for the current user
    bookings = db.session.query(Pemesanan, Lapangan, Toko, Pembayaran)\
        .join(Lapangan, Pemesanan.lapangan_id == Lapangan.id)\
        .join(Toko, Lapangan.toko_id == Toko.id)\
        .outerjoin(Pembayaran, Pemesanan.id == Pembayaran.pemesanan_id)\
        .filter(Pemesanan.user_id == current_user.id)\
        .order_by(Pemesanan.tanggal_booking.desc(), Pemesanan.jam_booking_mulai)\
        .all()
    
    return render_template('customer/bookings.html',
                           title='Booking Saya',
                           bookings=bookings)

@customer_bp.route('/profile')
@login_required
def profile():
    return render_template('customer/profile.html',
                           title='Profil Saya')

@customer_bp.route('/field/<int:field_id>/rate', methods=['GET', 'POST'])
@login_required
@customer_required
def rate_field(field_id):
    lapangan = Lapangan.query.get_or_404(field_id)
    
    # Check if user has completed bookings for this field
    completed_bookings = Pemesanan.query.filter(
        Pemesanan.user_id == current_user.id,
        Pemesanan.lapangan_id == field_id,
        Pemesanan.status == 'Completed'
    ).count()
    
    if completed_bookings == 0:
        flash('Anda harus menyelesaikan booking terlebih dahulu untuk memberikan rating.', 'warning')
        return redirect(url_for('customer.field_detail', field_id=field_id))
    
    # Check if user already rated
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id,
        lapangan_id=field_id
    ).first()
    
    form = RatingForm()
    
    if existing_rating:
        # Pre-fill the form with existing rating
        if not form.is_submitted():
            form.skor.data = existing_rating.skor
            form.komentar.data = existing_rating.komentar
    
    if form.validate_on_submit():
        if existing_rating:
            # Update existing rating
            existing_rating.skor = form.skor.data
            existing_rating.komentar = form.komentar.data
            flash('Rating berhasil diperbarui!', 'success')
        else:
            # Create new rating
            rating = Rating(
                user_id=current_user.id,
                lapangan_id=field_id,
                skor=form.skor.data,
                komentar=form.komentar.data
            )
            db.session.add(rating)
            flash('Terima kasih atas rating Anda!', 'success')
        
        db.session.commit()
        return redirect(url_for('customer.field_detail', field_id=field_id))
    
    return render_template('customer/rate.html',
                           title='Beri Rating',
                           lapangan=lapangan,
                           form=form,
                           is_update=existing_rating is not None)
