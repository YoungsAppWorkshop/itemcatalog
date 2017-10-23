import os

from flask import Flask, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

import serversidesession


app = Flask(__name__)


# Using server-side session to securely store user profile info
app.session_interface = serversidesession.RedisSessionInterface()

# Load default config and override config from an environment variable
app.config.from_object(os.environ['APP_SETTINGS'])

# Create a Database object
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable
from mod_api.controllers import mod_api as api_module
from mod_auth.controllers import mod_auth as auth_module
from mod_catalog.controllers import mod_catalog as catalog_module

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
