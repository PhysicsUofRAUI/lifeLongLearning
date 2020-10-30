import os
import io
import flask
import unittest
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy
from flask import session, url_for, template_rendered, current_app
from app.models import Worksheet, WorksheetCategory, Author, Post, PostCategory, Learner
from werkzeug.utils import secure_filename
from app.database import db
from config import TestConfiguration
from app import create_app as c_app
from contextlib import contextmanager
import pdfkit
from app.mail import mail

from werkzeug.security import check_password_hash

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)
    
def login_learner(client, email, password):
    return client.post('/learner_login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout_learner(client):
    return client.get('/learner_logout', follow_redirects=True)

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


    ###############################
    #### testing learner pages ####
    ###############################
    def test_learner_dashboard_nl(self):
        response = self.client.get('/learner_dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/learner_dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_change_password_nl(self):
        response = self.client.get('/learner_change_password/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/learner_change_password/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_change_email_nl(self):
        response = self.client.get('/learner_change_email/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/learner_change_email/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_change_screenname_nl(self):
        response = self.client.get('/learner_change_screenname/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/learner_change_screenname/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_signup_nl(self) :
        response = self.client.get('/learner_signup', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/learner_signup', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_learner_login_signup_choice_page_nl(self) :
        response = self.client.get('/learner_signup_login_choice', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/learner_signup_login_choice', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_learner_add_favourite_nl(self) :
        response = self.client.get('/add_favourite/1/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/add_favourite/1/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_delete_learner_nl(self):
        response = self.client.get('delete_learner/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('delete_learner/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_edit_learner_nl(self):
        response = self.client.get('edit_learner/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('edit_learner/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_learner_learner_password_reset(self):
        response = self.client.get('edit_learner', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('edit_learner', follow_redirects=False)
        self.assertEqual(response.status_code, 200)


class UserLoginLogout(TestCase):
    ############################
    #### setup and teardown ####
    ############################

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
        
    def test_learner_login(self):
        w_cat = WorksheetCategory(name='dunk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaid', email='kodyrogers21@gmail.com',
                        password='pbkdf2:sha256:150000$xZu2ipeP$5d4d84302c1d4628c57f7e3f2cfc4bea4fdf69ef1214e18333ba6ff29ec096d9')
        db.session.add(auth_1)
        db.session.commit()

        worksheet = Worksheet(pdf_url='tudoloos.pdf', name='tudoloos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)
        db.session.commit()

        worksheet_1 = Worksheet(pdf_url='tudol.pdf', name='tudol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$xZu2ipeP$5d4d84302c1d4628c57f7e3f2cfc4bea4fdf69ef1214e18333ba6ff29ec096d9')

        learner.favourites.append(worksheet)
        learner.favourites.append(worksheet_1)

        db.session.add(learner)
        db.session.commit()

        with self.app.test_client() as c:
            response = c.post('/learner_login', data=dict(
                email='kodyrogers21@gmail.com',
                password='RockOn'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(flask.session['learner_logged_in'], True)

            self.assertEqual(flask.session['learner_name'], 'KJsa')

            response_1 = c.get('/learner_logout', follow_redirects=True)
            self.assertEqual(response_1.status_code, 200)
            self.assertEqual(flask.session['learner_logged_in'], False)
            
            

class DatabaseEditTests(TestCase):
    def create_app(self):
        app = c_app(TestConfiguration)
        return app

    # executed prior to each test
    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        login(self.client, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))

    # executed after each test
    def tearDown(self):
        logout(self.client)

        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        
    #########################################
    ####### Tests For Pages Admin Uses ######
    #########################################
    
    def test_learner_delete(self) :
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

        login(self.client, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))

        r = self.client.get('delete_learner/1', follow_redirects=False)

        deleted_learner = Learner.query.filter_by(name='KJsa').first()

        self.assertEqual(deleted_learner, None)

        logout(self.client)

    def test_edit_learner(self) :
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

        login(self.client, os.getenv('LOGIN_USERNAME'), os.getenv('LOGIN_PASSWORD'))

        response = self.client.get(url_for('learner.edit_learner', id=learner.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/edit_learner/1',
                    data=dict(password='yehhaw'), follow_redirects=True)

        edited_learner = Learner.query.filter_by(name='KJsa').first()

        self.assertNotEqual(edited_learner, None)

        self.assertEqual(check_password_hash(learner.password, 'yehhaw'), True)

        logout(self.client)
        
        
    ##########################################
    ###### Tests For Pages Learner Uses ######
    ##########################################
    
    def test_learner_password_reset(self):
        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        db.session.add(learner)
        db.session.commit()

        self.assertEqual(check_password_hash(learner.password, 'RockOn'), True)

        response = self.client.get(url_for('learner.learner_password_reset'), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        with mail.record_messages() as outbox:
            response = self.client.post(url_for('learner.learner_password_reset'),
                                        data=dict(email='kodyrogers21@gmail.com'), follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            learner = Learner.query.filter_by(name='KJsa').first()
            assert len(outbox) == 1
            assert outbox[0].subject == "Temporary Password"
            assert outbox[0].recipients == [learner.email]

            self.assertNotEqual(check_password_hash(learner.password, 'RockOn'), True)

        with mail.record_messages() as outbox:
            response = self.client.post(url_for('learner.learner_password_reset'),
                                        data=dict(email='kodyrogers21@gmail.com'), follow_redirects=False)

            self.assertEqual(response.status_code, 302)

            learner = Learner.query.filter_by(name='KJsa').first()

            learner = Learner.query.filter_by(name='KJsa').first()
            assert len(outbox) == 1
            assert outbox[0].subject == "Temporary Password"
            assert outbox[0].recipients == [learner.email]

            self.assertNotEqual(check_password_hash(learner.password, 'RockOn'), True)


    def test_learner_signup(self):
        response = self.client.post('/learner_signup',
                    data=dict(name='Kody', screenname='kodster', email='kodyrogers21@gmail.com', password='weeeehooo'), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        learner = Learner.query.filter_by(name='Kody').first()

        self.assertEqual(learner.name, 'Kody')

        self.assertEqual(learner.screenname, 'kodster')

        self.assertEqual(learner.email, 'kodyrogers21@gmail.com')

        self.assertEqual(check_password_hash(learner.password, 'weeeehooo'), True)

    def test_learner_dashboard(self):
        w_cat = WorksheetCategory(name='dunk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaid', email='kodyrogers21@gmail.com',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        worksheet = Worksheet(pdf_url='tudoloos.pdf', name='tudoloos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)
        db.session.commit()

        worksheet_1 = Worksheet(pdf_url='tudol.pdf', name='tudol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        learner.favourites.append(worksheet)
        learner.favourites.append(worksheet_1)

        db.session.add(learner)
        db.session.commit()

        learner_1 = Learner(name='Kody', email='kodyrogers24@gmail.com', screenname='hack'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        worksheet_2 = Worksheet(pdf_url='tuol.pdf', name='tuol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        worksheet_3 = Worksheet(pdf_url='tdol.pdf', name='tdol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        learner.favourites.append(worksheet_2)
        learner.favourites.append(worksheet_3)

        db.session.add(learner_1)
        db.session.commit()

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                response = c.post('/learner_login', data=dict(
                    email='kodyrogers21@gmail.com',
                    password='RockOn'
                ), follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(flask.session['learner_logged_in'], True)

                self.assertEqual(flask.session['learner_name'], 'KJsa')

                r = c.get(url_for('learner.learner_dashboard', id=1))

                learner = Learner.query.filter_by(email='kodyrogers21@gmail.com').first()

                self.assertEqual(r.status_code, 200)

                template, context = templates[0]

                self.assertEqual(context['favourites'], learner.favourites)

                response_1 = c.get('/learner_logout', follow_redirects=True)
                self.assertEqual(response_1.status_code, 200)
                self.assertEqual(flask.session['learner_logged_in'], False)

    def test_learner_add_favourite(self):
        w_cat = WorksheetCategory(name='dunk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaid', email='kodyrogers21@gmail.com',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        worksheet = Worksheet(pdf_url='tudoloos.pdf', name='tudoloos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)
        db.session.commit()

        worksheet_1 = Worksheet(pdf_url='tudol.pdf', name='tudol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        learner.favourites.append(worksheet)
        learner.favourites.append(worksheet_1)

        db.session.add(learner)
        db.session.commit()

        worksheet_2 = Worksheet(pdf_url='tuol.pdf', name='tuol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        login_learner(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('learner.add_favourite', learner_id=learner.id, worksheet_id=worksheet_2.id), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        learner_1 = Learner.query.filter_by(email='kodyrogers21@gmail.com').first()
        self.assertEqual(learner_1.favourites, [worksheet, worksheet_1, worksheet_2])

        logout_learner(self.client)

    def test_learner_change_password(self) :
        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        db.session.add(learner)
        db.session.commit()

        login_learner(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('learner.learner_change_password', id=learner.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/learner_change_password/1',
                    data=dict(password='weeeehooo'), follow_redirects=True)

        learner = Learner.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(learner.email, 'kodyrogers21@gmail.com')

        self.assertEqual(check_password_hash(learner.password, 'weeeehooo'), True)

        logout_learner(self.client)

    def test_learner_change_email(self):
        learner_1 = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(learner_1)
        db.session.commit()

        login_learner(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('learner.learner_change_email', id=learner_1.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/learner_change_email/1',
                    data=dict(email='kody15@hotmail.com'), follow_redirects=True)

        learner = Learner.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(learner.email, 'kody15@hotmail.com')

        self.assertEqual(learner.password, 'pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        self.assertEqual(learner.screenname, 'kod')

        logout_learner(self.client)


    def test_learner_change_screenname(self) :
        learner_1 = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(learner_1)
        db.session.commit()

        login_learner(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('learner.learner_change_screenname', id=learner_1.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/learner_change_screenname/1',
                        data=dict(screenname='logical'), follow_redirects=True)

        learner = Learner.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(learner.email, 'kodyrogers21@gmail.com')

        self.assertEqual(learner.password, 'pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        self.assertEqual(learner.screenname, 'logical')

        logout_learner(self.client)
        

class DatabaseModelsTests(TestCase):

    ############################
    #### setup and teardown ####
    ############################

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
        
    
    def test_learner_model(self) :
        w_cat = WorksheetCategory(name='dunk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaid', email='kodyrogers21@gmail.com',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        worksheet = Worksheet(pdf_url='tudoloos.pdf', name='tudoloos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)
        db.session.commit()

        worksheet_1 = Worksheet(pdf_url='tudol.pdf', name='tudol', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet_1)
        db.session.commit()

        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$CgCWVBC6$4090facdcd3e093c7b458362daddbaa7b53387c6042ad46b5970dc7b6d00183c')

        learner.favourites.append(worksheet)
        learner.favourites.append(worksheet_1)

        db.session.add(learner)
        db.session.commit()

        assert learner in db.session

if __name__ == "__main__":
    unittest.main()
    
    