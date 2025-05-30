from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Toko' or 'Pembeli'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    toko = db.relationship('Toko', backref='owner', uselist=False, lazy=True)
    pemesanans = db.relationship('Pemesanan', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.nama}>'
    
    
class Toko(db.Model):
    __tablename__ = 'tokos'

    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nama_toko = db.Column(db.String(100), nullable=False)
    lokasi = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lapangans = db.relationship('Lapangan', backref='store', lazy=True)
    
    def __repr__(self):
        return f'<Toko {self.nama_toko}>'


class Lapangan(db.Model):
    __tablename__ = 'fields'
    
    id = db.Column(db.Integer, primary_key=True)
    toko_id = db.Column(db.Integer, db.ForeignKey('tokos.id'), nullable=False) # Diperbaiki
    nama_lapangan = db.Column(db.String(100), nullable=False)
    jenis_olahraga = db.Column(db.String(50), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    jam_operasional_buka = db.Column(db.Time, nullable=False)
    jam_operasional_tutup = db.Column(db.Time, nullable=False)
    gambar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pemesanans = db.relationship('Pemesanan', backref='bookings', lazy=True)
    ratings = db.relationship('Rating', backref='lapangan', lazy=True)
    
    def __repr__(self):
        return f'<Lapangan {self.nama_lapangan}>'
    
    @property
    def average_rating(self):
        if not self.ratings:
            return 0
        count = len(self.ratings)
        if count == 0:
            return 0
        return sum(r.skor for r in self.ratings) / count

    @property
    def formatted_price(self):
        return f'Rp {self.harga:,}'


class Pemesanan(db.Model):
    __tablename__ = 'pemesanans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pembayarans = db.relationship('Pembayaran', backref='pemesanan')
    lapangan_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    tanggal_booking = db.Column(db.Date, nullable=False)
    jam_booking_mulai = db.Column(db.Time, nullable=False)
    jam_booking_selesai = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Confirmed, Canceled, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pembayarans = db.relationship('Pembayaran', backref='bookings', lazy=True)
    
    def __repr__(self):
        return f'<Pemesanan {self.id}>'


class Pembayaran(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    pemesanan_id = db.Column(db.Integer, db.ForeignKey('pemesanans.id'), nullable=False)
    metode = db.Column(db.String(50), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Success, Failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pemesanan = db.relationship('Pemesanan', backref='pembayaran', lazy=True)
    
    def __repr__(self):
        return f'<Pembayaran {self.id}>'


class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Rating {self.id}>'
    
