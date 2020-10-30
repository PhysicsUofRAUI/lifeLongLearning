import unittest
from flask_testing import TestCase
from config import TestConfiguration
from app import create_app as c_app
import os
import flask
from app.models import Worksheet, WorksheetCategory, Author, Post, PostCategory, Learner
from app.database import db
from contextlib import contextmanager

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)

@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    flask.template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        flask.template_rendered.disconnect(record, app)

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
        
    def test_main_page(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_main_page_home(self):
        response = self.client.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/home', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_admin_page(self):
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_building_page(self):
        response = self.client.get('/building', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/building', follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        
        
        
class DatabaseTests(TestCase):
    def create_app(self):
        app = c_app(TestConfiguration)
        return app

    # executed prior to each test
    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # executed after each test
    def tearDown(self):

        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_other_database_pages(self):
        # contact page
        auth_1 = Author(name='Kidkaidf', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        db.session.commit()

        response = self.client.get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        auth_1 = Author.query.filter_by(name='Kidkaidf').first()
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/contact')
                template, context = templates[0]
                self.assertEqual(context['authors'], [auth_1])





        #
        # Testing the Admin Page
        #
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)

        p_cat = PostCategory(name='froots')

        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        learner_1 = Learner(name='Ksa', email='kodyroger21@gmail.com', screenname='kod_1'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        learner_2 = Learner(name='KoJsa', email='kodyrogers1@gmail.com', screenname='kod2'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        learner_3 = Learner(name='KJdsa', email='kodyrogers2@gmail.com', screenname='kod3'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        db.session.add(learner)
        db.session.add(learner_1)
        db.session.add(learner_2)
        db.session.add(learner_3)
        db.session.commit()

        db.session.add(p_cat)
        db.session.commit()

        worksheet = Worksheet(pdf_url='tudoloos.pdf', name='tudoloo', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_1 = Worksheet(pdf_url='tudoloo.pdf', name='tudolos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_2 = Worksheet(pdf_url='tudolos.pdf', name='tudooos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_3 = Worksheet(pdf_url='tudolos.pdf', name='tudloos', author_id=1, author=auth_1, category_id=1, category=w_cat)

        learner_1.favourites.append(worksheet)

        learner_2.favourites.append(worksheet)

        learner_2.favourites.append(worksheet_2)

        learner_3.favourites.append(worksheet_2)

        db.session.commit()

        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login(c, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))
                r = c.get('/admin', follow_redirects=False)
                self.assertEqual(r.status_code, 200)
                template, context = templates[1]
                self.assertEqual(context['post_categories'], [p_cat])
                self.assertEqual(context['worksheet_categories'], [w_cat])
                self.assertEqual(context['learners'], [learner, learner_1, learner_2, learner_3])
                logout(c)
                
                
if __name__ == "__main__":
    unittest.main()
    