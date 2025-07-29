from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .. import db
from ..models.collection import Collection, CollectionPermission
from ..models.image import TextureImage
from ..models.user import User
from ..utils.helpers import has_collection_permission

collections_bp = Blueprint('collections', __name__)

@collections_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_collection():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        
        collection = Collection(
            name=name,
            description=description,
            created_by=current_user.id
        )
        
        db.session.add(collection)
        db.session.commit()
        
        flash('Collection created successfully!')
        return redirect(url_for('collections.view_collection', id=collection.id))
    
    return render_template('create_collection.html')

@collections_bp.route('/<int:id>')
@login_required
def view_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this collection.')
        return redirect(url_for('main.dashboard'))
    
    images = TextureImage.query.filter_by(collection_id=id).all()
    return render_template('view_collection.html', collection=collection, images=images)

@collections_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'admin'):
        flash('You do not have permission to edit this collection.')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        collection.name = request.form['name']
        collection.description = request.form.get('description', '')
        db.session.commit()
        
        flash('Collection updated successfully!')
        return redirect(url_for('collections.view_collection', id=collection.id))
    
    return render_template('edit_collection.html', collection=collection)

@collections_bp.route('/<int:id>/delete')
@login_required
def delete_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this collection.')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(collection)
    db.session.commit()
    
    flash('Collection deleted successfully!')
    return redirect(url_for('main.dashboard'))

@collections_bp.route('/<int:id>/permissions', methods=['GET', 'POST'])
@login_required
def manage_permissions(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    users = User.query.all()
    permissions = CollectionPermission.query.filter_by(collection_id=id).all()
    return render_template('manage_permissions.html', collection=collection, users=users, permissions=permissions)

@collections_bp.route('/<int:id>/add_permission', methods=['POST'])
@login_required
def add_permission(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    user_id = request.form['user_id']
    permission_level = request.form['permission_level']
    
    # Check if permission already exists
    existing = CollectionPermission.query.filter_by(
        user_id=user_id, 
        collection_id=id
    ).first()
    
    if existing:
        existing.permission_level = permission_level
        flash('Permission updated successfully!')
    else:
        permission = CollectionPermission(
            user_id=user_id,
            collection_id=id,
            permission_level=permission_level
        )
        db.session.add(permission)
        flash('Permission added successfully!')
    
    db.session.commit()
    return redirect(url_for('collections.manage_permissions', id=id))

@collections_bp.route('/<int:id>/remove_permission/<int:permission_id>')
@login_required
def remove_permission(id, permission_id):
    collection = Collection.query.get_or_404(id)
    permission = CollectionPermission.query.get_or_404(permission_id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    db.session.delete(permission)
    db.session.commit()
    
    flash('Permission removed successfully!')
    return redirect(url_for('collections.manage_permissions', id=id))
