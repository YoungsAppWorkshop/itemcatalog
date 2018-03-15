# Project: Item Catalog

The `Item Catalog` is a web application using the Python framework Flask implementing third-party OAuth authentication, [Google plus](https://developers.google.com/identity/protocols/OAuth2) and [Facebook](https://developers.facebook.com/docs/facebook-login/web) log-in. It provides a list of game items within a variety of genres as well as provides a user registration and authentication system. This project is one of assignments for the [Udacity's Full Stack Web Developer Nanodegree program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

- 한글 리드미(README Korean) 파일: [README_ko.md](/README_ko.md)

## Demo
Demo Website URL: https://itemcatalog.youngsappworkshop.com

## Installation
Clone the github repository and install dependencies as follow.

```
git clone https://github.com/YoungsAppWorkshop/itemcatalog
cd itemcatalog
sudo pip3 install -r requirements.txt
```

## How to Start
Since `Item Catalog` is implementing third-party OAuth authentication APIs from [Google](https://developers.google.com/identity/protocols/OAuth2) and [Facebook](https://developers.facebook.com/docs/facebook-login/web), client secrets of both services should be stored in JSON files.

1. Download Google client secrets file and store it in `google_client_secrets.json` file.
2. Specify Facebook App ID and App Secret in the `fb_client_secrets.json` file.

After including the API credentials in the client secrets files, the app can be started with:

```
python3 run.py
```

## Structure of the app
```bash
└── itemcatalog
    ├── app
    │   ├── mod_api                 # JSON API module
    │   ├── mod_auth                # User authentication module
    │   ├── mod_catalog             # Catalog module
    │   ├── static
    │   ├── templates
    │   ├── __init__.py             # Base application
    │   └── models.py               # Database schema
    ├── uploads                     # User uploaded images
    │   ...
    ├── catalog.db                  # Sample database
    ├── config.py
    ├── fb_client_secrets.json      # Facebook OAuth2 credentials
    ├── google_client_secrets.json  # Google OAuth2 credentials
    ├── README_ko.md
    ├── README.md                   # This file
    └── run.py                      # Run the application
```

## Accessing to the JSON API
The `Item Catalog` provides a JSON API endpoint that users can easily find information about games registered. To access the API, you can browse `http://YOUR_SERVER_NAME/api`.

1. `/api/categories/all/` : Returns all games of all genres
2. `/api/categories/<int:category_id>/items/all/` : Returns all games of a genre
3. `/api/categories/<int:category_id>/items/<int:item_id>/` : Returns a game of a genre
3. `/api/users/all/` : Returns all users information

## Attributions

The `Item Catalog` app is built with [Flask](http://flask.pocoo.org/), [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/), [SQLAlchemy](https://www.sqlalchemy.org/), [Jinja2 Templates](http://jinja.pocoo.org/docs/2.10/), [httplib2](https://github.com/httplib2/httplib2), [oauth2client](https://github.com/google/oauth2client), [Bootstrap4](https://v4-alpha.getbootstrap.com/), and others. The below is the list of third-party sources which have been modified and used for the app:

1. [Flask Uploading File pattern](http://flask.pocoo.org/docs/0.12/patterns/fileuploads/) for uploading featured images of items
2. [Google OAuth Sample code from Udacity](https://github.com/udacity/OAuth2.0)

## License
This app is [MIT licensed](/LICENSE).
