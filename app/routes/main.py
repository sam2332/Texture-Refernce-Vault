from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from .. import db
from ..models.user import User
from ..models.collection import Collection
from ..models.image import TextureImage, ImageVersion

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
        
        # Calculate stats for admin (all images)
        total_images = TextureImage.query.count()
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_uploads = TextureImage.query.filter(TextureImage.created_at >= week_ago).count()
        
        # Get recent images for admin (all images)
        recent_images = TextureImage.query.order_by(desc(TextureImage.created_at)).limit(10).all()
        recently_updated = TextureImage.query.join(ImageVersion).filter(
            ImageVersion.is_current == True
        ).order_by(desc(ImageVersion.uploaded_at)).limit(10).all()
    else:
        # Get collections user created or has permissions for
        created_collections = Collection.query.filter_by(created_by=current_user.id).all()
        permitted_collection_ids = [p.collection_id for p in current_user.collection_permissions]
        permitted_collections = Collection.query.filter(Collection.id.in_(permitted_collection_ids)).all()
        collections = list(set(created_collections + permitted_collections))
        user_count = 1
        
        # Calculate stats only from accessible collections
        accessible_collection_ids = [c.id for c in collections]
        if accessible_collection_ids:
            total_images = TextureImage.query.filter(
                TextureImage.collection_id.in_(accessible_collection_ids)
            ).count()
            
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_uploads = TextureImage.query.filter(
                TextureImage.collection_id.in_(accessible_collection_ids),
                TextureImage.created_at >= week_ago
            ).count()
        else:
            total_images = 0
            recent_uploads = 0
        
        # Get recent images only from accessible collections
        if accessible_collection_ids:
            recent_images = TextureImage.query.filter(
                TextureImage.collection_id.in_(accessible_collection_ids)
            ).order_by(desc(TextureImage.created_at)).limit(10).all()
            
            recently_updated = TextureImage.query.join(ImageVersion).filter(
                TextureImage.collection_id.in_(accessible_collection_ids),
                ImageVersion.is_current == True
            ).order_by(desc(ImageVersion.uploaded_at)).limit(10).all()
        else:
            recent_images = []
            recently_updated = []
    
    return render_template('dashboard.html', 
                         collections=collections, 
                         current_time=datetime.utcnow(),
                         user_count=user_count,
                         total_images=total_images,
                         recent_uploads=recent_uploads,
                         recent_images=recent_images,
                         recently_updated=recently_updated)

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
