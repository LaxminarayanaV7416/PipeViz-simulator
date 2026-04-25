import { useRef, useState } from "react";
import { callApi } from "../util";

export default function StepInput({ onExtracted }) {
  const [activeTab, setActiveTab] = useState("text");
  const [inputText, setInputText] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  async function handleExtract() {
    setError(null);
    setLoading(true);

    const fd = new FormData();
    if (activeTab === "text") {
      fd.append("text", inputText);
    } else {
      fd.append("file", imageFile);
    }

    const res = await callApi({
      httpMethod: "POST",
      httpUrl: "/api/extract_config",
      formData: fd,
    });

    setLoading(false);

    if (res.ok) {
      onExtracted(res.data);
    } else {
      const msg = res.data?.detail || res.statusText || "Extraction failed";
      setError(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
  }

  const canExtract = activeTab === "text" ? inputText.trim().length > 0 : imageFile !== null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid #333" }}>
        {["text", "image"].map((tab) => (
          <button
            key={tab}
            onClick={() => { setActiveTab(tab); setError(null); }}
            style={{
              padding: "8px 20px",
              background: "none",
              border: "none",
              borderBottom: activeTab === tab ? "2px solid #3b82f6" : "2px solid transparent",
              color: activeTab === tab ? "#fff" : "#9ca3af",
              cursor: "pointer",
              fontSize: "14px",
              marginBottom: "-1px",
            }}
          >
            {tab === "text" ? "Paste Text" : "Upload Image"}
          </button>
        ))}
      </div>

      {/* Text input */}
      {activeTab === "text" && (
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste the processor configuration description here..."
          style={{
            backgroundColor: "#2a2a2a",
            border: "1px solid #333",
            borderRadius: "6px",
            color: "#fff",
            fontSize: "13px",
            lineHeight: "1.6",
            minHeight: "220px",
            padding: "12px",
            resize: "vertical",
          }}
        />
      )}

      {/* Image upload */}
      {activeTab === "image" && (
        <div
          onClick={() => fileInputRef.current.click()}
          style={{
            border: `2px dashed ${imageFile ? "#3b82f6" : "#444"}`,
            borderRadius: "6px",
            padding: "40px 20px",
            textAlign: "center",
            cursor: "pointer",
            backgroundColor: "#2a2a2a",
            minHeight: "140px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp"
            style={{ display: "none" }}
            onChange={(e) => { setImageFile(e.target.files?.[0] || null); setError(null); }}
          />
          {imageFile ? (
            <>
              <span style={{ fontSize: "24px" }}>✓</span>
              <span style={{ color: "#fff", fontSize: "14px" }}>{imageFile.name}</span>
              <span style={{ color: "#9ca3af", fontSize: "12px" }}>Click to change</span>
            </>
          ) : (
            <>
              <span style={{ fontSize: "28px", color: "#555" }}>+</span>
              <span style={{ color: "#9ca3af", fontSize: "14px" }}>Click to upload PNG / JPG / WebP</span>
            </>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ backgroundColor: "#3b1111", border: "1px solid #ef4444", borderRadius: "6px", color: "#fca5a5", fontSize: "13px", padding: "10px 14px" }}>
          {error}
        </div>
      )}

      {/* Extract button */}
      <button
        onClick={handleExtract}
        disabled={!canExtract || loading}
        style={{
          alignSelf: "flex-end",
          backgroundColor: canExtract && !loading ? "#3b82f6" : "#1e3a5f",
          border: "none",
          borderRadius: "6px",
          color: canExtract && !loading ? "#fff" : "#6b9fd4",
          cursor: canExtract && !loading ? "pointer" : "not-allowed",
          fontSize: "14px",
          fontWeight: "600",
          padding: "10px 24px",
        }}
      >
        {loading ? "Extracting..." : "Extract Config"}
      </button>
    </div>
  );
}
