"""
Insta485 index (main) view.

URLs include:
/
"""
import arrow
import flask
import insta485

TIME_STAMP_FORMAT = "YYYY-MM-DD HH:mm:ss"


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Step 1: Check if the user is logged in and if not redirect to login
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    connection = insta485.model.get_db()

    # Dont need this becuase when we select everything
    # from posts it will have everything

    logname = flask.session['user']

    # Step 2: Get the posts from user and people the user follows
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner = :logname OR owner IN ("
        "SELECT username2 FROM following WHERE username1 = :logname) "
        "ORDER BY postid DESC",
        {"logname": logname}
    )

    posts = cur.fetchall()

    # need to loop through every post and get the timestamp
    for post in posts:
        #post['timestamp'] = arrow.get(post["created"], TIME_STAMP_FORMAT).humanize()
        post['timestamp'] = arrow.get("2023-02-14 10:00:00", TIME_STAMP_FORMAT).humanize()
        # This is a dict that contains a user (or the filename of the user)
        # AKA profile pic
        cur = connection.execute(
            "SELECT filename FROM users "
            "WHERE username = :owner",
            {"owner": post["owner"]}
        )
        # grabbing the dict with the key for profile pictures
        post['owner_img_url'] = cur.fetchone()['filename']

        # Query the number of likes for the post
        cur = connection.execute(
            "SELECT * FROM likes "
            "WHERE postid = :postid ",
            {"postid": post["postid"]}
        )

        # Table of all the likes
        post['likes'] = len(cur.fetchall())

        cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE owner == :logname "
            "AND postid == :postid",
            {
                "logname": logname,
                "postid": post['postid']
            }
        )
        post['user_liked'] = (cur.fetchone() is not None)

        cur = connection.execute(
            "SELECT owner, text FROM comments "
            "WHERE postid = :postid "
            "ORDER BY commentid ASC",
            {"postid": post["postid"]}
        )

        post['comments'] = cur.fetchall()

    context = {"logname": logname, "posts": posts}

    return flask.render_template("index.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    # Step 1: Check if the user is logged in and if not redirect to login
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['user']

    # Connect to the database
    connection = insta485.model.get_db()

    # Get username and icon of users not followed by logname
    # Note username1 follows username2 in database
    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != :logname "
        "AND username NOT IN ("
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == :logname"
        ")",
        {"logname": logname}
    )

    not_following = cur.fetchall()

    # Build context object
    context = {
        "logname": logname,
        "not_following": not_following
    }

    # Find all users that logname is not following
    return flask.render_template('explore.html', **context)


@insta485.app.route('/posts/<postid>/')
def show_post(postid):
    """Display /post/<postid>/ route."""
    # Step 1: Check if the user is logged in and if not redirect to login
    if "user" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['user']

    # Get post information
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT owner, filename, created "
        "FROM posts "
        "WHERE postid == :postid",
        {"postid": postid}
    )

    result = cur.fetchone()
    owner = result['owner']
    filename = result['filename']
    timestamp = arrow \
        .get(result["created"], TIME_STAMP_FORMAT) \
        .humanize()

    # Get like count
    cur = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE postid == :postid ",
        {"postid": postid}
    )

    result = cur.fetchall()
    likes = len(result)

    # Get owner image url
    cur = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username == :owner",
        {"owner": owner}
    )

    owner_img_url = cur.fetchone()['filename']

    # Get post comments
    cur = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments "
        "WHERE postid == :postid "
        "ORDER BY commentid ASC",
        {"postid": postid}
    )

    comments = cur.fetchall()

    cur = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE postid == :postid "
        "AND owner == :logname",
        {
            "postid": postid,
            "logname": logname
        }
    )

    logname_likes_post = (cur.fetchone() is not None)

    context = {
        "logname": logname,
        "postid": postid,
        "filename": filename,
        "timestamp": timestamp,
        "logname_likes_post": logname_likes_post,
        "likes": likes,
        "owner": owner,
        "owner_img_url": owner_img_url,
        "comments": comments
    }

    return flask.render_template('post.html', **context)
