import { useState, useEffect } from "react";
import { Group, Panel, Separator } from "react-resizable-panels";
import CodeEditor from "./components/CodeEditor";
import PipelineGrid from "./components/PipelineGrid";
import ChatPanel from "./components/ChatPanel";
import ProcessorConfigModal from "./components/config/ProcessorConfigModal";
import { callApi } from "./components/util";
import "./App.css";

function App() {
  const [language, setLanguage] = useState("c");
  const [code, setCode] = useState("");
  const [processorConfig, setProcessorConfig] = useState(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [pipelineRows, setPipelineRows] = useState(null);
  const [workflowId, setWorkflowId] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
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

  async function handleCodeSubmit({ code, language, functionName, pipelineType, compilerOptimization, enableLoopUnrolling, enableForwarding }) {
    setSimLoading(true);
    setSimError(null);

    const res = await callApi({
      httpMethod: "POST",
      httpUrl: "/api/simulate_pipelines",
      queryParams: {
        language,
        mock_existing_code: false,
        function_name: functionName,
        pipeline_type: pipelineType,
        compiler_optimization: compilerOptimization,
        enable_loop_unrolling: enableLoopUnrolling,
        enable_forwarding: enableForwarding,
      },
      jsonData: { code },
    });

    setSimLoading(false);

    if (res.ok && res.data?.pipelines) {
      setPipelineRows(res.data.pipelines);
      setWorkflowId(res.data.workflow_id);
      setShowChat(false);
      setChatMessages([]);
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
          />
        </Panel>

        <Separator
          style={{ width: "6px", backgroundColor: "#333", cursor: "col-resize" }}
        />

        {/* Right panel - pipeline grid + optional chat */}
        <Panel
          defaultSize={50}
          minSize={20}
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            height: "100%",
          }}
        >
          {/* Header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "24px 24px 0 24px",
              flexShrink: 0,
            }}
          >
            <h2 style={{ margin: 0 }}>Pipeline</h2>
            {workflowId && !showChat && (
              <button
                onClick={() => setShowChat(true)}
                style={{
                  fontSize: "13px",
                  background: "#2563eb",
                  color: "#fff",
                  border: "none",
                  borderRadius: "6px",
                  padding: "6px 14px",
                  cursor: "pointer",
                }}
              >
                Ask AI
              </button>
            )}
          </div>

          {/* Status messages */}
          <div style={{ padding: "0 24px", flexShrink: 0 }}>
            {simLoading && (
              <div style={{ color: "#9ca3af", fontSize: "14px", marginTop: "12px" }}>
                Compiling and simulating…
              </div>
            )}
            {simError && !simLoading && (
              <div style={{ color: "#f87171", fontSize: "13px", whiteSpace: "pre-wrap", marginTop: "12px" }}>
                {simError}
              </div>
            )}
          </div>

          {/* Pipeline grid — always full size */}
          {!simLoading && (
            <div style={{ flex: 1, overflow: "auto", padding: "12px 24px 24px 24px" }}>
              <PipelineGrid rows={pipelineRows} />
            </div>
          )}
        </Panel>
      </Group>

      {/* Floating chat panel — bottom-right corner */}
      {showChat && (
        <div style={{
          position: "fixed",
          bottom: 0,
          right: 0,
          width: "380px",
          height: "480px",
          zIndex: 100,
          display: "flex",
          flexDirection: "column",
          boxShadow: "0 -4px 24px rgba(0,0,0,0.5)",
          borderRadius: "8px 0 0 0",
          overflow: "hidden",
        }}>
          <ChatPanel workflowId={workflowId} messages={chatMessages} onMessagesChange={setChatMessages} onClose={() => setShowChat(false)} />
        </div>
      )}

      {/* Config modal (hidden until re-enabled) */}
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
