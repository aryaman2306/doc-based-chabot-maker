import { useState } from "react";
import { createAgent } from "../api/agents";

export default function CreateAgentModal({ onClose, onCreated }) {
  const [name, setName] = useState("");
  const [type, setType] = useState("knowledge");

  const submit = async () => {
    await createAgent({ name, agent_type: type });
    onCreated();
    onClose();
  };

  return (
    <div className="card" style={{ position: "fixed", top: "20%", left: "40%" }}>
      <h3>Create Agent</h3>

      <input
        className="input"
        placeholder="Agent Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <select
        className="input"
        value={type}
        onChange={(e) => setType(e.target.value)}
        style={{ marginTop: 10 }}
      >
        <option value="faq">FAQ</option>
        <option value="knowledge">Knowledge</option>
        <option value="support">Support</option>
      </select>

      <div style={{ marginTop: 20 }}>
        <button className="button" onClick={submit}>
          Create
        </button>
        <button
          className="button"
          style={{ marginLeft: 10, background: "#334155" }}
          onClick={onClose}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

