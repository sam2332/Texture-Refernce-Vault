from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from .. import db
from ..models.collection import Collection, CollectionPermission
from ..models.image import TextureImage
from ..models.user import User
from ..models.invitation import CollectionInvitation
from ..utils.helpers import has_collection_permission

collections_bp = Blueprint('collections', __name__)

@collections_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_collection():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        is_public = bool(request.form.get('is_public'))
        
        collection = Collection(
            name=name,
            description=description,
            created_by=current_user.id,
            is_public=is_public
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
    return render_template('view_collection.html', 
                         collection=collection, 
                         images=images, 
                         has_collection_permission=has_collection_permission)

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
        collection.is_public = bool(request.form.get('is_public'))
        db.session.commit()
        
        flash('Collection updated successfully!')
        return redirect(url_for('collections.view_collection', id=collection.id))
    
    return render_template('edit_collection.html', collection=collection)

@collections_bp.route('/<int:id>/delete')
@login_required
def delete_collection(id):
    collection = Collection.query.get_or_404(id)
    
    # Allow deletion if user is owner, admin, or if collection is unowned and user has admin permission
    can_delete = (
        (collection.created_by and collection.created_by == current_user.id) or 
        current_user.is_admin or
        (not collection.created_by and has_collection_permission(current_user, collection, 'admin'))
    )
    
    if not can_delete:
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
    
    # Allow permission management if user is owner, admin, or if collection is unowned and user has admin permission
    can_manage = (
        (collection.created_by and collection.created_by == current_user.id) or 
        current_user.is_admin or
        (not collection.created_by and has_collection_permission(current_user, collection, 'admin'))
    )
    
    if not can_manage:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    users = User.query.all() if current_user.is_admin else None
    permissions = CollectionPermission.query.filter_by(collection_id=id).all()
    invitations = CollectionInvitation.query.filter_by(collection_id=id, accepted_at=None).all()
    
    return render_template('manage_permissions.html', 
                         collection=collection, 
                         users=users, 
                         permissions=permissions,
                         invitations=invitations)

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

@collections_bp.route('/<int:id>/invite', methods=['POST'])
@login_required
def invite_user(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    email = request.form['email'].strip().lower()
    permission_level = request.form['permission_level']
    
    # Check if user already has permission
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        existing_permission = CollectionPermission.query.filter_by(
            user_id=existing_user.id,
            collection_id=id
        ).first()
        if existing_permission:
            flash('User already has permission to this collection.')
            return redirect(url_for('collections.manage_permissions', id=id))
    
    # Check if invitation already exists
    existing_invitation = CollectionInvitation.query.filter_by(
        email=email,
        collection_id=id,
        accepted_at=None
    ).first()
    
    if existing_invitation:
        # Update existing invitation
        existing_invitation.permission_level = permission_level
        existing_invitation.invited_by = current_user.id
        existing_invitation.created_at = datetime.utcnow()
        existing_invitation.expires_at = datetime.utcnow() + timedelta(days=7)
        flash('Invitation updated and resent!')
    else:
        # Create new invitation
        invitation = CollectionInvitation(
            collection_id=id,
            invited_by=current_user.id,
            email=email,
            permission_level=permission_level
        )
        db.session.add(invitation)
        flash('Invitation sent successfully!')
    
    try:
        db.session.commit()
        # TODO: Send email notification here
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending invitation: {str(e)}')
    
    return redirect(url_for('collections.manage_permissions', id=id))

@collections_bp.route('/accept_invitation/<token>')
def accept_invitation(token):
    invitation = CollectionInvitation.query.filter_by(token=token).first_or_404()
    
    if invitation.is_expired:
        flash('This invitation has expired.')
        return redirect(url_for('main.index'))
    
    if invitation.is_accepted:
        flash('This invitation has already been accepted.')
        return redirect(url_for('main.index'))
    
    if current_user.is_authenticated:
        # User is logged in, check if email matches
        if current_user.email.lower() != invitation.email.lower():
            flash('This invitation is for a different email address.')
            return redirect(url_for('main.index'))
        
        # Accept the invitation
        try:
            # Check if user already has permission (edge case)
            existing_permission = CollectionPermission.query.filter_by(
                user_id=current_user.id,
                collection_id=invitation.collection_id
            ).first()
            
            if existing_permission:
                existing_permission.permission_level = invitation.permission_level
            else:
                permission = CollectionPermission(
                    user_id=current_user.id,
                    collection_id=invitation.collection_id,
                    permission_level=invitation.permission_level
                )
                db.session.add(permission)
            
            invitation.accepted_at = datetime.utcnow()
            invitation.accepted_by = current_user.id
            
            db.session.commit()
            flash('Invitation accepted successfully!')
            return redirect(url_for('collections.view_collection', id=invitation.collection_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error accepting invitation: {str(e)}')
            return redirect(url_for('main.index'))
    else:
        # User not logged in, redirect to register/login with invitation context
        return render_template('accept_invitation.html', invitation=invitation)

@collections_bp.route('/accept_invitation/<token>/register', methods=['POST'])
def accept_invitation_register(token):
    invitation = CollectionInvitation.query.filter_by(token=token).first_or_404()
    
    if invitation.is_expired or invitation.is_accepted:
        flash('This invitation is no longer valid.')
        return redirect(url_for('main.index'))
    
    # Check if user with this email already exists
    existing_user = User.query.filter_by(email=invitation.email).first()
    if existing_user:
        flash('An account with this email already exists. Please log in instead.')
        return redirect(url_for('auth.login'))
    
    username = request.form['username']
    password = request.form['password']
    
    # Create new user
    try:
        user = User(
            username=username,
            email=invitation.email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create permission
        permission = CollectionPermission(
            user_id=user.id,
            collection_id=invitation.collection_id,
            permission_level=invitation.permission_level
        )
        db.session.add(permission)
        
        # Mark invitation as accepted
        invitation.accepted_at = datetime.utcnow()
        invitation.accepted_by = user.id
        
        db.session.commit()
        
        flash('Account created and invitation accepted successfully! Please log in.')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating account: {str(e)}')
        return render_template('accept_invitation.html', invitation=invitation)

@collections_bp.route('/<int:id>/cancel_invitation/<int:invitation_id>')
@login_required
def cancel_invitation(id, invitation_id):
    collection = Collection.query.get_or_404(id)
    invitation = CollectionInvitation.query.get_or_404(invitation_id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage invitations for this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    db.session.delete(invitation)
    db.session.commit()
    
    flash('Invitation cancelled successfully!')
    return redirect(url_for('collections.manage_permissions', id=id))

@collections_bp.route('/<int:id>/join', methods=['POST'])
@login_required
def join_collection(id):
    """Allow users to join public collections with read permissions"""
    collection = Collection.query.get_or_404(id)
    
    # Check if collection is public
    if not collection.is_public:
        flash('This collection is private and cannot be joined directly.')
        return redirect(url_for('main.dashboard'))
    
    # Check if user already has permission
    existing_permission = CollectionPermission.query.filter_by(
        user_id=current_user.id,
        collection_id=id
    ).first()
    
    if existing_permission:
        flash('You already have access to this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    # Check if user is the creator
    if collection.created_by == current_user.id:
        flash('You are the creator of this collection.')
        return redirect(url_for('collections.view_collection', id=id))
    
    try:
        # Add read permission for the user
        permission = CollectionPermission(
            user_id=current_user.id,
            collection_id=id,
            permission_level='read'
        )
        db.session.add(permission)
        db.session.commit()
        
        flash(f'Successfully joined "{collection.name}" with read access!')
        return redirect(url_for('collections.view_collection', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error joining collection: {str(e)}')
        return redirect(url_for('main.dashboard'))

@collections_bp.route('/<int:id>/leave', methods=['POST'])
@login_required
def leave_collection(id):
    """Allow users to leave any collection, including their own"""
    collection = Collection.query.get_or_404(id)
    
    # Check if user has any relationship to this collection
    is_creator = collection.created_by == current_user.id
    user_permission = CollectionPermission.query.filter_by(
        user_id=current_user.id,
        collection_id=id
    ).first()
    
    if not is_creator and not user_permission:
        flash('You are not a member of this collection.')
        return redirect(url_for('main.dashboard'))
    
    try:
        if is_creator:
            # Owner is leaving - make collection unowned
            collection.created_by = None
            flash(f'You have left "{collection.name}". The collection is now unowned and can be claimed by other members.')
        
        # Remove user's permission if they have one
        if user_permission:
            db.session.delete(user_permission)
            if not is_creator:
                flash(f'You have left "{collection.name}".')
        
        db.session.commit()
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error leaving collection: {str(e)}')
        return redirect(url_for('collections.view_collection', id=id))

@collections_bp.route('/<int:id>/claim_ownership', methods=['POST'])
@login_required
def claim_ownership(id):
    """Allow members to claim ownership of unowned collections"""
    collection = Collection.query.get_or_404(id)
    
    # Check if collection is unowned
    if collection.created_by is not None:
        flash('This collection already has an owner.')
        return redirect(url_for('collections.view_collection', id=id))
    
    # Check if user has permission to the collection
    user_permission = CollectionPermission.query.filter_by(
        user_id=current_user.id,
        collection_id=id
    ).first()
    
    if not user_permission:
        flash('You must be a member of this collection to claim ownership.')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Set user as the new owner
        collection.created_by = current_user.id
        
        # Upgrade user's permission to admin if it's not already
        if user_permission.permission_level != 'admin':
            user_permission.permission_level = 'admin'
        
        db.session.commit()
        flash(f'You are now the owner of "{collection.name}"!')
        return redirect(url_for('collections.view_collection', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error claiming ownership: {str(e)}')
        return redirect(url_for('collections.view_collection', id=id))

@collections_bp.route('/<int:id>/transfer_ownership', methods=['POST'])
@login_required
def transfer_ownership(id):
    """Allow collection owner to transfer ownership to another member"""
    collection = Collection.query.get_or_404(id)
    
    # Only current owner can transfer ownership
    if collection.created_by != current_user.id:
        flash('You must be the owner to transfer ownership.')
        return redirect(url_for('collections.view_collection', id=id))
    
    new_owner_id = request.form.get('new_owner_id')
    if not new_owner_id:
        flash('Please select a new owner.')
        return redirect(url_for('collections.manage_permissions', id=id))
    
    try:
        new_owner_id = int(new_owner_id)
        
        # Check if the new owner has permission to the collection
        new_owner_permission = CollectionPermission.query.filter_by(
            user_id=new_owner_id,
            collection_id=id
        ).first()
        
        if not new_owner_permission:
            flash('The selected user is not a member of this collection.')
            return redirect(url_for('collections.manage_permissions', id=id))
        
        # Get the new owner user object for the flash message
        new_owner = User.query.get(new_owner_id)
        if not new_owner:
            flash('Selected user not found.')
            return redirect(url_for('collections.manage_permissions', id=id))
        
        # Transfer ownership
        collection.created_by = new_owner_id
        
        # Ensure new owner has admin permissions
        new_owner_permission.permission_level = 'admin'
        
        # Add current owner as a regular member with admin permissions
        current_owner_permission = CollectionPermission(
            user_id=current_user.id,
            collection_id=id,
            permission_level='admin'
        )
        db.session.add(current_owner_permission)
        
        db.session.commit()
        flash(f'Ownership of "{collection.name}" has been transferred to {new_owner.username}.')
        return redirect(url_for('collections.view_collection', id=id))
        
    except ValueError:
        flash('Invalid user selection.')
        return redirect(url_for('collections.manage_permissions', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error transferring ownership: {str(e)}')
        return redirect(url_for('collections.manage_permissions', id=id))

@collections_bp.route('/discover')
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
