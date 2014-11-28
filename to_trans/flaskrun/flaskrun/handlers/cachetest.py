__author__ = 'hcwang'

from ..models._base import cache
from ..models.book import Book
from flask import Blueprint
from time import ctime
import random

__all__ = ['bp']

bp = Blueprint('cache', __name__)


@bp.route('/')
@cache.memoize(timeout=50)
def randcache():
    return '%s' % random.randrange(1, 100)

@bp.route('/name/<name>')
@cache.memoize(50)
def getname(name):
    return '<h1>your name is %s, and the time is %s<h1>' % (name, ctime())

@bp.route('/<int:id>')
@cache.memoize(50)
def getbook(id):
    book = Book.query.filter_by(id=id)
    return '<h1>the book is %s<h1>' % book






