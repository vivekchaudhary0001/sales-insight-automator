import { useState, useRef, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const CheckIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="10" fill="#10b981"/>
    <path d="M6 10l3 3 5-6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const UploadIcon = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M16 20V8M10 14l6-6 6 6" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M6 24h20" strokeLinecap="round"/>
  </svg>
);

const SpinnerIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" className="spinner">
    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" strokeDasharray="40" strokeDashoffset="15" fill="none"/>
  </svg>
);

export default function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = useCallback((f) => {
    if (!f) return;
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["csv", "xlsx", "xls"].includes(ext)) {
      setErrorMsg("Only .csv and .xlsx files are supported.");
      setStatus("error");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setErrorMsg("File must be under 10MB.");
      setStatus("error");
      return;
    }
    setFile(f);
    setStatus("idle");
    setErrorMsg("");
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = () => setDragOver(false);

  const handleSubmit = async () => {
    if (!file || !email) return;
    setStatus("loading");
    setErrorMsg("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("recipient_email", email);

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setResult(data);
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message);
      setStatus("error");
    }
  };

  const reset = () => {
    setFile(null);
    setEmail("");
    setStatus("idle");
    setResult(null);
    setErrorMsg("");
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --ink: #0c1117;
          --paper: #f5f2ec;
          --cream: #ede9df;
          --gold: #c9a84c;
          --gold-light: #f0dea0;
          --muted: #6b6560;
          --success: #2d6a4f;
          --error: #8b1a1a;
          --border: #d4cfc6;
        }

        body {
          background: var(--paper);
          color: var(--ink);
          font-family: 'DM Sans', sans-serif;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }

        .noise {
          position: fixed; inset: 0; pointer-events: none; z-index: 0;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
        }

        .page {
          position: relative; z-index: 1;
          width: 100%; max-width: 560px;
        }

        .masthead {
          text-align: center;
          margin-bottom: 40px;
        }

        .masthead-label {
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: var(--gold);
          margin-bottom: 12px;
        }

        .masthead h1 {
          font-family: 'DM Serif Display', serif;
          font-size: clamp(32px, 6vw, 46px);
          line-height: 1.1;
          color: var(--ink);
          margin-bottom: 12px;
        }

        .masthead h1 em {
          font-style: italic;
          color: var(--gold);
        }

        .masthead p {
          color: var(--muted);
          font-size: 15px;
          line-height: 1.6;
          max-width: 400px;
          margin: 0 auto;
        }

        .rule {
          width: 60px;
          height: 2px;
          background: linear-gradient(90deg, transparent, var(--gold), transparent);
          margin: 20px auto;
        }

        .card {
          background: #fff;
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 36px;
          box-shadow: 0 4px 32px rgba(12,17,23,0.06), 0 1px 4px rgba(12,17,23,0.04);
        }

        .drop-zone {
          border: 2px dashed var(--border);
          border-radius: 12px;
          padding: 36px 20px;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
          background: var(--cream);
          margin-bottom: 24px;
          position: relative;
        }

        .drop-zone:hover, .drop-zone.over {
          border-color: var(--gold);
          background: #faf8f2;
        }

        .drop-zone.has-file {
          border-style: solid;
          border-color: var(--gold);
          background: #fdf9ee;
        }

        .drop-zone-icon {
          color: var(--gold);
          margin-bottom: 10px;
          opacity: 0.8;
        }

        .drop-zone-title {
          font-size: 15px;
          font-weight: 500;
          color: var(--ink);
          margin-bottom: 4px;
        }

        .drop-zone-sub {
          font-size: 13px;
          color: var(--muted);
        }

        .file-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: var(--ink);
          color: #fff;
          border-radius: 99px;
          padding: 6px 14px;
          font-size: 13px;
          font-weight: 500;
          margin-top: 12px;
        }

        .file-badge button {
          background: none; border: none; cursor: pointer;
          color: rgba(255,255,255,0.6); font-size: 16px; line-height: 1;
          padding: 0 0 0 4px;
          transition: color 0.15s;
        }
        .file-badge button:hover { color: #fff; }

        label.field-label {
          display: block;
          font-size: 13px;
          font-weight: 600;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          color: var(--muted);
          margin-bottom: 8px;
        }

        input[type="email"] {
          width: 100%;
          border: 1.5px solid var(--border);
          border-radius: 10px;
          padding: 12px 16px;
          font-size: 15px;
          font-family: 'DM Sans', sans-serif;
          color: var(--ink);
          background: #fff;
          transition: border-color 0.2s;
          outline: none;
          margin-bottom: 24px;
        }

        input[type="email"]:focus {
          border-color: var(--gold);
          box-shadow: 0 0 0 3px rgba(201,168,76,0.12);
        }

        .btn-primary {
          width: 100%;
          padding: 14px;
          background: var(--ink);
          color: #fff;
          font-family: 'DM Sans', sans-serif;
          font-size: 15px;
          font-weight: 600;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .btn-primary:hover:not(:disabled) {
          background: #1e2a38;
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(12,17,23,0.15);
        }

        .btn-primary:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .spinner {
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .success-box {
          text-align: center;
          padding: 8px 0;
        }

        .success-icon {
          margin: 0 auto 16px;
          width: fit-content;
        }

        .success-box h2 {
          font-family: 'DM Serif Display', serif;
          font-size: 26px;
          margin-bottom: 8px;
        }

        .success-box p {
          color: var(--muted);
          font-size: 15px;
          line-height: 1.6;
          margin-bottom: 20px;
        }

        .stats {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 24px;
        }

        .stat {
          background: var(--cream);
          border-radius: 10px;
          padding: 14px;
          text-align: center;
        }

        .stat-value {
          font-size: 28px;
          font-family: 'DM Serif Display', serif;
          color: var(--ink);
        }

        .stat-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: var(--muted);
          margin-top: 2px;
        }

        .preview-box {
          background: #f8f6f1;
          border: 1px solid var(--border);
          border-radius: 10px;
          padding: 16px;
          text-align: left;
          margin-bottom: 24px;
        }

        .preview-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          color: var(--gold);
          font-weight: 600;
          margin-bottom: 8px;
        }

        .preview-text {
          font-size: 13px;
          color: var(--muted);
          line-height: 1.7;
          white-space: pre-wrap;
        }

        .error-box {
          background: #fff5f5;
          border: 1px solid #fca5a5;
          border-radius: 10px;
          padding: 14px 16px;
          color: var(--error);
          font-size: 14px;
          margin-bottom: 20px;
          display: flex;
          align-items: flex-start;
          gap: 8px;
        }

        .btn-ghost {
          background: none;
          border: 1.5px solid var(--border);
          border-radius: 10px;
          padding: 12px;
          font-family: 'DM Sans', sans-serif;
          font-size: 14px;
          cursor: pointer;
          width: 100%;
          color: var(--muted);
          transition: all 0.2s;
        }

        .btn-ghost:hover {
          border-color: var(--ink);
          color: var(--ink);
        }

        .footer-note {
          text-align: center;
          margin-top: 20px;
          font-size: 12px;
          color: var(--muted);
        }

        .footer-note a {
          color: var(--gold);
          text-decoration: none;
        }
      `}</style>

      <div className="noise" />

      <main className="page">
        <div className="masthead">
          <p className="masthead-label">Rabbitt AI · Sales Intelligence</p>
          <h1>The Sales <em>Insight</em><br />Automator</h1>
          <div className="rule" />
          <p>Upload your quarterly data. Get an executive brief delivered straight to your inbox — powered by AI.</p>
        </div>

        <div className="card">
          {status === "success" && result ? (
            <div className="success-box">
              <div className="success-icon"><CheckIcon /></div>
              <h2>Brief Dispatched</h2>
              <p>Your AI-generated summary is on its way to <strong>{result.recipient}</strong>.</p>

              <div className="stats">
                <div className="stat">
                  <div className="stat-value">{result.rows_analyzed}</div>
                  <div className="stat-label">Rows Analyzed</div>
                </div>
                <div className="stat">
                  <div className="stat-value">{result.columns_detected}</div>
                  <div className="stat-label">Columns Detected</div>
                </div>
              </div>

              <div className="preview-box">
                <div className="preview-label">Summary Preview</div>
                <div className="preview-text">{result.summary_preview}</div>
              </div>

              <button className="btn-ghost" onClick={reset}>← Analyze Another File</button>
            </div>
          ) : (
            <>
              {/* Drop Zone */}
              <div
                className={`drop-zone ${dragOver ? "over" : ""} ${file ? "has-file" : ""}`}
                onClick={() => !file && fileInputRef.current?.click()}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  style={{ display: "none" }}
                  onChange={(e) => handleFile(e.target.files[0])}
                />
                {!file ? (
                  <>
                    <div className="drop-zone-icon"><UploadIcon /></div>
                    <div className="drop-zone-title">Drop your file here</div>
                    <div className="drop-zone-sub">or click to browse · CSV, XLSX · max 10MB</div>
                  </>
                ) : (
                  <>
                    <div className="drop-zone-icon" style={{ color: "#10b981" }}>
                      <CheckIcon />
                    </div>
                    <div className="drop-zone-title">File ready</div>
                    <div className="file-badge">
                      📄 {file.name}
                      <button onClick={(e) => { e.stopPropagation(); setFile(null); }}>✕</button>
                    </div>
                  </>
                )}
              </div>

              {/* Email Input */}
              <label className="field-label">Recipient Email</label>
              <input
                type="email"
                placeholder="exec@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              />

              {/* Error */}
              {status === "error" && errorMsg && (
                <div className="error-box">
                  <span>⚠</span>
                  <span>{errorMsg}</span>
                </div>
              )}

              {/* Submit */}
              <button
                className="btn-primary"
                onClick={handleSubmit}
                disabled={!file || !email || status === "loading"}
              >
                {status === "loading" ? (
                  <><SpinnerIcon /> Analyzing data...</>
                ) : (
                  "Generate & Send Brief →"
                )}
              </button>
            </>
          )}
        </div>

        <p className="footer-note">
          Need to test the API directly? View{" "}
          <a href={`${API_BASE.replace("/api/v1", "")}/docs`} target="_blank" rel="noreferrer">
            Swagger docs ↗
          </a>
        </p>
      </main>
    </>
  );
}
