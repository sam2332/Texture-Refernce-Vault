from flask import render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import desc
from ... import db
from ...models.user import User
from ...models.collection import Collection
from ...models.image import TextureImage, ImageVersion
from ...models.invitation import CollectionInvitation


@login_required
def dashboard():
    # Get pending invitations for current user
    pending_invitations = CollectionInvitation.query.filter_by(
        email=current_user.email.lower(),
        accepted_at=None
    ).filter(
        CollectionInvitation.expires_at > datetime.utcnow()
    ).all()
    
    # Get collections user has access to
    if current_user.is_admin:
        # For admins, get collections they're members of
        created_collections = Collection.query.filter_by(created_by=current_user.id).all()
        permitted_collection_ids = [p.collection_id for p in current_user.collection_permissions]
        permitted_collections = Collection.query.filter(Collection.id.in_(permitted_collection_ids)).all()
        member_collections = list(set(created_collections + permitted_collections))
        
        collections = member_collections
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
                         recently_updated=recently_updated,
                         pending_invitations=pending_invitations)


def register_route(app):
    """Register the dashboard route with the Flask app"""
    app.add_url_rule('/dashboard', 'main.dashboard', dashboard)
