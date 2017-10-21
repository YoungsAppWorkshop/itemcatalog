#!/usr/bin/env python3
from flask import Blueprint, jsonify, abort

# Import the database object from the main app module
from app import db
from app.models import Category, Item, User


# Define the blueprint: 'api', set its url prefix: app.url/api
mod_api = Blueprint('api', __name__, url_prefix='/api')


# Routes for JSON endpoints
@mod_api.route('/categories/all/JSON')
def jsonify_all_categories():
    """Return all categories information in JSON"""
    try:
        categories = db.session.query(Category).order_by(Category.id)
        return jsonify(Categories=[category.serialize for category in categories])  # noqa
    except Exception as e:
        abort(404)


@mod_api.route('/categories/all/items/JSON')
def jsonify_all_items():
    """Return all items information in JSON"""
    try:
        items = db.session.query(Item).order_by(Item.id)
        return jsonify(Items=[item.serialize for item in items])
    except Exception as e:
        abort(404)


@mod_api.route('/categories/<int:category_id>/items/JSON')
def jsonify_category_items(category_id):
    """Return all items information of a category in JSON"""
    try:
        items = db.session.query(Item).filter_by(
            category_id=category_id).all()
        return jsonify(Items=[item.serialize for item in items])
    except Exception as e:
        abort(404)


@mod_api.route('/categories/<int:category_id>/items/<int:item_id>/JSON')
def jsonify_item(category_id, item_id):
    """Return an item information of a category in JSON"""
    try:
        item = db.session.query(Item).filter_by(
            category_id=category_id, id=item_id).one()
        return jsonify(Item=item.serialize)
    except Exception as e:
        abort(404)


@mod_api.route('/users/all/JSON')
def jsonify_all_users():
    """Return all users information in JSON"""
    try:
        users = db.session.query(User).order_by(User.id)
        return jsonify(Users=[user.serialize for user in users])
    except Exception as e:
        abort(404)
