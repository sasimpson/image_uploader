#!/usr/bin/env python
# encoding: utf-8
"""
app.py

Created by Scott Simpson on 2012-01-13.
"""
import json
import cloudfiles

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('IMGR_SETTINGS')

def cf_get_dirs():
    cf = cloudfiles.Connection(app.config['CF_USER'], app.config['CF_KEY'])
    container = cf.get_container(app.config['CONTAINER'])
    dirs = container.list_objects(delimiter='/', prefix=app.config['PREFIX'])
    return dirs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=["GET"])
def get_new():
    """display form for adding new image"""
    return render_template('new.html', dirs=cf_get_dirs())
    
@app.route('/new', methods=["POST"])
def post_new():
    """create/upload new image"""
    cf = cloudfiles.Connection(app.config['CF_USER'], app.config['CF_KEY'])
    container = cf.get_container(app.config['CONTAINER'])
    image = request.files['image']
    if image:
        cf_image = container.list_objects(prefix="%s/" % image.filename, delimiter="/")
        if len(cf_image):
            return "Already exists, try another name."
        else:
            cf_image = container.create_object(image.filename)
            cf_image.content_type = image.content_type
            cf_image.write(image.read())
            return redirect(url_for('list'))
    else:
        return "need image."
    
@app.route('/dir/new', methods=["POST"])
def dir_new():
    """docstring for dir_new"""
    return "dir_new"

@app.route('/list')
def list():
    """docstring for list"""
    marker = request.args.get('marker', '')
    cf = cloudfiles.Connection(app.config['CF_USER'], app.config['CF_KEY'])
    container = cf.get_container(app.config['CONTAINER'])
    images = container.get_objects(prefix=app.config['PREFIX'], limit=100, marker=marker)
    print container.list_objects()
    if len(images) >= 100:
        return render_template('list.html', images=images, prev=images[0].name, next=images[-1].name, cname=app.config['CNAME'])
    else:
        return render_template('list.html', images=images, cname=app.config['CNAME'])

@app.route('/i/<path:image>', methods=['GET'])
def image():
    """docstring for image"""
    pass
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
