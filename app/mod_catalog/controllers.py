#!/usr/bin/env python3
import os
import re
import uuid
from functools import wraps

from werkzeug.utils import secure_filename
from flask import (Blueprint, request, render_template, redirect, url_for,
                   flash, abort)
from flask import session as login_session

# Import the database object from the main app module
from app import db
from app.models import Category, Item


# Set Upload folder and allowed file extentions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Define the blueprint: 'catalog', set its url prefix: app.url/catalog
mod_catalog = Blueprint('catalog', __name__, url_prefix='/catalog',
                        template_folder='templates')


# Helper Functions
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            flash('You should sign in first.')
            return redirect(url_for('auth.show_login'))
        else:
            return func(*args, **kwargs)
    return wrapper


def is_valid_category_id(category_id):
    try:
        target_category = db.session.query(Category).filter_by(
            id=category_id).one()
        return True
    except Exception:
        return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_youtube_id(youtube_url):
    # Extract the youtube ID from the url
    youtube_id_match = re.search(r'(?<=v=)[^&#]+', youtube_url)
    youtube_id_match = youtube_id_match or re.search(
        r'(?<=be/)[^&#]+', youtube_url)
    return (youtube_id_match.group(0) if youtube_id_match else None)


# Routes for HTML endpoints
@mod_catalog.route('/categories/all/')
def show_all_items():
    is_logged_in = 'username' in login_session
    categories = db.session.query(Category).order_by(Category.name)
    items = db.session.query(Item).order_by(Item.id)
    return render_template('show_items.html',
                           is_logged_in=is_logged_in,
                           categories=categories, items=items)


@mod_catalog.route('/categories/<int:category_id>/')
def show_category_items(category_id):
    is_logged_in = 'username' in login_session
    categories = db.session.query(Category).order_by(Category.name)
    items = db.session.query(Item).filter_by(category_id=category_id)
    return render_template('show_items.html', is_logged_in=is_logged_in,
                           categories=categories, items=items)


@mod_catalog.route('/search')
def search_items():
    is_logged_in = 'username' in login_session
    search_title = '%' + request.args.get('title') + '%'
    categories = db.session.query(Category).order_by(Category.name)
    items = db.session.query(Item).filter(Item.name.ilike(search_title))
    return render_template('search.html', is_logged_in=is_logged_in,
                           categories=categories, items=items)


@mod_catalog.route('/categories/new-item', methods=['GET', 'POST'])
@login_required
def create_new_item():
    # Check if user is logged in
    is_logged_in = 'username' in login_session

    # If logged in, handle the request
    if request.method == 'POST':
        file = request.files['feature_image']

        # Check if Item's name is submitted
        if request.form['name'] == '':
            flash('Title of the game should be specified.')
            return redirect(request.url)

        # Check if Youtube URL is properly submitted
        if extract_youtube_id(request.form['youtube_url']) is None:
            flash('Invalid Youtube URL. Check Trailer\'s URL.')
            return redirect(request.url)

        # Save Featured Image if submitted
        if file and allowed_file(file.filename):
            # Make sure if filename is safe and unique
            filename = secure_filename(file.filename)
            filename = filename.rsplit('.', 1)[0] + '_' + uuid.uuid4().hex + '.' + filename.rsplit('.', 1)[1]  # noqa
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Featured Image(JPG/JPEG, PNG, GIF) required. ')
            return redirect(request.url)

        item_name = request.form['name']
        item_description = request.form['description']
        item_price = '$ 0.0' if request.form['price'] == '' else request.form['price']  # noqa
        item_image_url = url_for('uploaded_file', filename=filename)
        item_youtube_url = request.form['youtube_url']
        item_category_id = request.form['category']

        # Validate category id
        if not is_valid_category_id(item_category_id):
            flash('Invalid Category')
            return redirect(request.url)
        item_user_id = get_user_id(login_session.get('email'))

        # Store in database
        new_item = Item(name=item_name, description=item_description,
                        price=item_price, image_url=item_image_url,
                        youtube_trailer_url=item_youtube_url,
                        user_id=item_user_id,
                        category_id=item_category_id)
        db.session.add(new_item)
        db.session.commit()
        flash('New Item %s Successfully Created' % new_item.name)

        return redirect(url_for('catalog.show_all_items'))
    else:
        categories = db.session.query(Category).order_by(Category.name)
        return render_template('new_item.html', is_logged_in=is_logged_in,
                               categories=categories)


@mod_catalog.route('/categories/<int:category_id>/items/<int:item_id>/')
def show_item(category_id, item_id):
    is_logged_in = 'username' in login_session
    target_item = None
    category = None
    try:
        category = db.session.query(Category).filter_by(id=category_id).one()
        target_item = db.session.query(Item).filter_by(category_id=category_id,
                                                       id=item_id).one()
    except Exception as e:
        abort(404)
    youtube_id = extract_youtube_id(target_item.youtube_trailer_url)
    return render_template('item_detail.html', is_logged_in=is_logged_in,
                           category=category,
                           item=target_item,
                           item_youtube_id=youtube_id)


@mod_catalog.route('/categories/<int:category_id>/items/<int:item_id>/edit',
                   methods=['GET', 'POST'])
@login_required
def edit_item(category_id, item_id):
    # Check if user is logged in
    is_logged_in = 'username' in login_session
    target_category = None
    target_item = None
    try:
        target_category = db.session.query(Category).filter_by(
            id=category_id).one()
        target_item = db.session.query(Item).filter_by(category_id=category_id,
                                                       id=item_id).one()
    except Exception as e:
        abort(404)
    # Handle the request
    if request.method == 'POST':
        file = request.files['feature_image']

        # If nothing is submitted, don't change
        if request.form['name'] != '':
            target_item.name = request.form['name']
        if request.form['description'] != '':
            target_item.description = request.form['description']
        if request.form['price'] != '':
            target_item.price = request.form['price']
        if request.form['category'] != '':
            if not is_valid_category_id(request.form['category']):
                flash('Invalid Category')
                return redirect(request.url)
            target_item.category_id = request.form['category']
        if file and file.filename != '':
            if allowed_file(file.filename):
                # Make sure if filename is safe and unique
                filename = secure_filename(file.filename)
                filename = filename.rsplit('.', 1)[0] + '_' + uuid.uuid4().hex + '.' + filename.rsplit('.', 1)[1]  # noqa
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                target_item.image_url = url_for('uploaded_file',
                                                filename=filename)
            else:
                flash('Invalid file type. JPG/JPEG, PNG, GIF file allowed. ')
                return redirect(request.url)
        # Check if Youtube URL is properly submitted
        if request.form['youtube_url'] != '':
            if extract_youtube_id(request.form['youtube_url']) is None:
                flash('Invalid Youtube URL')
                return redirect(request.url)
            target_item.youtube_url = request.form['youtube_url']

        db.session.add(target_item)
        db.session.commit()
        category_id = target_item.category_id
        flash('%s Successfully Updated' % target_item.name)
        return redirect(url_for('catalog.show_item',
                                category_id=category_id, item_id=item_id))
    else:
        categories = db.session.query(Category).order_by(Category.name)
        return render_template('edit_item.html', is_logged_in=is_logged_in,
                               categories=categories,
                               target_category=target_category,
                               item=target_item)


@mod_catalog.route('/categories/<int:category_id>/items/<int:item_id>/delete',
                   methods=['GET', 'POST'])
@login_required
def delete_item(category_id, item_id):
    is_logged_in = 'username' in login_session
    target_category = None
    target_item = None
    try:
        target_category = db.session.query(Category).filter_by(
            id=category_id).one()
        target_item = db.session.query(Item).filter_by(category_id=category_id,
                                                       id=item_id).one()
    except Exception as e:
        abort(404)
    if request.method == 'POST':
        db.session.delete(target_item)
        db.session.commit()
        flash('%s Successfully Deleted' % target_item.name)
        return redirect(url_for('catalog.show_all_items'))
    else:
        return render_template('delete_item.html', is_logged_in=is_logged_in,
                               target_category=target_category,
                               item=target_item)
