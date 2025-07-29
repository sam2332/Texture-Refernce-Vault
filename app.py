from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import shutil
from PIL import Image
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///texture_vault.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    
    uploader = db.relationship('User')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Template context processor to make functions available in templates
@app.context_processor
def utility_processor():
    return dict(has_collection_permission=has_collection_permission)

# Helper functions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_dimensions(filepath):
    try:
        with Image.open(filepath) as img:
            return img.size
    except:
        return None, None

def has_collection_permission(user, collection, required_level='read'):
    if user.is_admin:
        return True
    if collection.created_by == user.id:
        return True
    
    permission = CollectionPermission.query.filter_by(
        user_id=user.id, 
        collection_id=collection.id
    ).first()
    
    if not permission:
        return False
    
    levels = {'read': 1, 'write': 2, 'admin': 3}
    return levels.get(permission.permission_level, 0) >= levels.get(required_level, 0)

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Make first user admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get collections user has access to
    if current_user.is_admin:
        collections = Collection.query.all()
    else:
        # Get collections user created or has permissions for
        created_collections = Collection.query.filter_by(created_by=current_user.id).all()
        permitted_collection_ids = [p.collection_id for p in current_user.collection_permissions]
        permitted_collections = Collection.query.filter(Collection.id.in_(permitted_collection_ids)).all()
        collections = list(set(created_collections + permitted_collections))
    
    return render_template('dashboard.html', collections=collections, current_time=datetime.utcnow())

@app.route('/collections')
@login_required
def collections():
    return redirect(url_for('dashboard'))

@app.route('/collection/create', methods=['GET', 'POST'])
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
        return redirect(url_for('view_collection', id=collection.id))
    
    return render_template('create_collection.html')

@app.route('/collection/<int:id>')
@login_required
def view_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this collection.')
        return redirect(url_for('dashboard'))
    
    images = TextureImage.query.filter_by(collection_id=id).all()
    return render_template('view_collection.html', collection=collection, images=images)

@app.route('/collection/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'admin'):
        flash('You do not have permission to edit this collection.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        collection.name = request.form['name']
        collection.description = request.form.get('description', '')
        db.session.commit()
        
        flash('Collection updated successfully!')
        return redirect(url_for('view_collection', id=collection.id))
    
    return render_template('edit_collection.html', collection=collection)

@app.route('/collection/<int:id>/delete')
@login_required
def delete_collection(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this collection.')
        return redirect(url_for('dashboard'))
    
    db.session.delete(collection)
    db.session.commit()
    
    flash('Collection deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/collection/<int:id>/upload', methods=['GET', 'POST'])
@login_required
def upload_image(id):
    collection = Collection.query.get_or_404(id)
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to upload to this collection.')
        return redirect(url_for('view_collection', id=id))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            file.save(filepath)
            
            # Get image dimensions
            width, height = get_image_dimensions(filepath)
            
            # Create image record
            image = TextureImage(
                filename=filename,
                original_filepath=request.form.get('original_path', ''),
                current_filepath=filepath,
                width=width,
                height=height,
                file_size=os.path.getsize(filepath),
                collection_id=id,
                uploaded_by=current_user.id
            )
            
            db.session.add(image)
            db.session.commit()
            
            # Create initial version
            version = ImageVersion(
                image_id=image.id,
                version_number=1,
                filepath=filepath,
                uploaded_by=current_user.id,
                is_current=True
            )
            
            db.session.add(version)
            db.session.commit()
            
            flash('Image uploaded successfully!')
            return redirect(url_for('view_collection', id=id))
        else:
            flash('Invalid file type. Please upload an image file.')
    
    return render_template('upload_image.html', collection=collection)

@app.route('/image/<int:id>')
@login_required
def view_image(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'read'):
        flash('You do not have permission to view this image.')
        return redirect(url_for('dashboard'))
    
    versions = ImageVersion.query.filter_by(image_id=id).order_by(ImageVersion.version_number.desc()).all()
    return render_template('view_image.html', image=image, collection=collection, versions=versions)

@app.route('/image/<int:id>/upload_version', methods=['POST'])
@login_required
def upload_version(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to upload versions to this collection.')
        return redirect(url_for('view_image', id=id))
    
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('view_image', id=id))
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file')
        return redirect(url_for('view_image', id=id))
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    file.save(filepath)
    
    # Get next version number
    last_version = ImageVersion.query.filter_by(image_id=id).order_by(ImageVersion.version_number.desc()).first()
    next_version = (last_version.version_number + 1) if last_version else 1
    
    # Mark all previous versions as not current
    ImageVersion.query.filter_by(image_id=id).update({'is_current': False})
    
    # Create new version
    version = ImageVersion(
        image_id=id,
        version_number=next_version,
        filepath=filepath,
        uploaded_by=current_user.id,
        is_current=True
    )
    
    db.session.add(version)
    
    # Update image with new dimensions and filepath
    width, height = get_image_dimensions(filepath)
    image.current_filepath = filepath
    image.width = width
    image.height = height
    image.file_size = os.path.getsize(filepath)
    
    db.session.commit()
    
    flash('New version uploaded successfully!')
    return redirect(url_for('view_image', id=id))

@app.route('/image/<int:id>/publish')
@login_required
def publish_image(id):
    image = TextureImage.query.get_or_404(id)
    collection = image.collection
    
    if not has_collection_permission(current_user, collection, 'write'):
        flash('You do not have permission to publish images in this collection.')
        return redirect(url_for('view_image', id=id))
    
    if not image.original_filepath:
        flash('No original filepath specified for this image.')
        return redirect(url_for('view_image', id=id))
    
    try:
        # Copy current version to original filepath
        current_version = ImageVersion.query.filter_by(image_id=id, is_current=True).first()
        if current_version:
            shutil.copy2(current_version.filepath, image.original_filepath)
            image.is_published = True
            db.session.commit()
            flash('Image published successfully!')
        else:
            flash('No current version found.')
    except Exception as e:
        flash(f'Error publishing image: {str(e)}')
    
    return redirect(url_for('view_image', id=id))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    collections = Collection.query.all()
    return render_template('admin.html', users=users, collections=collections)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/collection/<int:id>/permissions', methods=['GET', 'POST'])
@login_required
def manage_permissions(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('view_collection', id=id))
    
    users = User.query.all()
    permissions = CollectionPermission.query.filter_by(collection_id=id).all()
    return render_template('manage_permissions.html', collection=collection, users=users, permissions=permissions)

@app.route('/collection/<int:id>/add_permission', methods=['POST'])
@login_required
def add_permission(id):
    collection = Collection.query.get_or_404(id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('view_collection', id=id))
    
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
    return redirect(url_for('manage_permissions', id=id))

@app.route('/collection/<int:id>/remove_permission/<int:permission_id>')
@login_required
def remove_permission(id, permission_id):
    collection = Collection.query.get_or_404(id)
    permission = CollectionPermission.query.get_or_404(permission_id)
    
    if collection.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage permissions for this collection.')
        return redirect(url_for('view_collection', id=id))
    
    db.session.delete(permission)
    db.session.commit()
    
    flash('Permission removed successfully!')
    return redirect(url_for('manage_permissions', id=id))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.')
        return redirect(url_for('profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Password updated successfully!')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
