import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout.tsx";
import Home from "./pages/Home.tsx";
import Reader from "./pages/Reader.tsx";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/reader/:documentId?" element={<Reader />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
