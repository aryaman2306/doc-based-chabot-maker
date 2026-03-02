import { useParams } from "react-router-dom";
import { useState } from "react";
import Sidebar from "../layout/Sidebar";
import ChatArea from "../components/ChatArea";
import InstructionsTab from "../components/InstructionsTab";

export default function Workspace() {
  const { agentId } = useParams();

  const [mode, setMode] = useState("test"); // test | live
  const [showInstructions, setShowInstructions] = useState(false);

  return (
    <div style={{ display: "flex", height: "100vh" }}>

      {/* Sidebar only visible in TEST mode */}
      {mode === "test" && (
        <Sidebar
          agentId={agentId}
          onInstructionsClick={() => setShowInstructions(true)}
        />
      )}

      <div
        className="main"
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column"
        }}
      >

        {/* Top Control Bar */}
        <div
          style={{
            padding: "15px 20px",
            borderBottom: "1px solid #1f2937",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <div style={{ fontSize: "14px", opacity: 0.7 }}>
            Mode: {mode.toUpperCase()}
          </div>

          <button
            className="button"
            onClick={() =>
              setMode(mode === "test" ? "live" : "test")
            }
          >
            Switch Mode
          </button>
        </div>

        {/* Chat Area */}
        <div style={{ flex: 1 }}>
          <ChatArea agentId={agentId} />
        </div>
      </div>

      {/* Slide-in Instructions Panel */}
      <InstructionsTab
        agentId={agentId}
        open={showInstructions}
        onClose={() => setShowInstructions(false)}
      />
    </div>
  );
}
