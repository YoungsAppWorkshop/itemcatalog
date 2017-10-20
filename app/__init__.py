import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import Flask, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

import app.serversidesession


app = Flask(__name__)


# Using server-side session to securely store user profile info
app.session_interface = serversidesession.RedisSessionInterface()
UPLOAD_FOLDER = 'uploads'
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///catalog.db',
    SECRET_KEY='development key',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=UPLOAD_FOLDER
))

# Create a Database object
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable
from app.mod_api.controllers import mod_api as api_module
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_catalog.controllers import mod_catalog as catalog_module

# Register blueprint(s)
app.register_blueprint(api_module)
app.register_blueprint(auth_module)
app.register_blueprint(catalog_module)


@app.route('/')
def redirect_to_all_category():
    return redirect(url_for('catalog.show_all_items'))


# Serving uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Build the database:
# This will create the database file using SQLAlchemy
# db.create_all()
