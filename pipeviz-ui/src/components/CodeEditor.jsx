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
}) {
  const [language, setLanguage] = useState(defaultLanguage);
  const [code, setCode] = useState(defaultCode);
  const [languages, setLanguages] = useState([]);
  const fileInputRef = useRef(null);
  const DEFAULT_PIPELINES = [
    "static_in_order",
    "scoreboard",
    "dynamic_in_order",
    "in_order_superscalar",
    "vliw",
    "tomasulo",
    "out_of_order",
  ];
  const [pipelines, setPipelines] = useState(DEFAULT_PIPELINES);
  const [selectedPipeline, setSelectedPipeline] = useState(DEFAULT_PIPELINES[0]);
  const [functionName, setFunctionName] = useState("fibonacci");
  const [compilerOptimization, setCompilerOptimization] = useState(0);
  const [enableLoopUnrolling, setEnableLoopUnrolling] = useState(false);

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

    event.target.value = "";
  }

  function handleSubmit() {
    if (!code.trim()) {
      alert("Please write some code first");
      return;
    }
    onCodeSubmuit({
      code,
      language,
      functionName,
      pipelineType: selectedPipeline,
      compilerOptimization,
      enableLoopUnrolling,
    });
  }

  function handleLanguageChange(e) {
    const newLang = e.target.value;
    setLanguage(newLang);
    if (onLanguageChange) onLanguageChange(newLang);
  }

  const labelStyle = { fontSize: "13px", color: "#9ca3af", marginRight: "6px" };
  const inputStyle = { padding: "5px 8px", fontSize: "13px", background: "#1e1e1e", color: "#e5e7eb", border: "1px solid #444", borderRadius: "4px" };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        gap: "12px",
      }}
    >
      {/* Row 1: Language + Pipeline */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <label style={labelStyle}>Language:</label>
          <select value={language} onChange={handleLanguageChange} style={inputStyle}>
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>{lang.label}</option>
            ))}
          </select>
        </div>

        <div style={{ display: "flex", alignItems: "center" }}>
          <label style={labelStyle}>Pipeline:</label>
          <select
            value={selectedPipeline}
            onChange={(e) => setSelectedPipeline(e.target.value)}
            style={inputStyle}
          >
            {pipelines.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Row 2: Function Name + Optimization + Loop Unrolling */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <label style={labelStyle}>Function Name:</label>
          <input
            type="text"
            value={functionName}
            onChange={(e) => setFunctionName(e.target.value)}
            style={{ ...inputStyle, width: "120px" }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center" }}>
          <label style={labelStyle}>Optimization:</label>
          <select
            value={compilerOptimization}
            onChange={(e) => setCompilerOptimization(Number(e.target.value))}
            style={inputStyle}
          >
            {[0, 1, 2, 3].map((lvl) => (
              <option key={lvl} value={lvl}>{lvl}</option>
            ))}
          </select>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <input
            type="checkbox"
            id="loopUnrolling"
            checked={enableLoopUnrolling}
            onChange={(e) => setEnableLoopUnrolling(e.target.checked)}
            style={{ cursor: "pointer" }}
          />
          <label htmlFor="loopUnrolling" style={{ ...labelStyle, marginRight: 0, cursor: "pointer" }}>
            Loop Unrolling
          </label>
        </div>
      </div>

      {/* File upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".c,.cpp,.rs,.cc"
        multiple={false}
        onChange={handleFileUpload}
        style={{ display: "none" }}
      />
      <button onClick={() => fileInputRef.current.click()} style={{ width: "fit-content" }}>
        Upload File
      </button>

      {/* Code editor */}
      <div style={{ flex: 1, overflow: "auto", fontSize: "15px" }}>
        <CodeMirror
          value={code}
          onChange={(value) => setCode(value)}
          extensions={[LANGUAGE_EXTENSIONS[language] ?? cpp()]}
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
