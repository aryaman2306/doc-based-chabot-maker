import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Agents from "./pages/Agents";
import Workspace from "./pages/Workspace";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/agents/:agentId" element={<Workspace />} />
      </Routes>
    </BrowserRouter>
  );
}

