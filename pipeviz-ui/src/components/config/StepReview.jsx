import { useState } from "react";

const SCHEDULING_OPTIONS = ["in_order", "tomasulo", "out_of_order", "scoreboard"];
const BRANCH_OPTIONS = ["static_not_taken", "static_always_taken", "dynamic_bpb_btb", "dynamic_bpb_only"];
const COMMIT_OPTIONS = ["in_order", "out_of_order"];

export default function StepReview({ config, onBack, onConfirm }) {
  const [stages, setStages] = useState([...(config.stages || [])]);
  const [stageInput, setStageInput] = useState("");
  const [fetchWidth, setFetchWidth] = useState(config.fetch_width ?? 1);
  const [issueWidth, setIssueWidth] = useState(config.issue_width ?? 1);
  const [schedulingPolicy, setSchedulingPolicy] = useState(config.scheduling_policy || "");
  const [speculativeExecution, setSpeculativeExecution] = useState(config.speculative_execution ?? false);
  const [latencyRows, setLatencyRows] = useState(() =>
    Object.entries(config.execution_latencies || {}).map(([k, v]) => ({ key: k, value: String(v) }))
  );
  const [forwardingReadyStage, setForwardingReadyStage] = useState(config.forwarding_ready_stage || "");
  const [structuralHazards, setStructuralHazards] = useState(config.structural_hazards ?? false);
  const [branchPrediction, setBranchPrediction] = useState(config.branch_prediction || "");
  const [branchResolutionStage, setBranchResolutionStage] = useState(config.branch_resolution_stage || "");
  const [commitPolicy, setCommitPolicy] = useState(config.commit_policy || "");
  const [multiCommitAllowed, setMultiCommitAllowed] = useState(config.multi_commit_allowed ?? false);
  const [specialRules, setSpecialRules] = useState([...(config.special_register_rules || [])]);

  // Compute warnings
  const warnings = [];
  if (Number(fetchWidth) === 0) warnings.push("fetch_width is 0 — verify this is correct");
  const zeroLatencies = latencyRows.filter(r => r.value === "0" || Number(r.value) === 0).map(r => r.key);
  if (zeroLatencies.length > 0) warnings.push(`Execution latency of 0 for: ${zeroLatencies.join(", ")} — verify these are correct`);
  if (latencyRows.length === 0) warnings.push("No execution latencies defined");

  function handleAddStage(e) {
    if (e.key === "Enter" && stageInput.trim()) {
      setStages([...stages, stageInput.trim().toUpperCase()]);
      setStageInput("");
    }
  }

  function handleConfirm() {
    onConfirm({
      stages,
      fetch_width: Number(fetchWidth),
      issue_width: Number(issueWidth),
      scheduling_policy: schedulingPolicy,
      speculative_execution: speculativeExecution,
      execution_latencies: Object.fromEntries(
        latencyRows.filter(r => r.key.trim()).map(r => [r.key.trim(), parseInt(r.value) || 0])
      ),
      forwarding_ready_stage: forwardingReadyStage,
      structural_hazards: structuralHazards,
      branch_prediction: branchPrediction,
      branch_resolution_stage: branchResolutionStage,
      commit_policy: commitPolicy,
      multi_commit_allowed: multiCommitAllowed,
      special_register_rules: specialRules,
    });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>

      {/* Warnings banner */}
      {warnings.length > 0 && (
        <div style={{ backgroundColor: "#3d2e00", border: "1px solid #f59e0b", borderRadius: "6px", color: "#fde68a", fontSize: "13px", marginBottom: "16px", padding: "10px 14px" }}>
          <strong>Review needed:</strong>
          <ul style={{ margin: "6px 0 0 0", paddingLeft: "18px" }}>
            {warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {/* Section 1: Pipeline Structure */}
      <Section title="Pipeline Structure">
        <Field label="Stages">
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
            {stages.map((s, i) => (
              <span key={i} style={tagStyle}>
                {s}
                <button onClick={() => setStages(stages.filter((_, j) => j !== i))} style={tagRemoveStyle}>×</button>
              </span>
            ))}
            <input
              value={stageInput}
              onChange={e => setStageInput(e.target.value)}
              onKeyDown={handleAddStage}
              placeholder="Add stage + Enter"
              style={{ ...inputStyle, width: "140px" }}
            />
          </div>
        </Field>
        <Row>
          <Field label="Fetch width (IF/cycle)">
            <input type="number" min="0" value={fetchWidth} onChange={e => setFetchWidth(e.target.value)}
              style={{ ...inputStyle, width: "80px", borderColor: Number(fetchWidth) === 0 ? "#f59e0b" : "#444" }} />
          </Field>
          <Field label="Issue width (IS/cycle)">
            <input type="number" min="0" value={issueWidth} onChange={e => setIssueWidth(e.target.value)}
              style={{ ...inputStyle, width: "80px" }} />
          </Field>
        </Row>
      </Section>

      {/* Section 2: Scheduling */}
      <Section title="Scheduling">
        <Row>
          <Field label="Policy">
            <select value={schedulingPolicy} onChange={e => setSchedulingPolicy(e.target.value)} style={selectStyle}>
              {SCHEDULING_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </Field>
          <Field label="Speculative execution">
            <Toggle value={speculativeExecution} onChange={setSpeculativeExecution} />
          </Field>
        </Row>
      </Section>

      {/* Section 3: Execution Latencies */}
      <Section title="Execution Latencies (EX stage cycles)">
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr>
              <th style={thStyle}>Instruction</th>
              <th style={thStyle}>Cycles</th>
              <th style={{ ...thStyle, width: "40px" }}></th>
            </tr>
          </thead>
          <tbody>
            {latencyRows.map((row, i) => (
              <tr key={i}>
                <td style={tdStyle}>
                  <input value={row.key} onChange={e => {
                    const updated = [...latencyRows];
                    updated[i] = { ...updated[i], key: e.target.value };
                    setLatencyRows(updated);
                  }} style={{ ...inputStyle, width: "100%" }} />
                </td>
                <td style={tdStyle}>
                  <input type="number" min="0" value={row.value} onChange={e => {
                    const updated = [...latencyRows];
                    updated[i] = { ...updated[i], value: e.target.value };
                    setLatencyRows(updated);
                  }} style={{ ...inputStyle, width: "70px", borderColor: Number(row.value) === 0 ? "#f59e0b" : "#444" }} />
                </td>
                <td style={tdStyle}>
                  <button onClick={() => setLatencyRows(latencyRows.filter((_, j) => j !== i))}
                    style={{ background: "none", border: "none", color: "#ef4444", cursor: "pointer", fontSize: "16px" }}>×</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button onClick={() => setLatencyRows([...latencyRows, { key: "", value: "1" }])}
          style={{ ...ghostButtonStyle, marginTop: "8px" }}>+ Add row</button>
      </Section>

      {/* Section 4: Forwarding & Hazards */}
      <Section title="Forwarding & Hazards">
        <Row>
          <Field label="Values ready at end of">
            <input value={forwardingReadyStage} onChange={e => setForwardingReadyStage(e.target.value)}
              style={{ ...inputStyle, width: "80px" }} placeholder="e.g. WB" />
          </Field>
          <Field label="Structural hazards">
            <Toggle value={structuralHazards} onChange={setStructuralHazards} />
          </Field>
        </Row>
      </Section>

      {/* Section 5: Branch Prediction */}
      <Section title="Branch Prediction">
        <Row>
          <Field label="Strategy">
            <select value={branchPrediction} onChange={e => setBranchPrediction(e.target.value)} style={selectStyle}>
              {BRANCH_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </Field>
          <Field label="Resolved at end of">
            <input value={branchResolutionStage} onChange={e => setBranchResolutionStage(e.target.value)}
              style={{ ...inputStyle, width: "80px" }} placeholder="e.g. WB" />
          </Field>
        </Row>
      </Section>

      {/* Section 6: Commit Policy */}
      <Section title="Commit Policy">
        <Row>
          <Field label="Policy">
            <select value={commitPolicy} onChange={e => setCommitPolicy(e.target.value)} style={selectStyle}>
              {COMMIT_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </Field>
          <Field label="Multi-commit allowed">
            <Toggle value={multiCommitAllowed} onChange={setMultiCommitAllowed} />
          </Field>
        </Row>
      </Section>

      {/* Section 7: Special Register Rules */}
      <Section title="Special Register Rules">
        {specialRules.map((rule, i) => (
          <div key={i} style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "8px" }}>
            <input value={rule.instruction_type} placeholder="Instruction"
              onChange={e => { const u = [...specialRules]; u[i] = { ...u[i], instruction_type: e.target.value }; setSpecialRules(u); }}
              style={{ ...inputStyle, width: "100px" }} />
            <input value={rule.register_name} placeholder="Register"
              onChange={e => { const u = [...specialRules]; u[i] = { ...u[i], register_name: e.target.value }; setSpecialRules(u); }}
              style={{ ...inputStyle, width: "100px" }} />
            <span style={{ color: "#9ca3af", fontSize: "13px" }}>ready at</span>
            <input value={rule.ready_at_stage} placeholder="Stage"
              onChange={e => { const u = [...specialRules]; u[i] = { ...u[i], ready_at_stage: e.target.value }; setSpecialRules(u); }}
              style={{ ...inputStyle, width: "80px" }} />
            <button onClick={() => setSpecialRules(specialRules.filter((_, j) => j !== i))}
              style={{ background: "none", border: "none", color: "#ef4444", cursor: "pointer", fontSize: "16px" }}>×</button>
          </div>
        ))}
        <button onClick={() => setSpecialRules([...specialRules, { instruction_type: "", register_name: "", ready_at_stage: "" }])}
          style={ghostButtonStyle}>+ Add rule</button>
      </Section>

      {/* Footer */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "8px", paddingTop: "16px", borderTop: "1px solid #333" }}>
        <button onClick={onBack} style={secondaryButtonStyle}>Back</button>
        <button onClick={handleConfirm} style={primaryButtonStyle}>Confirm Config</button>
      </div>
    </div>
  );
}

// ── Layout helpers ──────────────────────────────────────────────

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <div style={{ color: "#9ca3af", fontSize: "11px", fontWeight: "600", letterSpacing: "0.08em", marginBottom: "10px", textTransform: "uppercase" }}>
        {title}
      </div>
      <div style={{ backgroundColor: "#2a2a2a", borderRadius: "6px", padding: "14px 16px" }}>
        {children}
      </div>
    </div>
  );
}

function Row({ children }) {
  return <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>{children}</div>;
}

function Field({ label, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <label style={{ color: "#9ca3af", fontSize: "12px" }}>{label}</label>
      {children}
    </div>
  );
}

function Toggle({ value, onChange }) {
  return (
    <div onClick={() => onChange(!value)} style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", marginTop: "4px" }}>
      <div style={{
        width: "36px", height: "20px", borderRadius: "10px",
        backgroundColor: value ? "#3b82f6" : "#444",
        position: "relative", transition: "background 0.2s",
      }}>
        <div style={{
          position: "absolute", top: "3px",
          left: value ? "19px" : "3px",
          width: "14px", height: "14px",
          borderRadius: "50%", backgroundColor: "#fff",
          transition: "left 0.2s",
        }} />
      </div>
      <span style={{ color: "#e0e0e0", fontSize: "13px" }}>{value ? "Yes" : "No"}</span>
    </div>
  );
}

// ── Shared styles ───────────────────────────────────────────────

const inputStyle = {
  backgroundColor: "#1e1e1e",
  border: "1px solid #444",
  borderRadius: "4px",
  color: "#fff",
  fontSize: "13px",
  padding: "5px 8px",
};

const selectStyle = {
  ...inputStyle,
  cursor: "pointer",
};

const tagStyle = {
  alignItems: "center",
  backgroundColor: "#1e3a5f",
  borderRadius: "4px",
  color: "#93c5fd",
  display: "inline-flex",
  fontSize: "13px",
  gap: "4px",
  padding: "3px 8px",
};

const tagRemoveStyle = {
  background: "none",
  border: "none",
  color: "#93c5fd",
  cursor: "pointer",
  fontSize: "14px",
  lineHeight: 1,
  padding: "0",
};

const thStyle = {
  borderBottom: "1px solid #333",
  color: "#9ca3af",
  fontSize: "12px",
  fontWeight: "600",
  padding: "4px 8px",
  textAlign: "left",
};

const tdStyle = {
  padding: "4px 8px",
};

const ghostButtonStyle = {
  background: "none",
  border: "1px dashed #444",
  borderRadius: "4px",
  color: "#9ca3af",
  cursor: "pointer",
  fontSize: "13px",
  padding: "5px 12px",
};

const primaryButtonStyle = {
  backgroundColor: "#3b82f6",
  border: "none",
  borderRadius: "6px",
  color: "#fff",
  cursor: "pointer",
  fontSize: "14px",
  fontWeight: "600",
  padding: "10px 24px",
};

const secondaryButtonStyle = {
  backgroundColor: "transparent",
  border: "1px solid #444",
  borderRadius: "6px",
  color: "#9ca3af",
  cursor: "pointer",
  fontSize: "14px",
  padding: "10px 24px",
};
