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

from werkzeug.security import generate_password_hash, check_password_hash

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def login_author(client, email, password):
    return client.post('/author_login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout_author(client):
    return client.get('/author_logout', follow_redirects=True)

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
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


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


    def test_author_login(self):
        author = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(author)
        db.session.commit()



        with self.app.test_client() as c:
            response = c.post('/author_login', data=dict(
                email='kodyrogers21@gmail.com',
                password='RockOn'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(flask.session['author_logged_in'], True)

            self.assertEqual(flask.session['author_name'], 'KJsa')

            response_1 = c.get('/author_logout', follow_redirects=True)
            self.assertEqual(response_1.status_code, 200)
            self.assertEqual(flask.session['author_logged_in'], False)

        def test_learner_login(self):
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



class TestingWhileLearnerLoggedIn(TestCase):
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



class TestingWhileAuthorLoggedIn(TestCase):
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


    def test_author_change_about(self) :
        auth_1 = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('author.author_change_about', id=auth_1.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/author_change_about/1',
                    data=dict(about='I love rock music'), follow_redirects=True)

        auth = Author.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(auth.email, 'kodyrogers21@gmail.com')

        self.assertEqual(auth.about, 'I love rock music')

        logout_author(self.client)


    def test_author_change_password(self) :
        auth_1 = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('author.author_change_password', id=auth_1.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/author_change_password/1',
                    data=dict(password='weeeehooo'), follow_redirects=True)

        auth = Author.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(auth.email, 'kodyrogers21@gmail.com')

        self.assertEqual(check_password_hash(auth.password, 'weeeehooo'), True)

        logout_author(self.client)

    def test_author_change_screenname(self) :
        auth_1 = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('author.author_change_screenname', id=auth_1.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/author_change_screenname/1',
                        data=dict(screenname='logical'), follow_redirects=True)

        auth = Author.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(auth.email, 'kodyrogers21@gmail.com')

        self.assertEqual(auth.password, 'pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        self.assertEqual(auth.screenname, 'logical')

        logout_author(self.client)


    def test_author_change_email(self) :
        auth_1 = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get(url_for('author.author_change_email', id=auth_1.id), follow_redirects=False)

        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/author_change_email/1',
                    data=dict(email='kody15@hotmail.com'), follow_redirects=True)

        auth = Author.query.filter_by(name='KJsa').first()
        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(response_1.status_code, 200)

        self.assertEqual(auth.email, 'kody15@hotmail.com')

        self.assertEqual(auth.password, 'pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        self.assertEqual(auth.screenname, 'kod')

        logout_author(self.client)




    def test_author_dashboard(self):
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        auth_1 = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        worksheet = Worksheet(pdf_url='tudolsoos.pdf', name='tudoloods', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)

        db.session.commit()

        worksheet = Worksheet.query.filter_by(name='tudoloods').first()

        w_cat = WorksheetCategory.query.filter_by(name='dundk').first()



        w_cat_1 = WorksheetCategory(name='dund32k')
        db.session.add(w_cat_1)

        w_cat_2 = WorksheetCategory(name='dundfsdk')
        db.session.add(w_cat_2)
        db.session.commit()


        auth_2 = Author(name='Kidkafdidf', email='kodyrogers29@gmail.com', password='pbkdf2:sha256:150000$JbvZOh4x$40097777eeefb55bc6987f4e6983d3401dca4d863a9a8971b36548d41af927dd')
        db.session.add(auth_2)
        auth_3 = Author(name='Kif', email='kodyrogers22@gmail.com', password='pbkdf2:sha256:150000$JbvZOh4x$40097777eeefb55bc6987f4e6983d3401dca4d863a9a8971b36548d41af927dd')
        db.session.add(auth_3)

        db.session.commit()

        worksheet_1 = Worksheet(pdf_url='tudolsoo.pdf', name='tloods', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_2 = Worksheet(pdf_url='tudolsos.pdf', name='tudoldaghoods', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_3 = Worksheet(pdf_url='tudolos.pdf', name='tudol', author_id=3, author=auth_3, category_id=3, category=w_cat_2)
        worksheet_4 = Worksheet(pdf_url='tudsoos.pdf', name='tudolsagdgsshjoods', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_5 = Worksheet(pdf_url='tolsoos.pdf', name='tudoldfag', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_6 = Worksheet(pdf_url='lsoos.pdf', name='tudosdag', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_7 = Worksheet(pdf_url='tch.pdf', name='tudosgsggs', author_id=3, author=auth_3, category_id=3, category=w_cat_2)
        worksheet_8 = Worksheet(pdf_url='tudsfgos.pdf', name='montreal', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_9 = Worksheet(pdf_url='tersoos.pdf', name='toronto', author_id=3, author=auth_3, category_id=3, category=w_cat_2)
        worksheet_10 = Worksheet(pdf_url='tudosgagos.pdf', name='ottowa', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_11 = Worksheet(pdf_url='tusgsgos.pdf', name='saskatoon', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_12 = Worksheet(pdf_url='tusgsssoos.pdf', name='winnipeg', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        db.session.add(worksheet_1)
        db.session.add(worksheet_2)
        db.session.add(worksheet_3)
        db.session.add(worksheet_4)
        db.session.add(worksheet_5)
        db.session.add(worksheet_6)
        db.session.add(worksheet_7)
        db.session.add(worksheet_8)
        db.session.add(worksheet_9)
        db.session.add(worksheet_10)
        db.session.add(worksheet_11)
        db.session.add(worksheet_12)

        db.session.commit()

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                c.post('/author_login', data=dict(
                    email='kodyrogers21@gmail.com',
                    password='RockOn'
                ), follow_redirects=True)

                r = c.get(url_for('author.author_dashboard', id=1))

                self.assertEqual(r.status_code, 200)

                template, context = templates[0]

                self.assertEqual(context['worksheets'], [worksheet_11, worksheet_5, worksheet_1, worksheet])
                c.get('/author_logout', follow_redirects=True)

    



class DatabaseTests(TestCase):

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

    def test_Post_model(self) :

        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        db.session.add(post)
        db.session.commit()

        assert post in db.session

    def test_blog_category_model(self) :
        post_cat = PostCategory(name='tudoloos')
        db.session.add(post_cat)
        db.session.commit()

        assert post_cat in db.session

    def test_author_model(self) :
        author = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod',
                        about='What up?', password='pbkdf2:sha256:150000$CgCWVBC6$4090facdcd3e093c7b458362daddbaa7b53387c6042ad46b5970dc7b6d00183c')
        db.session.add(author)
        db.session.commit()

        assert author in db.session






class TestingWhileLoggedIn(TestCase):
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


    def test_add_post_page_li(self):
        p_cat = PostCategory(name='Resources')
        p_cat1 = PostCategory(name='Ressdgources')
        p_cat2 = PostCategory(name='Ressdgsdgources')
        p_cat3 = PostCategory(name='Reurces')
        db.session.add(p_cat)
        db.session.add(p_cat1)
        db.session.add(p_cat2)
        db.session.add(p_cat3)
        db.session.commit()

        all_cats = PostCategory.query.all()

        self.assertEqual([p_cat,p_cat1,p_cat2,p_cat3], all_cats)

        response = self.client.get('/add_post', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        data = dict(title='Hello', content='fagkjkjas', category=p_cat.id)

        response_1 = self.client.post('/add_post', follow_redirects=False, data=data, content_type='multipart/form-data')

        self.assertEqual(response_1.status_code, 302)

        new_post = db.session.query(Post).filter_by(name='Hello').first()

        self.assertNotEqual(new_post, None)


    def test_add_blog_category_page_li(self):
        response = self.client.get('/add_blog_category', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/add_blog_category', follow_redirects=True, data=dict(name='Resources'))

        p_cat = PostCategory.query.filter_by(name='Resources').first()

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(p_cat, None)





    

    def test_add_author_page_li(self):
        response = self.client.get('/add_author', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/add_author', follow_redirects=True, data=dict(name='Kody', email='kodyrogers21@gmail.com',
                    about='I am a hacker', screenname='blah', password='password'))

        auth = Author.query.filter_by(name='Kody').first()

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(auth, None)

        self.assertEqual(auth.name, 'Kody')

        self.assertEqual(auth.screenname, None)

        self.assertEqual(auth.about, None)

        self.assertEqual(auth.email, 'kodyrogers21@gmail.com')

        self.assertEqual(check_password_hash(auth.password, 'password'), True)

        response_1 = self.client.post('/add_author', follow_redirects=True, data=dict(name='Kody1', email='kodyrogers@gmail.com', password='honkog'))

        auth_1 = Author.query.filter_by(name='Kody1').first()

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(auth_1, None)

        self.assertEqual(auth_1.name, 'Kody1')

        self.assertEqual(auth_1.screenname, None)

        self.assertEqual(auth_1.about, None)

        self.assertEqual(check_password_hash(auth_1.password, 'honkog'), True)

    def test_edit_post_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        db.session.add(post)
        db.session.commit()

        response = self.client.get('/edit_post/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        data = dict(title='Good Day', content='fagkjkjas whate', category=p_cat.id)

        response_1 = self.client.post('/edit_post/1', follow_redirects=True, data=data)

        self.assertEqual(response_1.status_code, 200)

        edited_post = Post.query.filter_by(name='Good Day').first()

        self.assertNotEqual(edited_post, None)


    def test_delete_post_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        db.session.add(post)
        db.session.commit()

        response = self.client.get('/delete_post/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        deleted_post = Post.query.filter_by(name='Hello').first()

        self.assertEqual(deleted_post, None)

        assert post not in db.session


    


    def test_edit_blog_category_page_li(self):
        post_cat = PostCategory(name='tudoloos')
        db.session.add(post_cat)
        db.session.commit()

        response = self.client.get('/edit_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/edit_blog_category/1', follow_redirects=True, data=dict(name='yippe'))

        self.assertEqual(response_1.status_code, 200)

        edited_post_category = PostCategory.query.filter_by(name='yippe').first()

        self.assertNotEqual(edited_post_category, None)

    def test_edit_author_page_li(self):
        author = Author(name='KJsa', password='password', email='kodya@hotmail.com')
        db.session.add(author)
        db.session.commit()

        response = self.client.get('/edit_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/edit_author/1', follow_redirects=True, data=dict(password='RockOn'))

        self.assertEqual(response_1.status_code, 200)

        edited_author = Author.query.filter_by(name='KJsa').first()

        self.assertNotEqual(edited_author, None)

        self.assertNotEqual(edited_author.password, generate_password_hash('RockOn'))

        self.assertEqual(edited_author.email, 'kodya@hotmail.com')

        response_2 = self.client.post('/edit_author/1', follow_redirects=True, data=dict(password='RockOn', about='hey hey',
                                        screenname='yoh', name='Kody', email='kody15@nhl.com'))

        self.assertEqual(response_2.status_code, 200)

        edited_author_1 = Author.query.filter_by(name='Kody').first()

        self.assertNotEqual(edited_author_1, None)

        self.assertNotEqual(edited_author_1.password, generate_password_hash('RockOn'))

        self.assertEqual(edited_author_1.email, 'kody15@nhl.com')

        self.assertEqual(edited_author_1.screenname, None)

        self.assertEqual(edited_author_1.about, None)




    

    def test_delete_blog_category_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        response = self.client.get('/delete_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        p_cat = PostCategory.query.filter_by(name='froots').first()

        self.assertEqual(p_cat, None)

    def test_delete_author_page_li(self):
        auth_1 = Author(name='Kidkaid', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        response = self.client.get('/delete_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        auth_1 = Author.query.filter_by(name='kidkaid').first()

        self.assertEqual(auth_1, None)


    def test_blog_view_page(self):
        # blog page
        response = self.client.get('/blog', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        db.session.add(post)
        db.session.commit()

        post = Post.query.filter_by(name='Hello').first()

        p_cat = PostCategory.query.filter_by(name='froots').first()

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/blog')
                template, context = templates[0]
                self.assertEqual(context['posts'], [post])
                self.assertEqual(context['categories'], [p_cat])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)

        p_cat_1 = PostCategory(name='Tondits')
        db.session.add(p_cat_1)

        p_cat_2 = PostCategory(name='frootsLoops')
        db.session.add(p_cat_2)

        p_cat_3 = PostCategory(name='Roger')
        db.session.add(p_cat_3)

        db.session.commit()

        post_1 = Post(name='Post 1', content='Stephen king is awesome', category_id=1, category=p_cat)
        post_2 = Post(name='Hello 2', content='Shoe dog is a great book', category_id=2, category=p_cat_1)
        post_3 = Post(name='Hello 3', content='Zappos was a great company', category_id=3, category=p_cat_2)
        post_4 = Post(name='Hello 4', content='Gary bettman is crazy', category_id=4, category=p_cat_3)

        post_5 = Post(name='Hello 5', content='Today will be a great day', category_id=1, category=p_cat)
        post_6 = Post(name='Hello 6', content='Untested code is broken code', category_id=2, category=p_cat_1)
        post_7 = Post(name='Hello 7', content='Seeding is over!', category_id=3, category=p_cat_2)
        post_8 = Post(name='Hello 8', content='It is raining out', category_id=4, category=p_cat_3)

        post_9 = Post(name='Hello 9', content='I get confused easily', category_id=1, category=p_cat)
        post_10 = Post(name='Hello 10', content='I wonder if I should get water', category_id=2, category=p_cat_1)
        post_11 = Post(name='Hello 11', content='Hopefully I figure out that one test soon', category_id=3, category=p_cat_2)
        post_12 = Post(name='Hello 12', content='It is really frustrating me', category_id=4, category=p_cat_3)

        post_13 = Post(name='Hello 91', content='I get confused easily what', category_id=1, category=p_cat)
        post_14 = Post(name='Hello 101', content='I wonder if I should gewhatt water', category_id=2, category=p_cat_1)
        post_15 = Post(name='Hello 111', content='Hopefully I figure out thawhet one test soon', category_id=3, category=p_cat_2)
        post_16 = Post(name='Hello 121', content='It is really frustrating mewheat', category_id=4, category=p_cat_3)

        post_17 = Post(name='Hello 916', content='I get confused easilddy', category_id=1, category=p_cat)
        post_18 = Post(name='Hello 1031', content='I wonder if I shoulddsa get water', category_id=2, category=p_cat_1)
        post_19 = Post(name='Hello1 11', content='Hopefully I figure out thellohat one test soon', category_id=3, category=p_cat_2)
        post_20 = Post(name='Hello 112', content='It is really frustrating mdse', category_id=4, category=p_cat_3)

        post_21 = Post(name='Hello 924', content='I get confused easily mais ou menos', category_id=1, category=p_cat)
        post_22 = Post(name='Hello 102', content='I wonder if I should get water holy fuch', category_id=2, category=p_cat_1)
        post_23 = Post(name='Hello 411', content='Hopefully I figure out that one test soosdgn', category_id=3, category=p_cat_2)
        post_24 = Post(name='Hello 142', content='It is really frustrating me. It will be OK!', category_id=4, category=p_cat_3)

        db.session.commit()

        #
        # Testing specifying a category
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=3, post=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_23, post_19, post_15, post_11, post_7])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], url_for('blogs.blog', category=3, page=1, post=None))
                self.assertEqual(context['prev_url'], None)

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=3, post=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_3])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('blogs.blog', category=3, page=0, post=None))

        #
        # Test specifying a post
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', post=2, page=0, category=None))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_1])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)


        #
        # Test not specifying anything
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=None, post=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_24, post_23, post_22, post_21, post_20])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], url_for('blogs.blog', category=None, page=1, post=None))
                self.assertEqual(context['prev_url'], None)

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=None, post=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_19, post_18, post_17, post_16, post_15])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], url_for('blogs.blog', category=None, page=2, post=None))
                self.assertEqual(context['prev_url'], url_for('blogs.blog', category=None, page=0, post=None))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=None, post=None, page=2))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_14, post_13, post_12, post_11, post_10])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], url_for('blogs.blog', category=None, page=3, post=None))
                self.assertEqual(context['prev_url'], url_for('blogs.blog', category=None, page=1, post=None))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=None, post=None, page=3))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_9, post_8, post_7, post_6, post_5])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], url_for('blogs.blog', category=None, page=4, post=None))
                self.assertEqual(context['prev_url'], url_for('blogs.blog', category=None, page=2, post=None))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('blogs.blog', category=None, post=None, page=4))
                template, context = templates[0]
                self.assertEqual(context['posts'], [post_4, post_3, post_2, post_1, post])
                self.assertEqual(context['categories'], [p_cat, p_cat_1, p_cat_2, p_cat_3])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('blogs.blog', category=None, page=3, post=None))



    

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

    ##############################
    #### testing author pages ####
    ##############################

    def test_author_change_email_nl(self):
        response = self.client.get('/author_change_email/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/author_change_email/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)


    def test_author_change_about_nl(self):
        response = self.client.get('/author_change_about/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/author_change_about/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_author_change_password_nl(self):
        response = self.client.get('/author_change_password/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/author_change_password/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_author_change_screenname_nl(self):
        response = self.client.get('/author_change_screenname/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/author_change_screenname/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_author_dashboard_nl(self):
        response = self.client.get('/author_dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/author_dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)


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



    #######################
    #### testing Blogs ####
    #######################



    def test_add_post_page(self):
        response = self.client.get('/add_post', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_page(self):
        response = self.client.get('/edit_post/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_post_page(self):
        response = self.client.get('/delete_post/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_blog_category_page(self):
        response = self.client.get('/add_blog_category', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_blog_category_page(self):
        response = self.client.get('/edit_blog_category/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_blog_category_page(self):
        response = self.client.get('/delete_blog_category/2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # Now doing checking whether the stuff that should have been redirected is
    # redirected

    def test_add_post_page_r(self):
        response = self.client.get('/add_post', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_edit_post_page_r(self):
        response = self.client.get('/edit_post/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_post_page_r(self):
        response = self.client.get('/delete_post/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_add_blog_category_page_r(self):
        response = self.client.get('/add_blog_category', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_edit_blog_category_page_r(self):
        response = self.client.get('/edit_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_blog_category_page_r(self):
        response = self.client.get('/delete_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)





    def test_add_author_page(self):
        response = self.client.get('/add_author', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_author_page(self):
        response = self.client.get('/edit_author/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_author_page(self):
        response = self.client.get('/delete_author/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # checking if the user gets kicked out of protected views when not logged in
    # will check this to see if the request results in a redirect

    def test_add_author_page_r(self):
        response = self.client.get('/add_author', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_edit_author_page_r(self):
        response = self.client.get('/edit_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_author_page_r(self):
        response = self.client.get('/delete_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)



if __name__ == "__main__":
    unittest.main()
