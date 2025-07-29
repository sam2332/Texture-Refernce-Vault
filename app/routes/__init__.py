def register_routes(app):
    """Register all individual routes with the Flask app"""
    # Import and register auth routes
    from .auth.register import register_route as register_auth_register
    from .auth.login import register_route as register_auth_login
    from .auth.logout import register_route as register_auth_logout
    from .auth.profile import register_route as register_auth_profile
    from .auth.change_password import register_route as register_auth_change_password
    
    register_auth_register(app)
    register_auth_login(app)
    register_auth_logout(app)
    register_auth_profile(app)
    register_auth_change_password(app)
    
    # Import and register main routes
    from .main.index import register_route as register_main_index
    from .main.dashboard import register_route as register_main_dashboard
    from .main.admin import register_route as register_main_admin
    
    register_main_index(app)
    register_main_dashboard(app)
    register_main_admin(app)
    
    # Import and register collection routes
    from .collections.create_collection import register_route as register_collections_create_collection
    from .collections.view_collection import register_route as register_collections_view_collection
    from .collections.edit_collection import register_route as register_collections_edit_collection
    from .collections.delete_collection import register_route as register_collections_delete_collection
    from .collections.manage_permissions import register_route as register_collections_manage_permissions
    from .collections.add_permission import register_route as register_collections_add_permission
    from .collections.remove_permission import register_route as register_collections_remove_permission
    from .collections.invite_user import register_route as register_collections_invite_user
    from .collections.accept_invitation import register_route as register_collections_accept_invitation
    from .collections.accept_invitation_register import register_route as register_collections_accept_invitation_register
    from .collections.cancel_invitation import register_route as register_collections_cancel_invitation
    from .collections.join_collection import register_route as register_collections_join_collection
    from .collections.leave_collection import register_route as register_collections_leave_collection
    from .collections.claim_ownership import register_route as register_collections_claim_ownership
    from .collections.transfer_ownership import register_route as register_collections_transfer_ownership
    from .collections.discover_collections import register_route as register_collections_discover_collections
    
    register_collections_create_collection(app)
    register_collections_view_collection(app)
    register_collections_edit_collection(app)
    register_collections_delete_collection(app)
    register_collections_manage_permissions(app)
    register_collections_add_permission(app)
    register_collections_remove_permission(app)
    register_collections_invite_user(app)
    register_collections_accept_invitation(app)
    register_collections_accept_invitation_register(app)
    register_collections_cancel_invitation(app)
    register_collections_join_collection(app)
    register_collections_leave_collection(app)
    register_collections_claim_ownership(app)
    register_collections_transfer_ownership(app)
    register_collections_discover_collections(app)
    
    # Import and register image routes
    from .images.upload_image import register_route as register_images_upload_image
    from .images.view_image import register_route as register_images_view_image
    from .images.edit_image import register_route as register_images_edit_image
    from .images.upload_version import register_route as register_images_upload_version
    from .images.publish_image import register_route as register_images_publish_image
    from .images.restore_version import register_route as register_images_restore_version
    from .images.serve_image import register_route as register_images_serve_image
    from .images.serve_version import register_route as register_images_serve_version
    
    register_images_upload_image(app)
    register_images_view_image(app)
    register_images_edit_image(app)
    register_images_upload_version(app)
    register_images_publish_image(app)
    register_images_restore_version(app)
    register_images_serve_image(app)
    register_images_serve_version(app)

__all__ = ['register_routes']
