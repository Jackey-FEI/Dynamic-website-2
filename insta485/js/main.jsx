import React from "react";
import { createRoot } from "react-dom/client";
// import InfiniteScrollBox from "./infiniteScroll";
import Post from "./post";
import InfinScroll from "./scroll";
// Create a root
const root = createRoot(document.getElementById("reactEntry"));

// Ensures we start at top of page on reload
window.onbeforeunload = () => {
  window.scrollTo(0, 0);
};

// This method is only called once
// Insert the post component into the DOM
root.render(<InfinScroll url="/api/v1/posts/" />);
