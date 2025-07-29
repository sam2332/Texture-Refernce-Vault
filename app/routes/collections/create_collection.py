from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection


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


def register_route(app):
    """Register the create_collection route with the Flask app"""
    app.add_url_rule('/collection/create', 'collections.create_collection', create_collection, methods=['GET', 'POST'])
