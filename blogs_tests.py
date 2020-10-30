import unittest
from flask_testing import TestCase
from config import TestConfiguration
from app import create_app as c_app
import os
from flask import url_for, template_rendered
from app.models import Post, PostCategory
from app.database import db
from contextlib import contextmanager

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
        
    def test_delete_blog_category_page_li(self):
        p_cat = PostCategory(name='froots')

        db.session.add(p_cat)
        db.session.commit()

        response = self.client.get('/delete_blog_category/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        p_cat = PostCategory.query.filter_by(name='froots').first()

        self.assertEqual(p_cat, None)


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

if __name__ == "__main__":
    unittest.main()    
    