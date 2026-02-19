import { useState, useEffect, useRef } from "react";
import { sendMessage } from "./api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendMessage(input);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error connecting to server." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div style={styles.page}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <div>
          <h2 style={styles.logo}>AI Executive</h2>
          <p style={styles.tagline}>Your intelligent operations copilot</p>
        </div>
        <div style={styles.sidebarFooter}>
          <div style={styles.statusDot} />
          Connected
        </div>
      </div>

      {/* Chat Panel */}
      <div style={styles.chatContainer}>
        <div style={styles.header}>
          <h1 style={styles.title}>Executive Assistant</h1>
        </div>

        <div style={styles.chatBox}>
          {messages.length === 0 && (
            <div style={styles.emptyState}>
              <h3>How can I help today?</h3>
              <p>
                Ask about meetings, unread emails, scheduling, or daily plans.
              </p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.messageRow,
                justifyContent:
                  msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  ...styles.message,
                  ...(msg.role === "user"
                    ? styles.userMessage
                    : styles.assistantMessage),
                }}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div style={styles.messageRow}>
              <div style={styles.assistantMessage}>Thinking...</div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div style={styles.inputWrapper}>
          <input
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message your assistant..."
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            style={{
              ...styles.button,
              opacity: loading ? 0.6 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
            onClick={handleSend}
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  page: {
    height: "100vh",
    display: "flex",
    background:
      "linear-gradient(135deg, #0f172a 0%, #111827 50%, #0b1120 100%)",
    fontFamily: "Inter, sans-serif",
    color: "white",
  },

  sidebar: {
    width: 260,
    padding: 28,
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    background: "rgba(255,255,255,0.04)",
    borderRight: "1px solid rgba(255,255,255,0.08)",
  },

  logo: {
    fontSize: 20,
    fontWeight: 700,
    marginBottom: 6,
  },

  tagline: {
    opacity: 0.6,
    fontSize: 14,
  },

  sidebarFooter: {
    fontSize: 13,
    opacity: 0.7,
    display: "flex",
    alignItems: "center",
    gap: 8,
  },

  statusDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#22c55e",
  },

  chatContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },

  header: {
    padding: "20px 32px",
    borderBottom: "1px solid rgba(255,255,255,0.06)",
  },

  title: {
    fontSize: 22,
    fontWeight: 600,
  },

  chatBox: {
    flex: 1,
    overflowY: "auto",
    padding: "30px 60px",
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },

  emptyState: {
    textAlign: "center",
    marginTop: "20%",
    opacity: 0.6,
  },

  messageRow: {
    display: "flex",
  },

  message: {
    padding: "14px 18px",
    borderRadius: 18,
    maxWidth: "60%",
    fontSize: 15,
    lineHeight: 1.5,
    backdropFilter: "blur(10px)",
    animation: "fadeIn 0.25s ease-in",
  },

  userMessage: {
    background: "linear-gradient(135deg, #6366f1, #4f46e5)",
    boxShadow: "0 8px 20px rgba(79,70,229,0.4)",
  },

  assistantMessage: {
    background: "rgba(255,255,255,0.08)",
    border: "1px solid rgba(255,255,255,0.06)",
  },

  inputWrapper: {
    padding: 24,
    borderTop: "1px solid rgba(255,255,255,0.06)",
    display: "flex",
    gap: 12,
    background: "rgba(0,0,0,0.2)",
  },

  input: {
    flex: 1,
    padding: "14px 16px",
    borderRadius: 14,
    border: "1px solid rgba(255,255,255,0.1)",
    background: "rgba(255,255,255,0.05)",
    color: "white",
    fontSize: 15,
    outline: "none",
  },

  button: {
    padding: "14px 22px",
    borderRadius: 14,
    border: "none",
    background: "linear-gradient(135deg, #6366f1, #4f46e5)",
    color: "white",
    fontWeight: 600,
  },
};
