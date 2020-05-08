#
# If time permits the database and views should be tested together
#
# Need more work on this file
#

#
# Potentially Useful Links
# https://www.patricksoftwareblog.com/unit-testing-a-flask-application/
# https://flask.palletsprojects.com/en/1.1.x/testing/
# https://damyanon.net/post/flask-series-testing/
# https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1
# https://pythonhosted.org/Flask-Testing/
# https://www.rithmschool.com/courses/flask-fundamentals/testing-with-flask
#
# project/test_basic.py
import os
import unittest
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy
from flask import session, url_for
from app.models import Worksheet, WorksheetCategory, Author, Post, PostCategory

from run import app
from app import db

from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app import models

class DatabaseTests(TestCase):

    ############################
    #### setup and teardown ####
    ############################

    def create_app(self):
        app.config.from_object('config.TestConfiguration')

        return app

    # executed prior to each test
    def setUp(self):
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        self.session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.engine))
        Base.query = self.session.query_property()

        Base.metadata.create_all(bind=self.engine)

    # executed after each test
    def tearDown(self):
        self.session.remove()
        Base.metadata.drop_all(self.engine)

    def test_Post_model(self) :

        p_cat = PostCategory(name='froots')

        self.session.add(p_cat)
        self.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        self.session.add(post)
        self.session.commit()

        assert post in self.session

    def test_blog_category_model(self) :
        post_cat = PostCategory(name='tudoloos')
        self.session.add(post_cat)
        self.session.commit()

        assert post_cat in self.session

    def test_worksheet_model(self) :
        w_cat = WorksheetCategory(name='dunk')
        self.session.add(w_cat)
        self.session.commit()


        auth_1 = Author(name='Kidkaid')
        self.session.add(auth_1)
        self.session.commit()

        worksheet = Worksheet(pdf_url='tudoloos.pdf', name='tudoloos', author_id=1, author=auth_1, category_id=1, category=w_cat)
        self.session.add(worksheet)
        self.session.commit()

        assert worksheet in self.session

    def test_worksheet_category_model(self) :
        worksheet_cat = WorksheetCategory(name='jumbook')
        self.session.add(worksheet_cat)
        self.session.commit()

        assert worksheet_cat in self.session

    def test_author_model(self) :
        author = Author(name='KJsa')
        self.session.add(author)
        self.session.commit()

        assert author in self.session

    ################################
    #### Testing the Edit Views ####
    ################################

    def test_edit_post_page_li(self):
        p_cat = PostCategory(name='froots')

        self.session.add(p_cat)
        self.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        self.session.add(post)
        self.session.commit()
        self.session.close()
        self.session.remove()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/edit_post/1', follow_redirects=False)
            self.assertEqual(response.status_code, 200)

    def test_delete_post_page_li(self):
        p_cat = PostCategory(name='froots')

        self.session.add(p_cat)
        self.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        self.session.add(post)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/delete_post/1', follow_redirects=False)
            self.assertEqual(response.status_code, 302)

        assert post not in self.session


    def test_edit_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        self.session.add(worksheet_cat)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/edit_worksheet_category/1', follow_redirects=False)
            self.assertEqual(response.status_code, 200)


    def test_edit_blog_category_page_li(self):
        post_cat = PostCategory(name='tudoloos')
        self.session.add(post_cat)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/edit_blog_category/1', follow_redirects=False)
            self.assertEqual(response.status_code, 200)

    def test_edit_author_page_li(self):
        author = Author(name='KJsa')
        self.session.add(author)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/edit_author/1', follow_redirects=False)
            self.assertEqual(response.status_code, 200)

    def test_delete_worksheet_page_li(self):
        w_cat = WorksheetCategory(name='dundk')
        self.session.add(w_cat)
        self.session.commit()


        auth_1 = Author(name='Kidkaidf')
        self.session.add(auth_1)

        self.session.commit()

        worksheet = Worksheet(pdf_url='tudolsoos.pdf', name='tudoloods', author_id=1, author=auth_1, category_id=1, category=w_cat)
        self.session.add(worksheet)

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            self.session.commit()

            response = client.get('/delete_worksheet/1', follow_redirects=False)
            self.assertEqual(response.status_code, 302)

    def test_delete_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        self.session.add(worksheet_cat)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/delete_worksheet_category/1', follow_redirects=False)
            self.assertEqual(response.status_code, 302)

    def test_delete_blog_category_page_li(self):
        p_cat = PostCategory(name='froots')

        self.session.add(p_cat)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/delete_blog_category/1', follow_redirects=False)
            self.assertEqual(response.status_code, 302)

    def test_delete_author_page_li(self):
        auth_1 = Author(name='Kidkaid')
        self.session.add(auth_1)
        self.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/delete_author/1', follow_redirects=False)
            self.assertEqual(response.status_code, 302)



class BasicTests(TestCase):

    ############################
    #### setup and teardown ####
    ############################

    def create_app(self):
        app.config.from_object('config.TestConfiguration')
        return app

    # executed prior to each test
    def setUp(self):
        pass

    # executed after each test
    def tearDown(self):
        pass

    #############################
    #### testing Other Pages ####
    #############################

    def test_main_page(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_main_page_home(self):
        response = self.client.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    #######################
    #### testing Blogs ####
    #######################

    def test_blog_page(self):
        response = self.client.get('/blog', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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

    # Now testing the behaviour when the user is logged in.

    def test_add_post_page_li(self):
        with app.test_client() as client:
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['logged_in'] = True

                response = client.get('/add_post', follow_redirects=False)
                self.assertEqual(response.status_code, 200)





    def test_add_blog_category_page_li(self):
        with app.test_client() as client:
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['logged_in'] = True

                response = client.get('/add_blog_category', follow_redirects=False)
                self.assertEqual(response.status_code, 200)




    ###################################
    ### Testing the Worksheet Views ###
    ###################################

    # Checking if any have 404s
    def test_worksheet_page(self):
        response = self.client.get('/worksheets_page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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

    def test_add_author_page_r(self):
        response = self.client.get('/add_author', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_edit_author_page_r(self):
        response = self.client.get('/edit_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_author_page_r(self):
        response = self.client.get('/delete_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    # Checking if logged in whether a 200 is found without a redirect

    def test_add_worksheet_page_li(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/add_worksheet', follow_redirects=False)
            self.assertEqual(response.status_code, 200)



    def test_add_worksheet_category_page_li(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/add_worksheet_category', follow_redirects=False)
            self.assertEqual(response.status_code, 200)





    def test_add_author_page_li(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True

            response = client.get('/add_author', follow_redirects=False)
            self.assertEqual(response.status_code, 200)





    ##############################
    ### Testing the Auth Views ###
    ##############################

    def test_login_page(self):
        response = self.client.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_logout_page(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)




if __name__ == "__main__":
    unittest.main()
