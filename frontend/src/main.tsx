import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);

// import React from "react";
// import ReactDOM from "react-dom";
// import App from "./App";

// ReactDOM.createRoot(document.getElementById("root")).render(<App />);
