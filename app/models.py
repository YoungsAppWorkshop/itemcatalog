#!/usr/bin/env python3
from app import db


class Base(db.Model):
    """ Define a base model for other database tables to inherit"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class User(Base):
    """ Class for storing data related with a User

    Attributes:
        id: int. Primary key for DB
        username: string. Name of the user
        email: string. Email address of the user
        picture: string. Image Url for the user's profile image
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    picture = db.Column(db.String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'picture': self.picture
        }


class Category(Base):
    """ Class for storing data related with Category(genre of games)

    Attributes:
        id: int. Primary key for DB
        name: string. Name of genre
    """
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):
    """ Class for storing data related with an Item(game)

    Attributes:
        id: int. Primary key for DB
        name: string. Title of the game
        description: string. Short description of the game
        price: string. Price of the game
        image_url: string. Image URL for featured image of the game
        youtube_trailer_url: string. Youtube video URL for trailer movie
        category_id: int. Foreign Key related with category table
        user_id: int. Foreign Key related with user table
    """
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    image_url = db.Column(db.String(250))
    youtube_trailer_url = db.Column(db.String(250))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(Category)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'youtube_trailer_url': self.youtube_trailer_url,
            'category_id': self.category_id,
            'user_id': self.user_id
        }
