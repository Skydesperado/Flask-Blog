from flask import request, render_template, redirect, url_for, flash

from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.exceptions import HTTPException

from blog import app, db, bcrypt
from blog.models.user import User, UserAction
from blog.models.post import Post
from blog.models.comment import Comment

from blog.forms.authentication.login import LoginForm
from blog.forms.authentication.register import RegisterForm
from blog.forms.update.profile import UpdateProfileForm
from blog.forms.update.post import UpdatePostForm
from blog.forms.update.comment import UpdateCommentForm
from blog.forms.create.post import CreatePostForm
from blog.forms.create.comment import CreateCommentForm
from blog.forms.reset.request import ResetPasswordRequestForm
from blog.forms.reset.password import ResetPasswordForm

from blog.utilities.save.profilepicture import save_profile_picture
from blog.utilities.save.postpicture import save_post_picture
from blog.utilities.email.reset.password import send_reset_password_email
from blog.utilities.errors.http_403 import HTTP_403
from blog.utilities.errors.http_404 import HTTP_404


@app.route("/", methods=["GET"])
def home():
    try:
        page = request.args.get("page", 1, type=int)
        posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/home.html", posts=posts, popular_posts=popular_posts, title="Home")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/explore/", methods=["GET"])
def explore():
    popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
    return render_template("inc/explore.html", popular_posts=popular_posts)

@app.route("/search/", methods=["GET"])
def search():
    try:
        query = request.args.get("query", "").strip()
        if not query:
            flash("Please Enter a Search Query", "info")
            return redirect(url_for("home"))
        page = request.args.get("page", 1, type=int)
        posts = Post.query.filter(Post.title.ilike(f"%{query}%")).order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
        if not posts.items:
            flash(f"No Posts Round For Query: {query}", "info")
            return redirect(url_for("home"))
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/search.html", posts=posts, query=query, popular_posts=popular_posts, title=f"Search: {query}")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/about/", methods=["GET"])
def about():
    try:
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/about.html", popular_posts=popular_posts, title="About")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("about"))

@app.route("/posts/<string:username>/", methods=["GET"])
def user_posts(username):
    try:
        page = request.args.get("page", 1, type=int)
        user = User.query.filter_by(username=username).first_or_404()
        posts = Post.query.filter_by(author=user).order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/user/posts.html", user=user, posts=posts, popular_posts=popular_posts, title=f"{username}'s Posts")
    except HTTPException as http_exception:
        return HTTP_404(http_exception.code)
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/profile/", methods=["GET", "POST"])
@login_required
def user_profile():
    try:
        form = UpdateProfileForm()
        if form.validate_on_submit():
            if form.profile_picture.data:
                profile_picture = save_profile_picture(form.profile_picture.data)
                current_user.profile_picture = profile_picture
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Profile Updated Successfully!", "success")
            return redirect(url_for("user_profile"))
        elif request.method == "GET":
            form.username.data = current_user.username
            form.email.data = current_user.email
        profile_picture = url_for("static", filename="images/uploads/" + current_user.profile_picture)
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/user/profile.html", form=form, profile_picture=profile_picture, popular_posts=popular_posts, title="Profile")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/register/", methods=["GET", "POST"])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            user = User(username=form.username.data,email=form.email.data.lower(), password=hashed_password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Registered Successfully!", "success")
            return redirect(url_for("home"))
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/forms/authentication/register.html", form=form, popular_posts=popular_posts, title="Register")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/login/", methods=["GET", "POST"])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash("Logged In Successfully!", "success")
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Login Unsuccessful, Please Check Email and Password")
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/forms/authentication/login.html", form=form, popular_posts=popular_posts, title="Login")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/logout/", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("Logged Out", "success")
    return redirect(url_for("home"))

@app.route("/create/post/", methods=["GET", "POST"])
@login_required
def create_post():
    try:
        form = CreatePostForm()
        if form.validate_on_submit():
            post_picture = None
            if form.post_picture.data:
                post_picture = save_post_picture(form.post_picture.data)
            post = Post(author=current_user, title=form.title.data, content=form.content.data, post_picture=post_picture)
            db.session.add(post)
            db.session.commit()
            flash("Post Created Successfully!", "success")
            return redirect(url_for("home"))
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/forms/posts/create/post.html", form=form, popular_posts=popular_posts, title="Create Post")
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/post/<int:post_id>/", methods=["GET", "POST"])
def retrieve_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        form = CreateCommentForm()
        if form.validate_on_submit():
            comment = Comment(author=current_user, post=post, content=form.content.data)
            db.session.add(comment)
            db.session.commit()
            flash("Commented Successfully!", "success")
            return redirect(url_for("retrieve_post", post_id=post.id))
        comments = post.comments.order_by(Comment.created_at.desc()).all()
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/post.html", post=post, form=form, comments=comments, popular_posts=popular_posts, title="Post Detail")
    except HTTPException as http_exception:
        return HTTP_404(http_exception.code)
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/update/post/<int:post_id>/", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        if current_user != post.author:
            return HTTP_403(403)
        form = UpdatePostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Post Updated Successfully!", "success")
            return redirect(url_for("retrieve_post", post_id=post.id))
        elif request.method == "GET":
            form.title.data = post.title
            form.content.data = post.content
        popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
        return render_template("blog/forms/posts/update/post.html", post=post, form=form, popular_posts=popular_posts, title="Update Post")
    except HTTPException as http_exception:
        return HTTP_404(http_exception.code)
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/delete/post/<int:post_id>/", methods=["GET"])
@login_required
def delete_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        if current_user != post.author:
            return HTTP_403(403)
        db.session.delete(post)
        db.session.commit()
        flash("Post Deleted Successfully!", "success")
        return redirect(url_for("home"))
    except HTTPException as http_exception:
        return HTTP_404(http_exception.code)
    except Exception as exception:
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/upvote/post/<int:post_id>/", methods=["GET"])
@login_required
def upvote(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        user_action = UserAction.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if user_action:
            if user_action.action == "downvote":
                user_action.action = "upvote"
                post.upvotes += 1
                post.downvotes -= 1
            elif user_action.action == "upvote":
                db.session.delete(user_action)
                post.upvotes -= 1
        else:
            user_action = UserAction(user_id=current_user.id, post_id=post_id, action="upvote")
            db.session.add(user_action)
            post.upvotes += 1
        db.session.commit()
        next_url = request.referrer or url_for("home")
        return redirect(next_url)
    except HTTPException as http_exception:
        return HTTP_404(http_exception.code)
    except Exception as exception:
        db.session.rollback()
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/downvote/post/<int:post_id>/", methods=["GET"])
@login_required
def downvote(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        user_action = UserAction.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if user_action:
            if user_action.action == "upvote":
                user_action.action = "downvote"
                post.upvotes -= 1
                post.downvotes += 1
            elif user_action.action == "downvote":
                db.session.delete(user_action)
                post.downvotes -= 1
        else:
            user_action = UserAction(
                user_id=current_user.id, post_id=post_id, action="downvote")
            db.session.add(user_action)
            post.downvotes += 1
        db.session.commit()
        next_url = request.referrer or url_for("home")
        return redirect(next_url)
    except HTTPException as http_exception:
        return HTTP_404(http_exception.code)
    except Exception as exception:
        db.session.rollback()
        flash(f"An Error Occurred: {str(exception)}", "danger")
        return redirect(url_for("home"))

@app.route("/update/comment/<int:comment_id>/", methods=["GET", "POST"])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        return HTTP_403(403)
    form = UpdateCommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash("Comment Updated Successfully!", "success")
        return redirect(url_for("retrieve_post", post_id=comment.post.id))
    elif request.method == "GET":
        form.content.data = comment.content
    popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
    return render_template("blog/forms/comments/update/comment.html", form=form, popular_posts=popular_posts, title="Update Comment")

@app.route("/delete/comment/<int:comment_id>/", methods=["GET"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        return HTTP_403(403)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    flash("Comment Deleted Successfully!", "success")
    return redirect(url_for("retrieve_post", post_id=post_id))

@app.route("/reset/password/request/", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        send_reset_password_email(user)
        flash("An Email Has Been Sent With Instructions To Reset Your Password", "success")
        return redirect(url_for("login"))
    popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
    return render_template("blog/forms/reset/request.html", form=form, popular_posts=popular_posts, title="Reset Password Request")

@app.route("/reset/password/<token>/", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_password_token(token)
    if user is None:
        flash("Invalid or Expired Reset Password Token", "warning")
        return redirect(url_for("reset_password_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Password Updated Successfully!", "success")
        return redirect(url_for("login"))
    popular_posts = db.session.query(Post).order_by((Post.upvotes - Post.downvotes).desc()).limit(3).all()
    return render_template("blog/forms/reset/password.html", form=form, popular_posts=popular_posts, title="Reset Password")
