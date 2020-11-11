import unittest
from flask_testing import TestCase
from config import TestConfiguration
from app import create_app as c_app
import os
from flask import session, url_for, template_rendered
from app.models import Worksheet, WorksheetCategory, Author, Post, PostCategory, Learner
from app.database import db
from contextlib import contextmanager
import pdfkit
import io

from app.worksheets.forms import category_choices

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
    
    ###################################
    ### Testing the Worksheet Views ###
    ###################################

    # Checking if any have 404s
    def test_specific_worksheet_page(self):
        response = self.client.get('/specific_worksheet/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/specific_worksheet/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_add_worksheet_page(self):
        response = self.client.get('/add_worksheet', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_worksheet_page(self):
        response = self.client.get('/delete_worksheet/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_worksheet_category_page(self):
        response = self.client.get('/add_worksheet_category', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_worksheet_category_page(self):
        response = self.client.get('/edit_worksheet_category/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_worksheet_category_page(self):
        response = self.client.get('/delete_worksheet_category/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    # checking if the user gets kicked out of protected views when not logged in
    # will check this to see if the request results in a redirect
    
    def test_add_worksheet_page_r(self):
        response = self.client.get('/add_worksheet', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_worksheet_page_r(self):
        response = self.client.get('/delete_worksheet/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_add_worksheet_category_page_r(self):
        response = self.client.get('/add_worksheet_category', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_edit_worksheet_category_page_r(self):
        response = self.client.get('/edit_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_worksheet_category_page_r(self):
        response = self.client.get('/delete_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        
class DatabaseTests(TestCase):
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
        
    def test_category_choice_factory(self) :
        w_cat_1 = WorksheetCategory(name='dund32k')
        db.session.add(w_cat_1)

        w_cat_2 = WorksheetCategory(name='dundfsdk')
        db.session.add(w_cat_2)
        db.session.commit()
        
        choice_factory = category_choices()
        
        self.assertEqual(choice_factory.all(), WorksheetCategory.query.all())
        
    def test_worksheet_page(self) :
        # worksheet page
        response = self.client.get('/worksheets_page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        db.session.commit()

        worksheet = Worksheet(pdf_url='tudolsoos.pdf', name='tudoloods', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)

        db.session.commit()

        worksheet = Worksheet.query.filter_by(name='tudoloods').first()

        w_cat = WorksheetCategory.query.filter_by(name='dundk').first()

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/worksheets_page')
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet])
                self.assertEqual(context['categories'], [w_cat])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)

        w_cat_1 = WorksheetCategory(name='dund32k')
        db.session.add(w_cat_1)

        w_cat_2 = WorksheetCategory(name='dundfsdk')
        db.session.add(w_cat_2)
        db.session.commit()


        auth_2 = Author(name='Kidkafdidf', email='kodyrogers24@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_2)
        auth_3 = Author(name='Kif', email='kodyrogers25@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
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

        #
        # Testing the first page of an author
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=2, category=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_10, worksheet_8, worksheet_6,  worksheet_4, worksheet_2])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)

        #
        # Testing the first page of a category
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', category=2, author=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_10, worksheet_8, worksheet_6,  worksheet_4, worksheet_2])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)


        #
        # Testing the second page of an author
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=2, category=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=2, category=None, page=0))


        #
        # Testing the second page of a category
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', category=2, author=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', category=2, author=None, page=0))



        #
        # Testing the worksheet page with many worksheets inputted
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_3, worksheet_2, worksheet_1, worksheet])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=0))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=2))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=1))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_11, worksheet_10, worksheet_9, worksheet_8, worksheet_7, worksheet_6, worksheet_5, worksheet_4])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=1))
                self.assertEqual(context['prev_url'], None)

        #
        # Checking if author overwrites the category
        #
        worksheet_13 = Worksheet(pdf_url='tudosgadgos.pdf', name='ottowa sens', author_id=1, author=auth_1, category_id=3, category=w_cat_2)
        worksheet_14 = Worksheet(pdf_url='tusgsghjgos.pdf', name='saskatoon hobbo', author_id=1, author=auth_1, category_id=2, category=w_cat_1)
        worksheet_15 = Worksheet(pdf_url='tusdasgsssoos.pdf', name='winnipeg jets', author_id=1, author=auth_1, category_id=2, category=w_cat_1)
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', category=1, author=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_11, worksheet_5, worksheet_1, worksheet])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)


        worksheet_16 = Worksheet(pdf_url='tudoloo.pdf', name='tloos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_17 = Worksheet(pdf_url='tudosos.pdf', name='tudldaghoods', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_18 = Worksheet(pdf_url='tudlos.pdf', name='tudl', author_id=3, author=auth_3, category_id=3, category=w_cat_2)
        worksheet_19 = Worksheet(pdf_url='tusoos.pdf', name='tuolsagdgsshjoods', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_20 = Worksheet(pdf_url='tlsoos.pdf', name='tdoldfag', author_id=1, author=auth_1, category_id=1, category=w_cat)
        worksheet_21 = Worksheet(pdf_url='soos.pdf', name='tuosdag', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_22 = Worksheet(pdf_url='tc.pdf', name='tudsgsggs', author_id=3, author=auth_3, category_id=3, category=w_cat_2)
        worksheet_23 = Worksheet(pdf_url='tdsfgos.pdf', name='montreal_1', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_24 = Worksheet(pdf_url='ersoos.pdf', name='toronto_2', author_id=3, author=auth_3, category_id=3, category=w_cat_2)
        worksheet_25 = Worksheet(pdf_url='tudosagos.pdf', name='ottowa_1', author_id=2, author=auth_2, category_id=2, category=w_cat_1)
        worksheet_26 = Worksheet(pdf_url='tusggos.pdf', name='saskatoon_1', author_id=1, author=auth_1, category_id=1, category=w_cat)

        #
        # Testing the worksheet page with even more worksheets inputted
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_26, worksheet_25, worksheet_24, worksheet_23, worksheet_22, worksheet_21, worksheet_20, worksheet_19, worksheet_18])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'],  url_for('worksheets.worksheets_page', author=None, category=None, page=1))
                self.assertEqual(context['prev_url'], None)

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_17, worksheet_16, worksheet_15, worksheet_14, worksheet_13, worksheet_12, worksheet_11, worksheet_10, worksheet_9])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=2))
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=0))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=2))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_8, worksheet_7, worksheet_6, worksheet_5, worksheet_4, worksheet_3, worksheet_2, worksheet_1, worksheet])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=1))

        # testing the specific worksheet page
        res = self.client.get('/specific_worksheet/1', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
    
    
    def test_worksheet_page_learner_logged_in(self) :
        # worksheet page
        response = self.client.get('/worksheets_page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        db.session.commit()

        worksheet = Worksheet(pdf_url='tudolsoos.pdf', name='tudoloods', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)

        learner = Learner(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod'
                        , password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        db.session.commit()

        worksheet = Worksheet.query.filter_by(name='tudoloods').first()

        w_cat = WorksheetCategory.query.filter_by(name='dundk').first()

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')

                r = c.get('/worksheets_page', follow_redirects=False)
                template, context = templates[1]
                self.assertEqual(context['favourites'], [])
                self.assertEqual(context['worksheets'], [worksheet])
                self.assertEqual(context['categories'], [w_cat])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)

                logout_learner(c)

        w_cat_1 = WorksheetCategory(name='dund32k')
        db.session.add(w_cat_1)

        w_cat_2 = WorksheetCategory(name='dundfsdk')
        db.session.add(w_cat_2)
        db.session.commit()


        auth_2 = Author(name='Kidkafdidf', email='kodyrogers24@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_2)
        auth_3 = Author(name='Kif', email='kodyrogers25@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
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

        learner.favourites.append(worksheet)
        learner.favourites.append(worksheet_1)
        learner.favourites.append(worksheet_3)
        learner.favourites.append(worksheet_2)

        db.session.commit()

        #
        # Testing the first page of an author
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', author=2, category=None, page=0))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_10, worksheet_8, worksheet_6,  worksheet_4, worksheet_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)
                logout_learner(c)

        #
        # Testing the first page of a category
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', category=2, author=None, page=0))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_10, worksheet_8, worksheet_6,  worksheet_4, worksheet_2])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)
                logout_learner(c)


        #
        # Testing the second page of an author
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', author=2, category=None, page=1))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=2, category=None, page=0))
                logout_learner(c)


        #
        # Testing the second page of a category
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', category=2, author=None, page=1))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', category=2, author=None, page=0))
                logout_learner(c)



        #
        # Testing the worksheet page with many worksheets inputted
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=1))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [worksheet_3, worksheet_2, worksheet_1, worksheet])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=0))
                logout_learner(c)

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=2))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=1))
                logout_learner(c)

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=0))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_11, worksheet_10, worksheet_9, worksheet_8, worksheet_7, worksheet_6, worksheet_5, worksheet_4])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2])
                self.assertEqual(context['next_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=1))
                self.assertEqual(context['prev_url'], None)
                logout_learner(c)

        #
        # Checking if author overwrites the category
        #
        worksheet_13 = Worksheet(pdf_url='tudosgadgos.pdf', name='ottowa sens', author_id=1, author=auth_1, category_id=3, category=w_cat_2)
        worksheet_14 = Worksheet(pdf_url='tusgsghjgos.pdf', name='saskatoon hobbo', author_id=1, author=auth_1, category_id=2, category=w_cat_1)
        worksheet_15 = Worksheet(pdf_url='tusdasgsssoos.pdf', name='winnipeg jets', author_id=1, author=auth_1, category_id=2, category=w_cat_1)

        learner.favourites.append(worksheet_14)

        db.session.commit()

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                login_learner(c, email='kodyrogers21@gmail.com', password='RockOn')
                r = c.get(url_for('worksheets.worksheets_page', category=1, author=None, page=0))
                template, context = templates[1]
                self.assertEqual(context['worksheets'], [worksheet_11, worksheet_5, worksheet_1, worksheet])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['favourites'], [worksheet, worksheet_1, worksheet_3, worksheet_2, worksheet_14])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], None)
                logout_learner(c)
                
                
    def test_worksheet_count_page(self):
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf', email='kodyrogers21@gmail.com',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        db.session.commit()

        options = { 'quiet': '' }
        pdfkit.from_string('MicroPyramid groovy', 'test.pdf', options=options)
        self.assertEqual(True, os.path.exists('test.pdf'))

        worksheet_1 = Worksheet(pdf_url='test.pdf', name='trig', author_id=1, author=auth_1, category_id=1, category=w_cat)

        db.session.commit()

        # worksheet page
        response = self.client.get('/worksheets_count/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        worksheet = Worksheet.query.filter_by(name='trig').first()

        self.assertEqual(worksheet.count, 1)

        response = self.client.get('/worksheets_count/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        worksheet = Worksheet.query.filter_by(name='trig').first()

        self.assertEqual(worksheet.count, 2)

        os.remove('test.pdf')

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
    
    def test_delete_worksheet_page_author(self):
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        auth_1 = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod', about='What up?',
                        password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        auth_2 = Author(name='Kidkafdidf', email='kodyrogers24@gmail.com', password='pbkdf2:sha256:150000$JbvZOh4x$40097777eeefb55bc6987f4e6983d3401dca4d863a9a8971b36548d41af927dd')
        db.session.add(auth_2)

        auth_3 = Author(name='Kif', email='kodyrogers25@gmail.com', password='pbkdf2:sha256:150000$JbvZOh4x$40097777eeefb55bc6987f4e6983d3401dca4d863a9a8971b36548d41af927dd')
        db.session.add(auth_3)

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

        options = { 'quiet': '' }
        pdfkit.from_string('MicroPyramid', 'tudolsoo.pdf', options=options)
        self.assertEqual(True, os.path.exists('tudolsoo.pdf'))

        options = { 'quiet': '' }
        pdfkit.from_string('MicroPyramid hey yall', 'tudolsoos.pdf', options=options)
        self.assertEqual(True, os.path.exists('tudolsoos.pdf'))

        options = { 'quiet': '' }
        pdfkit.from_string('MicroPyramid woopie', 'tudolsos.pdf', options=options)
        self.assertEqual(True, os.path.exists('tudolsos.pdf'))

        options = { 'quiet': '' }
        pdfkit.from_string('MicroPyramid groovy', 'tudolos.pdf', options=options)
        self.assertEqual(True, os.path.exists('tudolos.pdf'))

        options = { 'quiet': '' }
        pdfkit.from_string('MicroPyramid is awesome', 'tudsoos.pdf', options=options)
        self.assertEqual(True, os.path.exists('tudsoos.pdf'))

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

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.get('/delete_worksheet/1', follow_redirects=False)

        w = Worksheet.query.filter_by(name='tudoloods').first()

        self.assertEqual(w, None)


        response_1 = self.client.get('/delete_worksheet/3', follow_redirects=False)

        w_1 = Worksheet.query.filter_by(name='tudoldaghoods').first()

        self.assertEqual(w_1, worksheet_2)

        logout_author(self.client)

        os.remove('tudolsoo.pdf')
        os.remove('tudolsos.pdf')
        os.remove('tudolos.pdf')
        os.remove('tudsoos.pdf')


    def test_edit_worksheet_page(self) :
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        db.session.commit()

        data = dict(title='trig', video_url='youtube.com', category=w_cat.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcdef"), 'test.pdf')

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response = self.client.post('/add_worksheet', follow_redirects=True, data=data, content_type='multipart/form-data')

        logout_author(self.client)

        self.assertEqual(True, os.path.exists('test.pdf'))

        worksheet = Worksheet.query.filter_by(name='trig').first()

        self.assertEqual(response.status_code, 200)

        self.assertNotEqual(worksheet, None)

        #
        # Now make a new worksheet to add
        # without logging in user
        #
        data = dict(title='Trigonometry', video_url='youtube.com', category=w_cat.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcd234ef"), 'test_1.pdf')

        response_1 = self.client.post('/edit_worksheet/1', follow_redirects=True, data=data, content_type='multipart/form-data')

        worksheet_1 = Worksheet.query.filter_by(name='Trigonometry').first()

        self.assertEqual(worksheet_1, None)

        worksheet_2 = Worksheet.query.filter_by(name='trig').first()
        self.assertEqual(worksheet_2.pdf_url, 'test.pdf')

        self.assertEqual(True, os.path.exists('test.pdf'))
        self.assertEqual(False, os.path.exists('test_1.pdf'))

        #
        # Now with user logged in
        #
        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')

        response_2 = self.client.post('/edit_worksheet/1', follow_redirects=False, content_type='multipart/form-data')

        self.assertEqual(response_2.status_code, 200)

        data = dict(title='Trigonometry', video_url='youtube.com', category=w_cat.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcd234ef"), 'test_1.pdf')

        response_1 = self.client.post('/edit_worksheet/1', follow_redirects=True, data=data, content_type='multipart/form-data')

        worksheet_1 = Worksheet.query.filter_by(name='Trigonometry').first()

        self.assertNotEqual(worksheet_1, None)

        worksheet_2 = Worksheet.query.filter_by(name='trig').first()
        self.assertEqual(worksheet_1.pdf_url, 'test_1.pdf')

        self.assertEqual(worksheet_2, None)

        self.assertEqual(False, os.path.exists('test.pdf'))
        self.assertEqual(True, os.path.exists('test_1.pdf'))

        #
        # Now not editing the pdf itself
        #
        data = dict(title='Trigonometry_1', video_url='youtube.com', category=w_cat.id)
        response_2 = self.client.post('/edit_worksheet/1', follow_redirects=True, data=data, content_type='multipart/form-data')

        self.assertEqual(response_2.status_code, 200)

        worksheet_2 = Worksheet.query.filter_by(name='Trigonometry_1').first()

        self.assertNotEqual(worksheet_2, None)

        self.assertEqual(True, os.path.exists('test_1.pdf'))

        logout_author(self.client)

        os.remove('test_1.pdf')

    def test_add_worksheet_page_author_li(self):
        w_cat = WorksheetCategory(name='Math')

        db.session.add(w_cat)

        auth = Author(name='kody', email='kodyrogers21@gmail.com', about='I am a hacker',
                password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')

        db.session.add(auth)

        db.session.commit()

        login_author(self.client, email='kodyrogers21@gmail.com', password='RockOn')
        response = self.client.get('/add_worksheet', follow_redirects=False)
        self.assertEqual(response.status_code, 200)


        data = dict(title='trig', video_url='youtube.com', category=w_cat.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcdef"), 'test.pdf')

        response_1 = self.client.post('/add_worksheet', follow_redirects=True, data=data, content_type='multipart/form-data')

        worksheet = Worksheet.query.filter_by(name='trig').first()

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(worksheet, None)

        os.remove('test.pdf')

        logout_author(self.client)
        
    def test_edit_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        db.session.add(worksheet_cat)
        db.session.commit()

        response = self.client.get('/edit_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/edit_worksheet_category/1', follow_redirects=True, data=dict(name='yippe'))

        self.assertEqual(response_1.status_code, 200)

        edited_worksheet_category = WorksheetCategory.query.filter_by(name='yippe').first()

        self.assertNotEqual(edited_worksheet_category, None)
        
    def test_delete_worksheet_page_li(self):
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)

        db.session.commit()

        worksheet = Worksheet(pdf_url='test.pdf', name='tudoloods', author_id=1, author=auth_1, category_id=1, category=w_cat)

        options = { 'quiet': '' }

        pdfkit.from_string('MicroPyramid', 'test.pdf', options=options)

        self.assertEqual(True, os.path.exists('test.pdf'))

        db.session.add(worksheet)

        db.session.commit()

        response = self.client.get('/delete_worksheet/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        w = Worksheet.query.filter_by(name='tudoloods').first()

        self.assertEqual(w, worksheet)

        self.assertEqual(True, os.path.exists('test.pdf'))

        os.remove('test.pdf')

    def test_delete_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        db.session.add(worksheet_cat)
        db.session.commit()

        response = self.client.get('/delete_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        w_cat = WorksheetCategory.query.filter_by(name='jumbook').first()

        self.assertEqual(w_cat, None)
        
    def test_add_worksheet_category_page_li(self):
        response = self.client.get('/add_worksheet_category', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/add_worksheet_category', follow_redirects=True, data=dict(name='Math'))

        w_cat = WorksheetCategory.query.filter_by(name='Math')

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(w_cat, None)
        
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
        
    def test_worksheet_model(self) :
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

        assert worksheet in db.session

    def test_worksheet_category_model(self) :
        worksheet_cat = WorksheetCategory(name='jumbook')
        db.session.add(worksheet_cat)
        db.session.commit()

        assert worksheet_cat in db.session



if __name__ == "__main__":
    unittest.main()
    