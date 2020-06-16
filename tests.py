import os
import io
import unittest
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy
from flask import session, url_for, template_rendered, current_app
from app.models import Worksheet, WorksheetCategory, Author, Post, PostCategory
from werkzeug.datastructures import MultiDict
from app.blogs.forms import PostForm
from app.database import db
from config import TestConfiguration
from app import create_app as c_app
from contextlib import contextmanager
import pdfkit

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
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        logout(self.client)


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

    def test_add_worksheet_page_li(self):
        w_cat = WorksheetCategory(name='Math')

        db.session.add(w_cat)

        auth = Author(name='kody', email='kodyrogers21@gmail.com', about='I am a hacker')

        db.session.add(auth)

        db.session.commit()

        response = self.client.get('/add_worksheet', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        data = dict(title='trig', video_url='youtube.com', category=w_cat.id, author=auth.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcdef"), 'test.pdf')

        response_1 = self.client.post('/add_worksheet', follow_redirects=True, data=data, content_type='multipart/form-data')

        worksheet = Worksheet.query.filter_by(name='trig').first()

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(worksheet, None)

        os.remove('test.pdf')



    def test_add_worksheet_category_page_li(self):
        response = self.client.get('/add_worksheet_category', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/add_worksheet_category', follow_redirects=True, data=dict(name='Math'))

        w_cat = WorksheetCategory.query.filter_by(name='Math')

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(w_cat, None)

    def test_add_author_page_li(self):
        response = self.client.get('/add_author', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/add_author', follow_redirects=True, data=dict(name='Kody', email='kodyrogers21@gmail.com', about='I am a hacker'))

        auth = Author.query.filter_by(name='Kody').first()

        self.assertEqual(response_1.status_code, 200)

        self.assertNotEqual(auth, None)

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
        author = Author(name='KJsa')
        db.session.add(author)
        db.session.commit()

        response = self.client.get('/edit_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 200)

        response_1 = self.client.post('/edit_author/1', follow_redirects=True, data=dict(name='yippe'))

        self.assertEqual(response_1.status_code, 200)

        edited_author = Author.query.filter_by(name='yippe').first()

        self.assertNotEqual(edited_author, None)

    def test_edit_worksheet_page(self) :
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf')
        db.session.add(auth_1)

        db.session.commit()

        data = dict(title='trig', video_url='youtube.com', category=w_cat.id, author=auth_1.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcdef"), 'test.pdf')

        response = self.client.post('/add_worksheet', follow_redirects=True, data=data, content_type='multipart/form-data')

        self.assertEqual(True, os.path.exists('test.pdf'))

        worksheet = Worksheet.query.filter_by(name='trig').first()

        self.assertEqual(response.status_code, 200)

        self.assertNotEqual(worksheet, None)

        #
        # Now make a new worksheet to add
        #
        data = dict(title='Trigonometry', video_url='youtube.com', category=w_cat.id, author=auth_1.id)

        data['worksheet_pdf'] = (io.BytesIO(b"abcd234ef"), 'test_1.pdf')

        response_1 = self.client.post('/edit_worksheet/1', follow_redirects=True, data=data, content_type='multipart/form-data')

        worksheet_1 = Worksheet.query.filter_by(name='Trigonometry').first()

        self.assertNotEqual(worksheet, None)

        self.assertEqual(worksheet.pdf_url, 'test_1.pdf')

        self.assertEqual(False, os.path.exists('test.pdf'))
        self.assertEqual(True, os.path.exists('test_1.pdf'))

        os.remove('test_1.pdf')





    def test_delete_worksheet_page_li(self):
        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf')
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

        self.assertEqual(w, None)

        self.assertEqual(False, os.path.exists('test.pdf'))

    def test_delete_worksheet_category_page_li(self):
        worksheet_cat = WorksheetCategory(name='jumbook')
        db.session.add(worksheet_cat)
        db.session.commit()

        response = self.client.get('/delete_worksheet_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        w_cat = WorksheetCategory.query.filter_by(name='jumbook').first()

        self.assertEqual(w_cat, None)

    def test_delete_blog_category_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        response = self.client.get('/delete_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        p_cat = PostCategory.query.filter_by(name='froots').first()

        self.assertEqual(p_cat, None)

    def test_delete_author_page_li(self):
        auth_1 = Author(name='Kidkaid')
        db.session.add(auth_1)
        db.session.commit()

        response = self.client.get('/delete_author/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        auth_1 = Author.query.filter_by(name='kidkaid').first()

        self.assertEqual(auth_1, None)

    def test_worksheet_page(self) :
        # worksheet page
        response = self.client.get('/worksheets_page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        w_cat = WorksheetCategory(name='dundk')
        db.session.add(w_cat)
        db.session.commit()


        auth_1 = Author(name='Kidkaidf')
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


        auth_2 = Author(name='Kidkafdidf')
        db.session.add(auth_2)
        auth_3 = Author(name='Kif')
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
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_10, worksheet_8, worksheet_6,  worksheet_4])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], url_for('worksheets.worksheets_page', author=2, category=None, page=1))
                self.assertEqual(context['prev_url'], None)

        #
        # Testing the first page of a category
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', category=2, author=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_10, worksheet_8, worksheet_6,  worksheet_4])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], url_for('worksheets.worksheets_page', category=2, author=None, page=1))
                self.assertEqual(context['prev_url'], None)


        #
        # Testing the second page of an author
        #
        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=2, category=None, page=1))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_2])
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
                self.assertEqual(context['worksheets'], [worksheet_2])
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
                self.assertEqual(context['worksheets'], [worksheet_7, worksheet_6, worksheet_5, worksheet_4, worksheet_3])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=2))
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=0))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=2))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_2, worksheet_1, worksheet])
                self.assertEqual(context['categories'], [w_cat, w_cat_1, w_cat_2])
                self.assertEqual(context['next_url'], None)
                self.assertEqual(context['prev_url'], url_for('worksheets.worksheets_page', author=None, category=None, page=1))

        with self.app.test_client() as c:
            with captured_templates(self.app) as templates:
                r = c.get(url_for('worksheets.worksheets_page', author=None, worksheet=None, category=None, page=0))
                template, context = templates[0]
                self.assertEqual(context['worksheets'], [worksheet_12, worksheet_11, worksheet_10, worksheet_9, worksheet_8])
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



    def test_other_database_pages(self):
        # contact page
        auth_1 = Author(name='Kidkaidf')
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

        db.session.add(p_cat)
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
                logout(c)



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

    def test_admin_page(self):
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(response.status_code, 302)



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

    ##############################
    ### Testing Error Views ######
    ##############################

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




if __name__ == "__main__":
    unittest.main()
