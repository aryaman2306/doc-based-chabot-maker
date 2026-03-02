import { useEffect, useState } from "react";
import { fetchAgent, updateInstructions } from "../api/agents";

export default function InstructionsTab({
  agentId,
  open,
  onClose
}) {
  const [instructions, setInstructions] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!open) return;

    fetchAgent(agentId).then((a) =>
      setInstructions(a.instructions || "")
    );
  }, [agentId, open]);

  const save = async () => {
    await updateInstructions(agentId, instructions);
    setSaved(true);
    setTimeout(() => setSaved(false), 1200);
  };

  if (!open) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        right: 0,
        width: "420px",
        height: "100vh",
        background: "#111827",
        padding: "30px",
        boxShadow: "-6px 0 20px rgba(0,0,0,0.5)",
        zIndex: 1000,
        display: "flex",
        flexDirection: "column"
      }}
    >
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <h3>Training Instructions</h3>

        <button
          onClick={onClose}
          style={{
            background: "transparent",
            border: "none",
            color: "#aaa",
            fontSize: "18px",
            cursor: "pointer"
          }}
        >
          ✕
        </button>
      </div>

      <textarea
        value={instructions}
        onChange={(e) =>
          setInstructions(e.target.value)
        }
        style={{
          flex: 1,
          marginTop: "20px",
          padding: "12px",
          background: "#1f2937",
          color: "white",
          border: "1px solid #374151",
          borderRadius: "6px",
          resize: "none"
        }}
      />

      <button
        onClick={save}
        style={{
          marginTop: "20px"
        }}
        className="button"
      >
        Save
      </button>

      {saved && (
        <span style={{
          marginTop: "10px",
          fontSize: "12px",
          opacity: 0.7
        }}>
          Saved
        </span>
      )}
    </div>
  );
}
