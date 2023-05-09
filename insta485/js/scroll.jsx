import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function InfinScroll({url}) {

      // const initialState = {
      //     item: [],
      //     urls: url,
      //     hasmore: true
      // };
      // const [state, setstates] = useState(initialState);
      // const handleChange = (e) => {
      //     setstates({ ...data, [e.target.name]: e.target.value });
      //   };
    
      const [urls, seturls] = useState("/api/v1/posts/");
      const [items, setitems] = useState([]);
      const [hasmore, setmore] = useState(true);


     function fetchMore()
    {
        // Declare a boolean flag that we can use to cancel the API request.
         let ignoreStaleRequest = false;

        // Call REST API to get the post's information
    fetch(urls, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
           seturls(data.next);
           setitems(items.concat(data.result));
           setmore((!data.next==""));
        }
      })
      .catch((error) => console.log(error));
    }

    useEffect(() => { 
      fetchMore();
    }, [url]);

   


    return (
      <main className="home"
      id="scrollableDiv"
      style={{
        height: 300,
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column-reverse',
            }}
      >
      {/*Put the scroll bar always on the bottom*/}
      <InfiniteScroll
        dataLength={items.length}
        next={fetchMore}
        //style={{ display: 'flex', flexDirection: 'column-reverse' }} //To put endMessage and loader to the top.
        //inverse={true} //
        hasMore={setmore}
        loader={<h4>Loading...</h4>}
        //scrollableTarget="scrollableDiv"
      >
      {items.map((result) => (
            <Post url={result.url} key={result.postid} />
          ))}
      </InfiniteScroll>
    </main>
    )
}
InfinScroll.propTypes = {
  url: PropTypes.string.isRequired,
};
