from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, TimeField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from datetime import datetime, time
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Ingat Saya')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    nama = StringField('Nama', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Daftar Sebagai', choices=[('Pembeli', 'Pembeli'), ('Toko', 'Pemilik Lapangan')])
    submit = SubmitField('Daftar')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email sudah terdaftar. Gunakan email lain atau login.')

class RegisterTokoForm(FlaskForm):
    nama_toko = StringField('Nama Toko', validators=[DataRequired(), Length(min=2, max=100)])
    lokasi = StringField('Lokasi', validators=[DataRequired(), Length(min=5, max=255)])
    deskripsi = TextAreaField('Deskripsi')
    submit = SubmitField('Daftarkan Toko')

class LapanganForm(FlaskForm):
    nama_lapangan = StringField('Nama Lapangan', validators=[DataRequired(), Length(min=2, max=100)])
    jenis_olahraga = SelectField('Jenis Olahraga', 
                                choices=[('Futsal', 'Futsal'), 
                                         ('Basket', 'Basket'), 
                                         ('Badminton', 'Badminton'), 
                                         ('Tenis', 'Tenis'), 
                                         ('Voli', 'Voli'),
                                         ('Lainnya', 'Lainnya')])
    harga = IntegerField('Harga per Jam (Rp)', validators=[DataRequired(), NumberRange(min=0)])
    jam_operasional_buka = TimeField('Jam Buka', validators=[DataRequired()], default=time(6, 0))
    jam_operasional_tutup = TimeField('Jam Tutup', validators=[DataRequired()], default=time(22, 0))
    gambar_url = StringField('URL Gambar', 
                            validators=[DataRequired()],
                            default='https://pixabay.com/get/g127f956abf1c60de16894116fcb04641530b79aa3b52c96cb59f8e7da284f613c1279698ad09dea2875d901107c0203cb9811a17f068207f457470c8d0f86444_1280.jpg')
    submit = SubmitField('Simpan Lapangan')
    
    def validate_jam_operasional_tutup(self, field):
        if field.data <= self.jam_operasional_buka.data:
            raise ValidationError('Jam tutup harus setelah jam buka.')

class BookingForm(FlaskForm):
    tanggal_booking = DateField('Tanggal Booking', validators=[DataRequired()])
    jam_booking_mulai = TimeField('Jam Mulai', validators=[DataRequired()])
    jam_booking_selesai = TimeField('Jam Selesai', validators=[DataRequired()])
    submit = SubmitField('Booking Sekarang')
    
    def validate_tanggal_booking(self, field):
        if field.data < datetime.now().date():
            raise ValidationError('Tidak dapat booking untuk tanggal yang sudah lewat.')
    
    def validate_jam_booking_selesai(self, field):
        if field.data <= self.jam_booking_mulai.data:
            raise ValidationError('Jam selesai harus setelah jam mulai.')

class PaymentForm(FlaskForm):
    metode = SelectField('Metode Pembayaran', 
                        choices=[('Transfer Bank', 'Transfer Bank'), 
                                 ('E-Wallet', 'E-Wallet'), 
                                 ('Kartu Kredit', 'Kartu Kredit'),
                                 ('Tunai', 'Tunai')])
    submit = SubmitField('Bayar Sekarang')

class RatingForm(FlaskForm):
    skor = SelectField('Rating', choices=[(1, '1 - Sangat Buruk'), 
                                         (2, '2 - Buruk'), 
                                         (3, '3 - Cukup'), 
                                         (4, '4 - Bagus'), 
                                         (5, '5 - Sangat Bagus')], 
                      coerce=int)
    komentar = TextAreaField('Komentar')
    submit = SubmitField('Kirim Rating')
