"""REST API for posts."""
import flask
import insta485
from insta485.api.helper import InvalidUsage, authenticate



@insta485.app.route('/api/v1/', methods=["GET"])
def get_api():
    """Return the basic /api/v1/ route."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }

    return flask.jsonify(**context), 200

@insta485.app.route("/api/v1/posts/", methods=["GET"])
def get_posts():
    """Get all posts."""

    # Query for postids and post urls
    connection = insta485.model.get_db()
    # logname = flask.session['username']
    logname = authenticate()
    context = {}
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)

    # Confirm the size and page arguments are valid
    if size < 0 or page < 0:
        raise InvalidUsage("Bad Request", 400)

    # Handle postid_lte
    postid_lte = flask.request.args.get(
        "postid_lte", default=None, type=int
    )
    offset = size * page
    if  postid_lte == None: 
      cur = connection.execute(
          "SELECT DISTINCT "
         "    posts.postid "
         "FROM posts "
         "WHERE posts.owner IN " 
         "(SELECT following.username2 FROM following "
            "WHERE following.username1 == ? "
            "UNION SELECT users.username FROM users "
            "WHERE users.username = ?) "
          "ORDER BY posts.postid DESC "
          "LIMIT ? OFFSET ? ", (logname, logname, size, offset)
          )
    else:
      cur = connection.execute(
          "SELECT "
         "    posts.postid "
         "FROM posts "
         "WHERE posts.owner IN " 
         "(SELECT following.username2 FROM following "
            "WHERE following.username1 == ? "
            "UNION SELECT users.username FROM users "
            "WHERE users.username = ?) "
	     " AND posts.postid <= ? "
         "ORDER BY posts.postid DESC"
         "LIMIT ? OFFSET ? ", (logname, logname, postid_lte, size, offset)
          )
    latest = cur.fetchone()
    postidlast = latest["postid"]
    postsall = cur.fetchall()
    numposts = len(postsall)
    for post in postsall :
       post["url"] = "/api/v1/posts/"+str(post["postid"])+"/"
    context["result"] = postsall
    context["url"] = flask.request.path
    if (numposts < size) :
       context["next"] = ""
    else:
       context["next"] = "/api/v1/posts/?size="+str(size)+"&page="+str(page+1)+"&postid_lte="+str(postidlast)
    return flask.jsonify(**context)   
    

@insta485.app.route("/api/v1/posts/<int:postid>/", methods=["GET"])
def get_post(postid):
    """Get all posts."""

    # Query for postids and post urls
    connection = insta485.model.get_db()
    # logname = flask.session['username']
    logname = authenticate()
    context = {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postid": "/posts/{}/".format(postid),
        "url": flask.request.path,
    }
    cur1 = connection.execute(
          "SELECT DISTINCT"
          "    posts.filename As imgUrl, "
          "    posts.owner, "
          "    users.filename As ownerImgUrl, "
          "    posts.created, "
          "    posts.postid "
          "FROM posts "
          "JOIN users "
          "  ON posts.owner = users.username "
          "WHERE posts.postid = ?",
          (postid, )
        )
    postinfo = cur1.fetchone()
    if not postinfo:
        raise InvalidUsage("Not Found", 404)

    context["comments_url"] = "/api/v1/comments/?postid="+str(postid)
    context["ownerShowUrl"] = "/users/"+str(postinfo["owner"])+"/"
    context["postShowUrl"] = "/posts/"+str(postid)+"/"
    context["url"] = flask.request.path
    context["imgUrl"] = "/uploads/" + postinfo["imgUrl"]
    context["owner"] = postinfo["owner"]
    context["ownerImgUrl"] = "/uploads/" + postinfo["ownerImgUrl"]
    context["created"] = postinfo["created"]
    context["postid"] = postinfo["postid"]
    #dict1['profile'] = flask.send_from_directory('/uploads/',dict1['profile'])
    commentss = connection.execute(
           "SELECT DISTINCT"
           "    comments.commentid, "
           "    comments.owner, "
           "    comments.text "
           "FROM comments "
           "JOIN posts "
           "  ON comments.postid = posts.postid "
           "WHERE posts.postid = ?",
           (postid, )
        )
    commentcur = commentss.fetchall()
    for comment in commentcur:
       comment["url"] = "/api/v1/comments/"+str(comment["commentid"])+"/"
       comment["ownerShowUrl"] = "/users/"+str(comment["owner"])+"/"
       if comment["owner"] != logname:
          comment["lognameOwnsThis"] = False
       else:
          comment["lognameOwnsThis"] = True
    context["comments"] = commentcur
    likedict = {}
    likecur = connection.execute(
            "SELECT "
            "   likeid, "
            "   owner "
            "FROM likes "
            "WHERE postid = ?",
            (postid, )
       )
    like= likecur.fetchall()
    numlike = len(like)
    likedict["numLikes"] = numlike
    ownerlike =False
    id = -1 
    for likeit in like:
       if likeit["owner"] == logname:
           ownerlike = True
           id = likeit["likeid"]
    likedict["lognameLikesThis"] = ownerlike
    if ownerlike :
       likedict["url"] = "/api/v1/likes/"+ str(id)+"/"
    else:
       likedict["url"] = None
    context["likes"] = likedict
    print(context)
    
    return flask.jsonify(**context)  
    
    
