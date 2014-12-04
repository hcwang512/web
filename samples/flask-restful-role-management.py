# coding=utf-8
from flask import Flask, request, abort, flash, redirect, url_for, session
from flask.ext.restful import Resource, Api
from flask import jsonify
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user, AnonymousUserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps
from flask.ext.script import Manager, Shell
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['DEBUG'] = True
api = Api(app)
db = SQLAlchemy(app)
login_manager = LoginManager()

login_manager.login_view = "login"
login_manager.session_protection = 'strong'
login_manager.init_app(app)
todos = {}


class User( UserMixin, db.Model):
    """
    用户类，用户有唯一的角色，代表其权限
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    name = db.Column(db.String(64), nullable=False, unique=True)
    password=db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '[id=%r, name=%r, password=%r, role_id=%r]' % (self.id, self.name, self.password, self.role_id)

    def can(self, permission):
        """
        判断用户是否有某一权限
        :param permission:
        :return:
        """

        print("can", self.role)
        #print('Roles', Role.query.all())
        return self.role is not None and self.role.permissions&permission==permission


class AnonymousUser(AnonymousUserMixin):
    """
    匿名用户，实现can，防止抛出异常
    """
    def can(self, permission):
        return False


login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    """
    用户的角色
    """
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    permissions = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '[id=%r, permissions=%d]' %(self.id, self.permissions)

@login_manager.user_loader
def load_user(userid):
    print 'loading user:' + userid + "   "+ User.query.get(userid)
    return User.query.filter_by(id=userid).first().id

def permission_required(permission):
    """
    装饰器，判断是否具有某一权限，无权限则abort
    :param permission:
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("permission required" )
            #print(current_user)
            print(session.get('userid'))
            user = User.query.filter_by(id=session.get('userid')).first()
            #user = current_user
            print(user)
            if not user or not user.can(permission):
                print("无权限")
                abort(403)
            print("有权限")
            return f(*args, **kwargs)
        return decorated_function
    return decorator



class Permission():
    """
    不同的http方法要求不同的权限
    """
    GET = 0b1
    POST = 0b10
    PUT = 0b100
    DELETE = 0b1000

def add_role():
    """
    向数据库中插入角色数据
    :return:
    """
    #print("增加")
    roles = {
        'guest': Permission.GET,
        'user': Permission.GET|Permission.POST,
        'moderate': Permission.GET|Permission.POST|Permission.PUT,
        'admin': Permission.GET|Permission.POST|Permission.PUT|Permission.DELETE
    }
    db.session.add

    db.session.add(Role(id=1, name='guest', permissions=roles.get('guest')))
    db.session.add(Role(id=2, name='user', permissions=roles.get('user')))
    db.session.add(Role(id=3, name='moderate', permissions=roles.get('moderate')))
    db.session.add(Role(id=4, name='admin', permissions=roles.get('admin')))
    db.session.commit()
    print(Role.query.all())

def add_user():
    """
    向用户数据库中插入数据
    :return:
    """
    guest = User(name='guest', password='guest', role_id=1)
    user = User(name='user', password='user',role_id=2)
    moderator = User(name='moderator', password='moderator', role_id=3)
    admin = User(name='admin', password='admin', role_id=4)
    db.session.add(guest)
    db.session.add(user)
    db.session.add(moderator)
    db.session.add(admin)
    db.session.commit()
    print(User.query.all())


class TodoSimple(Resource):
    """
    继承Resource， 相应的方法需要相应的权限
    """
    @permission_required(Permission.GET)
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    @permission_required(Permission.PUT)
    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return jsonify({todo_id: todos[todo_id]})

    @permission_required(Permission.DELETE)
    def delete(self, todo_id):
        del todos[todo_id]


api.add_resource(TodoSimple, '/hello/<todo_id>')

@app.route('/login/<name>/<password>', methods=['POST', 'GET'])
def login(name, password):
    user = User.query.filter_by(name=name).first()
    print(user)
    if user is not None and user.password == password:
        session['userid'] = user.id
        login_user(user, remember=True, force=True)
        return 'you have logged in, %r' % current_user
    flash('try again')
    return 'invalid password or username'

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    #flash(current_user)
    user = User.query.filter_by(id=session.get('userid')).first()
    print(user)
    logout_user()
    del session['userid']

    return 'you have logged out'


manager = Manager(app)
if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    add_role()
    add_user()
    manager.run()