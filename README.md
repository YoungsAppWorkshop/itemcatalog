# Project: Item Catalog

The project `Item Catalog` is a RESTful web application using the Python framework Flask implementing third-party OAuth authentication, Google plus and Facebook log-in. It provides a list of game items within a variety of genres as well as provide a user registration and authentication system.

Included files are:
* `application.py` : `Item Catalog` web application
* `model.py` : Database model for the application
* `google_client_secrets.json` : A JSON file storing client secrets of Google OAuth
* `fb_client_secrets.json` : A JSON file storing client secrets of Facebook OAuth
* `serversidesession.py` : A module which implements server-side session interface to the Flask framework
* `lotsofitem.py` : A python script which generates items and categories
* `static/` : Include static files - `.js`, `.css`, `.jpg`
* `templates/` : Include template files
* `uploads/` : User-uploaded files are stored here
* `README.md`

### Prepare to Start
Since `Item Catalog` is implementing third-party OAuth authentication APIs from Google and Facebook, you need to store client secrets of both services in JSON files.
1. Download Google client secrets file and rename it as `google_client_secrets.json` and store it in `/vagrant/catalog/` directory.
2. Specify Facebook App ID and App Secret in the `fb_client_secrets.json` file.

### How to Start
In your vagrant machine,
1. Change your working directory: `cd /vagrant/catalog`
2. Create database: `python3 model.py`
3. Populate some data to play with: `python3 lotsofitem.py`
4. Start the Redis server for server-side session interface: `redis-server &`
5. Start application: `python3 application.py`


### Code from external source
I used some of code from other websites while making this application. Here is the list of origins:
1. [Bootstrap Offcanvas example](https://v4-alpha.getbootstrap.com/examples/offcanvas/)  as my starter code for HTML templates and CSS.
2. [Flask Uploading File pattern](http://flask.pocoo.org/docs/0.12/patterns/fileuploads/) for uploading featured images of items
3. [Flask Snippet Server-side Session](http://flask.pocoo.org/snippets/75/) for securely storing user information in session
4. [Google OAuth Sample code from Udacity](https://github.com/udacity/OAuth2.0)
5. Nice and Handy [extract_youtube_id function](https://github.com/udacity/ud036_StarterCode/blob/master/fresh_tomatoes.py) from the Movie Trailer project

### License
This is a public domain work, dedicated using
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
# itemcatalog
