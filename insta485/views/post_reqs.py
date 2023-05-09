"""
Insta485 POST Request handlers.

URLs include:
/likes/
/comments/
/posts/
/following/
"""

import flask
import insta485
from insta485.views.accounts import store_file


@insta485.app.route('/likes/', methods=['POST'])
def handle_likes():
    """Handle /likes/ post request."""
    # Redirect if not logged in
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Handle operation
    operation = flask.request.form['operation']
    if operation == "like":
        postid = flask.request.form['postid']
        logname = flask.session['user']

        connection = insta485.model.get_db()

        # Confirm user hasn't already liked postId
        # Query for a like with postid == postid and owner == logname
        cur = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE owner == :logname "
            "AND postid == :postid",
            {
                "logname": logname,
                "postid": postid
            }
        )

        # If the above query returned, the user has already liked this post
        result = cur.fetchone()
        if result is not None:
            return flask.abort(409)

        # Insert like into database
        connection.execute(
            "INSERT INTO likes "
            "(owner, postid) "
            "VALUES "
            "(:logname, :postid)",
            {
                "logname": logname,
                "postid": postid
            }
        )

    elif operation == "unlike":
        postid = flask.request.form['postid']
        logname = flask.session['user']

        connection = insta485.model.get_db()

        # Confirm user likes postId
        # Query for a like with postid == postid and owner == logname
        cur = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE owner == :logname "
            "AND postid == :postid",
            {
                "logname": logname,
                "postid": postid
            }
        )

        # If the above query does not return, the user does not like this post
        result = cur.fetchone()
        if result is None:
            return flask.abort(409)

        # Delete like from database
        connection.execute(
            "DELETE FROM likes "
            "WHERE owner == :logname "
            "AND postid == :postid",
            {
                "logname": logname,
                "postid": postid
            }
        )

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


@insta485.app.route('/comments/', methods=['POST'])
def handle_comments():
    """Handle /comments/ post request."""
    # Redirect if not logged in
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    logname = flask.session['user']

    # Handle operation
    operation = flask.request.form['operation']
    if operation == "create":
        # Make sure text is filled
        if "text" not in flask.request.form \
                or flask.request.form['text'] == '':
            return flask.abort(400)

        postid = flask.request.form['postid']
        text = flask.request.form['text']

        # Insert comment into database
        connection = insta485.model.get_db()
        connection.execute(
            "INSERT INTO comments "
            "(owner, postid, text) "
            "VALUES "
            "(:logname, :postid, :text)",
            {
                "logname": logname,
                "postid": postid,
                "text": text
            }
        )

    elif operation == "delete":
        # Get comment id
        commentid = flask.request.form['commentid']

        # Get owner of comment from database
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid == ?",
            (commentid, )
        )

        comment_owner = cur.fetchone()['owner']

        # Handle malicous requests
        # (Make sure person trying to delete comment is owner)
        if comment_owner != logname:
            return flask.abort(403)

        # Delete comment from database
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid == :commentid",
            {"commentid": commentid}
        )

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


@insta485.app.route('/posts/', methods=['POST'])
def handle_posts():
    """Handle /posts/ post request."""
    # Redirect if not logged in
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    logname = flask.session['user']

    # Handle operation
    operation = flask.request.form['operation']
    if operation == "create":
        # Make sure there is a file
        if "file" not in flask.request.files:
            return flask.abort(400)

        # Store the file in the uploads
        # See accounts.py's store_file() function
        filename = store_file(flask.request.files['file'])

        # Insert post into database
        connection = insta485.model.get_db()
        connection.execute(
            "INSERT INTO posts "
            "(filename, owner) "
            "VALUES "
            "(:filename, :logname)",
            {
                "logname": logname,
                "filename": filename
            }
        )

    elif operation == "delete":
        # Get post id
        postid = flask.request.form['postid']
        print(postid)
        # Get owner of post from database
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT owner, filename "
            "FROM posts "
            "WHERE postid == :postid",
            {"postid": postid}
        )

        result = cur.fetchone()
        post_owner = result['owner']

        # Handle malicous requests
        # (Make sure person trying to delete comment is owner)
        if post_owner != logname:
            return flask.abort(403)

        # Remove post's image from file system
        path = insta485.app.config["UPLOAD_FOLDER"]/result['filename']
        path.unlink()

        # Delete comment from database
        connection.execute(
            "DELETE FROM posts "
            "WHERE postid == :postid",
            {"postid": postid}
        )

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(flask.url_for('relationship', username=logname))

    return flask.redirect(flask.request.args['target'])


@insta485.app.route('/following/', methods=['POST'])
def handle_following():
    """Handle /following/ post request."""
    # Redirect if not logged in
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Get logged in user
    logname = flask.session['user']
    # Get user to follow/unfollow
    user2 = flask.request.form['username']

    # Handle operation
    operation = flask.request.form['operation']
    if operation == "follow":
        # Make sure logname isn't following username already
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username1 == :logname "
            "AND username2 == :user2",
            {
                "logname": logname,
                "user2": user2
            }
        )

        result = cur.fetchone()

        if result is not None:
            # The user is already following so abort
            return flask.abort(409)

        # Create the following relationship
        connection.execute(
            "INSERT INTO following"
            "(username1, username2) "
            "VALUES "
            "(:logname, :user2)",
            {
                "logname": logname,
                "user2": user2
            }
        )

    elif operation == "unfollow":
        # Make sure logname is following username
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username1 == :logname "
            "AND username2 == :user2",
            {
                "logname": logname,
                "user2": user2
            }
        )

        result = cur.fetchone()

        print(result)

        if result is None:
            # The user is not following so abort
            return flask.abort(409)

        # Delete the relationship
        connection.execute(
            "DELETE FROM following "
            "WHERE username1 == :logname "
            "AND username2 == :user2",
            {
                "logname": logname,
                "user2": user2
            }
        )

    # Handle redirect to target
    if "target" not in flask.request.args:
        return flask.redirect(f"/users/{logname}/")

    return flask.redirect(flask.request.args['target'])
