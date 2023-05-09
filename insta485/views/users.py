"""
Insta485 users.

URLs include:
/users/<user_url_slug>/
/users/<user_url_slug>/following/
/users/<user_url_slug>/followers/
"""
import flask
import insta485


@insta485.app.route('/users/<username>/')
def relationship(username):
    """Display the /users/<username/ route."""
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    connection = insta485.model.get_db()

    # Make sure username exists
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == :username",
        {"username": username}
    )

    result = cur.fetchone()

    if result is None:
        # Username does not exist
        return flask.abort(404)

    logname = flask.session['user']

    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username1 = :username ",
        {"username": username}
    )

    result = cur.fetchall()

    following_amount = len(result)

    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username2 = :username ",
        {"username": username}
    )

    result = cur.fetchall()

    follower_amount = len(result)

    cur = connection.execute(
        "SELECT username1, username2 "
        "FROM following "
        "WHERE username1 == ? AND username2 = ?",
        (logname, username)
    )

    result = cur.fetchone()

    logname_follows_username = (result is not None)

    cur = connection.execute(
        "SELECT username1, username2 "
        "FROM following "
        "WHERE username1 == ? AND username2 = ?",
        (logname, username)
    )

    result = cur.fetchone()

    logname_follows_username = (result is not None)

    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username == :username",
        {"username": username}
    )

    fullname = cur.fetchone()['fullname']

    cur = connection.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner == :username",
        {"username": username}
    )

    posts = cur.fetchall()

    total_posts = len(posts)

    context = {"following": following_amount,
               "followers": follower_amount,
               "logname_follows_username": logname_follows_username,
               "fullname": fullname,
               "total_posts": total_posts,
               "posts": posts,
               "logname": logname,
               "username": username}

    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<username>/followers/')
def show_followers(username):
    """Display the /users/../followers/ route."""
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Make sure username exists
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == :username",
        {"username": username}
    )

    result = cur.fetchone()

    if result is None:
        # Username does not exist
        return flask.abort(404)

    logname = flask.session['user']

    # Find the people who follow username
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 == :username",
        {"username": username}
    )

    followers = cur.fetchall()

    for follower in followers:
        follower['username'] = follower['username1']

        # Get their image url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username == :follower_name ",
            {"follower_name": follower['username']}
        )

        result = cur.fetchone()
        follower['user_img_url'] = result['filename']

        # Check if logname is following the follower
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username1 == :logname "
            "AND username2 == :follower_name",
            {
                "logname": logname,
                "follower_name": follower['username']
            }
        )

        follower['logname_follows_username'] = (cur.fetchone() is not None)

    context = {
        "logname": logname,
        "username": username,
        "followers": followers
    }

    return flask.render_template('followers.html', **context)


@insta485.app.route('/users/<username>/following/')
def show_following(username):
    """Display the /users/../following/ route."""
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Make sure username exists
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username == :username",
        {"username": username}
    )

    result = cur.fetchone()

    if result is None:
        # Username does not exist
        return flask.abort(404)

    logname = flask.session['user']

    # Find the people who username follows
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == :username",
        {"username": username}
    )

    following = cur.fetchall()

    for follower in following:
        follower['username'] = follower['username2']

        # Get their image url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username == :follower_name ",
            {"follower_name": follower['username']}
        )

        result = cur.fetchone()
        follower['user_img_url'] = result['filename']

        # Check if logname is following the follower
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username1 == :logname "
            "AND username2 == :follower_name",
            {
                "logname": logname,
                "follower_name": follower['username']
            }
        )

        follower['logname_follows_username'] = (cur.fetchone() is not None)

    context = {
        "logname": logname,
        "username": username,
        "following": following
    }

    return flask.render_template('following.html', **context)
