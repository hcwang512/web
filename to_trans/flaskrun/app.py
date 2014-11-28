from flask import Flask
from flaskrun.handlers import cachetest
from flaskrun.models import db, cache

def createapp():
    app = Flask(__name__)
    app.register_blueprint(cachetest.bp, url_prefix='/book')
    db.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    return app

app = createapp()
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

if __name__ == '__main__':
    app.run()