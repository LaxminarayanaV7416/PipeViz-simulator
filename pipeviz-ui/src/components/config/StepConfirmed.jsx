export default function StepConfirmed({ config, onClose }) {

  const highlights = [
    { label: "Stages", value: config.stages?.join(" → ") },
    { label: "Scheduling", value: config.scheduling_policy },
    { label: "Speculative", value: config.speculative_execution ? "Yes" : "No" },
    { label: "Forwarding", value: `End of ${config.forwarding_ready_stage}` },
    { label: "Branch prediction", value: config.branch_prediction },
    { label: "Commit", value: config.commit_policy },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "20px", padding: "12px 0" }}>
      <div style={{ fontSize: "48px" }}>✓</div>
      <div style={{ textAlign: "center" }}>
        <div style={{ color: "#fff", fontSize: "18px", fontWeight: "600" }}>Config confirmed</div>
        <div style={{ color: "#9ca3af", fontSize: "13px", marginTop: "4px" }}>Ready to simulate</div>
      </div>

      <div style={{ backgroundColor: "#2a2a2a", borderRadius: "8px", padding: "16px 20px", width: "100%" }}>
        {highlights.map(({ label, value }) => (
          <div key={label} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #333", fontSize: "13px" }}>
            <span style={{ color: "#9ca3af" }}>{label}</span>
            <span style={{ color: "#e0e0e0" }}>{value || "—"}</span>
          </div>
        ))}
      </div>

      <button onClick={onClose} style={{ backgroundColor: "#3b82f6", border: "none", borderRadius: "6px", color: "#fff", cursor: "pointer", fontSize: "14px", fontWeight: "600", padding: "10px 28px" }}>
        Return to Simulation
      </button>
    </div>
  );
}
