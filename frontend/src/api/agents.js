const API_BASE = "http://localhost:8000";

export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  return res.json();
}

export async function createAgent(payload) {
  return fetch(`${API_BASE}/agents/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchAgent(agentId) {
  const res = await fetch(`${API_BASE}/agents/${agentId}`);
  return res.json();
}

export async function updateInstructions(agentId, instructions) {
  return fetch(`${API_BASE}/agents/${agentId}/instructions`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(instructions),
  });
}

export async function chat(agentId, question) {
  const res = await fetch(
    `${API_BASE}/agents/${agentId}/chat/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }
  );
  return res.json();
}

