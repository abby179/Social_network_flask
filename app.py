from flask import Flask, g, render_template, url_for, redirect, flash
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import forms
import models

app = Flask(__name__)
app.secret_key = '08\x9d\xbd-.\r \xa9\xf6\xea\t|\xdd\xbf\x07\x19\x95\x18\x91\x92\xf0r\x8e'

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'


@loginManager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """close the database connection after each request"""
    g.db.close()
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered successfully", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Your email or password does not match!', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password does not match!', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user.get_current_object(),
                           content=form.content.data)
        flash("Message posted!", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/')
def index():
    return 'Hello'


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(username='yaxizhang', email='abbyzhang2015@hotmail.com', password='password', admin=True)
    except ValueError:
        pass
    app.run(debug=True)
