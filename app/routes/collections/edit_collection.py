from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ... import db
from ...models.collection import Collection
from ...utils.helpers import has_collection_permission


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


def register_route(app):
    """Register the edit_collection route with the Flask app"""
    app.add_url_rule('/collection/<int:id>/edit', 'collections.edit_collection', edit_collection, methods=['GET', 'POST'])
