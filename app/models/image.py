from datetime import datetime
from .. import db

class TextureImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filepath = db.Column(db.String(500), nullable=False)
    current_filepath = db.Column(db.String(500))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    modification_date = db.Column(db.DateTime)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    
    uploader = db.relationship('User', backref='uploaded_images')
    versions = db.relationship('ImageVersion', backref='image', lazy=True, cascade='all, delete-orphan')

class ImageVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('texture_image.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_current = db.Column(db.Boolean, default=False)
    data = db.Column(db.LargeBinary, nullable=False)
    uploader = db.relationship('User')
