from datetime import datetime
from .. import db

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Now nullable for unowned collections
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_collections')
    images = db.relationship('TextureImage', backref='collection', lazy=True, cascade='all, delete-orphan')

class CollectionPermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False)  # 'read', 'write', 'admin'
    
    user = db.relationship('User', backref='collection_permissions')
    collection = db.relationship('Collection', backref='permissions')
