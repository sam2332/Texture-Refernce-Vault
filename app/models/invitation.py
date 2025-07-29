from datetime import datetime, timedelta
from .. import db
import uuid

class CollectionInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False)  # 'read', 'write', 'admin'
    token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    accepted_at = db.Column(db.DateTime, nullable=True)
    accepted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    collection = db.relationship('Collection', backref='invitations')
    inviter = db.relationship('User', foreign_keys=[invited_by], backref='sent_invitations')
    accepter = db.relationship('User', foreign_keys=[accepted_by], backref='accepted_invitations')
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_accepted(self):
        return self.accepted_at is not None
    
    @property
    def is_valid(self):
        return not self.is_expired and not self.is_accepted
