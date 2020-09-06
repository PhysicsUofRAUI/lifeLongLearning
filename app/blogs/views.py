from . import blogs
from flask import render_template, session, redirect, url_for, current_app, request
from ..models import Post, PostCategory
from .forms import PostForm, PostCategoryForm
from .. import db

#
# Blog
#   Description:
#       This is the view that will handle requests from users to look at blogs.
#       There is three paths:
#       1. A specific blog is requested and that is the only post sent to the template
#       2. A specific category is requested and all the posts from that category are
#       displayed along with pagination (the next_url and prev_url stuff).
#       3. Niether a category or a specific post is requested so all posts are sent out.
#
#   Variables:
#       post: The id of specific post if a specific post is selected. Default is None
#
#       category: The id of a specific category that has been selected. Default is None
#
#       page: the page number that is being requested. First page is 'page=0' and
#           the second page is 'page=1'. Each page will show 5 blog posts and the posts
#           will be in descending order (first posted to last posted)
#
@blogs.route('/blog/<int:page>', methods=['GET', 'POST'])
@blogs.route('/blog', defaults={'page' : 0}, methods=['GET', 'POST'])
def blog(page) :
    try :
        categories = PostCategory.query.all()
        post = request.args.get('post')
        category = request.args.get('category')
    except:
        db.session.rollback()
        return redirect(url_for('other.home'))

    if not post == None :
        try :
            # if a specific post has been selected this if statement will be ran
            blog = Post.query.get(post)

            posts = [blog]
        except:
            db.session.rollback()
            return redirect(url_for('other.home'))

        return render_template('blog.html.j2', posts=posts, categories=categories, next_url=None, prev_url=None)

    elif not category == None :
        try :
            # if a specific category has been selected this if statement will be ran
            posts = Post.query.filter_by(category_id=category).order_by(Post.id.desc()).offset(page * 5).limit(5).all()

            more = Post.query.filter_by(category_id=category).offset((page + 1) * 5).first()
        except:
            db.session.rollback()
            return redirect(url_for('other.home'))

        prev_url = None
        next_url = None
        if not page == 0 :
            prev_url = url_for('blogs.blog', category=category, page=page - 1, post=None)

        if not more == None :
            next_url = url_for('blogs.blog', post=None, category=category, page=page + 1)


        return render_template('blog.html.j2', posts=posts, categories=categories, next_url=next_url, prev_url=prev_url)

    else :
        try :
            # if a no specific post or category has been selected this if statement will be ran
            posts = Post.query.order_by(Post.id.desc()).offset(page * 5).limit(5).all()

            more = Post.query.offset((page + 1) * 5).first()
        except:
            db.session.rollback()
            return redirect(url_for('other.home'))

        prev_url = None
        next_url = None
        if not page == 0 :
            prev_url = url_for('blogs.blog', category=category, page=page - 1, post=None)

        if not more == None :
            next_url = url_for('blogs.blog', post=None, category=category, page=page + 1)

        return render_template('blog.html.j2', posts=posts, categories=categories, next_url=next_url, prev_url=prev_url)



#
# Add Post
# Description:
#   This view adds a post to the database. It will call the add_post template and
#   then the user will fill in the fieds required on the form that is presented.
#   It will then be added to the database to be called by the previously described
#   views that display blog posts.
#
@blogs.route('/add_post', methods=['GET', 'POST'])
def add_post():
    """
    Add a blog post
    """
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    form = PostForm()


    if form.validate_on_submit():
        try:
            new_post = Post(name=form.title.data, content=form.content.data, category_id=form.category.data.id, category=form.category.data)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('other.home'))
        except:
            db.session.rollback()
            raise

    return render_template('add_post.html.j2', form=form)

#
# Edit Post
# Description:
#   The following is the view that will allow the user to edit a blog post. The
#   user will first be directed to the edit_post template (form.validate_on_submit()=False)
#   after the user fills the form the database will be updated (form.validate_on_submit()=True).
#   The edits will now be uploaded instead of the old version in the previously
#   explained views that load blog posts.
#
@blogs.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    """
    Edit a blog post
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    post = Post.query.get(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        try :
            post.name = form.title.data
            post.content = form.content.data
            post.category_id = form.category.data.id
            post.category = form.category.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('other.home'))
        except :
            db.session.rollback()
            raise

    form.content.data = post.content
    form.title.data = post.name
    form.category.data = post.category
    return render_template('edit_post.html.j2', form=form, post=post, title="Edit Post")

#
# Delete Post
# Description:
#   This is a view that will delete a post. The id that is passed in is that of the
#   post that will be deleted.
#
@blogs.route('/delete_post/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    try :
        post = Post.query.get(id)
        db.session.delete(post)
        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise

#
# Add PostCategory
# Description:
#   This view adds a category to the database. It will call the add_category
#   template and then the user will specify the name of the new category.
#
@blogs.route('/add_blog_category', methods=['GET', 'POST'])
def add_blog_category():
    """
    Add a category for blog posts
    """
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    form = PostCategoryForm()

    if form.validate_on_submit():
        try:
            new_category = PostCategory(name=form.name.data)
            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('other.home'))
        except:
            db.session.rollback()
            raise



    return render_template('add_blog_category.html.j2', form=form)

#
# edit_blog_category
#   allow the user to edit a blog Category
#
@blogs.route('/edit_blog_category/<int:id>', methods=['GET', 'POST'])
def edit_blog_category(id) :
    """
    Edit a blog category
    """

    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    category = PostCategory.query.get(id)
    form = PostCategoryForm(obj=category)

    if form.validate_on_submit():
        try :
            category.name = form.name.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('other.home'))
        except :
            db.session.rollback()
            raise

    form.name.data = category.name

    return render_template('edit_blog_category.html.j2', form=form, category=category, title="Edit Blog Category")

#
# delete_blog_category
#   allow the user to delete a blog Category
#
@blogs.route('/delete_blog_category/<int:id>', methods=['GET', 'POST'])
def delete_blog_category(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    try :
        category = PostCategory.query.get(id)
        db.session.delete(category)
        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise
