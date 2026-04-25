import { useState, useEffect } from "react";
import { Group, Panel, Separator } from "react-resizable-panels";
import CodeEditor from "./components/CodeEditor";
import PipelineGrid from "./components/PipelineGrid";
import ProcessorConfigModal from "./components/config/ProcessorConfigModal";
import { callApi } from "./components/util";
import "./App.css";

function App() {
  const [language, setLanguage] = useState("rust");
  const [code, setCode] = useState("");
  const [processorConfig, setProcessorConfig] = useState(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [pipelineRows, setPipelineRows] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const [simError, setSimError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchMockCode() {
      const res = await callApi({
        httpMethod: "GET",
        httpUrl: "/api/get_mock_code",
        queryParams: { language },
      });

      if (!isMounted) return;

      if (res.ok && res.data && Array.isArray(res.data.code)) {
        setCode(res.data.code.join(""));
      } else {
        setCode("");
      }
    }

    fetchMockCode();

    return () => {
      isMounted = false;
    };
  }, [language]);

  async function handleCodeSubmit({ code, language }) {
    setSimLoading(true);
    setSimError(null);

    const res = await callApi({
      httpMethod: "POST",
      httpUrl: "/api/simulate_pipelines",
      jsonData: {
        language,
        code,
        function_name: "main",
        processor_config: processorConfig ?? null,
      },
    });

    setSimLoading(false);

    if (res.ok && res.data?.pipelines) {
      setPipelineRows(res.data.pipelines);
    } else {
      setSimError(res.data?.detail ?? "Simulation failed.");
    }
  }

  function handleConfigConfirm(config) {
    setProcessorConfig(config);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 24px",
          borderBottom: "1px solid #333",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <img
            src="/ND_Monogram_10127_RGB.png"
            alt="Logo"
            style={{ height: "40px" }}
          />
          <h1 style={{ margin: 0, fontSize: "22px" }}>PipeViz</h1>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          {/* Processor config button */}
          <button
            onClick={() => setShowConfigModal(true)}
            style={{
              alignItems: "center",
              backgroundColor: processorConfig ? "#0f2d1f" : "#1e1e1e",
              border: `1px solid ${processorConfig ? "#10b981" : "#444"}`,
              borderRadius: "6px",
              color: processorConfig ? "#10b981" : "#9ca3af",
              cursor: "pointer",
              display: "flex",
              fontSize: "13px",
              gap: "8px",
              padding: "6px 14px",
            }}
          >
            <span>⚙</span>
            <span>
              {processorConfig
                ? `Processor: ${processorConfig.scheduling_policy}`
                : "Configure Processor"}
            </span>
            <span
              style={{
                backgroundColor: processorConfig ? "#10b981" : "#333",
                borderRadius: "10px",
                color: processorConfig ? "#fff" : "#666",
                fontSize: "11px",
                padding: "1px 7px",
              }}
            >
              {processorConfig ? "✓ Set" : "Not set"}
            </span>
          </button>

          {/* Team names */}
          <div
            style={{ display: "flex", gap: "24px", fontSize: "14px", color: "#9ca3af" }}
          >
            <span>Laxminarayana Vadnala</span>
            <span>Patrick Do</span>
            <span>Jude Lynch</span>
          </div>
        </div>
      </div>

      <Group direction="horizontal" style={{ flex: 1, overflow: "hidden" }}>
        {/* Left panel - code editor */}
        <Panel
          defaultSize={50}
          minSize={20}
          style={{
            display: "flex",
            flexDirection: "column",
            padding: "24px",
            overflow: "hidden",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Code</h2>
          <CodeEditor
            defaultCode={code}
            defaultLanguage={language}
            onLanguageChange={setLanguage}
            onCodeSubmuit={handleCodeSubmit}
            processorConfig={processorConfig}
          />
        </Panel>

        <Separator
          style={{ width: "6px", backgroundColor: "#333", cursor: "col-resize" }}
        />

        {/* Right panel - pipeline grid */}
        <Panel
          defaultSize={50}
          minSize={20}
          style={{
            display: "flex",
            flexDirection: "column",
            padding: "24px",
            overflow: "auto",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Pipeline</h2>
          {simLoading && (
            <div style={{ color: "#9ca3af", fontSize: "14px" }}>
              Compiling and simulating…
            </div>
          )}
          {simError && !simLoading && (
            <div style={{ color: "#f87171", fontSize: "13px", whiteSpace: "pre-wrap" }}>
              {simError}
            </div>
          )}
          {!simLoading && <PipelineGrid rows={pipelineRows} />}
        </Panel>
      </Group>

      {/* Config modal */}
      {showConfigModal && (
        <ProcessorConfigModal
          existingConfig={processorConfig}
          onClose={() => setShowConfigModal(false)}
          onConfirm={handleConfigConfirm}
        />
      )}
    </div>
  );
}

export default App;
