from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from ..models.user import User
from ..models.collection import Collection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get collections user has access to
    if current_user.is_admin:
        collections = Collection.query.all()
        user_count = User.query.count()
    else:
        # Get collections user created or has permissions for
        created_collections = Collection.query.filter_by(created_by=current_user.id).all()
        permitted_collection_ids = [p.collection_id for p in current_user.collection_permissions]
        permitted_collections = Collection.query.filter(Collection.id.in_(permitted_collection_ids)).all()
        collections = list(set(created_collections + permitted_collections))
        user_count = 1
    
    return render_template('dashboard.html', 
                         collections=collections, 
                         current_time=datetime.utcnow(),
                         user_count=user_count)

@main_bp.route('/collections')
@login_required
def collections():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    collections = Collection.query.all()
    return render_template('admin.html', users=users, collections=collections)
