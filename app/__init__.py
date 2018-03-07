import os

from flask import Flask, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

# To load configuration variables from an instance folder, uncomment the below
# The instance folder can be used to store sensitive informations such as
# API secrets, DB URIs or to define a configuration specific for the instance
app = Flask(__name__, instance_relative_config=True)
# app = Flask(__name__)


# Load default config
app.config.from_object('config')

# To load configuration variables from an instance folder, uncomment the below
app.config.from_pyfile('config.py')


# Create a Database object
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable
from .mod_api.controllers import mod_api as api_module
from .mod_auth.controllers import mod_auth as auth_module
from .mod_catalog.controllers import mod_catalog as catalog_module

# Register blueprint(s)
app.register_blueprint(api_module)
app.register_blueprint(auth_module)
app.register_blueprint(catalog_module)


# Default route
@app.route('/')
def redirect_to_all_category():
    """ Redirect to show_all_items function"""

    return redirect(url_for('catalog.show_all_items'))


# Serving uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """ Serving uploaded files"""

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
