"""
Insta485 accounts view.

URLs include:
/accounts/?target=URL (POST)
/accounts/login/ (GET)
/accounts/create/ (GET)
/accounts/delete/ (GET)
/accounts/edit/ (GET)
/accounts/password/ (GET)
/accounts/logout/ (POST)
"""

import uuid
import pathlib
import flask
import insta485
from insta485.api.helper import hash_password, password_confirmation


@insta485.app.route('/accounts/', methods=['POST'])
def account_operations():
    """Handle account creation/modification then redirect."""
    operation = flask.request.form['operation']
    if operation == "login":
        return handle_login()

    if operation == "create":
        return handle_create()

    if operation == "delete":
        return handle_delete()

    if operation == "edit_account":
        return handle_edit()

    if operation == "update_password":
        return handle_update_pass()

    return flask.abort(400)


@insta485.app.route('/accounts/login/')
def show_login():
    """Account Login page view."""
    # If logged in redirect to index
    if "user" in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Else render the login template
    return flask.render_template("login.html")


@insta485.app.route('/accounts/create/')
def show_create():
    """Account creation page view."""
    # If logged in redirect to edit page
    if "user" in flask.session:
        return flask.redirect(flask.url_for('show_edit'))

    # Else render the create template
    return flask.render_template("create.html")


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Account Edit page view."""
    # If not logged in redirect to login page
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Else render the edit template
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    logname = flask.session["user"]
    cur = connection.execute(
        "SELECT username, fullname, "
        "filename, email "
        "FROM users "
        "WHERE username == ?",
        (logname, )
    )

    user_data = cur.fetchone()

    context = {
        "logname": user_data["username"],
        "user_icon": user_data["filename"],
        "fullname": user_data["fullname"],
        "email": user_data["email"]
    }
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Account deletion page view."""
    # If not logged in redirect to login page
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['user']

    context = {"logname": logname}

    # Else render the delete template
    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/password/')
def show_password():
    """Account change password page view."""
    # If not logged in redirect to login page
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    context = {
        "logname": flask.session['user']
    }

    # Else render the login template
    return flask.render_template("password.html", **context)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def handle_logout():
    """Account logout handler."""
    # Clear their session data
    flask.session.clear()

    # Redirect
    return flask.redirect(flask.url_for('show_login'))


def store_file(fileobj):
    """Store a file under a generated name and returns that name."""
    filename = fileobj.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name
    # is compatible with the filesystem.
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    return uuid_basename


def handle_login():
    """Handle the login post operation."""
    if "username" not in flask.request.form \
            or "password" not in flask.request.form:
        return flask.abort(400)

    # Try to find the username and password in the database
    connection = insta485.model.get_db()
    # Query database
    logname = flask.request.form["username"]
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username == ?",
        (logname, )
    )

    data = cur.fetchone()
    if data is None:
        # User does not exist in system
        return flask.abort(403)

    if not password_confirmation(
            flask.request.form['password'],
            data['password']):
        # Their password is wrong
        return flask.abort(403)

    # The user has the right password
    flask.session['user'] = logname

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


def handle_create():
    """Handle the create post operation."""
    # Make sure info is contained in form data
    if "username" not in flask.request.form \
            or "password" not in flask.request.form \
            or "fullname" not in flask.request.form \
            or "email" not in flask.request.form \
            or "file" not in flask.request.files:
        return flask.abort(400)

    # Make db connection
    connection = insta485.model.get_db()
    username = flask.request.form['username']
    # Confirm user data does not already exist (Abort 409)
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == ?",
        (username, )
    )

    result = cur.fetchone()
    if result is not None:
        # user already exists
        return flask.abort(409)

    # Handle file creation
    filename = store_file(flask.request.files['file'])

    # Get hashed password
    hashed_pass = hash_password(flask.request.form['password'])

    # Insert user into database
    cur = connection.execute(
        "INSERT INTO users "
        "(username, fullname, email, filename, password) "
        "VALUES (:username, :fullname, :email, :filename, "
        ":password)",
        {
            "username": username,
            "fullname": flask.request.form['password'],
            "email": flask.request.form['email'],
            "filename": filename,
            "password": hashed_pass
        }
    )

    flask.session['user'] = username

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


def handle_delete():
    """Handle the delete post operation."""
    if "user" not in flask.session:
        # No one is logged in abort 403
        return flask.abort(403)

    # get username
    username = flask.session['user']

    # Set up db connection
    connection = insta485.model.get_db()

    # Delete all post files from user
    cur = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = :logname",
        {"logname": username}
    )

    post_filenames = cur.fetchall()
    for filename in post_filenames:
        path = insta485.app.config["UPLOAD_FOLDER"]/filename['filename']
        path.unlink()

    # Delete user icon
    cur = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = :logname",
        {"logname": username}
    )

    user_filename = cur.fetchone()
    path = insta485.app.config["UPLOAD_FOLDER"]/user_filename['filename']

    path.unlink()

    # Delete user from database
    # All other deletes should cascade
    connection.execute(
        "DELETE FROM users "
        "WHERE username = :logname",
        {"logname": username}
    )

    # Clear session
    flask.session.clear()

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


def handle_edit():
    """Handle the edit_account post operation."""
    if "user" not in flask.session:
        # No one is logged in abort 403
        return flask.abort(403)

    # Get username
    username = flask.session['user']

    # Make sure info is contained in form data
    if "fullname" not in flask.request.form \
            or "email" not in flask.request.form:
        return flask.abort(400)

    # Open database connection
    connection = insta485.model.get_db()

    # Update fullname and email
    connection.execute(
        "UPDATE users "
        "SET "
        "fullname = :fullname, "
        "email = :email "
        "WHERE username = :username",
        {
            "username": username,
            "fullname": flask.request.form['fullname'],
            'email': flask.request.form['email']
        }
    )

    # Handle new file if it exists
    if 'file' in flask.request.files:
        # Get name of new file and store it
        new_filename = store_file(flask.request.files['file'])

        # Delete old file
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = :logname",
            {"logname": username}
        )

        user_filename = cur.fetchone()
        path = insta485.app.config["UPLOAD_FOLDER"]/user_filename['filename']
        path.unlink()

        # update filename in database
        connection.execute(
            "UPDATE users "
            "SET "
            "filename = :filename "
            "WHERE username = :username",
            {
                "username": username,
                "filename": new_filename
            }
        )

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


def handle_update_pass():
    """Handle the update_password post operation."""
    if "user" not in flask.session:
        # No one is logged in abort 403
        return flask.abort(403)

    # Make sure info is contained in form data
    if "password" not in flask.request.form \
            or "new_password1" not in flask.request.form \
            or "new_password2" not in flask.request.form:
        return flask.abort(400)

    # Open database connection
    connection = insta485.model.get_db()

    # Confirm user has correct password
    logname = flask.session['user']
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username == ?",
        (logname, )
    )

    correct_password = cur.fetchone()['password']

    if not password_confirmation(
            flask.request.form['password'],
            correct_password):
        # Their password is wrong
        return flask.abort(403)

    # Check if new passwords match
    new_pass1 = flask.request.form['new_password1']
    new_pass2 = flask.request.form['new_password2']

    if new_pass1 != new_pass2:
        return flask.abort(401)

    # Hash the new password
    hashed_pass = hash_password(new_pass1)

    # Update password in database
    connection.execute(
        "UPDATE users "
        "SET password = :password "
        "WHERE username = :username",
        {
            "username": logname,
            "password": hashed_pass
        }
    )

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])
