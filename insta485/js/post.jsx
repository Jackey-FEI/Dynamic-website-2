import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */
  const [states, setstates] = useState({})
  const [like, setLike] = useState({});
  const [numlikes,setnumLike] = useState(0);
  const [likestate,setlikestate] = useState(false);
  const [likestring,setstringlike] = useState("");
  const [comments, setComments] = useState([]);

  function Comment()
  { 
    const commentList = comments.map(comment =>
      <div key={comment.commentid}> <a href={comment.ownerShowUrl}>{comment.owner}</a> {comment.text }</div>
      );

    return (
      <div className="comment-text"> {commentList}</div>
    );
  }

  
  function PostTop({owner,ownerUrl, ownerImgUrl, postUrl, timestamp})
  {
    return (
      <div className="post-top">
                    <a className="user-link" href={ownerUrl}>
                        <img className="post-icon" src={ ownerImgUrl } alt="{ owner }'s icon" />
                        <p className="post-name">{ owner }</p>
                    </a>
                    <p className="timestamp"><a href= {postUrl}>{ timestamp }</a></p>
                </div>
    );
  }
  
  function OnUnlike() // Change from like to unlike
  {
    setnumLike(numlikes-1);
    setlikestate(false);
    setstringlike("like");
  }

  function OnLike() //change from unlike to like
  {
    if (!likestate)
    {
      setnumLike(numlikes+1);
      setlikestate(true);
      setstringlike("unlike");
    }

  }

  function Likebutton({likestring, OnUnlike,OnLike})
  {
    if (likestate)
    {
      return(
       <button className="like-unlike-button" onClick={OnUnlike}>
         {likestring}
       </button>
       );
    }
    else
    {
      return(
        <button className="like-unlike-button" onClick={OnLike}>
          {likestring}
        </button>
        );
    }
  }

  function Likesword({numlikes})
  {
    if (numlikes == 1)
    return (
      <div>
        1 like
      </div>
    );
    else 
    return (
      <div>
        {numlikes} likes
      </div>
    );
  }

  function Likes({likestring, numlikes, OnUnlike, OnLike})
  {
    return(
      <div>
        <Likebutton likestring={likestring} OnUnlike={OnUnlike} OnLike={OnLike}/>
        <Likesword numlikes={numlikes} />
      </div>
    );
  }

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setstates(data);
          setLike(data.likes);
          setnumLike(data.likes.numLikes);
          setlikestate(data.likes.lognameLikesThis)
          if (data.likes.lognameLikesThis)
           {
              setstringlike("unlike");
           }
           else
           {
              setstringlike("like");
           }
          setComments(data.comments);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // Render post image and post owner
  return (
    <div className="post-container">
        <PostTop
          owner={states.owner}
          ownerUrl={states.ownerShowUrl}
          ownerImgUrl={states.ownerImgUrl}
          postUrl={states.postShowUrl}
          timestamp={states.created}
        />
        <div className="post-main">
          <img
            src={states.imgUrl}
            className="post-img"
            alt="post"
            onDoubleClick={OnLike}
          />
        </div>
        <div className="post-footer">
          <Likes
            likestring={likestring}
            numlikes={numlikes}
            OnUnlike={OnUnlike}
            OnLike={OnLike}
          />
          <Comment />
          {/* <CommentInput onCommentAdd={this.handleCommentAdd} /> */}
        </div>
      </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};