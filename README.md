# Project: Item Catalog

The `Item Catalog` is a web application using the Python framework Flask implementing third-party OAuth authentication, [Google plus](https://developers.google.com/identity/protocols/OAuth2) and [Facebook](https://developers.facebook.com/docs/facebook-login/web) log-in. It provides a list of game items within a variety of genres as well as provide a user registration and authentication system.

- 한글 리드미(README Korean) 파일: [README_ko.md](/README_ko.md)

## Installation
Clone the github repository and install flask app as follow.

```
git clone https://github.com/YoungsAppWorkshop/itemcatalog
cd itemcatalog
sudo pip3 install -r requirements.txt
```

## How to Start
Since `Item Catalog` is implementing third-party OAuth authentication APIs from [Google](https://developers.google.com/identity/protocols/OAuth2) and [Facebook](https://developers.facebook.com/docs/facebook-login/web), client secrets of both services should be stored in JSON files.

1. Download Google client secrets file and store it in `instance/google_client_secrets.json` file.
2. Specify Facebook App ID and App Secret in the `instance/fb_client_secrets.json` file.

After including the API credentials in the client secrets files, the app can be started as:

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
    ├── instance
    │   ├── config.py               # Instance specific configurations  
    │   ├── fb_client_secrets.json
    │   └── google_client_secrets.json
    ├── uploads                     # User uploaded images
    │   ...
    ├── catalog.db                  # Sample database
    ├── config.py
    ├── README_ko.md
    ├── README.md                   # This file
    └── run.py                      # Run the application
```

## Accessing the JSON API
The `Item Catalog` provides a JSON API endpoint that users can easily find information about games registered. To access the API, you can browse `http://YOUR_SERVER_NAME/api`.

1. `/api/categories/all/` : Returns all games of all genres
2. `/api/categories/<int:category_id>/items/all/` : Returns all games of a genre
3. `/api/categories/<int:category_id>/items/<int:item_id>/` : Returns a game of a genre
3. `/api/users/all/` : Returns all users information

## Attributions
Below are the origins of source codes from others.
1. [Bootstrap Offcanvas example](https://v4-alpha.getbootstrap.com/examples/offcanvas/)  as starter code for HTML templates and CSS.
2. [Flask Uploading File pattern](http://flask.pocoo.org/docs/0.12/patterns/fileuploads/) for uploading featured images of items
3. [Google OAuth Sample code from Udacity](https://github.com/udacity/OAuth2.0)

## License
This app is [MIT licensed](/LICENSE).
