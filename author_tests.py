import unittest
from flask_testing import TestCase
from config import TestConfiguration
from app import create_app as c_app
import os
from flask import session, url_for, template_rendered
from app.models import Author, Worksheet, WorksheetCategory
from app.database import db
from contextlib import contextmanager

from werkzeug.security import generate_password_hash, check_password_hash

def login_author(client, email, password):
    return client.post('/author_login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout_author(client):
    return client.get('/author_logout', follow_redirects=True)

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
        
        
    #########################################
    ####### Tests For Pages Admin Uses ######
    #########################################
    
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
        
    #########################################
    ###### Tests For Pages Author Uses ######
    #########################################
    
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


    def test_delete_author_page_li(self):
        auth_1 = Author(name='Kidkaid', email='kodyrogers21@gmail.com', password='pbkdf2:sha256:150000$73fMtgAp$1a1d8be4973cb2676c5f17275c43dc08583c8e450c94a282f9c443d34f72464c')
        db.session.add(auth_1)
        db.session.commit()

        response = self.client.get('/delete_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        auth_1 = Author.query.filter_by(name='kidkaid').first()

        self.assertEqual(auth_1, None)
        
        
    #########################################
    ###### Tests For Pages Author Uses ######
    #########################################
    
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
            self.assertEqual(session['author_logged_in'], True)

            self.assertEqual(session['author_name'], 'KJsa')

            response_1 = c.get('/author_logout', follow_redirects=True)
            self.assertEqual(response_1.status_code, 200)
            self.assertEqual(session['author_logged_in'], False)
            

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
        
    def test_author_model(self) :
        author = Author(name='KJsa', email='kodyrogers21@gmail.com', screenname='kod',
                        about='What up?', password='pbkdf2:sha256:150000$CgCWVBC6$4090facdcd3e093c7b458362daddbaa7b53387c6042ad46b5970dc7b6d00183c')
        db.session.add(author)
        db.session.commit()

        assert author in db.session
        
        
if __name__ == "__main__":
    unittest.main()            
