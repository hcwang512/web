__author__ = 'hcwang'

from ._base import db, cache

__all__ = ['Book']

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bookname = db.Column(db.String, nullable=False, index=True)
    bookauthor = db.Column(db.String, nullable=False, index=True)
    stock = db.Column(db.Integer, default=0)
    borrow = db.Column(db.Integer, default=0)

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.bookname




