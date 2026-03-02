import { useState } from "react";
import { chat } from "../api/agents";

export default function ChatArea({ agentId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const send = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);

    const res = await chat(agentId, input);

    const assistantMsg = {
      role: "assistant",
      content: res.answer,
      sources: res.sources || []
    };

    setMessages(prev => [...prev, assistantMsg]);

    setInput("");
  };

  return (
    <>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 20 }}>
            <strong>
              {m.role === "user" ? "You" : "Agent"}
            </strong>
            <div style={{ marginTop: 6 }}>
              {m.content}
            </div>

            {/* Render sources if present */}
            {m.sources && m.sources.length > 0 && (
              <div style={{
                marginTop: 10,
                fontSize: "12px",
                opacity: 0.7
              }}>
                <div><strong>Sources:</strong></div>
                {m.sources.map((s, idx) => (
                  <div key={idx}>
                    📄 {s.source}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="chat-input-container">
        <input
          className="chat-input"
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") send();
          }}
        />
        <button className="send-btn" onClick={send}>
          ➤
        </button>
      </div>
    </>
  );
}
