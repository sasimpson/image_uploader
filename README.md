Image Uploader
==============

i created this for a friend to help him upload images to a CloudFiles container.  You can then use the public/cdn url or you can CNAME the container and use that.

Instructions
------------
1. get the code and put it somewhere.
2. requires (easy_install, pip, etc):
   * Flask
   * Flask-Login
   * Jinja
   * Werkzeug
   * python-cloudfiles
3. setup config with environment variable called IMGR_SETTINGS pointing to your config file:

        export IMGR_SETTINGS=/foo/bar/imgupload.cfg

    example config:

        SECRET_KEY = 'some key'
        CF_USER = 'cf_username'
        CF_KEY = 'cf_api_key'
        CONTAINER = 'container name'
        PREFIX = 'prefix if you are using pseudo directories'
        CNAME = 'cname you are using to point to cdn'
        SQLALCHEMY_DATABASE_URL = 'dburi'

4. run, quick and dirty with (i know its ghetto):

        from ipython:
          from app import db
          db.create_all()
          u = User('username', 'email@email.com', 'password123')
          db.session.add(u)
          db.session.commit(u)
        then:
        python     app.py
    
    and you can access from http://yourhost.com:5000

    You can setup proxy pass or mod_wsgi with apache. 
