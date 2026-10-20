import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// MediaPipe FaceMesh uses global WebAssembly state and cannot be initialized
// twice concurrently. React StrictMode deliberately re-runs effects in
// development, which starts two WebGazer instances at once.
ReactDOM.createRoot(document.getElementById("root")!).render(
  <App />
);
