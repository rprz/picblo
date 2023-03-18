import os
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, Picture
from app.forms import LoginForm, RegistrationForm, UploadForm

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
    pictures = Picture.query.order_by(Picture.timestamp.desc()).all()
    return render_template('index.html', pictures=pictures)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            logging.info(f'Successful login: {user.username}')
            return redirect(next_page)
        else:
            flash('Invalid username or password')
            logging.info('Failed login attempt')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        logging.info(f'Successful registration: {user.username}')
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            logging.info('Failed registration attempt')
    return render_template('register.html', title='Register', form=form)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            picture = Picture(image=filepath, user=current_user)
            db.session.add(picture)
            db.session.commit()
            flash('Image uploaded successfully.')
            return redirect(url_for('index'))
        else:
            flash('Allowed image types are: png, jpg, jpeg, gif')
    return render_template('upload.html', title='Upload', form=form)

@app.route('/vote/<int:picture_id>/<int:vote_value>')
@login_required
def vote(picture_id, vote_value):
    picture = Picture.query.get(picture_id)
    if picture:
        picture.votes += vote_value
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/users')
# @login_required
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)
