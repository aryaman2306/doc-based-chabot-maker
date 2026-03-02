import { useEffect, useState } from "react";
import { fetchAgents } from "../api/agents";
import { useNavigate } from "react-router-dom";
import CreateAgentModal from "../components/CreateAgentModal";

export default function Agents() {
  const [agents, setAgents] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const load = async () => {
    const data = await fetchAgents();
    setAgents(data);
  };

  useEffect(() => {
    load();
  }, []);

  const deleteAgent = async (agentId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this agent?"
    );

    if (!confirmDelete) return;

    await fetch(`http://localhost:8000/agents/${agentId}`, {
      method: "DELETE"
    });

    load();
  };

  return (
    <div className="container">
      <h2>Your Agents</h2>

      <button className="button" onClick={() => setShowModal(true)}>
        + New Agent
      </button>

      <div
        style={{
          display: "grid",
          gap: 20,
          marginTop: 30
        }}
      >
        {agents.map((a) => (
          <div
            key={a.agent_id}
            className="card"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              cursor: "pointer"
            }}
          >
            {/* LEFT SIDE (Click to open) */}
            <div
              onClick={() => navigate(`/agents/${a.agent_id}`)}
            >
              <h4 style={{ marginBottom: 6 }}>
                {a.name}
              </h4>

              <div
                style={{
                  fontSize: "13px",
                  opacity: 0.75
                }}
              >
                Type: {a.agent_type}
              </div>

              <div
                style={{
                  fontSize: "11px",
                  opacity: 0.5,
                  marginTop: 4
                }}
              >
                ID: {a.agent_id}
              </div>
            </div>

            {/* RIGHT SIDE (Delete icon) */}
            <div
              onClick={(e) => {
                e.stopPropagation();
                deleteAgent(a.agent_id);
              }}
              style={{
                fontSize: "18px",
                padding: "8px",
                borderRadius: "6px",
                transition: "0.2s",
              }}
            >
              🗑
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <CreateAgentModal
          onClose={() => setShowModal(false)}
          onCreated={load}
        />
      )}
    </div>
  );
}
