import FileList from "../components/FileList";

export default function Sidebar({
  agentId,
  onInstructionsClick
}) {
  return (
    <div
      className="sidebar"
      style={{
        width: "260px",
        padding: "20px",
        borderRight: "1px solid #1f2937",
        display: "flex",
        flexDirection: "column",
        gap: "20px"
      }}
    >
      {/* Instructions Button */}
      <button
        className="button"
        onClick={onInstructionsClick}
        style={{ width: "100%" }}
      >
        🧠 Instructions
      </button>

      {/* Knowledge Section */}
      <div>
        <h3 style={{ marginBottom: "10px" }}>
          Knowledge
        </h3>

        <FileList agentId={agentId} />
      </div>
    </div>
  );
}
