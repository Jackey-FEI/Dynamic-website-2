"""Helper functions for implementing REST API."""
import uuid
import hashlib
import flask
from flask import jsonify
import insta485


def authenticate():
    """Return logname is user is authenticated.

    User can be authenticated by either cookies
    or basic authentication.
    Aborts 403 otherwise.
    """
    logname = flask.session.get("user", None)

    if logname:
        return logname

    authorization = flask.request.authorization
    if authorization:
        username = flask.request.authorization.get("username", None)
        password = flask.request.authorization.get("password", None)

        # Check that username is in database and the
        # associated password is correct
        # Try to find the username and password in the database
        connection = insta485.model.get_db()
        # Query database
        cur = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username == ?",
            (username, )
        )

        data = cur.fetchone()
        if data and password_confirmation(password, data['password']):
            # The user exists and has the right password
            return username

    raise InvalidUsage("Forbidden", 403)


class InvalidUsage(Exception):
    """Special exception to raise flask errors."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Initialize the custom exception."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Turn exception data into a dictionary."""
        return_value = dict(self.payload or ())
        return_value['message'] = self.message
        return_value['status_code'] = self.status_code
        return return_value


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle InvalidUsage errors."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def password_confirmation(password, hashed_password):
    """Confirm a given password when hashed matches hashed_password."""
    algorithm = 'sha512'
    # Pull salt out of hashed_password
    # salt will be after the first $
    salt = hashed_password.split('$')[1]

    # hash the password now
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # see if the password equals what our db stored
    return password_db_string == hashed_password


def hash_password(password):
    """Hashes a password with a generated salt."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string
