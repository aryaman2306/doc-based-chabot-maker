import { useEffect, useState } from "react";

export default function FileList({ agentId }) {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/agents/${agentId}`)
      .then(res => res.json())
      .then(data => {
        if (data.files) setFiles(data.files);
      });
  }, [agentId]);

  return (
    <div>
      {files.map((f, i) => (
        <div key={i} style={{ marginBottom: 10 }}>
          {f}
        </div>
      ))}
      <button className="button" style={{ marginTop: 20 }}>
        Upload File
      </button>
    </div>
  );
}

