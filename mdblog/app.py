from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import g
from flask import flash

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import TextAreaField
from wtforms.validators import InputRequired

from .models import db
from .models import Article
from .models import User

# import sqlite3
import os


#DATABASE = "/vagrant/blog.db" #dame do osobitne default file-u

flask_app = Flask(__name__)


flask_app.config.from_pyfile("/vagrant/configs/default.py")

#if "MDBLOG_CONFIG" in os.environ:
    #flask_app.config.from_envvar("MDBLOG_CONFIG")

db.init_app(flask_app)

## FORMS

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired()])


class ArticleForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content")

class ChangePasswordForm(FlaskForm):
    old_password = StringField("Old Password", validators=[InputRequired()])
    new_password = StringField("New Password", validators=[InputRequired()])


## CONTROLLERS


@flask_app.route("/")
def view_welcome_page():
    return render_template("welcome_page.jinja")

@flask_app.route("/about/")
def view_about():
    return render_template("about.jinja")

@flask_app.route("/admin/")
def view_admin():
    if "logged" not in session:
        flash("You must be logged in", "alert-danger")
        return redirect(url_for("view_login"))
    return render_template("admin.jinja")

## ARTICLES


@flask_app.route("/articles/")
def view_articles():
    #db = get_db()
    #cur = db.execute("select * from articles order by id desc")
    #articles = cur.fetchall()
    articles = Article.query.order_by(Article.id.desc())
    return render_template("articles.jinja", articles=articles)

@flask_app.route("/articles/new", methods=["GET"])
def view_add_article():
    if "logged" not in session:
        return redirect(url_for("view_login"))

    form = ArticleForm()
    return render_template("article_editor.jinja", form=form)

@flask_app.route("/articles/", methods=["POST"])
def add_article():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    add_form = ArticleForm(request.form)
    if add_form.validate():
        #db = get_db()
        #db.execute("insert into articles (title, content) values (?, ?)",
                #[request.form.get("title"), request.form.get("content")])
        #db.commit()
        new_article = Article(title = add_form.title.data, content = add_form.content.data)
        db.session.add(new_article)
        db.session.commit()
        flash("Article was saved", "alert-success")
        return redirect(url_for("view_articles"))
    else:
        for error in login_form.errors:
            flask("{} is missing".format(error), "alert-danger")
        return render_template("article_editor.jinja", form=add_form)

@flask_app.route("/articles/<int:art_id>/")
def view_article(art_id):
    #db = get_db()
    #cur = db.execute("select * from articles where id=(?)",[art_id])
    #article = cur.fetchone()
    article = Article.query.filter_by(id=art_id).first()
    if article:
        return render_template("article.jinja", article=article)
    return render_template("article_not_found.jinja", art_id=art_id)

@flask_app.route("/articles/<int:art_id>/edit", methods=["GET"])
def view_article_editor(art_id):
    if "logged" not in session:
        return redirect(url_for("view_login"))
    #db = get_db()
    #cur = db.execute("select * from articles where id=(?)",[art_id])
    #article = cur.fetchone()
    article = Article.query.filter_by(id=art_id).first()
    if article:
        form = ArticleForm()
        form.title.data = article.title
        form.content.data = article.content
        return render_template("article_editor.jinja", form=form, article=article)
    return render_template("article_not_found.jinja", art_id=art_id)


@flask_app.route("/articles/<int:art_id>/edit", methods=["POST"])
def edit_article(art_id):
    if "logged" not in session:
        return redirect(url_for("view_login"))
    #db = get_db()
    #cur = db.execute("select * from articles where id=(?)",[art_id])
    #article = cur.fetchone()
    article = Article.query.filter_by(id=art_id).first()
    if article:
        edit_form = ArticleForm(request.form)
        if edit_form.validate():
            #db.execute("update articles set title=?, content=? where id=?", [edit_form.title.data, edit_form.content.data, art_id])
            #db.commit()
            article.title = edit_form.title.data
            article.content = edit_form.content.data
            db.session.add(article)
            db.session.commit()
            flash("Edit saved", "alert-success")
            return redirect(url_for("view_article", art_id=art_id))
        else:
            for error in login_form.errors:
                flask("{} is missing".format(error), "alert-danger")
            return redirect(url_for("view_login"))

## USER RELATED

@flask_app.route("/login/", methods=["GET"])
def view_login():
    login_form = LoginForm()
    return render_template("login.jinja", form=login_form)

@flask_app.route("/login/", methods=["POST"])
def login_user():
    login_form = LoginForm(request.form)
    if login_form.validate():
        user = User.query.filter_by(username = login_form.username.data).first()
        if user and user.check_password(login_form.password.data):
        # if login_form.username.data == flask_app.config["USERNAME"] and \
        #         login_form.password.data == flask_app.config["PASSWORD"]:
            session["logged"] = user.username
            flash("login succesfull", "alert-success")
            return redirect(url_for("view_admin"))
        else:
            flash("Invalid credential", "alert-danger")
            return render_template("login.jinja", form=login_form)

    else:
        for error in login_form.errors:
            flash("{} is missing".format(error), "alert-danger")
        return redirect(url_for("view_login"))

@flask_app.route("/changepassword/", methods=["GET"])
def view_change_password():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    form = ChangePasswordForm()
    return render_template("change_password.jinja", form=form)

@flask_app.route("/changepassword/", methods=["POST"])
def change_password():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    form = ChangePasswordForm()
    if form.validate():
        user = User.query.filter_by(username = session["logged"]).first()
        if user and user.check_password(form.old_password.data):
            user.set_password(form.new_password.data)
            db.session.add(user)
            db.session.commit()
            flash("Password changed!", "alert-success")
            return redirect(url_for("view_admin"))
        else:
            flash("Invalid credentials", "alert-danger")
            return render_template("change_password.jinja", form=form)
    else:
        for error in login_form.errors:
            flash("{} is missing".format(error), "alert-danger")
        return render_template("change_password.jinja", form=form)

@flask_app.route("/logout/", methods=["POST"])
def logout_user():
    session.pop("logged")
    flash("Logout successful")
    return redirect(url_for("view_welcome_page"))

## CLI COMMAND

def init_db(app):
    with app.app_context():
        db.create_all()
        print("database inicialized")

        default_user = User(username="admin")
        default_user.set_password("admin")

        db.session.add(default_user)
        db.session.commit()
        print("default user was created")
