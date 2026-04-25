import { useState, useRef, useEffect } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { cpp } from "@codemirror/lang-cpp";
import { rust } from "@codemirror/lang-rust";
import { callApi } from "./util";

const LANGUAGE_EXTENSIONS = {
  c: cpp(),
  cpp: cpp(),
  rust: rust(),
};

export default function CodeEditor({
  onCodeSubmuit,
  defaultCode = "",
  defaultLanguage = "c",
  onLanguageChange,
  processorConfig = null,
}) {
  const [language, setLanguage] = useState(defaultLanguage);
  const [code, setCode] = useState(defaultCode);
  const [languages, setLanguages] = useState([]);
  const fileInputRef = useRef(null);
  const [pipelines, setPipelines] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState("");

  useEffect(() => {
    setCode(defaultCode);
  }, [defaultCode]);

  useEffect(() => {
    let isMounted = true;

    async function fetchLanguages() {
      const res = await callApi({
        httpMethod: "GET",
        httpUrl: "/api/pipeline_supported_languages",
      });

      if (!isMounted) return;

      if (res.ok && res.data && Array.isArray(res.data.languages)) {
        const apiLanguages = res.data.languages.map((lang) => ({
          value: lang,
          label:
            lang === "cpp"
              ? "C++"
              : lang === "c"
                ? "C"
                : lang.charAt(0).toUpperCase() + lang.slice(1),
        }));

        setLanguages(apiLanguages);

        setLanguage((current) =>
          apiLanguages.find((l) => l.value === current)
            ? current
            : apiLanguages[0]?.value || defaultLanguage,
        );
      } else {
        const fallback = [
          { label: "C", value: "c" },
          { label: "C++", value: "cpp" },
          { label: "Rust", value: "rust" },
        ];
        setLanguages(fallback);
        setLanguage((current) =>
          fallback.find((l) => l.value === current)
            ? current
            : fallback[0]?.value || defaultLanguage,
        );
      }
    }

    fetchLanguages();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function fetchPipelines() {
      const res = await callApi({
        httpMethod: "GET",
        httpUrl: "/api/supported_pipelines",
      });

      if (!isMounted) return;

      if (res.ok && res.data && Array.isArray(res.data.supported_pipelines)) {
        setPipelines(res.data.supported_pipelines);
        setSelectedPipeline(
          (current) => current || res.data.supported_pipelines[0] || "",
        );
      } else {
        setPipelines([]);
        setSelectedPipeline("");
      }
    }

    fetchPipelines();

    return () => {
      isMounted = false;
    };
  }, []);

  function handleFileUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    let detectedLang = language;
    if (file.name.endsWith(".c")) detectedLang = "c";
    if (file.name.endsWith(".cpp") || file.name.endsWith(".cc"))
      detectedLang = "cpp";
    if (file.name.endsWith(".rs")) detectedLang = "rust";

    const reader = new FileReader();
    reader.onload = (e) => {
      setCode(e.target.result || "");
      setLanguage(detectedLang);
      if (onLanguageChange) onLanguageChange(detectedLang);
    };
    reader.readAsText(file);

    // Allow re-uploading the same file
    event.target.value = "";
  }

  function handleSubmit() {
    if (!code.trim()) {
      alert("Please write some code first");
      return;
    }
    onCodeSubmuit({ code, language });
  }

  function handleLanguageChange(e) {
    const newLang = e.target.value;
    setLanguage(newLang);
    if (onLanguageChange) onLanguageChange(newLang);
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        gap: "12px",
      }}
    >
      <select
        value={language}
        onChange={handleLanguageChange}
        style={{ width: "fit-content", padding: "6px 10px", fontSize: "14px" }}
      >
        {languages.map((lang) => (
          <option key={lang.value} value={lang.value}>
            {lang.label}
          </option>
        ))}
      </select>

      {processorConfig ? (
        <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px" }}>
          <span style={{ color: "#9ca3af" }}>Pipeline:</span>
          <span style={{ backgroundColor: "#0f2d1f", border: "1px solid #10b981", borderRadius: "4px", color: "#10b981", padding: "4px 10px" }}>
            {processorConfig.scheduling_policy}
          </span>
          <span style={{ color: "#555", fontSize: "12px" }}>configured ⚙</span>
        </div>
      ) : (
        <>
          <label style={{ marginRight: "8px", fontSize: "14px" }}>Pipeline:</label>
          <select
            value={selectedPipeline}
            onChange={(e) => setSelectedPipeline(e.target.value)}
            style={{ padding: "6px 10px", fontSize: "14px" }}
          >
            {pipelines.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </>
      )}
      <input
        ref={fileInputRef}
        type="file"
        accept=".c,.cpp,.rs,.cc"
        multiple={false}
        onChange={handleFileUpload}
        style={{ display: "none" }}
      />

      <button
        onClick={() => fileInputRef.current.click()}
        style={{ width: "fit-content" }}
      >
        Upload File
      </button>
      <div style={{ flex: 1, overflow: "auto", fontSize: "15px" }}>
        <CodeMirror
          value={code}
          onChange={(value) => setCode(value)}
          extensions={[LANGUAGE_EXTENSIONS[language]]}
          theme="dark"
          height="100%"
          style={{ height: "100%" }}
        />
      </div>

      <button onClick={handleSubmit} style={{ width: "fit-content" }}>
        Run Simulation
      </button>
    </div>
  );
}
