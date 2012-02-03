import os
import app
import unittest
import tempfile

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass
    
    def test_index_renders_template(self):
        rv = self.app.get('/')
        assert "Image Uploader" in rv.data
    
    def test_new_renders_template(self):
        pass
        
if __name__ == '__main__':
    unittest.main()