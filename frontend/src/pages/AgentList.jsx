import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAgents, createAgent } from "../api/agents";

export default function AgentList() {
  const [agents, setAgents] = useState([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("faq");

  const navigate = useNavigate();

  const load = async () => {
    const data = await fetchAgents();
    setAgents(data);
  };

  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    if (!name.trim()) return;
    await createAgent({ name, agent_type: type });
    setName("");
    load();
  };

  return (
    <div className="container">
      <h2>My Agents</h2>

      <div className="create-box">
        <input
          placeholder="Agent name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="faq">FAQ Bot</option>
          <option value="knowledge">Knowledge Bot</option>
          <option value="support">Support Bot</option>
        </select>
        <button onClick={create}>Create Agent</button>
      </div>

      <div className="agent-grid">
        {agents.map((a) => (
          <div
            key={a.agent_id}
            className="agent-card"
            onClick={() => navigate(`/agents/${a.agent_id}`)}
          >
            <h4>{a.name}</h4>
            <small>{a.agent_type}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

