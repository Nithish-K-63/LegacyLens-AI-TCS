import React, { useState, useEffect, useMemo, useRef } from "react";
import * as api from "./api/client";

// Navigation definition matching Figma UI
const navSections = [
  {
    section: "Workspace",
    items: [
      { label: "Overview", icon: "grid" },
      { label: "Upload", icon: "upload" },
      { label: "Analysis", icon: "pulse" },
      { label: "Module Explorer", icon: "layers" },
    ],
  },
  {
    section: "Intelligence",
    items: [
      { label: "Pipeline", icon: "route" },
      { label: "Code Intelligence", icon: "code" },
      { label: "Business Rules", icon: "book" },
      { label: "Dependencies", icon: "nodes" },
      { label: "Risk Heatmap", icon: "risk" },
      { label: "Technology Audit", icon: "check" },
    ],
  },
  {
    section: "Modernization",
    items: [
      { label: "Architecture", icon: "layers" },
      { label: "Roadmap", icon: "route" },
      { label: "Regression Tests", icon: "check" },
      { label: "Reports", icon: "file" },
    ],
  },
];

// SVG Icon system from Figma reference
function Icon({ name, size = 18 }) {
  const icons = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="2" />
        <rect x="14" y="3" width="7" height="7" rx="2" />
        <rect x="3" y="14" width="7" height="7" rx="2" />
        <rect x="14" y="14" width="7" height="7" rx="2" />
      </>
    ),
    upload: (
      <>
        <path d="M12 16V4m0 0L7 9m5-5 5 5" />
        <path d="M4 15v5h16v-5" />
      </>
    ),
    pulse: <path d="M3 12h4l2.5-7 5 14 2.5-7h4" />,
    code: (
      <>
        <path d="m8 9-4 3 4 3m8-6 4 3-4 3" />
        <path d="m14 5-4 14" />
      </>
    ),
    book: (
      <>
        <path d="M4 5a3 3 0 0 1 3-3h5v18H7a3 3 0 0 0-3 2z" />
        <path d="M20 5a3 3 0 0 0-3-3h-5v18h5a3 3 0 0 1 3 2z" />
      </>
    ),
    nodes: (
      <>
        <circle cx="6" cy="6" r="3" />
        <circle cx="18" cy="18" r="3" />
        <circle cx="18" cy="6" r="3" />
        <path d="M9 6h6M8 8l8 8" />
      </>
    ),
    risk: (
      <>
        <path d="M12 3 2.5 20h19z" />
        <path d="M12 9v4m0 3h.01" />
      </>
    ),
    layers: (
      <>
        <path d="m12 2 9 5-9 5-9-5z" />
        <path d="m3 12 9 5 9-5m-18 5 9 5 9-5" />
      </>
    ),
    route: (
      <>
        <circle cx="6" cy="18" r="2" />
        <circle cx="18" cy="6" r="2" />
        <path d="M6 16V9a3 3 0 0 1 3-3h7" />
      </>
    ),
    check: (
      <>
        <path d="m5 12 4 4L19 6" />
        <circle cx="12" cy="12" r="10" />
      </>
    ),
    file: (
      <>
        <path d="M6 2h8l4 4v16H6z" />
        <path d="M14 2v5h5M9 13h6m-6 4h6" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z" />
      </>
    ),
    search: (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-4-4" />
      </>
    ),
    bell: (
      <>
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </>
    ),
    moon: <path d="M20 15.5A9 9 0 0 1 8.5 4 9 9 0 1 0 20 15.5Z" />,
    sun: (
      <>
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </>
    ),
    menu: <path d="M4 7h16M4 12h16M4 17h16" />,
    x: <path d="m6 6 12 12M18 6 6 18" />,
    arrow: <path d="m9 18 6-6-6-6" />,
    copy: (
      <>
        <rect x="8" y="8" width="12" height="12" rx="2" />
        <path d="M16 8V4H4v12h4" />
      </>
    ),
    download: (
      <>
        <path d="M12 3v13m0 0 5-5m-5 5-5-5" />
        <path d="M4 21h16" />
      </>
    ),
    refresh: (
      <>
        <path d="M20 7v5h-5" />
        <path d="M19 12a7 7 0 1 0-2 5" />
      </>
    ),
    info: (
      <>
        <circle cx="12" cy="12" r="10" />
        <path d="M12 11v6m0-10h.01" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {icons[name] || icons.info}
    </svg>
  );
}

function Badge({ children, tone = "neutral" }) {
  return (
    <span className={`badge ${tone.toLowerCase().replace(/[\s_]+/g, "-")}`}>
      {children}
    </span>
  );
}

function Button({ children, onClick, variant = "primary", disabled = false, type = "button" }) {
  return (
    <button type={type} disabled={disabled} onClick={onClick} className={`button ${variant}`}>
      {children}
    </button>
  );
}

function SearchInput({ value, onChange, placeholder = "Search…" }) {
  return (
    <label className="search">
      <Icon name="search" size={16} />
      <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
    </label>
  );
}

function PageHeader({ title, description, actions }) {
  return (
    <>
      <header className="page-title">
        <div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        {actions && <div className="title-actions">{actions}</div>}
      </header>
      <SectionUniqueVisual title={title} />
    </>
  );
}

function SectionUniqueVisual({ title }) {
  const bars = [1, 2, 3, 2, 4, 3, 2, 1, 3, 4, 2, 3];
  let content = null;

  switch (title) {
    case "Upload project":
      content = (
        <div className="unique-upload">
          <div className="file-stack">
            <i />
            <i />
            <i><Icon name="upload" /></i>
          </div>
          <span className="flow-line" />
          <div className="intake-gates">
            <b>ZIP/GIT</b>
            <b>Validate</b>
            <b>Ready</b>
          </div>
          <strong>Secure intake flow</strong>
        </div>
      );
      break;
    case "Analysis":
      content = (
        <div className="unique-orbit">
          <i className="u-orbit o1" />
          <i className="u-orbit o2" />
          <strong>94%</strong>
          {["file", "nodes", "book", "risk"].map((icon, idx) => (
            <span key={icon} className={`sat s${idx}`}>
              <Icon name={icon} size={13} />
            </span>
          ))}
          <small>Agent convergence</small>
        </div>
      );
      break;
    case "Code intelligence":
      content = (
        <div className="unique-flame">
          {[38, 57, 46, 75, 61, 92, 69, 84, 55, 78].map((h, i) => (
            <i key={i} style={{ height: `${h}%` }}><b /></i>
          ))}
          <strong>Risk fingerprint</strong>
        </div>
      );
      break;
    case "Business rules":
      content = (
        <div className="unique-rules">
          <span className="rule-core">64</span>
          {["Pricing", "Access", "Tax", "Order"].map((cat, i) => (
            <i key={cat} className={`r${i}`}>{cat}</i>
          ))}
          <strong>Rule constellation</strong>
        </div>
      );
      break;
    case "Dependency explorer":
      content = (
        <div className="unique-deps">
          {["UI", "Order", "Price", "DB", "API"].map((mod, i) => (
            <span key={mod}>
              <i className={`dep-tone-${i}`}>{mod}</i>
              {i < 4 && <b />}
            </span>
          ))}
          <strong>Critical dependency path</strong>
        </div>
      );
      break;
    case "Modernization risk":
      content = (
        <div className="unique-risk">
          <div>
            {bars.map((b, i) => (
              <i key={i} className={`uheat h${b}`} />
            ))}
          </div>
          <span>
            <strong>81</strong>
            <small>exposure</small>
          </span>
          <b>Risk terrain</b>
        </div>
      );
      break;
    case "Target architecture":
      content = (
        <div className="unique-arch">
          <span>Gateway</span>
          <i />
          <div>
            <b>Order</b>
            <b>Pricing</b>
            <b>Customer</b>
          </div>
          <strong>Proposed capability boundaries</strong>
        </div>
      );
      break;
    case "Migration roadmap":
      content = (
        <div className="unique-road">
          {["Discover", "Contain", "Extract", "Scale"].map((step, i) => (
            <span key={step} style={{ transform: `translateY(${-i * 9}px)` }}>
              <i>{i + 1}</i>
              <b>{step}</b>
            </span>
          ))}
          <strong>Phased ascent</strong>
        </div>
      );
      break;
    case "Regression tests":
      content = (
        <div className="unique-tests">
          {[1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0].map((v, i) => (
            <i key={i} className={v ? "pass" : "gap"}>
              {v ? "✓" : "·"}
            </i>
          ))}
          <span>
            <strong>8/12</strong>
            <small>behavior paths</small>
          </span>
        </div>
      );
      break;
    case "Analysis report":
      content = (
        <div className="unique-report">
          <div className="report-pages">
            <i /><i />
            <i><b /><b /><b /></i>
          </div>
          <span>
            <strong>11 sections</strong>
            <small>Decision-ready evidence</small>
          </span>
        </div>
      );
      break;
    case "Settings":
      content = (
        <div className="unique-settings">
          {[72, 46, 88].map((pos, i) => (
            <span key={pos}>
              <i><b style={{ left: `${pos}%` }} /></i>
              <small>{["Analysis depth", "Inference", "Alerts"][i]}</small>
            </span>
          ))}
          <strong>Workspace controls</strong>
        </div>
      );
      break;
    default:
      content = (
        <div className="unique-radar">
          <svg viewBox="0 0 180 92">
            <polygon points="90,5 166,47 90,88 14,47" className="radar-grid" />
            <polygon points="90,20 143,47 90,74 37,47" className="radar-grid" />
            <polygon points="90,12 154,47 90,68 43,47" className="radar-value" />
            <circle cx="90" cy="12" r="3" />
            <circle cx="154" cy="47" r="3" />
            <circle cx="90" cy="68" r="3" />
            <circle cx="43" cy="47" r="3" />
          </svg>
          <span>
            <strong>86%</strong>
            <small>system clarity</small>
          </span>
        </div>
      );
  }

  return (
    <section className={`section-unique unique-${title.toLowerCase().replace(/[\s_]+/g, "-")}`}>
      {content}
    </section>
  );
}

function DetailItem({ label, children }) {
  return (
    <div className="detail">
      <span>{label}</span>
      <div>{children}</div>
    </div>
  );
}

function Drawer({ title, onClose, children }) {
  return (
    <div className="drawer-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <aside className="drawer" role="dialog" aria-modal="true">
        <div className="drawer-head">
          <strong>{title}</strong>
          <button onClick={onClose} aria-label="Close panel">
            <Icon name="x" />
          </button>
        </div>
        <div className="drawer-body">{children}</div>
      </aside>
    </div>
  );
}

// System Intelligence Map Visual Card on Overview Page
function SystemIntelligenceMap({ go, modules = [], edges = [] }) {
  const findMod = (id) => modules.find((m) => m.id === id);

  return (
    <section className="card intelligence-map-card">
      <div className="card-head">
        <div>
          <h2>System intelligence map</h2>
          <p>Risk, coupling, and business-rule concentration</p>
        </div>
        <button className="text-button" onClick={() => go("Dependencies")}>
          Explore graph <Icon name="arrow" size={15} />
        </button>
      </div>
      <div className="intelligence-map">
        <div className="map-key">
          <span><i className="key-critical" /> Critical</span>
          <span><i className="key-watch" /> Watch</span>
          <span><i className="key-stable" /> Stable</span>
        </div>
        <svg viewBox="0 0 650 290" role="img" aria-label="Animated system risk map">
          <defs>
            <radialGradient id="mapGlow">
              <stop offset="0" stopColor="#45c48e" stopOpacity=".22" />
              <stop offset="1" stopColor="#45c48e" stopOpacity="0" />
            </radialGradient>
            <filter id="softGlow">
              <feGaussianBlur stdDeviation="7" />
            </filter>
          </defs>
          <circle cx="325" cy="145" r="125" className="map-orbit orbit-one" />
          <circle cx="325" cy="145" r="82" className="map-orbit orbit-two" />
          <circle cx="325" cy="145" r="102" fill="url(#mapGlow)" filter="url(#softGlow)" />
          {edges.map((e, idx) => {
            const u = findMod(e.from || e.from_node);
            const v = findMod(e.to || e.to_node);
            if (!u || !v) return null;
            return (
              <line
                key={`${u.id}-${v.id}-${idx}`}
                x1={u.x + 35}
                y1={u.y + 25}
                x2={v.x + 35}
                y2={v.y + 25}
                className={`map-link ${e.inferred ? "inferred" : ""}`}
                style={{ animationDelay: `${idx * 180}ms` }}
              />
            );
          })}
          {modules.map((m, idx) => (
            <g
              key={m.id}
              className={`map-module ${m.risk >= 80 ? "critical" : m.risk >= 60 ? "watch" : "stable"}`}
              style={{ animationDelay: `${idx * 110}ms` }}
            >
              <circle cx={m.x + 35} cy={m.y + 25} r="29" className="module-halo" />
              <circle cx={m.x + 35} cy={m.y + 25} r="19" className="module-core" />
              <text x={m.x + 35} y={m.y + 29} className="module-score" textAnchor="middle">
                {m.risk}
              </text>
              <text x={m.x + 35} y={m.y + 62} className="module-name" textAnchor="middle">
                {m.name}
              </text>
            </g>
          ))}
        </svg>
        <div className="map-caption">
          <span><strong>{modules.filter((m) => m.risk >= 80).length}</strong> critical clusters</span>
          <span><strong>{edges.filter((e) => !e.inferred).length}</strong> cross-boundary links</span>
          <span><strong>{edges.filter((e) => e.inferred).length}</strong> inferred edges</span>
        </div>
      </div>
    </section>
  );
}

// 1. Overview Page
function OverviewPage({ go, record, onExport }) {
  const metrics = record?.metrics || [];
  const findings = record?.findings || [];
  const modules = record?.modules || [];
  const edges = record?.edges || [];

  return (
    <>
      <PageHeader
        title="Overview"
        description="Understand the system before changing it."
        actions={
          <>
            <Button variant="secondary" onClick={onExport}>
              <Icon name="download" size={16} /> Export report
            </Button>
            <Button onClick={() => go("Upload")}>
              <Icon name="upload" size={16} /> Analyze project
            </Button>
          </>
        }
      />
      <section className="metric-grid">
        {metrics.map((m, i) => (
          <article key={m.label} className="metric-card">
            <div className={`metric-icon c${i}`}>
              <Icon name={["file", "layers", "nodes", "book", "risk"][i] || "file"} />
            </div>
            <p>{m.label}</p>
            <strong>{m.value}</strong>
            <span>{m.delta}</span>
          </article>
        ))}
      </section>

      {/* Product Understanding & Real Token Audit Section */}
      <section className="card" style={{ marginBottom: 20 }}>
        <div className="card-head">
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              <h2>{record?.product_profile?.product_type || "Software System"}</h2>
              <Badge tone="success">Product Identified</Badge>
              {record?.pipelines?.length > 0 && (
                <button
                  className="text-button"
                  onClick={() => go("Pipeline")}
                  style={{ color: "var(--accent)", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: 4 }}
                >
                  View Execution Pipeline <Icon name="arrow" size={14} />
                </button>
              )}
            </div>
            <p style={{ marginTop: 4 }}>{record?.product_profile?.purpose || record?.executive_summary?.slice(0, 140) || "Legacy system modernization assessment."}</p>
          </div>
          <Badge tone="accent">{record?.product_profile?.architectural_pattern || "Layered Architecture"}</Badge>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16, marginTop: 16 }}>
          <div style={{ background: "var(--surface2)", padding: 14, borderRadius: 8, border: "1px solid var(--border)" }}>
            <strong style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", display: "block", marginBottom: 8 }}>
              Detected Frameworks & Libraries
            </strong>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {record?.product_profile?.detected_frameworks?.length ? (
                record.product_profile.detected_frameworks.map((fw) => (
                  <Badge key={fw} tone="info">{fw}</Badge>
                ))
              ) : (
                <span style={{ color: "var(--muted)", fontSize: 13 }}>Standard library</span>
              )}
            </div>
          </div>

          <div style={{ background: "var(--surface2)", padding: 14, borderRadius: 8, border: "1px solid var(--border)" }}>
            <strong style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", display: "block", marginBottom: 8 }}>
              Discovered Entry Points
            </strong>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {record?.product_profile?.entry_points?.length ? (
                record.product_profile.entry_points.map((ep, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 12 }}>
                    <code>{ep.file}</code>
                    <span style={{ color: "var(--muted)" }}>{ep.role}</span>
                  </div>
                ))
              ) : (
                <span style={{ color: "var(--muted)", fontSize: 13 }}>Default application root</span>
              )}
            </div>
          </div>

          <div style={{ background: "var(--surface2)", padding: 14, borderRadius: 8, border: "1px solid var(--border)" }}>
            <strong style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", display: "block", marginBottom: 8 }}>
              Gemini AI Token Tracking
            </strong>
            <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Total Consumed:</span>
                <strong>{record?.token_usage?.total_tokens ? record.token_usage.total_tokens.toLocaleString() : "0"}</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", color: "var(--muted)", fontSize: 12 }}>
                <span>Prompt / Output:</span>
                <span>{record?.token_usage?.prompt_tokens?.toLocaleString() || 0} / {record?.token_usage?.candidate_tokens?.toLocaleString() || 0}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", color: "var(--muted)", fontSize: 12 }}>
                <span>Model:</span>
                <span>{record?.token_usage?.model_name || "Static Heuristics"}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="dashboard-grid">
        <SystemIntelligenceMap go={go} modules={modules} edges={edges} />

        <section className="card visual-summary">
          <div className="card-head">
            <div>
              <h2>Risk distribution</h2>
              <p>{findings.length} evidence-backed findings</p>
            </div>
            <button className="text-button" onClick={() => go("Risk Heatmap")}>
              Details <Icon name="arrow" size={15} />
            </button>
          </div>
          <div className="risk-content">
            <div className="donut">
              <div>
                <strong>{findings.length}</strong>
                <span>findings</span>
              </div>
            </div>
            <div className="legend">
              {[
                ["Critical", findings.filter((f) => f.severity === "Critical").length, "critical"],
                ["High", findings.filter((f) => f.severity === "High").length, "high"],
                ["Medium", findings.filter((f) => f.severity === "Medium").length, "medium"],
                ["Low", findings.filter((f) => f.severity === "Low").length, "low"],
              ].map(([lvl, cnt, cls]) => (
                <div key={lvl}>
                  <span className={`dot ${cls}`} />
                  <span>{lvl}</span>
                  <strong>{cnt}</strong>
                </div>
              ))}
            </div>
          </div>
          <div className="coverage-bars">
            {[
              ["Code mapped", 94, "green"],
              ["Rules evidenced", 78, "violet"],
              ["Tests located", 46, "amber"],
            ].map(([lbl, pct, cls], idx) => (
              <div key={lbl}>
                <span>
                  {lbl} <strong>{pct}%</strong>
                </span>
                <i>
                  <b className={cls} style={{ width: `${pct}%`, animationDelay: `${idx * 150}ms` }} />
                </i>
              </div>
            ))}
          </div>
          <div className="visual-insight">
            <span className="insight-spark">
              <i /><i /><i />
            </span>
            <div>
              <strong>Concentration detected</strong>
              <p>{record?.executive_summary?.slice(0, 75) || "62% of high-risk behavior touches Order Service."}...</p>
            </div>
          </div>
        </section>
      </div>

      <section className="card review-card">
        <div className="review-heading">
          <div className="review-icon">
            <Icon name="risk" />
          </div>
          <div>
            <h2>Review before modernization</h2>
            <p>High-impact components where evidence is incomplete or behavior is business-critical.</p>
          </div>
          <Badge tone="critical">
            {findings.filter((f) => f.review === "Needs Investigation" || f.review === "Unreviewed").length} require review
          </Badge>
        </div>
        <div className="review-list">
          {findings.slice(0, 3).map((f) => (
            <button key={f.id} onClick={() => go("Code Intelligence")}>
              <div>
                <Badge tone={f.classification === "BUSINESS_CRITICAL" ? "critical" : "warning"}>
                  {f.classification.replace(/_/g, " ")}
                </Badge>
                <h3>{f.file.split("/").pop()}</h3>
                <p>{f.evidence}</p>
              </div>
              <span className="confidence">
                {f.confidence}%<small>confidence</small>
              </span>
              <Icon name="arrow" />
            </button>
          ))}
        </div>
      </section>
    </>
  );
}

// 2. Upload Page
function UploadPage({ go, onStartAnalysis, activeProjectName }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [projectName, setProjectName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".zip")) {
      setError("Please select a ZIP archive (e.g. project source bundle).");
      return;
    }
    if (file.size > 100 * 1024 * 1024) {
      setError("Archive exceeds the 100 MB maximum upload limit.");
      return;
    }
    setSelectedFile(file);
    if (!projectName) {
      setProjectName(file.name.replace(/\.zip$/i, ""));
    }
    setError("");
  };

  const handleStartAnalysis = async () => {
    setError("");
    setLoading(true);

    try {
      if (selectedFile) {
        // Upload ZIP
        const res = await api.analyzeUpload(selectedFile, projectName || selectedFile.name.replace(/\.zip$/i, ""));
        onStartAnalysis(res.analysis_id, res.project_name);
        go("Analysis");
      } else if (repoUrl.trim()) {
        // Public GitHub Repository
        const res = await api.analyzeRepository(repoUrl.trim(), projectName || undefined);
        onStartAnalysis(res.analysis_id, res.project_name);
        go("Analysis");
      } else {
        setError("Please select a ZIP file or provide a public GitHub repository URL.");
      }
    } catch (err) {
      setError(err.message || "Failed to start analysis");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Upload project"
        description="Prepare a legacy system repository or archive for static analysis."
      />
      <div className="setup-grid">
        <section className="card form-card">
          <div className="step-label">
            <span>1</span>
            <div>
              <h2>Project details</h2>
              <p>Name this analysis workspace.</p>
            </div>
          </div>
          <label className="field">
            <span>Project name</span>
            <input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. Northstar Commerce, Core Banking, Billing Gateway"
            />
          </label>
          <label className="field">
            <span>Public GitHub Repository <em>Optional</em></span>
            <input
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repository"
            />
          </label>
        </section>

        <section className="card form-card">
          <div className="step-label">
            <span>2</span>
            <div>
              <h2>Source archive</h2>
              <p>Or upload the project source as a ZIP archive.</p>
            </div>
          </div>

          {selectedFile ? (
            <div className="selected-file">
              <span><Icon name="file" /></span>
              <div>
                <strong>{selectedFile.name}</strong>
                <p>{(selectedFile.size / 1024 / 1024).toFixed(2)} MB · Ready for secure upload</p>
              </div>
              <Button variant="ghost" onClick={() => setSelectedFile(null)}>Remove</Button>
            </div>
          ) : (
            <div
              className="dropzone"
              tabIndex={0}
              role="button"
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) => e.key === "Enter" && fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                handleFileChange(e.dataTransfer.files[0]);
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".zip"
                hidden
                onChange={(e) => handleFileChange(e.target.files?.[0])}
              />
              <span><Icon name="upload" size={26} /></span>
              <h3>Drop your ZIP archive here</h3>
              <p>or click to browse files</p>
              <small>ZIP archive · Maximum 100 MB · Safe sandbox extraction</small>
            </div>
          )}

          {error && (
            <div className="inline-error">
              <Icon name="risk" size={16} />
              {error}
            </div>
          )}
        </section>
      </div>

      <div className="action-bar">
        <div>
          <strong>Ready for analysis</strong>
          <p>Source files will be analyzed statically with zero runtime execution.</p>
        </div>
        <Button variant="secondary" onClick={() => go("Overview")}>
          Explore demo
        </Button>
        <Button
          disabled={loading || (!selectedFile && !repoUrl.trim())}
          onClick={handleStartAnalysis}
        >
          {loading ? "Initializing..." : "Continue to analysis"} <Icon name="arrow" size={16} />
        </Button>
      </div>
    </>
  );
}

// 3. Analysis Progress Page
function AnalysisPage({ analysisId, record, onCompleted, go, onNavigateToCode }) {
  const [statusData, setStatusData] = useState(null);
  const [polling, setPolling] = useState(true);

  const steps = [
    ["Inventory", "Catalog files, languages, and modules"],
    ["Dependency analysis", "Map observed and inferred relationships"],
    ["Business-rule extraction", "Identify evidence-backed system behavior"],
    ["Risk assessment", "Assess modernization impact and uncertainty"],
    ["Report generation", "Assemble recommendations and limitations"],
  ];

  useEffect(() => {
    if (!analysisId || analysisId === "demo") {
      setPolling(false);
      return;
    }

    let intervalId;
    const fetchStatus = async () => {
      try {
        const res = await api.getAnalysisStatus(analysisId);
        setStatusData(res);
        if (res.status === "completed") {
          setPolling(false);
          clearInterval(intervalId);
          onCompleted(res.record);
        } else if (res.status === "failed") {
          setPolling(false);
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error("Status polling failed:", err);
      }
    };

    fetchStatus();
    intervalId = setInterval(fetchStatus, 1500);
    return () => clearInterval(intervalId);
  }, [analysisId]);

  const activeProgress = statusData?.progress ?? (record?.progress || 100);
  const isDone = (statusData?.status || record?.status) === "completed";
  const stage = statusData?.stage || record?.stage || "completed";

  return (
    <>
      <PageHeader
        title="Analysis"
        description="Track evidence gathering, static AST parsing, and report generation."
      />
      <section className="card analysis-visual">
        <div className="analysis-intro">
          <Badge tone={isDone ? "success" : "warning"}>
            {isDone ? "Analysis complete" : `Stage: ${stage.toUpperCase()}`}
          </Badge>
          <h2>System understanding</h2>
          <p>
            Five analysis agents converged on one evidence graph. Visual weight represents discovered content, not code execution.
          </p>
          <div className="analysis-kpis">
            <div>
              <strong>{record?.metrics?.[0]?.value || "1,284"}</strong>
              <span>files</span>
            </div>
            <div>
              <strong>{record?.metrics?.[3]?.value || "64"}</strong>
              <span>rules</span>
            </div>
            <div>
              <strong>{record?.metrics?.[2]?.value || "312"}</strong>
              <span>links</span>
            </div>
          </div>
        </div>

        <div className="analysis-orbit" aria-label="Analysis coverage visual">
          <span className="orbit-ring ring-a" />
          <span className="orbit-ring ring-b" />
          <span className="orbit-ring ring-c" />
          <div className="orbit-core">
            <Icon name="pulse" size={24} />
            <strong>{activeProgress}%</strong>
            <span>{isDone ? "converged" : "analyzing"}</span>
          </div>
          {[
            ["file", "Inventory", "agent-one"],
            ["nodes", "Dependencies", "agent-two"],
            ["book", "Rules", "agent-three"],
            ["risk", "Risk", "agent-four"],
            ["file", "Report", "agent-five"],
          ].map(([icon, label, cls]) => (
            <span key={label} className={`orbit-agent ${cls}`}>
              <Icon name={icon} size={14} />
              <b>{label}</b>
            </span>
          ))}
        </div>

        <div className="signal-panel">
          <span>Evidence confidence</span>
          <strong>87%</strong>
          <div className="signal-wave">
            {[34, 62, 44, 78, 52, 88, 67, 95, 73, 82, 59, 76].map((h, i) => (
              <i key={i} style={{ height: `${h}%`, animationDelay: `${i * 70}ms` }} />
            ))}
          </div>
          <small>Weighted across observed repository evidence</small>
        </div>
      </section>

      <section className="card process-card">
        <div className="card-head">
          <div>
            <h2>Analysis pipeline</h2>
            <p>{isDone ? "All analysis stages executed cleanly." : "Currently executing pipeline stages..."}</p>
          </div>
          {isDone && (
            <Button onClick={() => (onNavigateToCode ? onNavigateToCode("") : go("Code Intelligence"))}>
              View findings <Icon name="arrow" size={16} />
            </Button>
          )}
        </div>
        <div className="visual-pipeline">
          {steps.map(([stepTitle, stepDesc], i) => {
            const stepThreshold = (i + 1) * 20;
            const isCompletedStep = activeProgress >= stepThreshold || isDone;
            return (
              <div key={stepTitle}>
                <span className={`step-check ${isCompletedStep ? "done" : ""}`}>
                  <Icon name={["file", "nodes", "book", "risk", "check"][i]} size={17} />
                </span>
                <div>
                  <strong>{stepTitle}</strong>
                  <p>{stepDesc}</p>
                </div>
                <span className="pipeline-state">{isCompletedStep ? "Complete" : "Queued"}</span>
                {i < steps.length - 1 && <i className="pipeline-link" />}
              </div>
            );
          })}
        </div>
      </section>
    </>
  );
}

// 3b. Module Explorer Page
function ModuleExplorerPage({ moduleTree = [], findings = [], record, onNavigateToCode }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [search, setSearch] = useState("");

  const projectName = record?.project_name || "Repository";

  // Match findings by relative path or basename
  const relatedFindings = selectedFile
    ? (findings || []).filter((f) => {
        if (!f.file) return false;
        const normF = f.file.replace(/\\/g, "/").toLowerCase();
        const normSel = selectedFile.path.replace(/\\/g, "/").toLowerCase();
        return normF === normSel || normF.endsWith(normSel) || normSel.endsWith(normF);
      })
    : [];

  return (
    <>
      <PageHeader
        title={`${projectName} — Repository Explorer`}
        description="Interactive structural tree of folders, files, and architectural component roles with real evidence citation counts."
      />

      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20 }}>
        <section className="card">
          <div className="toolbar" style={{ marginBottom: 12 }}>
            <SearchInput value={search} onChange={setSearch} placeholder="Filter files and folders…" />
          </div>
          <div style={{ maxHeight: 650, overflowY: "auto", fontFamily: "monospace", fontSize: 13 }}>
            {moduleTree.length ? (
              moduleTree.map((node) => (
                <TreeNode
                  key={node.path}
                  node={node}
                  depth={0}
                  onSelectFile={setSelectedFile}
                  selectedPath={selectedFile?.path}
                  search={search}
                />
              ))
            ) : (
              <div className="empty">
                <p>No module structure available. Upload a project archive to view.</p>
              </div>
            )}
          </div>
        </section>

        <section className="card">
          {selectedFile ? (
            <>
              <div className="card-head">
                <div>
                  <Badge tone="accent">{selectedFile.role || "Component"}</Badge>
                  <h2 style={{ wordBreak: "break-all", marginTop: 8 }}>{selectedFile.name}</h2>
                </div>
                <Badge tone="info">{selectedFile.language || "Text"}</Badge>
              </div>
              <DetailItem label="Relative Path">
                <code>{selectedFile.path}</code>
              </DetailItem>
              <DetailItem label="File Size">
                {selectedFile.size_bytes
                  ? selectedFile.size_bytes < 1024
                    ? `${selectedFile.size_bytes} bytes`
                    : selectedFile.size_bytes < 1024 * 1024
                    ? `${(selectedFile.size_bytes / 1024).toFixed(1)} KB (${selectedFile.size_bytes} bytes)`
                    : `${(selectedFile.size_bytes / (1024 * 1024)).toFixed(2)} MB`
                  : "0 KB"}
              </DetailItem>
              <DetailItem label="Classified Role">
                <strong>{selectedFile.role || "General Source File"}</strong>
              </DetailItem>
              <DetailItem label="Discovered Evidence Citations">
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 4 }}>
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 700,
                      padding: "3px 10px",
                      borderRadius: 12,
                      background: relatedFindings.length ? "var(--brand, #ef5a31)" : "var(--surface2)",
                      color: relatedFindings.length ? "#fff" : "inherit"
                    }}
                  >
                    {relatedFindings.length} {relatedFindings.length === 1 ? "Citation" : "Citations"}
                  </span>
                  {relatedFindings.length > 0 && (
                    <Button
                      variant="primary"
                      onClick={() => onNavigateToCode && onNavigateToCode(selectedFile.path)}
                      style={{ fontSize: 11, padding: "4px 10px" }}
                    >
                      <Icon name="search" size={12} /> Inspect in Code Intelligence
                    </Button>
                  )}
                </div>
              </DetailItem>
              <DetailItem label="Related Findings Details">
                {relatedFindings.length ? (
                  relatedFindings.map((f) => (
                    <div key={f.id} style={{ background: "var(--surface2)", padding: 10, borderRadius: 6, marginBottom: 8 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <Badge tone={f.severity.toLowerCase()}>{f.severity}</Badge>
                        <strong style={{ fontSize: 12 }}>{f.id}</strong>
                        <span style={{ fontSize: 10, color: "var(--muted)", marginLeft: "auto" }}>Lines {f.lines}</span>
                      </div>
                      <p style={{ margin: 0, fontSize: 12 }}>{f.evidence}</p>
                      {f.impact && (
                        <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--muted)" }}>
                          <strong>Impact: </strong>{f.impact}
                        </p>
                      )}
                    </div>
                  ))
                ) : (
                  <span style={{ color: "var(--muted)", fontSize: 13 }}>No critical issues flagged in this file.</span>
                )}
              </DetailItem>
            </>
          ) : (
            <div className="empty" style={{ paddingTop: 80 }}>
              <Icon name="file" />
              <h3>Select a file</h3>
              <p>Click any file in the tree to inspect its component role, size, and findings.</p>
            </div>
          )}
        </section>
      </div>
    </>
  );
}

function TreeNode({ node, depth, onSelectFile, selectedPath, search }) {
  const [isOpen, setIsOpen] = useState(depth < 2);
  const isFolder = node.type === "folder";

  if (search && !node.path.toLowerCase().includes(search.toLowerCase())) {
    if (isFolder && (!node.children || !node.children.some(c => c.path.toLowerCase().includes(search.toLowerCase())))) {
      return null;
    }
  }

  const formatSize = (bytes) => {
    if (!bytes) return "";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div style={{ marginLeft: depth * 14 }}>
      <div
        onClick={() => {
          if (isFolder) setIsOpen(!isOpen);
          else onSelectFile(node);
        }}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "5px 8px",
          borderRadius: 4,
          cursor: "pointer",
          background: selectedPath === node.path ? "var(--accent)" : "transparent",
          color: selectedPath === node.path ? "#fff" : "inherit"
        }}
      >
        <span style={{ fontSize: 14 }}>{isFolder ? (isOpen ? "📂" : "📁") : "📄"}</span>
        <span style={{ flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{node.name}</span>
        {node.size_bytes > 0 && (
          <span style={{ fontSize: 10, opacity: 0.65, fontFamily: "sans-serif" }}>{formatSize(node.size_bytes)}</span>
        )}
        {node.evidence_count > 0 && (
          <span
            style={{
              fontSize: 9,
              fontWeight: 700,
              padding: "1px 6px",
              borderRadius: 8,
              background: "var(--brand, #ef5a31)",
              color: "#fff"
            }}
          >
            {node.evidence_count}
          </span>
        )}
        {!isFolder && node.role && (
          <span style={{ fontSize: 10, opacity: 0.7, textTransform: "uppercase" }}>{node.role}</span>
        )}
      </div>
      {isFolder && isOpen && node.children && (
        <div>
          {node.children.map(child => (
            <TreeNode
              key={child.path}
              node={child}
              depth={depth + 1}
              onSelectFile={onSelectFile}
              selectedPath={selectedPath}
              search={search}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// 3c. Pipeline Page
function PipelinePage({ pipelines = [], record }) {
  const [selectedStage, setSelectedStage] = useState(null);
  const activePipeline = pipelines[0] || null;

  return (
    <>
      <PageHeader
        title="Real Product Pipeline"
        description="Evidence-based execution and data-flow pipeline traced from actual entry points and module boundaries."
      />

      {activePipeline ? (
        <>
          <section className="card" style={{ marginBottom: 20 }}>
            <div className="card-head">
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <h2>{activePipeline.name}</h2>
                  <Badge tone={activePipeline.status === "Complete" ? "success" : "warning"}>
                    {activePipeline.status}
                  </Badge>
                </div>
                <p style={{ marginTop: 4 }}>{activePipeline.purpose}</p>
              </div>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: 12, color: "var(--muted)" }}>Primary Entry Point</span>
                <div><code>{activePipeline.entry_point}</code></div>
              </div>
            </div>

            {/* Pipeline Stage Sequence Flow */}
            <div style={{ marginTop: 24, display: "flex", flexDirection: "column", gap: 16 }}>
              {activePipeline.stages.map((st) => (
                <div
                  key={st.id}
                  onClick={() => setSelectedStage(st)}
                  className="card"
                  style={{
                    cursor: "pointer",
                    border: "1px solid var(--border)",
                    borderRadius: 10,
                    padding: 18,
                    background: selectedStage?.id === st.id ? "var(--surface3)" : "var(--surface2)",
                    transition: "all 0.2s ease"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <span style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 32,
                        height: 32,
                        borderRadius: "50%",
                        background: "var(--accent)",
                        color: "#fff",
                        fontWeight: 700,
                        fontSize: 14
                      }}>
                        {st.order}
                      </span>
                      <div>
                        <strong style={{ fontSize: 16 }}>{st.name}</strong>
                        <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>{st.responsibility}</p>
                      </div>
                    </div>
                    <Badge tone={st.confidence >= 90 ? "success" : "warning"}>{st.confidence}% Confirmed</Badge>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginTop: 12, fontSize: 12 }}>
                    <div style={{ background: "var(--surface)", padding: 10, borderRadius: 6 }}>
                      <span style={{ color: "var(--muted)", display: "block", textTransform: "uppercase", fontSize: 11 }}>Input Payload</span>
                      <strong>{st.input}</strong>
                    </div>
                    <div style={{ background: "var(--surface)", padding: 10, borderRadius: 6 }}>
                      <span style={{ color: "var(--muted)", display: "block", textTransform: "uppercase", fontSize: 11 }}>Output / Mutated State</span>
                      <strong>{st.output}</strong>
                    </div>
                    <div style={{ background: "var(--surface)", padding: 10, borderRadius: 6 }}>
                      <span style={{ color: "var(--muted)", display: "block", textTransform: "uppercase", fontSize: 11 }}>Responsible Modules</span>
                      <div>{st.modules.slice(0, 2).map((m) => <code key={m} style={{ display: "block", margin: "2px 0" }}>{m}</code>)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {activePipeline.alternate_workflows?.length > 0 && (
            <section className="card">
              <h2>Alternate & Exception Workflows</h2>
              <ul style={{ marginTop: 10, paddingLeft: 20, color: "var(--muted)", fontSize: 14, lineHeight: 1.8 }}>
                {activePipeline.alternate_workflows.map((aw, i) => (
                  <li key={i}>{aw}</li>
                ))}
              </ul>
            </section>
          )}

          {/* Drill-down Drawer for Stage Evidence */}
          {selectedStage && (
            <Drawer title={`${selectedStage.name} (Stage ${selectedStage.order})`} onClose={() => setSelectedStage(null)}>
              <Badge tone="accent">{selectedStage.id}</Badge>
              <h2>{selectedStage.responsibility}</h2>
              <DetailItem label="Input Specification">{selectedStage.input}</DetailItem>
              <DetailItem label="Output Specification">{selectedStage.output}</DetailItem>
              <DetailItem label="Data Passed to Next Stage">{selectedStage.data_passed}</DetailItem>
              <DetailItem label="Responsible Source Modules">
                {selectedStage.modules.map((m) => (
                  <div key={m}><code>{m}</code></div>
                ))}
              </DetailItem>
              <DetailItem label="Dependencies & Libraries">
                {selectedStage.dependencies?.join(" · ") || "Internal components"}
              </DetailItem>
              <DetailItem label="Failure Points & Boundary Risks">
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                  {selectedStage.failure_points?.map((fp, i) => <li key={i}>{fp}</li>)}
                </ul>
              </DetailItem>
              <DetailItem label="Performance Bottlenecks">
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                  {selectedStage.bottlenecks?.map((bn, i) => <li key={i}>{bn}</li>)}
                </ul>
              </DetailItem>
              <DetailItem label="Source Evidence & Citation">
                <code>{selectedStage.evidence}</code>
              </DetailItem>
              <DetailItem label="Confidence Level">
                {selectedStage.confidence}% — Traced from observed entry and module boundaries.
              </DetailItem>
            </Drawer>
          )}
        </>
      ) : (
        <div className="card empty">
          <Icon name="search" />
          <h3>No pipeline detected</h3>
          <p>Analyze a project repository or upload a ZIP archive to reconstruct its execution pipeline.</p>
        </div>
      )}
    </>
  );
}

// 4. Code Intelligence Page
function CodeIntelligencePage({ findings = [], initialSearch = "" }) {
  const [search, setSearch] = useState(initialSearch || "");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [reviewFilter, setReviewFilter] = useState("All");
  const [selectedFinding, setSelectedFinding] = useState(null);

  useEffect(() => {
    if (initialSearch) {
      setSearch(initialSearch);
    }
  }, [initialSearch]);

  const critCount = (findings || []).filter((f) => f.severity === "Critical").length;
  const highCount = (findings || []).filter((f) => f.severity === "High").length;
  const medLowCount = (findings || []).filter((f) => f.severity === "Medium" || f.severity === "Low").length;
  const reviewCount = (findings || []).filter((f) => f.review === "Needs Investigation").length;

  const filtered = (findings || []).filter(
    (f) =>
      (severityFilter === "All" || f.severity === severityFilter) &&
      (reviewFilter === "All" || (f.review || "Unreviewed") === reviewFilter) &&
      `${f.id || ""} ${f.category || ""} ${f.file || ""} ${f.evidence || ""}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <PageHeader
        title="Code intelligence"
        description="Inspect findings with source evidence, impact, and uncertainty."
      />
      <div className="summary-strip" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 18 }}>
        <div className="card" style={{ padding: "12px 16px" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Total Discovered Findings</span>
          <strong style={{ display: "block", fontSize: 22, fontWeight: 700, marginTop: 4 }}>{findings.length}</strong>
        </div>
        <div className="card" style={{ padding: "12px 16px", borderLeft: "4px solid #ef4444" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Critical Severity</span>
          <strong style={{ display: "block", fontSize: 22, fontWeight: 700, marginTop: 4, color: "#ef4444" }}>{critCount}</strong>
        </div>
        <div className="card" style={{ padding: "12px 16px", borderLeft: "4px solid #f97316" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>High Severity</span>
          <strong style={{ display: "block", fontSize: 22, fontWeight: 700, marginTop: 4, color: "#f97316" }}>{highCount}</strong>
        </div>
        <div className="card" style={{ padding: "12px 16px", borderLeft: "4px solid #3b82f6" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Medium / Low</span>
          <strong style={{ display: "block", fontSize: 22, fontWeight: 700, marginTop: 4, color: "#3b82f6" }}>{medLowCount}</strong>
        </div>
        <div className="card" style={{ padding: "12px 16px", borderLeft: "4px solid #eab308" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Needs Investigation</span>
          <strong style={{ display: "block", fontSize: 22, fontWeight: 700, marginTop: 4, color: "#eab308" }}>{reviewCount}</strong>
        </div>
      </div>
      <div className="toolbar">
        <SearchInput value={search} onChange={setSearch} placeholder="Search findings or files…" />
        <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
          <option>All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
        <select value={reviewFilter} onChange={(e) => setReviewFilter(e.target.value)}>
          <option>All</option>
          <option>Unreviewed</option>
          <option>Verified</option>
          <option>Needs Investigation</option>
        </select>
      </div>

      <section className="card table-card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Finding</th>
                <th>Category</th>
                <th>Severity</th>
                <th>Source</th>
                <th>Confidence</th>
                <th>Review</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtered.map((f) => (
                <tr key={f.id} onClick={() => setSelectedFinding(f)}>
                  <td>
                    <strong>{f.id}</strong>
                    <span>{f.evidence}</span>
                  </td>
                  <td>{f.category}</td>
                  <td>
                    <Badge tone={f.severity}>{f.severity}</Badge>
                  </td>
                  <td>
                    <code>{f.file}</code>
                    <span>Lines {f.lines}</span>
                  </td>
                  <td>{f.confidence}%</td>
                  <td>
                    <Badge tone={f.review === "Verified" ? "success" : "warning"}>{f.review}</Badge>
                  </td>
                  <td>
                    <Icon name="arrow" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="empty" style={{ padding: "32px 16px", textAlign: "center" }}>
            <Icon name="search" />
            <h3>No findings match</h3>
            <p>
              {findings.length > 0
                ? "Try widening your search terms or clearing active severity and review filters."
                : "No code intelligence findings recorded. Run an analysis on a repository or upload a ZIP archive."}
            </p>
            {findings.length > 0 && (
              <Button
                variant="secondary"
                style={{ marginTop: 12 }}
                onClick={() => {
                  setSearch("");
                  setSeverityFilter("All");
                  setReviewFilter("All");
                }}
              >
                Reset filters
              </Button>
            )}
          </div>
        )}
      </section>

      {selectedFinding && (
        <Drawer title={selectedFinding.id} onClose={() => setSelectedFinding(null)}>
          <Badge tone={selectedFinding.classification === "BUSINESS_CRITICAL" ? "critical" : "warning"}>
            {selectedFinding.classification}
          </Badge>
          <h2>{selectedFinding.evidence}</h2>
          <DetailItem label="Source">
            <code>{selectedFinding.file}:{selectedFinding.lines}</code>
          </DetailItem>
          <DetailItem label="Why it matters">{selectedFinding.impact}</DetailItem>
          <DetailItem label="Affected modules">
            {selectedFinding.modules?.join(" · ") || "Core Module"}
          </DetailItem>
          <DetailItem label="Uncertainty">
            {100 - selectedFinding.confidence}% — dynamic behavior and production paths require human verification.
          </DetailItem>
          <DetailItem label="Recommended action">{selectedFinding.recommendation}</DetailItem>
          <DetailItem label="Verification steps">
            <ol>
              <li>Confirm behavior with a domain owner.</li>
              <li>Capture representative production inputs.</li>
              <li>Add a characterization test before changing code.</li>
            </ol>
          </DetailItem>
          <Button
            onClick={() =>
              navigator.clipboard.writeText(
                `${selectedFinding.id}\n${selectedFinding.file}:${selectedFinding.lines}\n${selectedFinding.evidence}`
              )
            }
          >
            <Icon name="copy" size={16} /> Copy evidence
          </Button>
        </Drawer>
      )}
    </>
  );
}

// 5. Business Rules Page
function BusinessRulesPage({ rules = [] }) {
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [selectedRule, setSelectedRule] = useState(null);
  const [localReviews, setLocalReviews] = useState({});

  const categories = ["All", ...new Set(rules.map((r) => r.category))];
  const filtered = rules.filter(
    (r) =>
      (categoryFilter === "All" || r.category === categoryFilter) &&
      `${r.name} ${r.description} ${r.id}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <PageHeader
        title="Business rules"
        description="Preserve the behavior that keeps the business running."
        actions={
          <Button
            variant="secondary"
            onClick={() => {
              const blob = new Blob([JSON.stringify(rules, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "business-rules.json";
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            <Icon name="download" size={16} /> Export JSON
          </Button>
        }
      />
      <div className="toolbar">
        <SearchInput value={search} onChange={setSearch} placeholder="Search rules…" />
        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
      </div>

      <div className="rule-grid">
        {filtered.map((r) => (
          <article key={r.id} className="card rule-card" onClick={() => setSelectedRule(r)}>
            <div className="rule-top">
              <Badge tone={r.critical ? "critical" : "neutral"}>{r.id}</Badge>
              <Badge tone={r.critical ? "warning" : "neutral"}>
                {r.critical ? "Undocumented critical rule" : r.category}
              </Badge>
            </div>
            <h2>{r.name}</h2>
            <p>{r.description}</p>
            <div className="rule-source">
              <Icon name="code" size={15} />
              <code>{r.source}</code>
            </div>
            <div className="rule-meta">
              <div>
                <span>Confidence</span>
                <strong>{r.confidence}%</strong>
              </div>
              <div>
                <span>Impact</span>
                <strong>{r.impact}</strong>
              </div>
              <div>
                <span>Review</span>
                <strong>{localReviews[r.id] || r.review}</strong>
              </div>
            </div>
          </article>
        ))}
      </div>

      {selectedRule && (
        <Drawer title={`${selectedRule.id} · ${selectedRule.category}`} onClose={() => setSelectedRule(null)}>
          <h2>{selectedRule.name}</h2>
          <p className="lead">{selectedRule.description}</p>
          <DetailItem label="Evidence">
            <code>{selectedRule.source}</code>
          </DetailItem>
          <DetailItem label="Business impact">
            {selectedRule.impact} — changing this behavior may alter customer eligibility or transaction outcomes.
          </DetailItem>
          <DetailItem label="Dependencies">{selectedRule.dependencies?.join(" · ") || "None"}</DetailItem>
          <DetailItem label="Suggested regression tests">
            <ul>
              {selectedRule.tests?.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </DetailItem>
          <DetailItem label="Review status">
            <select
              value={localReviews[selectedRule.id] || selectedRule.review}
              onChange={(e) => setLocalReviews({ ...localReviews, [selectedRule.id]: e.target.value })}
            >
              <option>Unreviewed</option>
              <option>Verified</option>
              <option>Needs Investigation</option>
            </select>
          </DetailItem>
          <Button
            onClick={() =>
              navigator.clipboard.writeText(
                `${selectedRule.id}: ${selectedRule.name}\n${selectedRule.description}\nSource: ${selectedRule.source}`
              )
            }
          >
            <Icon name="copy" size={16} /> Copy rule
          </Button>
        </Drawer>
      )}
    </>
  );
}

// 6. Dependencies Page
// 4b. Technology Requirements & Version Audit Page
function TechnologyAuditPage({ versionAudit = [], projectName = "Project" }) {
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [selectedAudit, setSelectedAudit] = useState(null);

  const filtered = useMemo(() => {
    return (versionAudit || []).filter((v) => {
      const matchPri = priorityFilter === "All" || v.upgrade_priority === priorityFilter;
      const q = search.toLowerCase();
      const matchSearch =
        !q ||
        (v.component || "").toLowerCase().includes(q) ||
        (v.category || "").toLowerCase().includes(q) ||
        (v.reason || "").toLowerCase().includes(q);
      return matchPri && matchSearch;
    });
  }, [versionAudit, priorityFilter, search]);

  const criticalCount = (versionAudit || []).filter((v) => v.upgrade_priority === "Critical").length;
  const highCount = (versionAudit || []).filter((v) => v.upgrade_priority === "High").length;
  const noUpgradeCount = (versionAudit || []).filter((v) => v.upgrade_priority === "No Upgrade Needed").length;

  return (
    <>
      <PageHeader
        title="Technology & Version Audit"
        description="Inspect declared vs resolved technology versions, EOL support status, and 12-field upgrade explanations."
      />

      <div className="summary-strip" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 20 }}>
        <div className="card" style={{ padding: "14px 16px" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Total Dependencies Audited</span>
          <strong style={{ display: "block", fontSize: 24, fontWeight: 700, marginTop: 4 }}>{versionAudit.length}</strong>
        </div>
        <div className="card" style={{ padding: "14px 16px", borderLeft: "4px solid #ef4444" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Critical Priority</span>
          <strong style={{ display: "block", fontSize: 24, fontWeight: 700, marginTop: 4, color: "#ef4444" }}>{criticalCount}</strong>
        </div>
        <div className="card" style={{ padding: "14px 16px", borderLeft: "4px solid #f97316" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>High Priority</span>
          <strong style={{ display: "block", fontSize: 24, fontWeight: 700, marginTop: 4, color: "#f97316" }}>{highCount}</strong>
        </div>
        <div className="card" style={{ padding: "14px 16px", borderLeft: "4px solid #22c55e" }}>
          <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>Supported & Stable</span>
          <strong style={{ display: "block", fontSize: 24, fontWeight: 700, marginTop: 4, color: "#22c55e" }}>{noUpgradeCount}</strong>
        </div>
      </div>

      <div className="toolbar">
        <SearchInput value={search} onChange={setSearch} placeholder="Search component or framework…" />
        <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option>All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
          <option>No Upgrade Needed</option>
        </select>
      </div>

      <section className="card table-card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Component</th>
                <th>Category</th>
                <th>Declared</th>
                <th>Resolved</th>
                <th>Target Version</th>
                <th>Support</th>
                <th>Security</th>
                <th>Priority</th>
                <th>Action</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtered.map((v, i) => (
                <tr key={i} onClick={() => setSelectedAudit(v)} style={{ cursor: "pointer" }}>
                  <td>
                    <strong>{v.component}</strong>
                    <span style={{ fontSize: 11, color: "var(--c-text-muted)", display: "block" }}>{v.source_evidence}</span>
                  </td>
                  <td>{v.category}</td>
                  <td><code>{v.current_version}</code></td>
                  <td><code>{v.resolved_version || "N/A"}</code></td>
                  <td><strong style={{ color: "#2563eb" }}>{v.recommended_version}</strong></td>
                  <td>
                    <Badge tone={v.support_status === "Supported" ? "success" : v.support_status === "EOL" ? "critical" : "warning"}>
                      {v.support_status}
                    </Badge>
                  </td>
                  <td>
                    <Badge tone={v.security_status === "Secure" ? "success" : v.security_status === "Critical CVE" ? "critical" : "warning"}>
                      {v.security_status}
                    </Badge>
                  </td>
                  <td>
                    <Badge tone={v.upgrade_priority === "Critical" ? "critical" : v.upgrade_priority === "High" ? "warning" : v.upgrade_priority === "No Upgrade Needed" ? "success" : "neutral"}>
                      {v.upgrade_priority}
                    </Badge>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{v.suggested_action}</span>
                  </td>
                  <td>
                    <Icon name="arrow" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div className="empty" style={{ padding: "32px 16px", textAlign: "center" }}>
            <Icon name="search" />
            <h3>No dependencies match filter</h3>
            <p>Try widening your search or selecting 'All' in the priority filter.</p>
            <Button variant="secondary" style={{ marginTop: 12 }} onClick={() => { setSearch(""); setPriorityFilter("All"); }}>
              Reset filters
            </Button>
          </div>
        )}
      </section>

      {/* 12-Field Interactive Upgrade Explanation Modal */}
      {selectedAudit && (
        <Drawer title={`Upgrade Explanation: ${selectedAudit.component}`} onClose={() => setSelectedAudit(null)}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
            <Badge tone={selectedAudit.upgrade_priority === "Critical" ? "critical" : selectedAudit.upgrade_priority === "High" ? "warning" : "success"}>
              Priority: {selectedAudit.upgrade_priority}
            </Badge>
            <Badge tone="neutral">{selectedAudit.category}</Badge>
            <Badge tone={selectedAudit.support_status === "Supported" ? "success" : "critical"}>
              {selectedAudit.support_status}
            </Badge>
          </div>

          <h2 style={{ fontSize: 18, margin: "8px 0" }}>{selectedAudit.component} Upgrade Path</h2>
          <p style={{ color: "var(--c-text-muted)", fontSize: 13, marginBottom: 16 }}>{selectedAudit.reason}</p>

          <DetailItem label="1. Component & Category">
            <strong>{selectedAudit.component}</strong> ({selectedAudit.category})
          </DetailItem>

          <DetailItem label="2. Current Version (Declared vs Resolved)">
            Declared: <code>{selectedAudit.current_version}</code> | Resolved: <code>{selectedAudit.resolved_version || "Not pinned in lockfile"}</code>
          </DetailItem>

          <DetailItem label="3. Recommended Target Version">
            <strong style={{ color: "#2563eb", fontSize: 15 }}>{selectedAudit.recommended_version}</strong>
          </DetailItem>

          <DetailItem label="4. Why Recommended">
            {selectedAudit.reason}
          </DetailItem>

          <DetailItem label="5. Source Evidence (Manifest & Line)">
            <code>{selectedAudit.source_evidence}</code>
          </DetailItem>

          <DetailItem label="6. Expected Modernization Benefits">
            {Array.isArray(selectedAudit.benefits) ? (
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {selectedAudit.benefits.map((b, idx) => (
                  <li key={idx} style={{ marginBottom: 4 }}>{b}</li>
                ))}
              </ul>
            ) : (
              <p style={{ margin: 0 }}>{selectedAudit.benefits || "Improved security, performance, and long-term LTS support."}</p>
            )}
          </DetailItem>

          <DetailItem label="7. Upgrade Risks & Breaking Changes">
            {(() => {
              const risks = selectedAudit.risks_and_breaking_changes || selectedAudit.breaking_changes;
              return Array.isArray(risks) ? (
                <ul style={{ margin: 0, paddingLeft: 18, color: "#dc2626" }}>
                  {risks.map((r, idx) => (
                    <li key={idx} style={{ marginBottom: 4 }}>{r}</li>
                  ))}
                </ul>
              ) : (
                <p style={{ margin: 0, color: "#dc2626" }}>{risks || "None reported."}</p>
              );
            })()}
          </DetailItem>

          <DetailItem label="8. Dependencies Affected">
            {(() => {
              const deps = selectedAudit.dependencies_affected || selectedAudit.affected_dependencies;
              return Array.isArray(deps) && deps.length > 0
                ? deps.join(" · ")
                : (typeof deps === "string" && deps) || "Isolated component — no immediate downstream dependency breaking detected";
            })()}
          </DetailItem>

          <DetailItem label="9. Recommended Step-by-Step Upgrade Path">
            <code>{selectedAudit.recommended_upgrade_path || selectedAudit.upgrade_path || "Review documentation and bump dependency version in manifest."}</code>
          </DetailItem>

          <DetailItem label="10. Testing Requirements">
            {Array.isArray(selectedAudit.testing_requirements) ? (
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {selectedAudit.testing_requirements.map((t, idx) => (
                  <li key={idx} style={{ marginBottom: 4 }}>{t}</li>
                ))}
              </ul>
            ) : (
              <p style={{ margin: 0 }}>{selectedAudit.testing_requirements || "Execute regression test suite and characterization tests on staging."}</p>
            )}
          </DetailItem>

          <DetailItem label="11. Priority Basis">
            {selectedAudit.priority_basis}
          </DetailItem>

          <DetailItem label="12. Recommended Action">
            <Badge tone={selectedAudit.suggested_action === "Upgrade" ? "primary" : selectedAudit.suggested_action === "Keep" ? "success" : "warning"}>
              {selectedAudit.suggested_action}
            </Badge>
            <span style={{ marginLeft: 8, fontSize: 12 }}>{selectedAudit.compatibility_impact}</span>
          </DetailItem>
        </Drawer>
      )}
    </>
  );
}

function DependenciesPage({ modules = [], edges = [], findings = [], databaseSummary = {} }) {
  const [selectedNode, setSelectedNode] = useState(modules[0] || null);
  const [search, setSearch] = useState("");
  const [zoomLevel, setZoomLevel] = useState(1);

  const filteredModules = modules.filter((m) => m.name.toLowerCase().includes(search.toLowerCase()));
  const findMod = (id) => modules.find((m) => m.id === id);

  const sharedTables = databaseSummary?.shared_tables || [
    {
      table: "CUSTOMER_CREDIT",
      writers_count: 2,
      readers_count: 1,
      writers: ["legacy/db/CUSTREC.cbl", "src/order/DiscountEngine.java"],
      risk: "High direct-write contention across independent modules"
    }
  ];
  const storedProcs = databaseSummary?.stored_procedures || ["PROCESS_MONTHLY_INTEREST"];

  return (
    <>
      <PageHeader
        title="Dependency explorer"
        description="Trace observed and inferred relationships across services, modules, and database boundaries."
      />
      <div className="dep-layout">
        <section className="card graph-card">
          <div className="graph-toolbar">
            <SearchInput value={search} onChange={setSearch} placeholder="Find a module…" />
            <div className="graph-legend">
              <span><i className="solid" /> Observed</span>
              <span><i className="dashed" /> Inferred</span>
            </div>
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              <button
                type="button"
                style={{ padding: "3px 8px", fontSize: 13, borderRadius: 5, border: "1px solid var(--border)", background: "transparent", cursor: "pointer", color: "inherit" }}
                onClick={() => setZoomLevel((z) => Math.min(1.8, +(z + 0.15).toFixed(2)))}
                title="Zoom In"
              >
                +
              </button>
              <button
                type="button"
                style={{ padding: "3px 8px", fontSize: 13, borderRadius: 5, border: "1px solid var(--border)", background: "transparent", cursor: "pointer", color: "inherit" }}
                onClick={() => setZoomLevel((z) => Math.max(0.6, +(z - 0.15).toFixed(2)))}
                title="Zoom Out"
              >
                −
              </button>
              <button
                type="button"
                style={{ padding: "3px 8px", fontSize: 11, borderRadius: 5, border: "1px solid var(--border)", background: "transparent", cursor: "pointer", color: "inherit" }}
                onClick={() => setZoomLevel(1)}
                title="Reset Zoom"
              >
                Reset
              </button>
              <span style={{ fontSize: 11, color: "var(--c-text-muted)" }}>{Math.round(zoomLevel * 100)}%</span>
            </div>
          </div>
          <div className="graph">
            <svg viewBox="0 0 650 300" role="img" aria-label="Module dependency graph">
              <g transform={`scale(${zoomLevel})`} style={{ transformOrigin: "325px 150px", transition: "transform 0.15s ease-out" }}>
              <defs>
                <marker id="arrow" markerWidth="7" height="7" refX="6" refY="3.5" orient="auto">
                  <path d="M0,0 L7,3.5 L0,7 z" />
                </marker>
              </defs>
              {edges.map((e, idx) => {
                const u = findMod(e.from || e.from_node);
                const v = findMod(e.to || e.to_node);
                if (!u || !v) return null;
                return (
                  <line
                    key={idx}
                    x1={u.x + 70}
                    y1={u.y + 27}
                    x2={v.x + 70}
                    y2={v.y + 27}
                    className={e.inferred ? "edge inferred" : "edge"}
                    markerEnd="url(#arrow)"
                  />
                );
              })}
              {filteredModules.map((n) => (
                <g
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  className={`node ${selectedNode?.id === n.id ? "selected" : ""}`}
                  tabIndex={0}
                  role="button"
                >
                  <rect x={n.x} y={n.y} width="140" height="54" rx="9" />
                  <circle cx={n.x + 18} cy={n.y + 27} r="7" />
                  <text x={n.x + 32} y={n.y + 23}>{n.name}</text>
                  <text className="node-type" x={n.x + 32} y={n.y + 39}>{n.type}</text>
                </g>
              ))}
              </g>
            </svg>
          </div>
        </section>

        {selectedNode && (
          <aside className="card node-detail">
            <Badge tone={selectedNode.type === "Database" ? "warning" : "neutral"}>
              {selectedNode.type}
            </Badge>
            <h2>{selectedNode.name}</h2>
            <p>{selectedNode.reason}</p>
            <div className="count-row">
              <div>
                <strong>{selectedNode.incoming}</strong>
                <span>Incoming</span>
              </div>
              <div>
                <strong>{selectedNode.outgoing}</strong>
                <span>Outgoing</span>
              </div>
              <div>
                <strong>{selectedNode.risk}</strong>
                <span>Risk score</span>
              </div>
            </div>
            <DetailItem label="Connected findings">
              {findings
                .filter((f) => f.modules?.includes(selectedNode.name))
                .slice(0, 3)
                .map((f) => (
                  <div key={f.id} className="linked">
                    <strong>{f.id}</strong> {f.evidence}
                  </div>
                ))}
            </DetailItem>
            <DetailItem label="Inbound Dependents (Callers)">
              {edges
                .filter((e) => (e.to || e.to_node) === selectedNode?.id)
                .map((e) => findMod(e.from || e.from_node))
                .filter(Boolean).length === 0 ? (
                <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>None (Root entry service)</span>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {edges
                    .filter((e) => (e.to || e.to_node) === selectedNode?.id)
                    .map((e) => findMod(e.from || e.from_node))
                    .filter(Boolean)
                    .map((inMod, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => setSelectedNode(inMod)}
                        style={{ padding: "2px 8px", fontSize: 11, borderRadius: 12, border: "1px solid var(--border)", background: "transparent", cursor: "pointer", color: "inherit" }}
                      >
                        ← {inMod.name}
                      </button>
                    ))}
                </div>
              )}
            </DetailItem>

            <DetailItem label="Outbound Dependencies">
              {edges
                .filter((e) => (e.from || e.from_node) === selectedNode?.id)
                .map((e) => findMod(e.to || e.to_node))
                .filter(Boolean).length === 0 ? (
                <span style={{ fontSize: 12, color: "var(--c-text-muted)" }}>None (Leaf / Terminal module)</span>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {edges
                    .filter((e) => (e.from || e.from_node) === selectedNode?.id)
                    .map((e) => findMod(e.to || e.to_node))
                    .filter(Boolean)
                    .map((outMod, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => setSelectedNode(outMod)}
                        style={{ padding: "2px 8px", fontSize: 11, borderRadius: 12, border: "1px solid var(--border)", background: "transparent", cursor: "pointer", color: "inherit" }}
                      >
                        → {outMod.name}
                      </button>
                    ))}
                </div>
              )}
            </DetailItem>

            <DetailItem label="Evidence quality">
              Observed edges use static call and schema references. Dashed edges are inferred and require verification.
            </DetailItem>
          </aside>
        )}
      </div>

      {/* Database Dependency Analysis & Shared Table Contention Section */}
      <section className="card" style={{ marginTop: 14, padding: 18 }}>
        <div className="card-head" style={{ border: 0, padding: "0 0 14px 0" }}>
          <div>
            <h2>Database dependency analysis & shared table contention</h2>
            <p>Direct writers, query callers, and stored procedure boundaries across subsystems</p>
          </div>
          <Badge tone="warning">{sharedTables.length} shared contention points</Badge>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 12 }}>
          {sharedTables.map((st, i) => (
            <article key={i} style={{ border: "1px solid var(--border)", borderRadius: 8, padding: 14, background: "var(--surface2)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <strong style={{ fontSize: 13, fontFamily: "DM Mono, monospace", color: "var(--brand)" }}>
                  {st.table}
                </strong>
                <Badge tone="critical">{st.writers_count} writers</Badge>
              </div>
              <p style={{ fontSize: 11, color: "var(--muted)", marginBottom: 8 }}>{st.risk}</p>
              <div style={{ fontSize: 10, color: "var(--text)" }}>
                <span style={{ color: "var(--muted)", textTransform: "uppercase", fontSize: 8, fontWeight: 700, display: "block", marginBottom: 3 }}>
                  Direct Writing Modules:
                </span>
                {st.writers?.map((w, wIdx) => (
                  <code key={wIdx} style={{ display: "block", fontSize: 9, marginBottom: 2 }}>• {w}</code>
                ))}
              </div>
            </article>
          ))}
        </div>

        {storedProcs.length > 0 && (
          <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", fontWeight: 700 }}>
              Stored Procedures & Triggers:
            </span>
            {storedProcs.map((sp, idx) => (
              <Badge key={idx} tone="neutral">{sp}</Badge>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

// 7. Risk Heatmap Page
function RiskHeatmapPage({ risks = [], findings = [], onNavigateToCode }) {
  const [selectedRisk, setSelectedRisk] = useState(risks[0] || null);
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [search, setSearch] = useState("");

  // Keep selectedRisk in sync when risks update
  useEffect(() => {
    if (risks.length && (!selectedRisk || !risks.some(r => r.name === selectedRisk.name))) {
      setSelectedRisk(risks[0]);
    }
  }, [risks]);

  const filteredRisks = (risks || []).filter((r) => {
    const matchesPriority = priorityFilter === "All" || (r.priority || r.severity) === priorityFilter;
    const matchesSearch = !search ||
      `${r.name} ${r.action || ""} ${r.technical_debt || ""} ${r.security_risk || ""}`.toLowerCase().includes(search.toLowerCase());
    return matchesPriority && matchesSearch;
  });

  const totalModules = risks.length;
  const criticalCount = risks.filter(r => (r.priority || r.severity) === "Critical" || r.score >= 75).length;
  const highDebtCount = risks.filter(r => r.technical_debt === "Critical" || r.technical_debt === "High").length;
  const totalCitations = risks.reduce((acc, r) => acc + (r.evidence_count || 0), 0) || findings.length;

  return (
    <>
      <PageHeader
        title="Modernization risk heatmap"
        description="Module and file prioritization derived strictly from discovered source evidence, architectural coupling, and technical debt."
      />

      {/* Summary KPI strip */}
      <div className="metric-grid" style={{ marginBottom: 20 }}>
        <div className="metric-card">
          <small>Total Modules</small>
          <strong>{totalModules}</strong>
          <span>Discovered in codebase</span>
        </div>
        <div className="metric-card">
          <small>Critical Priority</small>
          <strong style={{ color: "var(--brand, #ef5a31)" }}>{criticalCount}</strong>
          <span>Require immediate guardrails</span>
        </div>
        <div className="metric-card">
          <small>High Technical Debt</small>
          <strong style={{ color: "#d97706" }}>{highDebtCount}</strong>
          <span>Obsolete APIs & anti-patterns</span>
        </div>
        <div className="metric-card">
          <small>Discovered Citations</small>
          <strong>{totalCitations}</strong>
          <span>Deduplicated source findings</span>
        </div>
      </div>

      {/* Toolbar */}
      <div className="toolbar" style={{ marginBottom: 18 }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Search modules, files, or actions…" />
        <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option>All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </div>

      {/* Modern Module Priority Grid */}
      <section className="card" style={{ marginBottom: 24, padding: 20 }}>
        <div className="card-head" style={{ marginBottom: 16 }}>
          <div>
            <h2>Discovered Module Risk Grid</h2>
            <p>Select any module below to inspect its file-level breakdown and associated findings.</p>
          </div>
          <div className="heat-legend">
            <span>Low</span>
            <i /><i /><i />
            <span>Critical</span>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
          {filteredRisks.map((r) => {
            const isSelected = selectedRisk?.name === r.name;
            const prio = r.priority || r.severity || "Medium";
            const scoreColor = prio === "Critical" ? "#ef4444" : prio === "High" ? "#f97316" : prio === "Medium" ? "#eab308" : "#10b981";

            return (
              <div
                key={r.name}
                onClick={() => setSelectedRisk(r)}
                style={{
                  padding: 16,
                  borderRadius: 10,
                  border: isSelected ? "2px solid var(--brand, #ef5a31)" : "1px solid var(--border)",
                  background: isSelected ? "var(--surface2)" : "var(--surface)",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  display: "flex",
                  flexDirection: "column",
                  gap: 10
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <strong style={{ fontSize: 14, wordBreak: "break-word" }}>{r.name}</strong>
                    <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>
                      {r.files?.length || 1} {r.files?.length === 1 ? "file" : "files"} · {r.evidence_count || 0} citations
                    </div>
                  </div>
                  <Badge tone={prio.toLowerCase()}>{prio}</Badge>
                </div>

                {/* Score bar */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 4 }}>
                    <span style={{ color: "var(--muted)" }}>Risk Score</span>
                    <strong style={{ color: scoreColor }}>{r.score}/100</strong>
                  </div>
                  <div style={{ height: 6, background: "var(--surface2)", borderRadius: 3, overflow: "hidden" }}>
                    <div style={{ width: `${r.score}%`, height: "100%", background: scoreColor, borderRadius: 3 }} />
                  </div>
                </div>

                {/* Dimension Badges */}
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5, fontSize: 10 }}>
                  <span style={{ padding: "2px 6px", borderRadius: 4, background: "var(--surface2)", border: "1px solid var(--border)" }}>
                    Debt: <strong>{r.technical_debt || "Low"}</strong>
                  </span>
                  <span style={{ padding: "2px 6px", borderRadius: 4, background: "var(--surface2)", border: "1px solid var(--border)" }}>
                    Sec: <strong>{r.security_risk || "Low"}</strong>
                  </span>
                  <span style={{ padding: "2px 6px", borderRadius: 4, background: "var(--surface2)", border: "1px solid var(--border)" }}>
                    Crit: <strong>{r.business_criticality || "Medium"}</strong>
                  </span>
                  <span style={{ padding: "2px 6px", borderRadius: 4, background: "var(--surface2)", border: "1px solid var(--border)" }}>
                    Conf: <strong>{r.confidence || 85}%</strong>
                  </span>
                </div>

                <div style={{ fontSize: 11, color: "var(--muted)", marginTop: "auto", borderTop: "1px solid var(--border)", paddingTop: 8 }}>
                  <strong>Action: </strong>{r.action || r.recommended_action || "Verify contracts and isolate."}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Selected Module Detail & File-Level Drill-Down */}
      {selectedRisk && (
        <section className="card" style={{ padding: 20 }}>
          <div className="card-head" style={{ marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <h2>File-Level Drill-Down: {selectedRisk.name}</h2>
                <Badge tone={(selectedRisk.priority || selectedRisk.severity).toLowerCase()}>
                  {selectedRisk.priority || selectedRisk.severity}
                </Badge>
              </div>
              <p style={{ marginTop: 4 }}>
                Real files associated with this module, scored by technical debt, security risk, and evidence density.
              </p>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 12, color: "var(--muted)" }}>Module Confidence</div>
              <strong style={{ fontSize: 18 }}>{selectedRisk.confidence || 85}%</strong>
            </div>
          </div>

          {/* Contributing Factors & Action */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20, background: "var(--surface2)", padding: 14, borderRadius: 8 }}>
            <div>
              <strong style={{ fontSize: 12, textTransform: "uppercase", color: "var(--muted)" }}>Contributing Evidence Factors</strong>
              <ul style={{ margin: "6px 0 0 16px", fontSize: 12, lineHeight: 1.6 }}>
                {selectedRisk.factors?.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
            <div>
              <strong style={{ fontSize: 12, textTransform: "uppercase", color: "var(--muted)" }}>Recommended Action Plan</strong>
              <p style={{ margin: "6px 0 0 0", fontSize: 13, lineHeight: 1.5 }}>
                {selectedRisk.action || selectedRisk.recommended_action}
              </p>
            </div>
          </div>

          {/* Drill-down Table */}
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>File / Source Path</th>
                  <th>Priority</th>
                  <th>Risk Score</th>
                  <th>Evidence</th>
                  <th>Technical Debt</th>
                  <th>Security Risk</th>
                  <th>Criticality</th>
                  <th>Recommended Action</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {(selectedRisk.files && selectedRisk.files.length > 0) ? (
                  selectedRisk.files.map((file) => (
                    <tr key={file.file_path}>
                      <td>
                        <strong>{file.name}</strong>
                        <div style={{ fontSize: 10, color: "var(--muted)" }}><code>{file.file_path}</code></div>
                      </td>
                      <td>
                        <Badge tone={(file.priority || "Medium").toLowerCase()}>{file.priority || "Medium"}</Badge>
                      </td>
                      <td>
                        <strong>{file.score}</strong>
                      </td>
                      <td>
                        <span style={{
                          fontSize: 11,
                          fontWeight: 700,
                          padding: "2px 7px",
                          borderRadius: 8,
                          background: file.evidence_count > 0 ? "var(--brand, #ef5a31)" : "var(--surface2)",
                          color: file.evidence_count > 0 ? "#fff" : "inherit"
                        }}>
                          {file.evidence_count} {file.evidence_count === 1 ? "finding" : "findings"}
                        </span>
                      </td>
                      <td>{file.technical_debt || "Low"}</td>
                      <td>
                        <Badge tone={file.security_risk === "Critical" ? "critical" : file.security_risk === "High" ? "warning" : "neutral"}>
                          {file.security_risk || "Low"}
                        </Badge>
                      </td>
                      <td>{file.business_criticality || "Medium"}</td>
                      <td style={{ fontSize: 11, maxWidth: 220 }}>{file.recommended_action}</td>
                      <td>
                        <Button
                          variant="secondary"
                          onClick={() => onNavigateToCode && onNavigateToCode(file.file_path)}
                          style={{ fontSize: 11, padding: "4px 8px" }}
                        >
                          Inspect <Icon name="arrow" size={12} />
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} style={{ textAlign: "center", padding: 24, color: "var(--muted)" }}>
                      No separate source files cataloged under this module.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}

// 8. Architecture Page
function ArchitecturePage({ architecture }) {
  const arch = architecture || {};
  const current = arch.current_state?.components || [
    { name: "Web & batch clients", sub: "Mixed entry points" },
    { name: "Order monolith", sub: "Pricing · Auth · Validation", tone: "legacy" },
    { name: "Customer DB", sub: "Shared tables" },
    { name: "Warehouse SOAP", sub: "External API" },
  ];
  const target = arch.target_state?.components || [
    { name: "API gateway", sub: "Versioned contracts", tone: "target" },
    { name: "Order capability", sub: "Workflow owner", tone: "target" },
    { name: "Pricing capability", sub: "Rule boundary", tone: "target" },
    { name: "Customer data API", sub: "Governed writes", tone: "target" },
    { name: "Warehouse adapter", sub: "Idempotent boundary", tone: "target" },
  ];

  return (
    <>
      <PageHeader
        title="Target architecture"
        description="Compare the current system with a proposed modernization path."
      />
      <div className="architecture-grid">
        <section className="card arch">
          <div className="card-head">
            <div>
              <h2>Current state</h2>
              <p>Observed from source evidence</p>
            </div>
            <Badge>As analyzed</Badge>
          </div>
          <div className="arch-diagram">
            <div className="arch-box">
              <strong>{current[0]?.name}</strong>
              <span>{current[0]?.sub}</span>
            </div>
            <span>↓</span>
            <div className={`arch-box ${current[1]?.tone || ""}`}>
              <strong>{current[1]?.name}</strong>
              <span>{current[1]?.sub}</span>
            </div>
            <div className="arch-row">
              <div className="arch-box">
                <strong>{current[2]?.name}</strong>
                <span>{current[2]?.sub}</span>
              </div>
              <div className="arch-box">
                <strong>{current[3]?.name}</strong>
                <span>{current[3]?.sub}</span>
              </div>
            </div>
          </div>
        </section>

        <section className="card arch proposed">
          <div className="card-head">
            <div>
              <h2>Proposed target</h2>
              <p>Recommendation — not deployed</p>
            </div>
            <Badge tone="demo">Proposed</Badge>
          </div>
          <div className="arch-diagram">
            <div className="arch-box target">
              <strong>{target[0]?.name}</strong>
              <span>{target[0]?.sub}</span>
            </div>
            <span>↓</span>
            <div className="arch-row">
              <div className="arch-box target">
                <strong>{target[1]?.name}</strong>
                <span>{target[1]?.sub}</span>
              </div>
              <div className="arch-box target">
                <strong>{target[2]?.name}</strong>
                <span>{target[2]?.sub}</span>
              </div>
            </div>
            <span>↓</span>
            <div className="arch-row">
              <div className="arch-box target">
                <strong>{target[3]?.name}</strong>
                <span>{target[3]?.sub}</span>
              </div>
              <div className="arch-box target">
                <strong>{target[4]?.name}</strong>
                <span>{target[4]?.sub}</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="card alternatives">
        <div className="card-head">
          <div>
            <h2>Migration alternatives</h2>
            <p>Trade-offs and constraints for human review</p>
          </div>
        </div>
        <div className="alt-grid">
          <article>
            <Badge tone="success">Recommended</Badge>
            <h3>Incremental strangler</h3>
            <p>Extract stable capabilities behind versioned boundaries.</p>
            <strong>Trade-off</strong>
            <span>Slower initial progress, lower operational risk.</span>
          </article>
          <article>
            <Badge>Alternative</Badge>
            <h3>Modular monolith first</h3>
            <p>Enforce internal boundaries before distributing services.</p>
            <strong>Trade-off</strong>
            <span>Faster simplification, shared deployment remains.</span>
          </article>
          <article>
            <Badge tone="critical">High risk</Badge>
            <h3>Full rewrite</h3>
            <p>Replace all capabilities in a single coordinated release.</p>
            <strong>Constraint</strong>
            <span>Undocumented rules make parity difficult to prove.</span>
          </article>
        </div>
      </section>
    </>
  );
}

// 9. Roadmap Page
function RoadmapPage({ phases = [] }) {
  const [openPhase, setOpenPhase] = useState(0);

  return (
    <>
      <PageHeader
        title="Migration roadmap"
        description="A phased recommendation with explicit approvals and rollback paths."
        actions={
          <Button
            variant="secondary"
            onClick={() => {
              const blob = new Blob([JSON.stringify(phases, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "migration-roadmap.json";
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            <Icon name="download" size={16} /> Export plan
          </Button>
        }
      />
      <div className="roadmap">
        {phases.map((p, idx) => (
          <section key={p.name} className={`card phase ${openPhase === idx ? "open" : ""}`}>
            <button
              className="phase-summary"
              onClick={() => setOpenPhase(openPhase === idx ? -1 : idx)}
            >
              <span className="phase-number">{idx + 1}</span>
              <div>
                <div>
                  <h2>{p.name}</h2>
                  <Badge tone={idx === 0 ? "success" : "demo"}>{p.status}</Badge>
                </div>
                <p>{p.objective}</p>
              </div>
              <div className="phase-effort">
                <span>Estimated effort</span>
                <strong>{p.effort}</strong>
              </div>
              <Icon name="arrow" />
            </button>
            {openPhase === idx && (
              <div className="phase-body">
                <div className="phase-columns">
                  <DetailItem label="Affected modules">{p.modules?.join(" · ")}</DetailItem>
                  <DetailItem label="Business rules at risk">{p.rules?.join(" · ")}</DetailItem>
                  <DetailItem label="Prerequisites">{p.prerequisites}</DetailItem>
                  <DetailItem label="Risks & mitigation">
                    <strong>{p.risks}</strong>
                    <br />
                    {p.mitigation}
                  </DetailItem>
                  <DetailItem label="Acceptance criteria">{p.criteria}</DetailItem>
                  <DetailItem label="Rollback strategy">{p.rollback}</DetailItem>
                </div>
                <div className="approval">
                  <Icon name="check" />
                  <div>
                    <strong>Human approval checkpoint</strong>
                    <p>{p.approval}</p>
                  </div>
                </div>
              </div>
            )}
          </section>
        ))}
      </div>
      <p className="estimate-note">
        <Icon name="info" size={15} /> Effort values are illustrative estimates, not delivery commitments.
      </p>
    </>
  );
}

// 10. Regression Tests Page
function RegressionTestsPage({ tests = [] }) {
  const [search, setSearch] = useState("");
  const filtered = tests.filter((t) =>
    `${t.name} ${t.rule} ${t.module}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <PageHeader
        title="Regression tests"
        description="AI-generated suggestions mapped to business rules and source evidence."
        actions={
          <Button
            variant="secondary"
            onClick={() => {
              const blob = new Blob([JSON.stringify(tests, null, 2)], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "regression-tests.json";
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            <Icon name="download" size={16} /> Export
          </Button>
        }
      />
      <div className="suggestion-warning">
        <Icon name="info" />
        <div>
          <strong>Suggested, not executed</strong>
          <p>These specifications were synthesized from static rule evidence. Verify and execute in testing environment.</p>
        </div>
      </div>
      <div className="toolbar">
        <SearchInput value={search} onChange={setSearch} placeholder="Search tests, rules, or modules…" />
      </div>
      <div className="test-list">
        {filtered.map((t) => (
          <article key={t.name} className="card test-card">
            <div className="test-priority">
              <Badge tone={t.priority === "P0" ? "critical" : "warning"}>{t.priority}</Badge>
              <Badge tone="demo">{t.status}</Badge>
            </div>
            <div>
              <h2>{t.name}</h2>
              <p>{t.behavior}</p>
              <div className="test-links">
                <span><Icon name="book" size={14} /> {t.rule}</span>
                <code>{t.source}</code>
                <span>{t.module}</span>
              </div>
            </div>
            <Button
              variant="secondary"
              onClick={() =>
                navigator.clipboard.writeText(
                  `Test: ${t.name}\nRule: ${t.rule}\nSource: ${t.source}\nExpected Behavior: ${t.behavior}`
                )
              }
            >
              <Icon name="copy" size={15} /> Copy spec
            </Button>
          </article>
        ))}
      </div>
    </>
  );
}

// 11. Reports Page
function ReportsPage({ record, currentAnalysisId }) {
  const [activeTab, setActiveTab] = useState("Executive summary");

  const handleDownload = (format) => {
    api.downloadReport(currentAnalysisId || "demo", format, record?.project_name || "omnistrat");
  };

  return (
    <>
      <PageHeader
        title="Analysis report"
        description="A decision-ready view of evidence, risks, and recommendations."
        actions={
          <>
            <Button variant="secondary" onClick={() => handleDownload("markdown")}>
              <Icon name="download" size={16} /> Markdown
            </Button>
            <Button onClick={() => handleDownload("json")}>
              <Icon name="download" size={16} /> JSON
            </Button>
          </>
        }
      />
      <div className="report-layout">
        <aside className="card report-nav">
          {["Executive summary", "Business rules", "Dependencies", "Risk & debt", "Modernization plan", "Limitations"].map(
            (tab) => (
              <button
                key={tab}
                className={activeTab === tab ? "active" : ""}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
                <Icon name="arrow" size={15} />
              </button>
            )
          )}
        </aside>

        <article className="card report">
          <Badge tone={record?.ai_enabled ? "success" : "demo"}>
            {record?.ai_enabled ? "AI Augmented" : "Static Analysis"}
          </Badge>
          <h1>{activeTab}</h1>

          {activeTab === "Executive summary" && (
            <>
              <p className="report-lead">{record?.executive_summary}</p>
              <h2>Key conclusion</h2>
              <p>Modernization should begin with knowledge stabilization—not premature code rewriting.</p>
              <div className="report-callout">
                <Icon name="risk" />
                <div>
                  <strong>Review before modernization</strong>
                  <p>Preserve discount ordering, credit override auditing, and timeout semantics through characterization tests.</p>
                </div>
              </div>
              <h2>Recommended direction</h2>
              <p>Use an incremental strangler approach: encapsulate shared data access, then extract pricing and warehouse capabilities.</p>
            </>
          )}

          {activeTab === "Business rules" && (
            <>
              {record?.rules?.map((r) => (
                <div key={r.id} className="report-item">
                  <strong>{r.id} · {r.name}</strong>
                  <p>{r.description}</p>
                  <code>{r.source}</code>
                </div>
              ))}
            </>
          )}

          {activeTab === "Dependencies" && (
            <>
              <p className="report-lead">Observed module relationships across services, modules, and database boundaries.</p>
              {record?.modules?.map((m) => (
                <div key={m.id} className="report-item">
                  <strong>{m.name}</strong>
                  <p>{m.incoming} incoming · {m.outgoing} outgoing · {m.reason}</p>
                </div>
              ))}
            </>
          )}

          {activeTab === "Risk & debt" && (
            <>
              {record?.risks?.map((r) => (
                <div key={r.name} className="report-item">
                  <strong>{r.name} · {r.score}/100 ({r.severity})</strong>
                  <p>{r.factors?.join(" · ")}</p>
                </div>
              ))}
            </>
          )}

          {activeTab === "Modernization plan" && (
            <>
              {record?.phases?.map((p) => (
                <div key={p.name} className="report-item">
                  <strong>{p.name}</strong>
                  <p>{p.objective} Estimated effort: {p.effort}.</p>
                </div>
              ))}
            </>
          )}

          {activeTab === "Limitations" && (
            <>
              <p className="report-lead">Important analysis boundaries and disclosures.</p>
              <ul className="limitations">
                {record?.limitations?.map((l, i) => (
                  <li key={i}>{l}</li>
                ))}
              </ul>
            </>
          )}
        </article>
      </div>
    </>
  );
}

// 12. Settings Page with Functional Google Gemini API Configuration
function SettingsPage({ isDark, setIsDark, backendHealth, onRefreshHealth, record, history = [], onSelectHistory }) {
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [selectedModel, setSelectedModel] = useState("gemini-2.5-flash");
  const [supportedModels, setSupportedModels] = useState(["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]);
  const [geminiStatus, setGeminiStatus] = useState("idle"); // idle, testing, connected, failed
  const [statusMessage, setStatusMessage] = useState("");
  const [maskedKey, setMaskedKey] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load existing Gemini configuration from backend on mount
  useEffect(() => {
    loadGeminiSettings();
  }, []);

  const loadGeminiSettings = async () => {
    try {
      const data = await api.getGeminiSettings();
      if (data.configured) {
        setGeminiStatus("connected");
        setMaskedKey(data.masked_key);
        setStatusMessage(`Connected via server environment (${data.model})`);
      } else {
        setGeminiStatus("not_configured");
      }
      if (data.model) setSelectedModel(data.model);
      if (data.supported_models?.length) setSupportedModels(data.supported_models);
    } catch {
      setGeminiStatus("not_configured");
    }
  };

  const handleTestConnection = async () => {
    setLoading(true);
    setGeminiStatus("testing");
    setStatusMessage("Testing live connection to Google Gemini API...");

    try {
      const res = await api.testGeminiConnection(geminiApiKey, selectedModel);
      if (res.success) {
        setGeminiStatus("connected");
        setStatusMessage(res.message);
        setMaskedKey(res.masked_key || maskedKey);
        onRefreshHealth();
      } else {
        setGeminiStatus("failed");
        setStatusMessage(res.message);
      }
    } catch (err) {
      setGeminiStatus("failed");
      setStatusMessage(err.message || "Failed to reach Gemini API.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfigureKey = async () => {
    if (!geminiApiKey.trim()) {
      setStatusMessage("Please enter a valid Gemini API key.");
      setGeminiStatus("failed");
      return;
    }

    setLoading(true);
    setGeminiStatus("testing");
    setStatusMessage("Validating and saving API key in backend memory...");

    try {
      const res = await api.configureGemini(geminiApiKey.trim(), selectedModel);
      if (res.success) {
        setGeminiStatus("connected");
        setStatusMessage(`API Key successfully configured and tested! Active model: ${res.model}`);
        setMaskedKey(res.masked_key);
        setGeminiApiKey("");
        onRefreshHealth();
      } else {
        setGeminiStatus("failed");
        setStatusMessage(res.message);
      }
    } catch (err) {
      setGeminiStatus("failed");
      setStatusMessage(err.message || "Configuration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Settings"
        description="Project metadata, Gemini API configuration, and connection status."
      />
      <div className="settings-grid">
        {/* Google Gemini AI Provider Settings */}
        <section className="card settings-card" style={{ gridColumn: "span 2" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div>
              <h2 style={{ fontSize: 16 }}>Google Gemini AI Integration</h2>
              <p style={{ marginTop: 2 }}>Configure official Google Gen AI SDK for AI-augmented modernization explanations.</p>
            </div>
            <Badge
              tone={
                geminiStatus === "connected"
                  ? "success"
                  : geminiStatus === "testing"
                  ? "warning"
                  : geminiStatus === "failed"
                  ? "critical"
                  : "neutral"
              }
            >
              {geminiStatus === "connected"
                ? "Connected"
                : geminiStatus === "testing"
                ? "Testing..."
                : geminiStatus === "failed"
                ? "Failed"
                : "Not Configured"}
            </Badge>
          </div>

          {maskedKey && (
            <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", background: "var(--surface2)", borderRadius: 7, border: "1px solid var(--border)", marginBottom: 14 }}>
              <Icon name="check" size={16} />
              <div style={{ flex: 1, fontSize: 11 }}>
                <span>Active Server Key: </span>
                <code style={{ color: "var(--brand)", fontWeight: 700 }}>{maskedKey}</code>
              </div>
              <Badge tone="demo">{selectedModel}</Badge>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr 180px", gap: 12 }}>
            <label className="field" style={{ marginTop: 0 }}>
              <span>
                Gemini API Key <em>{maskedKey ? "Enter new key to update" : "Required for AI augmentation"}</em>
              </span>
              <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                <input
                  type={showKey ? "text" : "password"}
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  placeholder="AIzaSy... (Paste Gemini API Key)"
                  style={{ paddingRight: 75 }}
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  style={{
                    position: "absolute",
                    right: 8,
                    fontSize: 10,
                    color: "var(--muted)",
                    padding: "4px 8px",
                    borderRadius: 4,
                    background: "var(--surface)",
                    border: "1px solid var(--border)"
                  }}
                >
                  {showKey ? "Hide" : "Show"}
                </button>
              </div>
            </label>

            <label className="field" style={{ marginTop: 0 }}>
              <span>Model Selection</span>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                style={{ width: "100%", height: 38 }}
              >
                {supportedModels.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div style={{ display: "flex", gap: 8, marginTop: 14, alignItems: "center", flexWrap: "wrap" }}>
            <Button
              variant="primary"
              disabled={loading || !geminiApiKey.trim()}
              onClick={handleConfigureKey}
            >
              {loading ? "Processing..." : "Save & Configure"}
            </Button>
            <Button
              variant="secondary"
              disabled={loading || (!geminiApiKey.trim() && !maskedKey)}
              onClick={handleTestConnection}
            >
              <Icon name="pulse" size={14} /> Test Connection
            </Button>
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              style={{ fontSize: 11, color: "var(--brand)", textDecoration: "none", marginLeft: "auto", display: "flex", alignItems: "center", gap: 4 }}
            >
              Get free Gemini Key from Google AI Studio &rarr;
            </a>
          </div>

          {statusMessage && (
            <div
              style={{
                marginTop: 12,
                padding: "9px 12px",
                borderRadius: 7,
                fontSize: 11,
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: geminiStatus === "connected" ? "var(--surface2)" : geminiStatus === "failed" ? "#fff0ef" : "var(--surface2)",
                color: geminiStatus === "connected" ? "var(--brand)" : geminiStatus === "failed" ? "#b33f39" : "var(--text)",
                border: "1px solid var(--border)"
              }}
            >
              <Icon name={geminiStatus === "connected" ? "check" : geminiStatus === "failed" ? "risk" : "info"} size={16} />
              <span>{statusMessage}</span>
            </div>
          )}

          <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid var(--border)", fontSize: 10, color: "var(--muted)", lineHeight: 1.5 }}>
            <p>
              <strong>🔒 Security & Persistence:</strong> API keys configured in this interface are transferred directly to the server and retained in backend process memory. Never commit keys to version control. To persist permanently across server restarts, add <code>GEMINI_API_KEY=your_key</code> in your local <code>.env</code> file.
            </p>
          </div>
        </section>

        <section className="card settings-card">
          <h2>Project details</h2>
          <p>Current workspace metadata.</p>
          <label className="field">
            <span>Project name</span>
            <input value={record?.project_name || "Northstar Commerce"} readOnly />
          </label>
          <label className="field">
            <span>Repository</span>
            <input value={record?.repo_url || "Local uploaded archive"} readOnly disabled />
          </label>
        </section>

        <section className="card settings-card">
          <h2>Appearance</h2>
          <p>Stored for this browser session.</p>
          <div className="setting-row">
            <div>
              <strong>Dark theme</strong>
              <span>Use a low-light interface.</span>
            </div>
            <button
              className={`switch ${isDark ? "on" : ""}`}
              onClick={() => setIsDark(!isDark)}
              aria-label="Toggle dark theme"
            >
              <i />
            </button>
          </div>
          <div className="setting-row">
            <div>
              <strong>Interface language</strong>
              <span>Display language</span>
            </div>
            <select>
              <option>English</option>
            </select>
          </div>
        </section>

        <section className="card settings-card" style={{ gridColumn: "span 2" }}>
          <h2>Analysis history</h2>
          <p>Recent analyses in this workspace. Click to switch active workspace.</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 10, marginTop: 10 }}>
            {history.map((h) => (
              <div
                key={h.id}
                className="history-item"
                onClick={() => onSelectHistory(h.id)}
                style={{ cursor: "pointer", border: "1px solid var(--border)", padding: 10, borderRadius: 8, background: "var(--surface2)" }}
              >
                <span className="activity-icon a0">
                  <Icon name="check" size={16} />
                </span>
                <div>
                  <strong>{h.name}</strong>
                  <p>ID: {h.id} · {h.status}</p>
                </div>
                <Badge tone={h.id === "demo" ? "demo" : "success"}>{h.id === "demo" ? "Demo" : "Analyzed"}</Badge>
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}

// Main Application Shell
export default function App() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // Active Analysis State
  const [currentAnalysisId, setCurrentAnalysisId] = useState("demo");
  const [analysisRecord, setAnalysisRecord] = useState(null);
  const [backendHealth, setBackendHealth] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([
    { id: "demo", name: "Northstar Commerce", status: "Completed" }
  ]);

  // Initial load: Fetch health and demo record
  useEffect(() => {
    checkHealthStatus();
    loadAnalysis("demo");
  }, []);

  const checkHealthStatus = async (retry = true) => {
    try {
      const h = await api.checkHealth();
      setBackendHealth(h);
    } catch {
      if (retry) {
        setTimeout(() => checkHealthStatus(false), 1500);
      } else {
        setBackendHealth({ status: "error" });
      }
    }
  };

  const loadAnalysis = async (id, retry = true) => {
    try {
      const res = await api.getAnalysisStatus(id);
      if (res.record) {
        setAnalysisRecord(res.record);
        setCurrentAnalysisId(id);
      }
    } catch (e) {
      if (retry) {
        setTimeout(() => loadAnalysis(id, false), 1500);
      } else {
        console.error("Could not load analysis", id, e);
      }
    }
  };

  const handleStartAnalysis = (newId, pName) => {
    setCurrentAnalysisId(newId);
    setAnalysisRecord(null);
    setCodeSearchQuery("");
    setAnalysisHistory((prev) => [{ id: newId, name: pName, status: "Analyzing" }, ...prev]);
  };

  const handleCompletedAnalysis = (rec) => {
    if (rec) {
      setAnalysisRecord(rec);
      setAnalysisHistory((prev) =>
        prev.map((h) => (h.id === rec.id ? { ...h, status: "Completed" } : h))
      );
    }
  };

  const [codeSearchQuery, setCodeSearchQuery] = useState("");

  const navigateTo = (tab) => {
    setActiveTab(tab);
    setIsMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const navigateToCode = (query = "") => {
    setCodeSearchQuery(query);
    navigateTo("Code Intelligence");
  };

  // Render view
  const currentView = useMemo(() => {
    switch (activeTab) {
      case "Overview":
        return (
          <OverviewPage
            go={navigateTo}
            record={analysisRecord}
            onExport={() => api.downloadReport(currentAnalysisId, "markdown", analysisRecord?.project_name)}
          />
        );
      case "Upload":
        return (
          <UploadPage
            go={navigateTo}
            onStartAnalysis={handleStartAnalysis}
            activeProjectName={analysisRecord?.project_name}
          />
        );
      case "Analysis":
        return (
          <AnalysisPage
            analysisId={currentAnalysisId}
            record={analysisRecord}
            onCompleted={handleCompletedAnalysis}
            go={navigateTo}
            onNavigateToCode={navigateToCode}
          />
        );
      case "Module Explorer":
        return (
          <ModuleExplorerPage
            moduleTree={analysisRecord?.module_tree || []}
            findings={analysisRecord?.findings || []}
            record={analysisRecord}
            onNavigateToCode={navigateToCode}
          />
        );
      case "Pipeline":
        return (
          <PipelinePage
            pipelines={analysisRecord?.pipelines || []}
            record={analysisRecord}
          />
        );
      case "Code Intelligence":
        return <CodeIntelligencePage findings={analysisRecord?.findings || []} initialSearch={codeSearchQuery} />;
      case "Business Rules":
        return <BusinessRulesPage rules={analysisRecord?.rules || []} />;
      case "Technology Audit":
        return (
          <TechnologyAuditPage
            versionAudit={analysisRecord?.version_audit || []}
            projectName={analysisRecord?.project_name}
          />
        );
      case "Dependencies":
        return (
          <DependenciesPage
            modules={analysisRecord?.modules || []}
            edges={analysisRecord?.edges || []}
            findings={analysisRecord?.findings || []}
            databaseSummary={analysisRecord?.database_summary}
          />
        );
      case "Risk Heatmap":
        return (
          <RiskHeatmapPage
            risks={analysisRecord?.risks || []}
            findings={analysisRecord?.findings || []}
            onNavigateToCode={navigateToCode}
          />
        );
      case "Architecture":
        return <ArchitecturePage architecture={analysisRecord?.architecture} />;
      case "Roadmap":
        return <RoadmapPage phases={analysisRecord?.phases || []} />;
      case "Regression Tests":
        return <RegressionTestsPage tests={analysisRecord?.tests || []} />;
      case "Reports":
        return <ReportsPage record={analysisRecord} currentAnalysisId={currentAnalysisId} />;
      case "Settings":
        return (
          <SettingsPage
            isDark={isDark}
            setIsDark={setIsDark}
            backendHealth={backendHealth}
            onRefreshHealth={checkHealthStatus}
            record={analysisRecord}
            history={analysisHistory}
            onSelectHistory={(id) => loadAnalysis(id)}
          />
        );
      default:
        return null;
    }
  }, [activeTab, isDark, analysisRecord, currentAnalysisId, backendHealth, analysisHistory, codeSearchQuery]);

  return (
    <div className={`app ${isDark ? "dark" : ""}`}>
      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarCollapsed ? "collapsed" : ""} ${isMobileMenuOpen ? "mobile-open" : ""}`}>
        <div className="brand">
          <div className="logo"><span /></div>
          {!isSidebarCollapsed && (
            <div>
              <strong>OmniStrat</strong>
              <small>AI</small>
            </div>
          )}
          <button onClick={() => setIsMobileMenuOpen(false)} className="mobile-close">
            <Icon name="x" />
          </button>
        </div>

        <div
          className="project-switch"
          onClick={() => {
            const nextId = currentAnalysisId === "demo" && analysisHistory.length > 1 ? analysisHistory[0].id : "demo";
            loadAnalysis(nextId);
          }}
          title="Click to switch between active analyses"
          style={{ cursor: "pointer" }}
        >
          <div>{analysisRecord?.project_name?.slice(0, 2).toUpperCase() || "OS"}</div>
          {!isSidebarCollapsed && (
            <span>
              <strong>{analysisRecord?.project_name || "Northstar Commerce"}</strong>
              <small>{currentAnalysisId === "demo" ? "Demo workspace" : "Active analysis"}</small>
            </span>
          )}
          {!isSidebarCollapsed && <Icon name="arrow" size={15} />}
        </div>

        <nav>
          <div className="nav-lens-line" />
          {navSections.map((sec, sIdx) => (
            <div key={sec.section} className={`nav-group nav-zone-${sIdx}`}>
              {!isSidebarCollapsed && <p>{sec.section}</p>}
              {sec.items.map((it) => (
                <button
                  key={it.label}
                  title={it.label}
                  className={activeTab === it.label ? "active" : ""}
                  onClick={() => navigateTo(it.label)}
                >
                  <span className="nav-orb">
                    <Icon name={it.icon} />
                  </span>
                  {!isSidebarCollapsed && <span>{it.label}</span>}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            className={activeTab === "Settings" ? "active" : ""}
            onClick={() => navigateTo("Settings")}
          >
            <Icon name="settings" />
            {!isSidebarCollapsed && <span>Settings</span>}
          </button>
          <button className="collapse" onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}>
            <Icon name="arrow" />
            {!isSidebarCollapsed && <span>Collapse sidebar</span>}
          </button>
        </div>
      </aside>

      {isMobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setIsMobileMenuOpen(false)} />
      )}

      {/* Main Shell */}
      <div className="main-shell">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setIsMobileMenuOpen(true)} aria-label="Open menu">
            <Icon name="menu" />
          </button>
          <button
            className="collapse desktop"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            aria-label="Toggle sidebar"
          >
            <Icon name="menu" />
          </button>

          <div className="workspace-status">
            <i style={{ background: backendHealth?.status === "ok" ? "#45c48e" : "#e05c55" }} />
            {currentAnalysisId === "demo" ? "Demo data" : "Live analysis"}
          </div>

          <div className="top-actions">
            <button onClick={() => setIsDark(!isDark)} aria-label="Toggle theme">
              <Icon name={isDark ? "sun" : "moon"} />
            </button>
            <div className="profile-wrap">
              <button className="avatar" onClick={() => setIsProfileOpen(!isProfileOpen)}>
                AM
              </button>
              {isProfileOpen && (
                <div className="profile-menu">
                  <strong>Alex Morgan</strong>
                  <span>Demo reviewer</span>
                  <hr />
                  <button
                    onClick={() => {
                      navigateTo("Settings");
                      setIsProfileOpen(false);
                    }}
                  >
                    Workspace settings
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main>{currentView}</main>
      </div>
    </div>
  );
}

