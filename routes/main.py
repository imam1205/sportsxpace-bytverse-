from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from models import Lapangan, Toko
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch featured fields for homepage
    featured_fields = Lapangan.query.order_by(Lapangan.id.desc()).limit(6).all()
    
    # Fetch popular sports types
    popular_sports = db.session.query(
        Lapangan.jenis_olahraga, 
        db.func.count(Lapangan.id).label('count')
    ).group_by(Lapangan.jenis_olahraga).order_by(db.text('count DESC')).limit(6).all()
    
    # Redirect if user is logged in
    if current_user.is_authenticated:
        if current_user.role == 'Toko':
            return redirect(url_for('owner.dashboard'))
    
    return render_template('index.html', 
                           title='Home', 
                           featured_fields=featured_fields,
                           popular_sports=popular_sports)

@main_bp.route('/about')
def about():
    return render_template('about.html', title='About Us')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Us')

@main_bp.route('/error/<message>')
def error(message):
    return render_template('error.html', message=message, title='Error')
