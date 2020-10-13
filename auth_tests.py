


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
        response = self.client.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/login', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        #
        # Now check for to see if it logins in correctly
        #
        login(self.client, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))
        self.assertEqual(flask.session['logged_in'], True)

    def test_logout_page(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # See if it redirected
        response = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        #
        # Test behaviour while logged in
        #
        login(self.client, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))

        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(flask.session['logged_in'], False)

        # See if it redirected
        login(self.client, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))

        response = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(flask.session['logged_in'], False)
