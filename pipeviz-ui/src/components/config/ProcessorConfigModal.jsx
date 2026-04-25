import { useState } from "react";
import StepInput from "./StepInput";
import StepReview from "./StepReview";
import StepConfirmed from "./StepConfirmed";

const STEP_LABELS = ["Input", "Review", "Done"];

export default function ProcessorConfigModal({ onClose, onConfirm, existingConfig }) {
  const [step, setStep] = useState(existingConfig ? 2 : 1);
  const [extractedConfig, setExtractedConfig] = useState(existingConfig || null);

  function handleExtracted(config) {
    setExtractedConfig(config);
    setStep(2);
  }

  function handleConfirm(config) {
    setExtractedConfig(config);
    onConfirm(config);
    setStep(3);
  }

  const titles = ["Configure Processor", "Review & Edit", "Config Confirmed"];

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
          <span style={{ color: "#fff", fontSize: "16px", fontWeight: "600" }}>
            {titles[step - 1]}
          </span>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "#9ca3af", cursor: "pointer", fontSize: "20px", lineHeight: 1, padding: "0" }}>×</button>
        </div>

        {/* Step indicator */}
        <div style={{ display: "flex", alignItems: "center", marginBottom: "24px" }}>
          {STEP_LABELS.map((label, i) => {
            const num = i + 1;
            const done = num < step;
            const active = num === step;
            return (
              <div key={num} style={{ display: "flex", alignItems: "center" }}>
                <div style={{ alignItems: "center", display: "flex", gap: "6px" }}>
                  <div style={{
                    alignItems: "center",
                    backgroundColor: done ? "#10b981" : active ? "#3b82f6" : "#333",
                    borderRadius: "50%",
                    color: "#fff",
                    display: "flex",
                    fontSize: "12px",
                    fontWeight: "bold",
                    height: "24px",
                    justifyContent: "center",
                    width: "24px",
                  }}>
                    {done ? "✓" : num}
                  </div>
                  <span style={{ color: active ? "#fff" : done ? "#10b981" : "#555", fontSize: "13px" }}>
                    {label}
                  </span>
                </div>
                {i < STEP_LABELS.length - 1 && (
                  <div style={{ backgroundColor: i < step - 1 ? "#10b981" : "#333", height: "1px", margin: "0 12px", width: "32px" }} />
                )}
              </div>
            );
          })}
        </div>

        {/* Step content */}
        <div style={{ overflowY: "auto", maxHeight: "60vh", paddingRight: "4px" }}>
          {step === 1 && <StepInput onExtracted={handleExtracted} />}
          {step === 2 && extractedConfig && (
            <StepReview config={extractedConfig} onBack={() => setStep(1)} onConfirm={handleConfirm} />
          )}
          {step === 3 && extractedConfig && (
            <StepConfirmed config={extractedConfig} onClose={onClose} />
          )}
        </div>

      </div>
    </div>
  );
}

const overlayStyle = {
  alignItems: "center",
  backgroundColor: "rgba(0, 0, 0, 0.75)",
  bottom: 0,
  display: "flex",
  justifyContent: "center",
  left: 0,
  position: "fixed",
  right: 0,
  top: 0,
  zIndex: 1000,
};

const modalStyle = {
  backgroundColor: "#1e1e1e",
  border: "1px solid #333",
  borderRadius: "10px",
  boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
  maxHeight: "90vh",
  maxWidth: "90vw",
  overflow: "hidden",
  padding: "24px",
  width: "580px",
};
