#!/usr/bin/env python
# encoding: utf-8
import json
import cloudfiles
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask.ext.login import LoginManager, login_required, login_user, logout_user
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('IMGR_SETTINGS')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.setup_app(app)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(32))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return u"%s" % self.id


@login_manager.user_loader
def load_user(userid):
    try:
        return User.query.filter_by(id=userid).one()
    except:
        return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get('rememberme', False)
        next_page = request.args.get('next', '/')
        print request.args['next']
        print "next page: %s" % next_page
        try:
            user = User.query.filter_by(email=email, password=password).one()
        except:
            flash('bad email/password', category="error")
            return redirect(url_for('login'))
        login_user(user, remember=remember)
        flash("you have been logged in", category="success")
        return redirect('/')
    else:
        next_page = request.args.get('next', '/')
        return render_template("users_login.html", next=next_page)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

def cf_connect():
    cf = cloudfiles.Connection(app.config['CF_USER'], app.config['CF_KEY'])
    container = cf.get_container(app.config['CONTAINER'])
    return container


def cf_get_dirs():
    container = cf_connect()
    dirs = container.list_objects(delimiter='/', prefix=app.config['PREFIX'])
    return dirs


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/new', methods=["GET"])
@login_required
def get_new():
    """display form for adding new image"""
    return render_template('new.html', dirs=cf_get_dirs())


@app.route('/new', methods=["POST"])
@login_required
def post_new():
    """create/upload new image"""
    container = cf_connect()
    image = request.files['image']
    if image:
        cf_image = container.list_objects(
            prefix="%s/" % image.filename, delimiter="/")
        if len(cf_image):
            return "Already exists, try another name."
        else:
            cf_image = container.create_object(image.filename)
            cf_image.content_type = image.content_type
            cf_image.write(image.read())
            return redirect(url_for('list'))
    else:
        return "need image."


@app.route('/list')
@login_required
def list():
    """docstring for list"""
    marker = request.args.get('marker', '')
    container = cf_connect()
    images = container.get_objects(
        prefix=app.config['PREFIX'], limit=100, marker=marker)
    if len(images) >= 100:
        return render_template('list.html', images=images, prev=images[0].name,
            next=images[-1].name, cname=app.config['CNAME'])
    else:
        return render_template('list.html', images=images,
            cname=app.config['CNAME'])


@app.route('/delete/<path:image_name>', methods=['GET'])
@app.route('/<path:image_name>', methods=['DELETE'])
@login_required
def delete(image_name):
    if image_name:
        container = cf_connect()
        try:
            image = container.get_object(image_name)
            container.delete_object(image.name)
            return redirect(url_for('list'))
        except cloudfiles.errors.NoSuchObject:
            abort(404)
    else:
        abort(404)


@app.route('/help', methods=['GET'])
@login_required
def help():
    abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('4xx.html', code='404',
        message="Sorry, we couldn't find what you were looking for."), 404


@app.errorhandler(405)
def page_not_found(error):
    return render_template('4xx.html', code=405,
        message="That method is not allowed here."), 405


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
