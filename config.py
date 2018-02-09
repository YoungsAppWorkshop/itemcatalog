# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

# Define the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'catalog.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Define API secret files for OAuth2 authentication
GOOGLE_CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'instance/google_client_secrets.json')  # noqa
FB_CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'instance/fb_client_secrets.json')  # noqa

# Define upload folder for users to upload images
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Secret key for signing cookies
SECRET_KEY = "YOUR_SECRET_KEY_HERE"
