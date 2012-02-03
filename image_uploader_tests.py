import os
import app
import unittest
import tempfile

class Object(object):
    """mock for Object"""
    def __init__(self, **kw):
        for k in kw.keys():
            setattr(self, k, kw[k])
    def public_uri(self):
        return self.pub_uri
        

class Container(object):
    """mock for Container"""
    def __init__(self, **kw):
        for k in kw.keys():
            setattr(self, k, kw[k])
        
    def get_objects(self, **kw):
        if self.empty:
            return []
        else:
            return [
                Object(name="foo.jpg", size=65432, content_type="image/jpeg", pub_uri="http://foo.bar.com/foo.jpg"),
                Object(name="bar.jpg", size=12345, content_type="image/jpeg", pub_uri="http://foo.bar.com/bar.jpg")
            ]
    

def cf_connect_stub():
    return Container(name="foo", empty=False)

def cf_connect_empty_stub():
    return Container(name="foo", empty=True)

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['CNAME'] = 'http://foo.com'
        self.app = app.app.test_client()

    def tearDown(self):
        pass
    
    def test_index_renders_template(self):
        rv = self.app.get('/')
        assert "Image Uploader" in rv.data
    
    def test_list_no_content(self):
        old_cf_connect = app.cf_connect
        app.cf_connect = cf_connect_empty_stub
        rv = self.app.get('/list')
        assert "No images found." in rv.data
        app.cf_connect = old_cf_connect

    def test_list_with_content(self):
        old_cf_connect = app.cf_connect
        app.cf_connect = cf_connect_stub
        rv = self.app.get('/list')
        assert "foo.jpg" in rv.data
        assert "bar.jpg" in rv.data
        app.cf_connect = old_cf_connect
    
    def test_new_get_form(self):
        rv = self.app.get('/new')
        assert "submit" in rv.data
        assert "Image File" in rv.data
    
    def test_new_post_form(self):
        rv = self.app.post()
    

if __name__ == '__main__':
    unittest.main()
