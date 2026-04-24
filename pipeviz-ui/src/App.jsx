import { useState, useEffect } from "react";
import { Group, Panel, Separator } from "react-resizable-panels";
import FileUpload from "./components/FileUpload";
import CodeEditor from "./components/CodeEditor";
import PipelineGrid from "./components/PipelineGrid";
import { callApi } from "./components/util";
import "./App.css";

const MOCK_DATA = {
  totalCycles: 48,
  instructions: [
    { label: "8ab4: sub sp, sp, #0x40", ifCycle: 1 },
    { label: "8ab8: stp x29, x30, [sp, #48]", ifCycle: 2 },
    { label: "8abc: add x29, sp, #0x30", ifCycle: 3 },
    { label: "8ac0: stur w0, [x29, #-20]", ifCycle: 6 },
    { label: "8ac4: stur w0, [x29, #-4]", ifCycle: 7 },
    { label: "8ac8: cbz w0, 8ae0", ifCycle: 8 },
    { label: "8acc: b 8ad0", ifCycle: 10 },
    { label: "8ad0: ldur w8, [x29, #-20]", ifCycle: 12 },
    { label: "8ad4: subs w8, w8, #0x1", ifCycle: 15 },
    { label: "8ad8: b.eq 8b00", ifCycle: 16 },
    { label: "8adc: b 8ae8", ifCycle: 18 },
    { label: "8ae0: stur xzr, [x29, #-16]", ifCycle: 20 },
    { label: "8ae4: b 8b80", ifCycle: 21 },
    { label: "8ae8: ldur w8, [x29, #-20]", ifCycle: 23 },
    { label: "8aec: subs w9, w8, #0x1", ifCycle: 26 },
    { label: "8af0: str w9, [sp, #24]", ifCycle: 29 },
    { label: "8af4: subs w8, w8, #0x1", ifCycle: 30 },
    { label: "8af8: b.cc 8b30", ifCycle: 31 },
    { label: "8afc: b 8b0c", ifCycle: 33 },
    { label: "8b00: mov w8, #0x1", ifCycle: 35 },
    { label: "8b04: stur x8, [x29, #-16]", ifCycle: 38 },
    { label: "8b08: b 8b80", ifCycle: 39 },
    { label: "8b0c: ldr w0, [sp, #24]", ifCycle: 41 },
    { label: "8b10: bl 8ab4", ifCycle: 42 },
    { label: "8b14: ldur w8, [x29, #-20]", ifCycle: 44 },
  ],
};

function App() {
  const [language, setLanguage] = useState("rust");
  const [code, setCode] = useState("");

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

  function handleCodeSubmit({ code, language }) {
    console.log("User submitted code:", { language, code });
    //later: send to backend API
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
          flexShrine: 0,
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

        <div
          style={{
            display: "flex",
            gap: "24px",
            fontSize: "14px",
            color: "#9ca3af",
          }}
        >
          <span>Laxminarayana Vadnala</span>
          <span>Patrick Do</span>
          <span>Jude Lynch</span>
        </div>
      </div>
      <Group direction="horizontal" style={{ height: "100vh" }}>
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

        {/* Drag Handle */}
        <Separator
          style={{
            width: "6px",
            backgroundColor: "#333",
            cursor: "col-resize",
          }}
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
          <h2 style={{ martinTop: 0 }}>Pipeline</h2>
          <PipelineGrid data={MOCK_DATA} />
        </Panel>
      </Group>
    </div>
  );
}

export default App;
