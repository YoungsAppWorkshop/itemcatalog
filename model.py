#!/usr/bin/env python3
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """ Class for storing data related with a User

    Attributes:
        id: int. Primary key for DB
        username: string. Name of the user
        email: string. Email address of the user
        picture: string. Image Url for the user's profile image
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False)
    email = Column(String(100), index=True, nullable=False)
    picture = Column(String(250))

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

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)

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

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    image_url = Column(String(250))
    youtube_trailer_url = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

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


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
