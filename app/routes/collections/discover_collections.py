from flask import render_template
from flask_login import login_required, current_user
from ...models.collection import Collection


@login_required
def discover_collections():
    """Show public and unowned collections that users can join or claim"""
    
    # Get collections user is already a member of
    user_created_collections = Collection.query.filter_by(created_by=current_user.id).all()
    permitted_collection_ids = [p.collection_id for p in current_user.collection_permissions]
    permitted_collections = Collection.query.filter(Collection.id.in_(permitted_collection_ids)).all()
    member_collection_ids = {c.id for c in (user_created_collections + permitted_collections)}
    
    # Get public collections user is not a member of
    public_collections = Collection.query.filter(
        Collection.is_public == True,
        ~Collection.id.in_(member_collection_ids) if member_collection_ids else True
    ).order_by(Collection.created_at.desc()).all()
    
    # Get unowned collections (only public ones should be discoverable)
    unowned_collections = Collection.query.filter(
        Collection.created_by.is_(None),
        Collection.is_public == True  # Only show public unowned collections
    ).order_by(Collection.created_at.desc()).all()
    
    # Filter unowned collections to only show those user isn't already a member of
    unowned_collections = [c for c in unowned_collections if c.id not in member_collection_ids]
    
    # Get some stats for the discovery page
    total_public = Collection.query.filter_by(is_public=True).count()
    total_collections = Collection.query.count()
    
    return render_template('discover_collections.html',
                         public_collections=public_collections,
                         unowned_collections=unowned_collections,
                         total_public=total_public,
                         total_collections=total_collections)


def register_route(app):
    """Register the discover_collections route with the Flask app"""
    app.add_url_rule('/collection/discover', 'collections.discover_collections', discover_collections)
