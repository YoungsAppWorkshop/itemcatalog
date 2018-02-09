#!/usr/bin/env python3
import random
import string
import json

import httplib2

from flask import (request, render_template, redirect, url_for, flash,
                   Blueprint, abort, make_response)
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Import the database object from the main app module
from .. import app, db
from ..models import User


# Load OAuth Client Secrets from JSON files
GOOGLE_API_SECRET_FILE = app.config['GOOGLE_CLIENT_SECRET_FILE']
FB_API_SECRET_FILE = app.config['FB_CLIENT_SECRET_FILE']

GOOGLE_CLIENT_ID = json.loads(open(GOOGLE_API_SECRET_FILE, 'r').read())['web']['client_id']  # noqa
FB_APP_ID = json.loads(open(FB_API_SECRET_FILE, 'r').read())['web']['app_id']  # noqa
FB_APP_SECRET = json.loads(open(FB_API_SECRET_FILE, 'r').read())['web']['app_secret']  # noqa
FB_REDIRECT_URI = json.loads(open(FB_API_SECRET_FILE, 'r').read())['web']['redirect_uri']  # noqa


# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth',
                     template_folder='templates')


# HTML endpoints for Authentication & Authorization
@mod_auth.route('/login')
def show_login():
    """ Create an anti-forgery token and show login page"""

    is_logged_in = 'username' in login_session
    # Create anti-forgery state token
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', is_logged_in=is_logged_in,
                           GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID,
                           GOOGLE_REDIRECT=url_for('catalog.show_all_items'),
                           FB_APP_ID=FB_APP_ID,
                           FB_REDIRECT_URI=FB_REDIRECT_URI,
                           STATE=state)


@mod_auth.route('/logout')
def logout():
    """ Check if the user is logged in, and redirect to disconnect functions
        according to the OAuth provider
    """

    stored_provider = login_session.get('provider')
    if stored_provider is None:
        flash('Current user not connected.')
        return redirect(url_for('catalog.show_all_items'))
    elif stored_provider == 'google+':
        return redirect(url_for('auth.gdisconnect'))
    elif stored_provider == 'facebook':
        return redirect(url_for('auth.fbdisconnect'))
    abort(500)


# Facebook OAuth endpoints
@mod_auth.route('/fbconnect')
def fbconnect():
    """ Facebook OAuth Authentication function.
        Authenticate the user using authorization code, get the user info
        from Facebook, and create login_session object.
    """
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
            return redirect(url_for('catalog.show_all_items'))

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
    return redirect(url_for('catalog.show_all_items'))


@mod_auth.route('/fbdisconnect')
def fbdisconnect():
    """ Revoke Facebook OAuth token and delete login_session object.
    """

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
        return redirect(url_for('catalog.show_all_items'))
    else:
        abort(400, 'Failed to revoke token for given user.')


# Google+ OAuth endpoints
@mod_auth.route('/gconnect', methods=['POST'])
def gconnect():
    """ Google OAuth Authentication function.
        Authenticate the user using authorization code, get the user info
        from Google, and create login_session object.
    """

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
        oauth_flow = flow_from_clientsecrets(GOOGLE_API_SECRET_FILE,
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


@mod_auth.route('/gdisconnect')
def gdisconnect():
    """ Revoke Google OAuth token and delete login_session object.
    """

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
        return redirect(url_for('catalog.show_all_items'))
    else:
        abort(400, 'Failed to revoke token for given user.')


# Helper Functions
def create_user(login_session):
    """ Create a new user and store data in database"""

    new_user = User(username=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    db.session.add(new_user)
    db.session.commit()
    user = db.session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """ Get user information from database"""

    user = db.session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    """ Get user_id using email"""

    try:
        user = db.session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None
