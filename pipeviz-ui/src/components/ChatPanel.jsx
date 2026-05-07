import { useState, useEffect, useRef } from "react";
import Markdown from "react-markdown";
import { callApi } from "./util";

export default function ChatPanel({
  workflowId,
  messages,
  onMessagesChange,
  onClose,
}) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    let isMounted = true;

    async function loadHistory() {
      if (!workflowId || messages.length > 0) return;

      const res = await callApi({
        httpMethod: "GET",
        httpUrl: "/api/chat_history",
        queryParams: { workflow_id: workflowId },
      });

      if (!isMounted) return;

      const history = Array.isArray(res.data?.chat_history)
        ? res.data.chat_history
        : [];

      if (history.length === 0) return;

      const hydrated = history.flatMap((item) => {
        const out = [];
        if (item.question) out.push({ role: "user", content: item.question });
        if (item.response)
          out.push({ role: "assistant", content: item.response });
        return out;
      });

      if (hydrated.length > 0) {
        onMessagesChange(hydrated);
      }
    }

    loadHistory();

    return () => {
      isMounted = false;
    };
  }, [workflowId, messages.length, onMessagesChange]);

  async function sendMessage() {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    onMessagesChange((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    const res = await callApi({
      httpMethod: "POST",
      httpUrl: "/api/chat",
      queryParams: { workflow_id: workflowId, question },
      timeoutMs: 600000,
    });

    setLoading(false);
    const reply =
      res.ok && res.data?.response
        ? res.data.response
        : `Error: ${res.data?.detail ?? "Chat request failed."}`;
    onMessagesChange((prev) => [
      ...prev,
      { role: "assistant", content: reply },
    ]);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        borderTop: "1px solid #333",
        background: "#111827",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 16px",
          borderBottom: "1px solid #333",
          fontSize: "13px",
          fontWeight: 600,
          color: "#9ca3af",
          flexShrink: 0,
        }}
      >
        <span>AI Chat</span>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "#6b7280",
              cursor: "pointer",
              fontSize: "20px",
              lineHeight: 1,
              padding: "0 2px",
            }}
            aria-label="Minimize chat"
          >
            −
          </button>
        )}
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "12px 16px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: "#6b7280", fontSize: "13px", margin: 0 }}>
            Ask anything about the pipeline simulation — hazards, stalls, stage
            behaviour, optimisation tips…
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                maxWidth: "85%",
                padding: "8px 12px",
                borderRadius:
                  msg.role === "user"
                    ? "12px 12px 2px 12px"
                    : "12px 12px 12px 2px",
                background: msg.role === "user" ? "#2563eb" : "#1f2937",
                color: "#e5e7eb",
                fontSize: "13px",
                lineHeight: "1.5",
              }}
            >
              {msg.role === "assistant" ? (
                <Markdown
                  components={{
                    p: ({ children }) => (
                      <p style={{ margin: "0 0 6px 0" }}>{children}</p>
                    ),
                    code: ({ children }) => (
                      <code
                        style={{
                          background: "#374151",
                          padding: "1px 4px",
                          borderRadius: "3px",
                          fontSize: "12px",
                        }}
                      >
                        {children}
                      </code>
                    ),
                    pre: ({ children }) => (
                      <pre
                        style={{
                          background: "#374151",
                          padding: "8px",
                          borderRadius: "4px",
                          overflowX: "auto",
                          fontSize: "12px",
                          margin: "4px 0",
                        }}
                      >
                        {children}
                      </pre>
                    ),
                    ul: ({ children }) => (
                      <ul style={{ margin: "4px 0", paddingLeft: "18px" }}>
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol style={{ margin: "4px 0", paddingLeft: "18px" }}>
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li style={{ marginBottom: "2px" }}>{children}</li>
                    ),
                  }}
                >
                  {msg.content}
                </Markdown>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start" }}>
            <div
              style={{
                padding: "8px 12px",
                borderRadius: "12px 12px 12px 2px",
                background: "#1f2937",
                color: "#6b7280",
                fontSize: "13px",
                fontStyle: "italic",
              }}
            >
              Thinking…
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input row */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          padding: "10px 16px",
          borderTop: "1px solid #333",
          flexShrink: 0,
        }}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question…"
          rows={2}
          style={{
            flex: 1,
            resize: "none",
            padding: "8px 10px",
            fontSize: "13px",
            background: "#1e1e1e",
            color: "#e5e7eb",
            border: "1px solid #444",
            borderRadius: "6px",
            outline: "none",
            fontFamily: "inherit",
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            padding: "0 16px",
            fontSize: "13px",
            background: loading || !input.trim() ? "#374151" : "#2563eb",
            color: loading || !input.trim() ? "#6b7280" : "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            alignSelf: "flex-end",
            height: "36px",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
