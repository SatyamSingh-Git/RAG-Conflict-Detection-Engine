"use client";

import { useState, useEffect, useRef } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ───────────────────────────────────────────────────────────────────
interface ProvenanceDoc {
  id: string;
  score: number;
  content: string;
  metadata: {
    department?: string;
    date?: string;
    filename?: string;
    source_type?: string;
    author?: string;
    text?: string;
    [key: string]: unknown;
  };
}

interface ConfidenceBreakdownItem {
  value: number;
  weight: number;
  label: string;
}

interface RAGResponse {
  answer: string;
  conflicting_evidence: string[];
  confidence_level: "High" | "Medium" | "Low";
  confidence_score?: number;
  confidence_breakdown?: Record<string, ConfidenceBreakdownItem>;
  reasoning: string;
  provenance: ProvenanceDoc[];
  error?: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
const DEPT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  "Patient Relations": { bg: "bg-emerald-500/20", text: "text-emerald-300", border: "border-emerald-500/30" },
  Emergency: { bg: "bg-orange-500/20", text: "text-orange-300", border: "border-orange-500/30" },
  Radiology: { bg: "bg-blue-500/20", text: "text-blue-300", border: "border-blue-500/30" },
  Facilities: { bg: "bg-amber-500/20", text: "text-amber-300", border: "border-amber-500/30" },
  Surgical: { bg: "bg-teal-500/20", text: "text-teal-300", border: "border-teal-500/30" },
  ICU: { bg: "bg-rose-500/20", text: "text-rose-300", border: "border-rose-500/30" },
  HR: { bg: "bg-violet-500/20", text: "text-violet-300", border: "border-violet-500/30" },
  "General Wards": { bg: "bg-sky-500/20", text: "text-sky-300", border: "border-sky-500/30" },
  Finance: { bg: "bg-indigo-500/20", text: "text-indigo-300", border: "border-indigo-500/30" },
  "Labor Relations": { bg: "bg-pink-500/20", text: "text-pink-300", border: "border-pink-500/30" },
};

function getDeptStyle(dept: string) {
  return DEPT_COLORS[dept] || { bg: "bg-slate-500/20", text: "text-slate-300", border: "border-slate-500/30" };
}

function getConfidenceColor(level: string) {
  if (level === "High") return { ring: "stroke-emerald-400", text: "text-emerald-300", label: "HIGH CONF.", glow: "shadow-emerald-500/30", bar: "bg-emerald-400" };
  if (level === "Medium") return { ring: "stroke-amber-400", text: "text-amber-300", label: "MED CONF.", glow: "shadow-amber-500/30", bar: "bg-amber-400" };
  return { ring: "stroke-rose-400", text: "text-rose-300", label: "LOW CONF.", glow: "shadow-rose-500/30", bar: "bg-rose-400" };
}

// ─── Confidence Gauge Component (Clickable + Expandable) ─────────────────────
function ConfidenceGauge({ level, score, breakdown }: { level: string; score?: number; breakdown?: Record<string, ConfidenceBreakdownItem> }) {
  const [expanded, setExpanded] = useState(false);
  const pct = score ?? (level === "High" ? 85 : level === "Medium" ? 55 : 25);
  const colors = getConfidenceColor(level);
  const circumference = 2 * Math.PI * 42;
  const offset = circumference - (pct / 100) * circumference;

  const barColors: Record<string, string> = {
    retrieval_similarity: "bg-blue-400",
    llm_confidence: "bg-purple-400",
    source_diversity: "bg-cyan-400",
    score_spread: "bg-amber-400",
  };

  return (
    <div className="flex flex-col items-center gap-1 shrink-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className={`relative w-20 h-20 rounded-full shadow-lg ${colors.glow} cursor-pointer hover:scale-105 transition-transform`}
        title="Click to see breakdown"
      >
        <svg className="w-20 h-20 -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="6" />
          <circle
            cx="50" cy="50" r="42" fill="none"
            className={colors.ring}
            strokeWidth="6" strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 1s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-white font-bold text-lg">{Math.round(pct)}%</span>
        </div>
      </button>
      <span className={`text-[10px] font-bold tracking-widest uppercase ${colors.text}`}>{colors.label}</span>
      <span className="text-[9px] text-white/30 mt-0.5 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        {expanded ? "▲ Hide" : "▼ Details"}
      </span>

      {/* Expandable Breakdown */}
      {expanded && breakdown && (
        <div className="mt-3 w-56 space-y-2.5 animate-in fade-in slide-in-from-top-2 duration-300">
          {Object.entries(breakdown).map(([key, item]) => (
            <div key={key} className="space-y-1">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-white/70 font-medium">{item.label}</span>
                <span className="text-white/50 font-mono">{Math.round(item.value)}% <span className="text-white/30">({item.weight}%w)</span></span>
              </div>
              <div className="h-1.5 rounded-full bg-white/[0.08] overflow-hidden">
                <div
                  className={`h-full rounded-full ${barColors[key] || "bg-indigo-400"} transition-all duration-700`}
                  style={{ width: `${item.value}%` }}
                />
              </div>
            </div>
          ))}
          <div className="pt-1.5 border-t border-white/[0.06]">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-white/80 font-semibold">Weighted Total</span>
              <span className={`font-bold font-mono ${colors.text}`}>{Math.round(pct)}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Orbital Loader Component ────────────────────────────────────────────────
function OrbitalLoader() {
  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <div className="relative w-40 h-40">
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full border-2 border-dashed border-indigo-400/40 animate-[spin_8s_linear_infinite]" />
        {/* Middle ring */}
        <div className="absolute inset-4 rounded-full border-2 border-indigo-500/30 animate-[spin_5s_linear_infinite_reverse]" />
        {/* Inner glow */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-indigo-500/30 blur-xl animate-pulse" />
          <div className="absolute w-5 h-5 rounded-full bg-indigo-400 shadow-lg shadow-indigo-400/60" />
        </div>
        {/* Orbiting dot 1 — glows and dims */}
        <div className="absolute inset-0 animate-[spin_3s_linear_infinite]">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-indigo-300 animate-pulse" style={{ boxShadow: "0 0 10px 3px rgba(129,140,248,0.6), 0 0 20px 6px rgba(129,140,248,0.3)" }} />
        </div>
        {/* Orbiting dot 2 — glows and dims */}
        <div className="absolute inset-2 animate-[spin_4s_linear_infinite_reverse]">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full bg-purple-300 animate-pulse" style={{ boxShadow: "0 0 10px 3px rgba(192,132,252,0.6), 0 0 20px 6px rgba(192,132,252,0.3)", animationDelay: "500ms" }} />
        </div>
      </div>
      <div className="text-center space-y-3">
        <p className="text-white/70 text-base font-medium">Retrieving documents &amp; analyzing for conflicts...</p>
        <div className="flex items-center justify-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "150ms" }} />
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────
export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [activeQuery, setActiveQuery] = useState("");
  const [sortBy, setSortBy] = useState<"relevance" | "date">("relevance");
  const [showFadeIn, setShowFadeIn] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [chunkExplanations, setChunkExplanations] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<string>("Conflicts");

  const sourcesRef = useRef<HTMLDivElement>(null);
  const analyticsRef = useRef<HTMLDivElement>(null);
  const conflictsRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settingsLoading, setSettingsLoading] = useState<string | null>(null);
  const [settingsToast, setSettingsToast] = useState<{ msg: string; type: "success" | "error" } | null>(null);

  useEffect(() => {
    if (response && !response.error) {
      setTimeout(() => setShowFadeIn(true), 50);
    }
  }, [response]);

  const handleQuery = async (q?: string) => {
    const question = q || query;
    if (!question.trim()) return;

    setQuery(question);
    setActiveQuery(question);
    setLoading(true);
    setResponse(null);
    setShowFadeIn(false);

    try {
      const res = await fetch(`${API_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });
      const data = await res.json();
      setResponse(data);
    } catch {
      setResponse({ error: "Failed to connect to backend.", answer: "", conflicting_evidence: [], confidence_level: "Low", reasoning: "", provenance: [] });
    }
    setLoading(false);
  };

  const handleShowDetails = async () => {
    if (!response?.provenance) return;
    setShowDetailsModal(true);
    setDetailsLoading(true);
    setChunkExplanations([]);

    const topChunks = [...response.provenance]
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(c => ({ id: c.id, score: c.score, content: c.content, metadata: c.metadata }));

    try {
      const res = await fetch(`${API_URL}/api/explain-chunks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: activeQuery, chunks: topChunks }),
      });
      const data = await res.json();
      setChunkExplanations(data.explanations || []);
    } catch {
      setChunkExplanations([]);
    }
    setDetailsLoading(false);
  };

  const showToast = (msg: string, type: "success" | "error") => {
    setSettingsToast({ msg, type });
    setTimeout(() => setSettingsToast(null), 4000);
  };

  const handleUploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSettingsLoading("upload");
    setSettingsOpen(false);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_URL}/api/upload-file`, { method: "POST", body: formData });
      const data = await res.json();
      if (data.status === "success") showToast(`✅ ${data.message}`, "success");
      else showToast(`❌ ${data.message}`, "error");
    } catch { showToast("❌ Failed to upload file", "error"); }
    setSettingsLoading(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleRecreateEmbeddings = async () => {
    setSettingsLoading("recreate");
    setSettingsOpen(false);
    try {
      const res = await fetch(`${API_URL}/api/recreate-embeddings`, { method: "POST" });
      const data = await res.json();
      if (data.status === "success") showToast(`✅ ${data.message}`, "success");
      else showToast(`❌ ${data.message}`, "error");
    } catch { showToast("❌ Failed to recreate embeddings", "error"); }
    setSettingsLoading(null);
  };

  const handleDeleteEmbeddings = async () => {
    if (!confirm("⚠️ This will permanently delete ALL embeddings from Pinecone. Continue?")) return;
    setSettingsLoading("delete");
    setSettingsOpen(false);
    try {
      const res = await fetch(`${API_URL}/api/delete-embeddings`, { method: "DELETE" });
      const data = await res.json();
      if (data.status === "success") showToast(`✅ ${data.message}`, "success");
      else showToast(`❌ ${data.message}`, "error");
    } catch { showToast("❌ Failed to delete embeddings", "error"); }
    setSettingsLoading(null);
  };

  const suggestions = [
    { icon: "📈", text: "Has patient satisfaction improved in Q1?" },
    { icon: "🏥", text: "What is the status of the new MRI machine?" },
    { icon: "🦠", text: "Are infection rates decreasing?" },
  ];

  const hasConflicts = response && response.conflicting_evidence && response.conflicting_evidence.length > 0;

  const sortedProvenance = response?.provenance
    ? [...response.provenance].sort((a, b) => {
      if (sortBy === "relevance") return b.score - a.score;
      return (b.metadata.date || "").localeCompare(a.metadata.date || "");
    })
    : [];

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white font-sans flex flex-col">
      {/* ── Top Nav ─────────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-[#0a0e1a]/80 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-[1100px] mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <span className="font-bold text-[15px] tracking-tight">Envint Intelligence</span>
          </div>

          {response && !response.error && (
            <div className="hidden md:flex items-center gap-1">
              {["Dashboard", "Conflicts", "Sources", "Analytics"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => {
                    if (tab === "Dashboard") { setResponse(null); setActiveQuery(""); setQuery(""); setActiveTab("Conflicts"); return; }
                    setActiveTab(tab);
                    if (tab === "Sources" && sourcesRef.current) sourcesRef.current.scrollIntoView({ behavior: "smooth" });
                    if (tab === "Conflicts" && conflictsRef.current) conflictsRef.current.scrollIntoView({ behavior: "smooth" });
                    if (tab === "Analytics" && analyticsRef.current) analyticsRef.current.scrollIntoView({ behavior: "smooth" });
                  }}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${tab === activeTab ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30" : "text-white/50 hover:text-white/80 hover:bg-white/5"}`}
                >
                  {tab}
                </button>
              ))}
            </div>
          )}

          <div className="flex items-center gap-3">
            {response && !response.error && (
              <div className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[11px] text-indigo-400 font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Powered by DeepSeek
              </div>
            )}
            <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center relative">
              <button onClick={() => setSettingsOpen(!settingsOpen)} className="w-full h-full flex items-center justify-center rounded-full hover:bg-white/20 transition-all">
                {settingsLoading ? (
                  <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-indigo-400 rounded-full animate-spin" />
                ) : (
                  <svg className="w-3.5 h-3.5 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                )}
              </button>

              {/* Settings Dropdown */}
              {settingsOpen && (
                <>
                  <div className="fixed inset-0 z-[60]" onClick={() => setSettingsOpen(false)} />
                  <div className="absolute right-0 top-9 z-[70] w-64 rounded-xl bg-[#161c3a] border border-white/[0.12] shadow-2xl overflow-hidden">
                    <div className="px-4 py-2.5 border-b border-white/[0.06]">
                      <p className="text-xs font-bold text-white/80 uppercase tracking-wider">Document Management</p>
                    </div>

                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full px-4 py-3 flex items-center gap-3 hover:bg-white/[0.06] transition-all text-left group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center shrink-0">
                        <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                      </div>
                      <div>
                        <p className="text-sm text-white/90 font-medium group-hover:text-white">Upload Document</p>
                        <p className="text-[10px] text-white/40">PDF, TXT, or MD → auto-ingest</p>
                      </div>
                    </button>

                    <button
                      onClick={handleRecreateEmbeddings}
                      className="w-full px-4 py-3 flex items-center gap-3 hover:bg-white/[0.06] transition-all text-left group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-blue-500/15 flex items-center justify-center shrink-0">
                        <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                      </div>
                      <div>
                        <p className="text-sm text-white/90 font-medium group-hover:text-white">Recreate Embeddings</p>
                        <p className="text-[10px] text-white/40">Clear index & re-embed all files</p>
                      </div>
                    </button>

                    <div className="border-t border-white/[0.06]">
                      <button
                        onClick={handleDeleteEmbeddings}
                        className="w-full px-4 py-3 flex items-center gap-3 hover:bg-rose-500/[0.08] transition-all text-left group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-rose-500/15 flex items-center justify-center shrink-0">
                          <svg className="w-4 h-4 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                        </div>
                        <div>
                          <p className="text-sm text-rose-300 font-medium group-hover:text-rose-200">Delete All Embeddings</p>
                          <p className="text-[10px] text-white/40">Permanently clear Pinecone index</p>
                        </div>
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
            <input ref={fileInputRef} type="file" accept=".pdf,.txt,.md" className="hidden" onChange={handleUploadFile} />
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-[11px] font-bold">S</div>
          </div>
        </div>
      </nav>

      {/* ── Content ──────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[1100px] mx-auto px-6 pb-36">

          {/* ── Empty State ──────────────────────────────── */}
          {!response && !loading && (
            <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
              <div className="w-16 h-16 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mb-8">
                <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9zm3.75 11.625a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold mb-4 tracking-tight">Query Hospital Performance Data</h1>
              <p className="text-white/60 max-w-md leading-relaxed mb-10 text-[15px]">
                Ask about hospital metrics, conflict detection, or performance analytics. Envint AI retrieves and verifies data sources for you.
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                {suggestions.map((s) => (
                  <button
                    key={s.text}
                    onClick={() => { setQuery(s.text); handleQuery(s.text); }}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/[0.06] border border-white/[0.12] text-sm text-white/70 hover:text-white hover:bg-white/[0.12] hover:border-white/[0.2] transition-all duration-300"
                  >
                    <span>{s.icon}</span>
                    {s.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ── Loading State ──────────────────────────── */}
          {loading && (
            <div className="flex items-center justify-center min-h-[70vh]">
              <OrbitalLoader />
            </div>
          )}

          {/* ── Error State ───────────────────────────── */}
          {response?.error && (
            <div className="flex items-center justify-center min-h-[70vh]">
              <div className="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-8 text-center max-w-md">
                <p className="text-rose-400 font-medium">{response.error}</p>
              </div>
            </div>
          )}

          {/* ── Results ───────────────────────────────── */}
          {response && !response.error && (
            <div className={`py-8 space-y-8 transition-all duration-700 ${showFadeIn ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>

              {/* Title section */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded bg-indigo-500 flex items-center justify-center">
                    <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 8 8"><rect width="8" height="8" rx="1" /></svg>
                  </span>
                  <span className="text-indigo-400 text-xs font-bold tracking-widest uppercase">Conflict Analysis</span>
                </div>
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold tracking-tight">{activeQuery}</h2>
                  <span className="text-white/50 text-xs flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-white/20" />
                    Analyzed just now
                  </span>
                </div>
              </div>

              {/* AI Synthesis Card */}
              <div ref={conflictsRef} />
              <div className="rounded-2xl bg-gradient-to-br from-[#161c3a] to-[#111730] border border-white/[0.1] p-6 md:p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/[0.05] rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
                <div className="flex items-start gap-6">
                  <ConfidenceGauge level={response.confidence_level} score={response.confidence_score} breakdown={response.confidence_breakdown} />
                  <div className="flex-1 space-y-4">
                    <h3 className="text-white font-semibold flex items-center gap-2">
                      <span className="text-lg">✨</span> AI Synthesis
                    </h3>
                    <p className="text-white/90 leading-relaxed text-[15px]">{response.answer}</p>
                    <div className="pt-3 mt-3 border-t border-white/[0.08]">
                      <p className="text-white/60 text-sm leading-relaxed"><span className="text-white/80 font-semibold">Reasoning: </span>{response.reasoning}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Conflict Detection Card */}
              {hasConflicts && (
                <div className="rounded-2xl bg-gradient-to-br from-[#1f1228] to-[#161020] border border-rose-500/25 p-6 md:p-8 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/[0.06] rounded-full blur-3xl pointer-events-none" />

                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-rose-500/15 flex items-center justify-center">
                        <svg className="w-4 h-4 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                      </div>
                      <div>
                        <h4 className="text-white font-semibold text-[15px]">Conflicting Evidence Detected</h4>
                        <p className="text-white/50 text-xs mt-0.5">Direct contradiction found across {response.conflicting_evidence.length} primary sources</p>
                      </div>
                    </div>
                    <button
                      onClick={handleShowDetails}
                      className="px-4 py-2 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold hover:bg-indigo-500/30 transition-all flex items-center gap-1.5"
                    >
                      Show Details <span>→</span>
                    </button>
                  </div>

                  {/* Side by side conflict cards */}
                  <div className="flex flex-col md:flex-row gap-4 items-stretch relative">
                    {response.conflicting_evidence.slice(0, 2).map((evidence, i) => {
                      const parts = evidence.split(" -> ");
                      const source = parts[0] || "Source";
                      const claim = parts[1] || evidence;
                      return (
                        <div key={i} className="flex-1 rounded-xl bg-white/[0.05] border border-white/[0.1] p-5 space-y-3">
                          <div className="flex items-center gap-2">
                            <div className={`w-6 h-6 rounded flex items-center justify-center text-xs ${i === 0 ? "bg-rose-500/25 text-rose-300" : "bg-amber-500/25 text-amber-300"}`}>
                              {i === 0 ? "📊" : "📋"}
                            </div>
                            <span className="text-white/90 text-sm font-semibold">{source.split("_chunk")[0].replace(/_/g, " ")}</span>
                          </div>
                          <p className="text-white/70 text-sm leading-relaxed">{claim}</p>
                        </div>
                      );
                    })}
                    {/* VS Badge */}
                    {response.conflicting_evidence.length >= 2 && (
                      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden md:flex">
                        <span className="w-9 h-9 rounded-full bg-rose-500/30 border-2 border-rose-500/40 flex items-center justify-center text-rose-300 text-xs font-bold shadow-lg shadow-rose-500/20">VS</span>
                      </div>
                    )}
                  </div>

                  {/* Extra conflicts */}
                  {response.conflicting_evidence.length > 2 && (
                    <div className="mt-4 space-y-2">
                      {response.conflicting_evidence.slice(2).map((evidence, i) => (
                        <div key={i} className="rounded-lg bg-rose-500/5 border border-rose-500/10 p-3 text-sm text-rose-300/70 flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 shrink-0" />
                          {evidence}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Retrieved Sources */}
              <div ref={sourcesRef} />
              {response.provenance && response.provenance.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-white font-semibold text-lg">Retrieved Sources</h3>
                    <div className="flex items-center gap-1 bg-white/[0.03] rounded-lg p-0.5 border border-white/[0.06]">
                      <button onClick={() => setSortBy("relevance")} className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${sortBy === "relevance" ? "bg-white/10 text-white" : "text-white/40 hover:text-white/60"}`}>By Relevance</button>
                      <button onClick={() => setSortBy("date")} className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${sortBy === "date" ? "bg-white/10 text-white" : "text-white/40 hover:text-white/60"}`}>By Date</button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {sortedProvenance.map((doc, i) => {
                      const fname = doc.metadata.filename || doc.id || "";
                      const nameParts = fname.replace(/\.(pdf|txt|md)$/i, "").split("_").filter(p => isNaN(Number(p)));
                      const dept = doc.metadata.department || nameParts[0] || "Unknown";
                      const deptStyle = getDeptStyle(dept);
                      const matchPct = (doc.score * 100).toFixed(1);
                      return (
                        <div key={i} className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-5 hover:bg-white/[0.07] hover:border-white/[0.15] transition-all duration-300 group space-y-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${deptStyle.bg} ${deptStyle.text} border ${deptStyle.border}`}>
                                {dept}
                              </span>
                              <span className="text-white/50 text-xs">{doc.metadata.date || ""}</span>
                            </div>
                            <span className="text-xs font-mono text-emerald-300 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">
                              {matchPct}% Match
                            </span>
                          </div>
                          <p className="text-sm font-semibold text-white/90 group-hover:text-white transition-colors">
                            {doc.metadata.filename?.replace(/_/g, " ").replace(/\.(pdf|txt|md)$/i, "") || "Document"}
                          </p>
                          <p className="text-xs text-white/60 line-clamp-3 leading-relaxed">
                            &ldquo;{doc.content}&rdquo;
                          </p>
                          {doc.metadata.author && (
                            <div className="flex items-center gap-1.5 pt-1">
                              <div className="w-4 h-4 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center text-[8px] font-bold">
                                {doc.metadata.author.charAt(0)}
                              </div>
                              <span className="text-[11px] text-white/45">{doc.metadata.author}</span>
                            </div>
                          )}
                          <div className="text-[10px] text-white/30 font-mono pt-1 border-t border-white/[0.06]">
                            ID: {doc.id}
                          </div>
                        </div>
                      );
                    })}

                    {/* Connect more sources placeholder */}
                    <div className="rounded-xl border-2 border-dashed border-white/[0.1] p-5 flex flex-col items-center justify-center gap-2 text-white/35 hover:text-white/50 hover:border-white/[0.15] transition-all cursor-pointer min-h-[160px]">
                      <div className="w-8 h-8 rounded-full border border-white/10 flex items-center justify-center">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                      </div>
                      <span className="text-xs font-medium">Connect more data sources</span>
                    </div>
                  </div>
                </div>
              )}

              {/* ── Analytics Section ─────────────────────────────── */}
              <div ref={analyticsRef} />
              <div className="space-y-6">
                <h3 className="text-white font-semibold text-lg flex items-center gap-2">
                  <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                  Analytics
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Stat Card 1: Chunks Retrieved */}
                  <div className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-5 space-y-2">
                    <p className="text-xs text-white/40 uppercase tracking-wider font-semibold">Chunks Retrieved</p>
                    <p className="text-3xl font-bold text-white">{response.provenance?.length || 0}</p>
                    <p className="text-xs text-white/40">from Pinecone vector index</p>
                  </div>

                  {/* Stat Card 2: Conflicts Found */}
                  <div className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-5 space-y-2">
                    <p className="text-xs text-white/40 uppercase tracking-wider font-semibold">Conflicts Found</p>
                    <p className={`text-3xl font-bold ${hasConflicts ? "text-rose-400" : "text-emerald-400"}`}>{response.conflicting_evidence?.length || 0}</p>
                    <p className="text-xs text-white/40">{hasConflicts ? "cross-source contradictions" : "no contradictions detected"}</p>
                  </div>

                  {/* Stat Card 3: Avg Similarity */}
                  <div className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-5 space-y-2">
                    <p className="text-xs text-white/40 uppercase tracking-wider font-semibold">Avg Similarity</p>
                    <p className="text-3xl font-bold text-blue-400">
                      {response.provenance && response.provenance.length > 0
                        ? (response.provenance.reduce((s, d) => s + d.score, 0) / response.provenance.length * 100).toFixed(1)
                        : "0"}%
                    </p>
                    <p className="text-xs text-white/40">cosine similarity average</p>
                  </div>
                </div>

                {/* Score Distribution Bar Chart */}
                <div className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-5 space-y-4">
                  <p className="text-sm font-semibold text-white/80">Score Distribution per Chunk</p>
                  <div className="space-y-2.5">
                    {sortedProvenance.map((doc, i) => {
                      const pct = (doc.score * 100);
                      const barColors = ["bg-blue-400", "bg-indigo-400", "bg-purple-400", "bg-cyan-400", "bg-violet-400"];
                      return (
                        <div key={i} className="flex items-center gap-3">
                          <span className="text-[10px] text-white/50 font-mono w-20 truncate shrink-0">
                            {doc.metadata.filename?.replace(/_/g, " ").split(".")[0]?.slice(0, 12) || `Chunk ${i + 1}`}
                          </span>
                          <div className="flex-1 h-3 rounded-full bg-white/[0.06] overflow-hidden">
                            <div
                              className={`h-full rounded-full ${barColors[i % barColors.length]} transition-all duration-700`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-mono text-white/60 w-12 text-right">{pct.toFixed(1)}%</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Department Breakdown */}
                {(() => {
                  const deptCounts: Record<string, number> = {};
                  response.provenance?.forEach(d => {
                    const fname = d.metadata.filename || d.id || "";
                    const nameParts = fname.replace(/\.(pdf|txt|md)$/i, "").split("_").filter((p: string) => isNaN(Number(p)));
                    const dept = d.metadata.department || nameParts[0] || "Unknown";
                    deptCounts[dept] = (deptCounts[dept] || 0) + 1;
                  });
                  const deptEntries = Object.entries(deptCounts).sort((a, b) => b[1] - a[1]);
                  const total = response.provenance?.length || 1;

                  return (
                    <div className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-5 space-y-4">
                      <p className="text-sm font-semibold text-white/80">Department Breakdown</p>
                      <div className="flex flex-wrap gap-3">
                        {deptEntries.map(([dept, count]) => {
                          const style = getDeptStyle(dept);
                          const widthPct = (count / total) * 100;
                          return (
                            <div key={dept} className="flex-1 min-w-[140px] space-y-1.5">
                              <div className="flex items-center justify-between">
                                <span className={`text-xs font-bold ${style.text}`}>{dept}</span>
                                <span className="text-[10px] text-white/40 font-mono">{count} chunk{count > 1 ? "s" : ""} ({widthPct.toFixed(0)}%)</span>
                              </div>
                              <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden">
                                <div className={`h-full rounded-full ${style.bg.replace("/20", "/60")} transition-all duration-700`} style={{ width: `${widthPct}%` }} />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })()}

              </div>

            </div>
          )}
        </div>
      </div>

      {/* ── Details Modal Overlay ───────────────────────────────────── */}
      {showDetailsModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setShowDetailsModal(false)} />

          {/* Modal */}
          <div className="relative bg-[#12162a] border border-white/[0.12] rounded-2xl shadow-2xl w-full max-w-3xl max-h-[85vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-[#12162a]/95 backdrop-blur-xl border-b border-white/[0.08] p-6 flex items-center justify-between z-10">
              <div>
                <h3 className="text-lg font-bold text-white">📋 Chunk Analysis — Top 3 Sources</h3>
                <p className="text-white/50 text-xs mt-1">AI-powered analysis of why these chunks matter most</p>
              </div>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="w-8 h-8 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] flex items-center justify-center text-white/50 hover:text-white transition-all"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-5">
              {detailsLoading && (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-400 rounded-full animate-spin" />
                  <p className="text-white/40 text-sm">Analyzing chunks with DeepSeek...</p>
                </div>
              )}

              {!detailsLoading && chunkExplanations.length === 0 && (
                <p className="text-white/40 text-center py-12">No explanations available.</p>
              )}

              {!detailsLoading && chunkExplanations.map((exp, i: number) => {
                const topChunks = response?.provenance
                  ? [...response.provenance].sort((a, b) => b.score - a.score).slice(0, 3)
                  : [];
                const chunk = topChunks[i];
                const stanceColor = exp.stance === "contradicts"
                  ? { bg: "bg-rose-500/15", text: "text-rose-300", border: "border-rose-500/25", label: "⚠ Contradicts" }
                  : exp.stance === "supports"
                    ? { bg: "bg-emerald-500/15", text: "text-emerald-300", border: "border-emerald-500/25", label: "✓ Supports" }
                    : { bg: "bg-slate-500/15", text: "text-slate-300", border: "border-slate-500/25", label: "— Neutral" };

                return (
                  <div key={i} className="rounded-xl bg-white/[0.04] border border-white/[0.08] overflow-hidden">
                    {/* Chunk Header */}
                    <div className="px-5 py-3 bg-white/[0.02] border-b border-white/[0.06] flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="w-7 h-7 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-300 text-xs font-bold">#{i + 1}</span>
                        <span className="text-white font-semibold text-sm">{exp.title || `Chunk ${i + 1}`}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${stanceColor.bg} ${stanceColor.text} border ${stanceColor.border}`}>
                          {stanceColor.label}
                        </span>
                        {chunk && (
                          <span className="text-xs font-mono text-emerald-300 bg-emerald-400/10 px-2 py-0.5 rounded">
                            {(chunk.score * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Full Chunk Content */}
                    {chunk && (
                      <div className="px-5 py-3 bg-white/[0.01] border-b border-white/[0.04]">
                        <p className="text-xs text-white/30 uppercase tracking-wider font-semibold mb-2">Full Document Chunk</p>
                        <p className="text-sm text-white/75 leading-relaxed whitespace-pre-wrap">{chunk.content}</p>
                      </div>
                    )}

                    {/* AI Explanation */}
                    <div className="px-5 py-4 space-y-3">
                      <div>
                        <p className="text-xs text-indigo-400 uppercase tracking-wider font-semibold mb-1.5">Why This Matters</p>
                        <p className="text-sm text-white/80 leading-relaxed">{exp.relevance}</p>
                      </div>
                      {exp.key_claims && exp.key_claims.length > 0 && (
                        <div>
                          <p className="text-xs text-amber-400 uppercase tracking-wider font-semibold mb-1.5">Key Claims</p>
                          <ul className="space-y-1">
                            {exp.key_claims.map((claim: string, j: number) => (
                              <li key={j} className="flex items-start gap-2 text-sm text-white/70">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                                {claim}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── Bottom Input ──────────────────────────────────────────────── */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-[#0a0e1a] via-[#0a0e1a] to-transparent pt-8 pb-4 px-6 z-50">
        <div className="max-w-[800px] mx-auto">
          <form onSubmit={(e) => { e.preventDefault(); handleQuery(); }} className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-2xl blur-lg opacity-50" />
            <div className="relative flex items-center bg-[#161c30] rounded-2xl border border-white/[0.12] shadow-2xl">
              <div className="pl-4">
                <div className="w-8 h-8 rounded-lg bg-white/[0.04] flex items-center justify-center">
                  <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                </div>
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={loading ? "Please wait while engine initializes..." : response ? "Ask a follow-up question about this conflict..." : "Ask a question about your data..."}
                className="flex-1 bg-transparent px-4 py-4 text-white text-sm focus:outline-none placeholder:text-white/40"
                disabled={loading}
              />
              <div className="flex items-center gap-2 pr-3">
                <button type="button" className="w-8 h-8 rounded-lg flex items-center justify-center text-white/25 hover:text-white/50 transition-colors">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                </button>
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="w-9 h-9 rounded-xl bg-indigo-500 hover:bg-indigo-400 disabled:bg-white/[0.06] disabled:text-white/15 text-white flex items-center justify-center transition-all shadow-lg shadow-indigo-500/20 disabled:shadow-none"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18" /></svg>
                </button>
              </div>
            </div>
          </form>
          <p className="text-center mt-3 text-[11px] text-white/20">
            AI can make mistakes. Please verify critical conflicts manually.
          </p>
        </div>
      </div>

      {/* ── Toast Notification ────────────────────────────────────────── */}
      {settingsToast && (
        <div className={`fixed bottom-24 right-6 z-[80] px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-xl flex items-center gap-2.5 animate-in slide-in-from-right-5 duration-300 ${settingsToast.type === "success"
          ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
          : "bg-rose-500/15 border-rose-500/30 text-rose-300"
          }`}>
          <p className="text-sm font-medium max-w-xs">{settingsToast.msg}</p>
          <button onClick={() => setSettingsToast(null)} className="text-white/40 hover:text-white/70 transition-colors ml-2">✕</button>
        </div>
      )}
    </div>
  );
}
