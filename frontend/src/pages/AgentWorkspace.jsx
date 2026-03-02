import { useParams, Link } from "react-router-dom";
import { useState } from "react";
import InstructionsTab from "../components/InstructionsTab";
import ChatTab from "../components/ChatTab";

export default function AgentWorkspace() {
  const { agentId } = useParams();
  const [tab, setTab] = useState("instructions");

  return (
    <div className="container">
      <Link to="/">← Back</Link>

      <div className="tabs">
        <button onClick={() => setTab("instructions")}>
          Instructions
        </button>
        <button onClick={() => setTab("chat")}>
          Test Chat
        </button>
      </div>

      {tab === "instructions" && (
        <InstructionsTab agentId={agentId} />
      )}
      {tab === "chat" && <ChatTab agentId={agentId} />}
    </div>
  );
}

