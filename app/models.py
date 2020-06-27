from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, backref
from app.database import db


#
# BlogPost
#   Name: a string for the title
#
#   Category: a foreign key linking the blog to a specific blog
#       category
#
#   ID: An auto incrimented numerical ID
#
#   Content: The html that will be displayed
#
class Post(db.Model) :
    """
    Create Posts Table
    """

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    content = Column(Text())

    # relation to category
    category_id = Column(Integer, ForeignKey('post_categories.id'), nullable=False)

    category = relationship('PostCategory', backref=backref('posts', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.name

#
# PostCategory
#   ID: An auto incrimented numerical ID
#   Name: A string to hold the name of the category
#
# Note: Each entry can be linked to many blogs
#
class PostCategory(db.Model) :
    """
    Create Categories table For Posts
    """

    __tablename__ = 'post_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)

    def __repr__(self):
        return '<PostCategory %r>' % self.name


#
# Worksheet
#   ID: An auto incrimented numerical ID
#   name: a location in which the website knows to look to find the
#       pdf-file to serve
#   data: a large binary column to hold the pdf data
#   author: foreign key designated to what author created it
#   Category: a foreign key that signifies what category the worksheet belongs to
#
class Worksheet(db.Model) :
    """
    Create Posts Table
    """

    __tablename__ = 'worksheets'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    pdf_url = Column(String(300), default=None, nullable=True)
    video_url = Column(String(300), default=None, nullable=True)

    # relation to category
    category_id = Column(Integer, ForeignKey('worksheet_categories.id'), nullable=False)

    category = relationship('WorksheetCategory', backref=backref('worksheets', lazy=True))

    # relation to author
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)

    author = relationship('Author', backref=backref('worksheets', lazy=True))

    def __repr__(self):
        return '<Worksheet %r>' % self.name


#
# Worksheet Category
#   ID: An auto incrimented numerical ID
#   name: A string to hold the name of the category
#
# Note: Each entry can be linked to many worksheets
#
class WorksheetCategory(db.Model) :
    """
    Create Categories table For Worksheet Categories
    """

    __tablename__ = 'worksheet_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)

    def __repr__(self):
        return '<WorksheetCategory %r>' % self.name


#
# Author
#   name: the name of the author
#   ID: An auto incrimented numerical ID
#
#   email: a string containing the authors email
#   about: a large string containing a few words about the author
#
# Note: Each entry can be linked to many worksheets
#
class Author(db.Model) :
    """
    Create Author table
    """

    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    email = Column(String(64), default=None, nullable=True)
    about = Column(String(1200), default=None, nullable=True)
    screenname = Column(String(64), default=None, nullable=True, unique=True)
    password = Column(String(200), nullable=False)

    def __repr__(self):
        return '<Author %r>' % self.name
