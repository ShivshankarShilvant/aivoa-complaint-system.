import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { extractFromFile, extractFromText } from "../store/complaintSlice";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function AIAssistantPanel() {
  const dispatch = useDispatch();
  const extractionStatus = useSelector((s) => s.complaint.extractionStatus);
  const aiSummary = useSelector((s) => s.complaint.aiSummary);
  const riskClassification = useSelector((s) => s.complaint.riskClassification);
  const capaRecommendation = useSelector((s) => s.complaint.capaRecommendation);
  const possibleDuplicateId = useSelector((s) => s.complaint.possibleDuplicateId);
  const rawText = useSelector((s) => s.complaint.rawText);

  const [pastedText, setPastedText] = useState("");
  const [question, setQuestion] = useState("");
  const [chatLog, setChatLog] = useState([]);

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (file) dispatch(extractFromFile(file));
  };

  const handlePasteSubmit = () => {
    if (pastedText.trim()) dispatch(extractFromText(pastedText));
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    const userMsg = { role: "user", text: question };
    setChatLog((log) => [...log, userMsg]);
    setQuestion("");

    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context_text: rawText, question: userMsg.text }),
    });
    const data = await res.json();
    setChatLog((log) => [...log, { role: "assistant", text: data.answer }]);
  };

  return (
    <div style={{ padding: 24, maxWidth: 420, borderLeft: "1px solid #eee" }}>
      <h3>AI complaint intake assistant</h3>

      <div style={{ border: "1px dashed #ccc", padding: 20, textAlign: "center", marginBottom: 12 }}>
        <input type="file" accept=".pdf,.docx,.txt,.eml" onChange={handleFile} />
        <p style={{ fontSize: 12, color: "#888" }}>PDF, DOCX, TXT, EML - max 10MB</p>
      </div>

      <p style={{ textAlign: "center", color: "#aaa", fontSize: 12 }}>OR</p>

      <textarea
        placeholder="Paste complaint text / email"
        value={pastedText}
        onChange={(e) => setPastedText(e.target.value)}
        rows={4}
        style={{ width: "100%", marginBottom: 8 }}
      />
      <button onClick={handlePasteSubmit} disabled={extractionStatus === "loading"}>
        {extractionStatus === "loading" ? "Extracting..." : "Extract details"}
      </button>

      {extractionStatus === "succeeded" && (
        <div style={{ marginTop: 16, fontSize: 13 }}>
          {aiSummary && <p><strong>Summary:</strong> {aiSummary}</p>}
          {riskClassification && <p><strong>Risk:</strong> {riskClassification}</p>}
          {capaRecommendation && <p><strong>CAPA suggestion:</strong> {capaRecommendation}</p>}
          {possibleDuplicateId && (
            <p style={{ color: "#c0392b" }}>
              Possibly a duplicate of complaint {possibleDuplicateId}
            </p>
          )}
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <h4>Ask me anything about this complaint</h4>
        <div style={{ maxHeight: 160, overflowY: "auto", marginBottom: 8, fontSize: 13 }}>
          {chatLog.map((m, i) => (
            <p key={i}><strong>{m.role === "user" ? "You" : "AI"}:</strong> {m.text}</p>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Ask me anything about this complaint..."
            style={{ flex: 1 }}
          />
          <button onClick={handleAsk}>Send</button>
        </div>
        <p style={{ fontSize: 11, color: "#aaa", marginTop: 4 }}>
          AI responses may contain errors. Please verify information.
        </p>
      </div>
    </div>
  );
}
