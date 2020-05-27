import os
import unittest
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy
from flask import session, url_for
from app.models import Worksheet, WorksheetCategory, Author, Post, PostCategory

from app.database import db
from config import TestConfiguration
from app import create_app as c_app

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)



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

    def test_worksheet_model(self) :
        w_cat = WorksheetCategory(name='dunk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaid')
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

    def test_author_model(self) :
        author = Author(name='KJsa')
        db.session.add(author)
        db.session.commit()

        assert author in db.session

    ################################
    #### Testing the Edit Views ####
    ################################






class TestingWhileLoggedIn(TestCase):
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


    def test_add_post_page_li(self):
        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/add_post', follow_redirects=False)
        self.assertEqual(response.status_code, 200)


    def test_add_blog_category_page_li(self):
        login(self.client, 'LLLRocks', 'h0ngk0ng')
        response = self.client.get('/add_blog_category', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_add_worksheet_page_li(self):
        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/add_worksheet', follow_redirects=False)
        self.assertEqual(response.status_code, 200)



    def test_add_worksheet_category_page_li(self):
        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/add_worksheet_category', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_add_author_page_li(self):
        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/add_author', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        db.session.add(post)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/edit_post/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_delete_post_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        post = Post(name='Hello', content='3fhskajlga', category_id=1, category=p_cat)
        db.session.add(post)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/delete_post/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        assert post not in db.session


    def test_edit_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        db.session.add(worksheet_cat)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/edit_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)


    def test_edit_blog_category_page_li(self):
        post_cat = PostCategory(name='tudoloos')
        db.session.add(post_cat)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/edit_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_edit_author_page_li(self):
        author = Author(name='KJsa')
        db.session.add(author)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/edit_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    def test_delete_worksheet_page_li(self):
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf')
        db.session.add(auth_1)

        db.session.commit()

        worksheet = Worksheet(pdf_url='tudolsoos.pdf', name='tudoloods', author_id=1, author=auth_1, category_id=1, category=w_cat)
        db.session.add(worksheet)

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        db.session.commit()

        response = self.client.get('/delete_worksheet/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        db.session.add(worksheet_cat)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/delete_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_blog_category_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/delete_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_delete_author_page_li(self):
        auth_1 = Author(name='Kidkaid')
        db.session.add(auth_1)
        db.session.commit()

        login(self.client, 'LLLRocks', 'h0ngk0ng')

        response = self.client.get('/delete_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_worksheet_page(self):
        response = self.client.get('/worksheets_page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_blog_page(self):
        response = self.client.get('/blog', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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

    #############################
    #### testing Other Pages ####
    #############################

    def test_main_page(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_main_page_home(self):
        response = self.client.get('/home', follow_redirects=True)
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




    ###################################
    ### Testing the Worksheet Views ###
    ###################################

    # Checking if any have 404s


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
