import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="container">
      <h1>AI Agent Builder</h1>

      <div style={{ display: "grid", gap: 20, marginTop: 40 }}>
        <div className="card" onClick={() => navigate("/agents")}>
          <h3>Create Agent</h3>
          <p>Build a knowledge-based AI chatbot.</p>
        </div>

        <div className="card">
          <h3>API Agent (Coming Soon)</h3>
          <p>Train agents on APIs and live data.</p>
        </div>

        <div className="card">
          <h3>Public Embed Agent (Coming Soon)</h3>
          <p>Deploy agents to your website.</p>
        </div>
      </div>
    </div>
  );
}

