import unittest
from flask_testing import TestCase
from config import TestConfiguration
from app import create_app as c_app
import os
import flask

class BasicTests(TestCase):

    ############################
    #### setup and teardown ####
    ############################

    def create_app(self):
        app = c_app(TestConfiguration)
        return app

    # executed prior to each test
    def setUp(self):
        pass

    # executed after each test
    def tearDown(self):
        pass
        
    def test_404_page(self) :
        response = self.client.get('/loop', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/dsagj/aghdsa/sadf', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/worksheets', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/posts', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/bloogs', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_500_page(self):
        # should through 500 errors because there is no database initialized
        response = self.client.get('/worksheets_page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
