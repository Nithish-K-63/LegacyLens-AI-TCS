import sys

new_heatmap_code = '''// 7. Risk Heatmap Page
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
}'''

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace from '// 7. Risk Heatmap Page' up to '// 8. Architecture Page'
start_idx = content.find('// 7. Risk Heatmap Page')
end_idx = content.find('// 8. Architecture Page')

if start_idx == -1 or end_idx == -1:
    print('Failed to find markers')
    sys.exit(1)

updated = content[:start_idx] + new_heatmap_code + '\n\n' + content[end_idx:]

with open('frontend/src/App.jsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(updated)

print('Successfully replaced RiskHeatmapPage')

