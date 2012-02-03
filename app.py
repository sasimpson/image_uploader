#!/usr/bin/env python
# encoding: utf-8
import json
import cloudfiles

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('IMGR_SETTINGS')

def cf_connect():
    cf = cloudfiles.Connection(app.config['CF_USER'], app.config['CF_KEY'])
    container = cf.get_container(app.config['CONTAINER'])
    return container

def cf_get_dirs():
    container = cf_connect()
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
    container = cf_connect()
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
    
@app.route('/list')
def list():
    """docstring for list"""
    marker = request.args.get('marker', '')
    container = cf_connect()
    images = container.get_objects(prefix=app.config['PREFIX'], limit=100, marker=marker)
    if len(images) >= 100:
        return render_template('list.html', images=images, prev=images[0].name, next=images[-1].name, cname=app.config['CNAME'])
    else:
        return render_template('list.html', images=images, cname=app.config['CNAME'])

@app.route('/delete/<path:image_name>', methods=['GET'])
@app.route('/<path:image_name>', methods=['DELETE'])
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
def help():
    abort(404)    

@app.errorhandler(404)
def page_not_found(error):
    return render_template('4xx.html', code='404', message="Sorry, we couldn't find what you were looking for."), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template('4xx.html', code=405, message="That method is not allowed here."), 405


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
