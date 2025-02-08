from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

from forms import LoginForm, SignUpForm, JournalForm, ChangePasswordForm, UpdateEmailForm
from models import db, User, JournalEntry

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Incorrect password. Please try again.', 'error')
        else:
            flash('Email not found. Please try again.', 'error')

    return render_template('login.html', form=form)

@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('signup.html', form=form)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/write', methods=['GET', 'POST'])
@login_required
def write_journal():
    form = JournalForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_entry = JournalEntry(
            user_id=current_user.id,
            date=date.today(),
            prompt=("How did you feel today, what was the highlight or challenge, "
                    "what have you accomplished, and what are you grateful for or learned?"), 
            entry=form.entry.data
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('write_journal.html', form=form)

@main_bp.route('/view')
@login_required
def view_journals():
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date.desc()).all()
    return render_template('view_journals.html', entries=entries)

@main_bp.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = JournalEntry.query.get(entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()

    return redirect(url_for('main.view_journals'))

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)

    if user:
        JournalEntry.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        logout_user()

        return redirect(url_for('main.index'))

    return redirect(url_for('main.settings'))

@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data

        if not check_password_hash(current_user.password, current_password):
            return redirect(url_for('main.change_password'))

        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('main.settings'))
    
    return render_template('change_password.html', form=form)

@main_bp.route('/update_email', methods=['GET', 'POST'])
@login_required
def update_email():
    form = UpdateEmailForm()

    if form.validate_on_submit():
        new_email = form.new_email.data
        current_password = form.current_password.data

        if not check_password_hash(current_user.password, current_password):
            return redirect(url_for('main.update_email'))
        current_user.email = new_email
        db.session.commit()
        flash('Your email has been updated successfully.', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('update_email.html', form=form)