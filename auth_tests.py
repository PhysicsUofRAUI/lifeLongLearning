import unittest
from flask_testing import TestCase
from config import TestConfiguration
from app import create_app as c_app
import os
import flask

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)



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

    def test_login_page(self):
        #
        # Test whether the page and form is found
        #
        response = self.client.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/login', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        #
        # Now check for to see if it logins in correctly
        #
        with self.app.test_client() as c:
            response = c.post('/login', data=dict(
                username=os.getenv('LOGIN_USERNAME'),
                password=os.getenv('LOGIN_PASSWORD')
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(flask.session.get('logged_in'), True)

            #
            # Logout and verify the responses
            #
            response_1 = c.get('/logout', follow_redirects=True)
            self.assertEqual(response_1.status_code, 200)
            self.assertEqual(flask.session['logged_in'], False)
            
            
            #
            # Try the same things as before, but without following redirects
            #
            response = c.post('/login', data=dict(
                username=os.getenv('LOGIN_USERNAME'),
                password=os.getenv('LOGIN_PASSWORD')
            ), follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(flask.session.get('logged_in'), True)

            response_1 = c.get('/logout', follow_redirects=False)
            self.assertEqual(response_1.status_code, 302)
            self.assertEqual(flask.session['logged_in'], False)

    def test_logout_page(self):
        #
        # Testing the logout page while not logged in
        #
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # See if it redirected
        response = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main()
