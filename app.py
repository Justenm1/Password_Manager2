"""A flask madel of a password manager that
   allows you to create and delete passwords."""

from socket import gethostname
from flask import render_template, session, redirect, url_for, request, flash

from modules.globals import app, db
from modules.helpers import (logged_in, create_session, verify_pw, encrypt,
                             decrypt)
from modules.db_Classes import Credentials, UserEntryCloud
from sys import getsizeof

@app.route('/')
def index():
    """The home page of the website.

        If the user is not logged in, it redirects them to login page.
        The home contains a table of the user's passwords for their
        respective websites."""

    app.logger.info('index: user at home page')

    if not logged_in():
        return redirect(url_for('login'))

    cloud_query = db.session.execute(db.select(UserEntryCloud)).scalars().all()
    print(cloud_query)
    entryids = db.session.execute(db.select(UserEntryCloud).where(
        UserEntryCloud.user_id == session['id']))
    for entry in entryids.scalars():
        print(entry)


    rolecheck = session['role']
    idcheck = session['id']
    print(rolecheck)
    print(idcheck)





    return render_template('index.html',
                           rolecheck=rolecheck,
                           idcheck=idcheck,
                           session=session,
                           userentries=cloud_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Log the user into the website

        If the user is already logged in, redirect them to the home page,
        otherwise show them the login page.
    """

    app.logger.info("login: user at login page")

    if logged_in():
        return redirect(url_for('index'))

    if request.method == "POST":

        # check if the user exists in the database
        account = db.session.execute(db.select(Credentials).where(
            Credentials.username == request.form['username'])).scalars().first()

        if account is None:
            flash("Invalid credentials", "error")
        elif account.role == 'H':
                if verify_pw(account.password, request.form['password']):
                    create_session(account.user_id, account.username, account.role)
                    # flash("Successfully logged in", "success")
                    return redirect(url_for('index'))
        else:
            passwordtodecrypt = db.session.execute(db.select(Credentials.password).where(
                Credentials.username == request.form['username'])).scalars().first()
            print(passwordtodecrypt)
            ivtobeused = db.session.execute(db.select(Credentials.iv).where(
                Credentials.username == request.form['username'])).scalars().first()
            print(account.password)
            print(account.iv)
            print(getsizeof(account.iv))
            print(ivtobeused)
            if decrypt(passwordtodecrypt, ivtobeused) == str.encode(request.form['password']):
                create_session(account.user_id, account.username, account.role)
                # flash("Successfully logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials", "error")



    return render_template('login.html', session=session)


@app.route('/logout')
def logout():
    """ Log the user out of the website

        If the user is not logged in, redirect them to the login page,
        otherwise clear the session cookie stored on their browser and
        redirect them to the login page.
    """
    app.logger.info("logout: user at logout page")

    if not logged_in():
        return redirect(url_for('login'))

    # remove session data to log the user out
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('role', None)
    session.pop('username', None)

    # redirect user to login page
    app.logger.info('logout: user logged out and redirected to login page')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Register a new user

        If the user is already logged in, redirect them to the home page,
        otherwise show them the register page.
    """
    app.logger.info("register: user at register page")

    if logged_in():
        return redirect(url_for('index'))

    if request.method == 'POST':

        # get account from database if it exists
        account = db.session.execute(db.select(Credentials).where(Credentials.username == request.form['username'])).scalars().first()


        if account is not None:
            flash("Account already exists", "error")
        elif request.form['password1'] != request.form['password2']:
            flash("Passwords do not match", "error")
        else:
            ciphertext, IV = encrypt(request.form['password1'])
            print(IV)
            user_id = db.session.execute(db.insert(Credentials).values(
                username=request.form['username'],
                password=ciphertext,
                role="R",
                iv = IV
            )).inserted_primary_key[0]
            db.session.commit()
            create_session(user_id, request.form['username'], "R")
            # flash("Account created successfully", "success")
            redirect(url_for('index'))


    return render_template('register.html')

@app.route('/create_user_entry', methods=['GET', 'POST'])
def create_user_entry():

    """Create a new patient file

        If the user is already logged in, redirect them to the home page,
        otherwise show them the create_user_entry page.
    """
    app.logger.info("create_user_entry: user at create_user_entry page")

    if not logged_in():
        return redirect(url_for('login'))

    if request.method == "POST":
        ciphertext, IV = encrypt(request.form['site_password'])
        print(ciphertext)
        print(IV)
        print(request.form['site_password'])

        new_entry = db.session.execute(db.insert(UserEntryCloud).values(
            user_id=session['id'],
            site_name=request.form["site_name"],
            site_username=request.form["site_username"],
            site_password=ciphertext,
            iv=IV
        )).inserted_primary_key[0]
        db.session.commit()
        print(db.session.execute(db.select(UserEntryCloud.iv).where(UserEntryCloud.user_id == session['id'])).scalars().first())
        flash("Entry successfully added to database", "success")




    return render_template('create_user_entry.html')


if __name__ == '__main__':
    if 'liveconsole' not in gethostname():
        app.logger.info("administrative: (6) flask application ready, running...")
        app.run(host='localhost', port=5000, debug=True)