"""REST API for likes."""
import flask
import insta485
from insta485.api.helper import InvalidUsage, authenticate


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def post_like():
    """Add like."""

    # Query for postids and post urls
    connection = insta485.model.get_db()
    # logname = flask.session['username']
    logname = authenticate()
    context = {}
    postid = flask.request.args.get('postid', None)
    cur = connection.execute(
        "SELECT "
        "  likeid "
        "FROM likes "
        "WHERE "
        "  postid = ? AND owner = ?",
        (postid, logname)
    )
    like = cur.fetchone()
    if like:
        context["likeid"] = like["likeid"]
        context["url"] = "/api/v1/likes/"+str(context["likeid"])+"/"
        return flask.jsonify(**context), 200
    else:
        connection.execute(
            "INSERT INTO likes(owner, postid) "
            "VALUES (? , ?)", (logname, postid)
        )
        cur = connection.execute(
            "SELECT "
            "  likeid "
            "FROM likes "
            "WHERE "
            "  postid = ? AND owner = ?",
            (postid, logname)
        )
        newlike = cur.fetchone()
        context["likeid"] = newlike["likeid"]
        context["url"] = "/api/v1/likes/"+str(context["likeid"])+"/"
        return flask.jsonify(**context), 201

@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def delete_like(likeid):
    """Add like."""

    # Query for postids and post urls
    connection = insta485.model.get_db()
    # logname = flask.session['username']
    logname = authenticate()
    context = {}
    check = connection.execute(
        "SELECT "
        "  likeid, "
        "  owner "
        "FROM likes "
        "WHERE "
        "  likeid = ?",
        (likeid, )
    )
    checkone = check.fetchone()
    if not checkone:
        raise InvalidUsage("Not Found", 404)
    elif checkone["owner"] != logname:
        raise InvalidUsage("Forbidden", 403)
    else:
        connection.execute(
            "DELETE FROM likes "
            "WHERE likes.likeid = ?",
            (likeid, )
        )
        return "", 204
    