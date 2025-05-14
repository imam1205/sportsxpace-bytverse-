from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Toko':
            flash('Akses ditolak. Anda harus login sebagai pemilik lapangan.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Pembeli':
            flash('Akses ditolak. Anda harus login sebagai pembeli.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
