#!/usr/bin/env python3
import os
import random
import string
import re
import json
import uuid

import httplib2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from werkzeug.utils import secure_filename
from flask import (Flask, request, render_template, redirect, url_for, flash,
                   jsonify, abort, make_response, send_from_directory)
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import serversidesession
from model import Base, Category, Item, User

# Set Upload folder and allowed file extentions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Load OAuth Client Secrets from JSON files
GOOGLE_CLIENT_SECRET_FILE = 'google_client_secrets.json'
GOOGLE_CLIENT_ID = json.loads(open(GOOGLE_CLIENT_SECRET_FILE, 'r').read())['web']['client_id']  # noqa
FB_APP_ID = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']  # noqa
FB_APP_SECRET = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']  # noqa
FB_REDIRECT_URI = json.loads(open('fb_client_secrets.json', 'r').read())['web']['redirect_uri']  # noqa

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# app.session_interface = serversidesession.RedisSessionInterface()
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    SESSION_INTERFACE=serversidesession.RedisSessionInterface()
))


# HTML endpoints for Authentication & Authorization
@app.route('/login')
def show_login():
    is_logged_in = 'username' in login_session
    # Create anti-forgery state token
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', is_logged_in=is_logged_in,
                           GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID,
                           GOOGLE_REDIRECT=url_for('show_all_items'),
                           FB_APP_ID=FB_APP_ID,
                           FB_REDIRECT_URI=FB_REDIRECT_URI,
                           STATE=state)


@app.route('/logout')
def logout():
    stored_provider = login_session.get('provider')
    if stored_provider is None:
        flash('Current user not connected.')
        return redirect(url_for('show_all_items'))
    elif stored_provider == 'google+':
        return redirect(url_for('gdisconnect'))
    elif stored_provider == 'facebook':
        return redirect(url_for('fbdisconnect'))
    abort(500)


# Facebook OAuth endpoints
@app.route('/fbconnect')
def fbconnect():
    # Validate anti-forgery state token
    if request.args.get('state') != login_session['state']:
        abort(401, 'Invalid state parameter.')

    # When error occurs (e.g. user denies access to facebook account)
    if request.args.get('error') is not None:
        abort(500, request.args.get('error'))

    # Get Facebook access token using authorization code
    authorization_code = request.args.get('code')
    url = 'https://graph.facebook.com/v2.10/oauth/access_token?'
    url += 'client_id=%s' % FB_APP_ID
    url += '&client_secret=%s' % FB_APP_SECRET
    url += '&code=%s' % authorization_code
    url += '&redirect_uri=%s' % FB_REDIRECT_URI
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    result = json.loads(response.decode('utf-8'))
    access_token = result.get('access_token')
    if result.get('error') is not None:
        # If there was an error getting the access token, abort.
        abort(500, result.get('error'))

    # Get application access token before inspecting user access token
    url = 'https://graph.facebook.com/v2.10/oauth/access_token?'
    url += 'client_id=%s' % FB_APP_ID
    url += '&client_secret=%s' % FB_APP_SECRET
    url += '&grant_type=client_credentials'
    response = h.request(url, 'GET')[1]
    result = json.loads(response.decode('utf-8'))
    app_token = result.get('access_token')
    if result.get('error') is not None:
        # If there was an error getting the app token, abort.
        abort(500, result.get('error'))

    # Inspect user access token
    url = 'https://graph.facebook.com/debug_token?'
    url += 'input_token=%s' % access_token
    url += '&access_token=%s' % app_token
    response = h.request(url, 'GET')[1]
    result = json.loads(response.decode('utf-8'))
    if result.get('error') is not None:
        # If there was an error inspecting the access token, abort.
        abort(500, result.get('error'))
    is_valid_token = result['data']['is_valid']
    issued_to_app = result['data']['app_id']
    issued_to_user = result['data']['user_id']
    if not is_valid_token:
        abort(401, 'Invalid Access Token')
    if issued_to_app != FB_APP_ID:
        abort(401, 'Token\'s client ID does not match app\'s.')

    # Get user data(name, id, email, picture) from Facebook
    url = 'https://graph.facebook.com/v2.8/me?fields=name,id,email,picture'
    url += '&access_token=%s' % access_token
    response = h.request(url, 'GET')[1]
    fb_user_data = json.loads(response.decode('utf-8'))
    facebook_user_id = fb_user_data.get('id')

    # Verify that the access token is used for the intended user.
    if issued_to_user != facebook_user_id:
        abort(401, 'Token\'s user ID doesn\'t match given user ID.')

    stored_provider = login_session.get('provider')
    stored_access_token = login_session.get('access_token')
    stored_id = login_session.get('id')

    # Check if user is already logged in
    if stored_access_token is not None:
        if stored_provider == 'facebook' and stored_id == facebook_user_id:
            flash('Current user is already connected.')
            return redirect(url_for('show_all_items'))

    # Store the access token, user data in the session
    login_session['provider'] = 'facebook'
    login_session['access_token'] = access_token
    login_session['username'] = fb_user_data.get('name')
    login_session['email'] = fb_user_data.get('email')
    login_session['picture'] = fb_user_data.get('picture')['data']['url']
    login_session['id'] = facebook_user_id

    # See if user exists, if it doesn't make a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash("you are now logged in as %s" % login_session['username'])
    return redirect(url_for('show_all_items'))


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session.get('id')
    access_token = login_session.get('access_token')
    # Only disconnect a connected user.
    if access_token is None:
        abort(401, 'Current user not connected.')
    # Revoke a current user's token
    url = 'https://graph.facebook.com/%s/permissions?' % facebook_id
    url += 'access_token=%s' % access_token
    h = httplib2.Http()
    response = h.request(url, 'DELETE')[1]
    is_success = json.loads(response.decode('utf-8')).get('success')

    if is_success:
        # Reset the user's sesson.
        del login_session['provider']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['id']
        flash('You are successfully disconnected.')
        return redirect(url_for('show_all_items'))
    else:
        abort(400, 'Failed to revoke token for given user.')


# Google+ OAuth endpoints
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate anti-forgery state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify if request have `X-Requested-With` header
    if not request.headers.get('X-Requested-With'):
        response = make_response(json.dumps('Forbidden'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    # Upgrade the authorization code into a credentials object
    try:
        oauth_flow = flow_from_clientsecrets(GOOGLE_CLIENT_SECRET_FILE,
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != GOOGLE_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_provider = login_session.get('provider')
    stored_access_token = login_session.get('access_token')
    stored_id = login_session.get('id')

    # Check if user is already logged in
    if stored_access_token is not None:
        if stored_provider == 'google+' and stored_id == gplus_id:
            response = make_response(json.dumps(
                'Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo?'
    userinfo_url += 'alt=json&access_token=%s' % access_token

    h = httplib2.Http()
    response = h.request(userinfo_url, 'GET')[1]
    str_response = response.decode('utf-8')
    data = json.loads(str_response)

    # Store the access token, user data in the session
    login_session['provider'] = 'google+'
    login_session['access_token'] = access_token
    login_session['username'] = data.get('name')
    login_session['email'] = data.get('email')
    login_session['picture'] = data.get('picture')
    login_session['id'] = gplus_id

    # See if user exists, if it doesn't make a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = 'Welcome, ' + login_session['username'] + '!'
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['provider']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['id']

        flash('You are successfully disconnected.')
        return redirect(url_for('show_all_items'))
    else:
        abort(400, 'Failed to revoke token for given user.')


# Routes for HTML endpoints
@app.route('/')
def redirect_to_all_category():
    return redirect(url_for('show_all_items'))


@app.route('/categories/all/')
def show_all_items():
    is_logged_in = 'username' in login_session
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Item).order_by(Item.id)
    return render_template('show_items.html', is_logged_in=is_logged_in,
                           categories=categories, items=items)


@app.route('/categories/<int:category_id>/')
def show_category_items(category_id):
    is_logged_in = 'username' in login_session
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template('show_items.html', is_logged_in=is_logged_in,
                           categories=categories, items=items)


@app.route('/search')
def search_items():
    is_logged_in = 'username' in login_session
    search_title = '%' + request.args.get('title') + '%'
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Item).filter(Item.name.ilike(search_title))
    return render_template('search.html', is_logged_in=is_logged_in,
                           categories=categories, items=items)


@app.route('/categories/new-item', methods=['GET', 'POST'])
def create_new_item():
    # Check if user is logged in
    is_logged_in = 'username' in login_session
    if not is_logged_in:
        flash('You should sign in to create a new item.')
        return redirect('/login')

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
        session.add(new_item)
        session.commit()
        flash('New Item %s Successfully Created' % new_item.name)

        return redirect(url_for('show_all_items'))
    else:
        categories = session.query(Category).order_by(Category.name)
        return render_template('new_item.html', is_logged_in=is_logged_in,
                               categories=categories)


@app.route('/categories/<int:category_id>/items/<int:item_id>/')
def show_item(category_id, item_id):
    is_logged_in = 'username' in login_session
    target_item = None
    category = None
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        target_item = session.query(Item).filter_by(category_id=category_id,
                                                    id=item_id).one()
    except Exception as e:
        abort(404)
    youtube_id = extract_youtube_id(target_item.youtube_trailer_url)
    return render_template('item_detail.html', is_logged_in=is_logged_in,
                           category=category,
                           item=target_item,
                           item_youtube_id=youtube_id)


@app.route('/categories/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    # Check if user is logged in
    is_logged_in = 'username' in login_session
    if not is_logged_in:
        flash('You should sign in to edit the item.')
        return redirect('/login')
    target_category = None
    target_item = None
    try:
        target_category = session.query(Category).filter_by(
            id=category_id).one()
        target_item = session.query(Item).filter_by(category_id=category_id,
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

        session.add(target_item)
        session.commit()
        category_id = target_item.category_id
        flash('%s Successfully Updated' % target_item.name)
        return redirect(url_for('show_item',
                                category_id=category_id, item_id=item_id))
    else:
        categories = session.query(Category).order_by(Category.name)
        return render_template('edit_item.html', is_logged_in=is_logged_in,
                               categories=categories,
                               target_category=target_category,
                               item=target_item)


@app.route('/categories/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    is_logged_in = 'username' in login_session
    if not is_logged_in:
        flash('You should sign in to delete the item.')
        return redirect('/login')
    target_category = None
    target_item = None
    try:
        target_category = session.query(Category).filter_by(
            id=category_id).one()
        target_item = session.query(Item).filter_by(category_id=category_id,
                                                    id=item_id).one()
    except Exception as e:
        abort(404)
    if request.method == 'POST':
        session.delete(target_item)
        session.commit()
        flash('%s Successfully Deleted' % target_item.name)
        return redirect(url_for('show_all_items'))
    else:
        return render_template('delete_item.html', is_logged_in=is_logged_in,
                               target_category=target_category,
                               item=target_item)


# Serving uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Routes for JSON endpoints
@app.route('/categories/all/JSON')
def jsonify_all_categories():
    try:
        categories = session.query(Category).order_by(Category.id)
        return jsonify(Categories=[category.serialize for category in categories])  # noqa
    except Exception as e:
        abort(404)


@app.route('/categories/all/items/JSON')
def jsonify_all_items():
    try:
        items = session.query(Item).order_by(Item.id)
        return jsonify(Items=[item.serialize for item in items])
    except Exception as e:
        abort(404)


@app.route('/categories/<int:category_id>/items/JSON')
def jsonify_category_items(category_id):
    try:
        items = session.query(Item).filter_by(
            category_id=category_id).all()
        return jsonify(Items=[item.serialize for item in items])
    except Exception as e:
        abort(404)


@app.route('/categories/<int:category_id>/items/<int:item_id>/JSON')
def jsonify_item(category_id, item_id):
    try:
        item = session.query(Item).filter_by(
            category_id=category_id, id=item_id).one()
        return jsonify(Item=item.serialize)
    except Exception as e:
        abort(404)


@app.route('/users/all/JSON')
def jsonify_all_users():
    try:
        users = session.query(User).order_by(User.id)
        return jsonify(Users=[user.serialize for user in users])
    except Exception as e:
        abort(404)


# Helper Functions
def is_valid_category_id(category_id):
    try:
        target_category = session.query(Category).filter_by(
            id=category_id).one()
        return True
    except NoResultFound:
        return False


def create_user(login_session):
    new_user = User(username=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_youtube_id(youtube_url):
    # Extract the youtube ID from the url
    youtube_id_match = re.search(r'(?<=v=)[^&#]+', youtube_url)
    youtube_id_match = youtube_id_match or re.search(
        r'(?<=be/)[^&#]+', youtube_url)
    return (youtube_id_match.group(0) if youtube_id_match else None)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.debug = True
    # Using server-side session to securely store user profile info
    app.session_interface = serversidesession.RedisSessionInterface()
    app.run(host='0.0.0.0', port=8000)
