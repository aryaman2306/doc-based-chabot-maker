import { useState } from "react";
import { chat } from "../api/agents";

export default function ChatTab({ agentId }) {
  const [q, setQ] = useState("");
  const [a, setA] = useState("");

  const ask = async () => {
    const res = await chat(agentId, q);
    setA(res.answer);
  };

  return (
    <div>
      <textarea
        rows={3}
        placeholder="Ask a test question..."
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <br />
      <button onClick={ask}>Ask</button>

      {a && (
        <>
          <h4>Answer</h4>
          <p>{a}</p>
        </>
      )}
    </div>
  );
}

