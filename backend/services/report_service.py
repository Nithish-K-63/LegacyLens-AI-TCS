"""Report assembly and export service for JSON and Markdown deliverables."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.schemas.models import (
    AnalysisRecord, AnalysisFinding, BusinessRule, DependencyNode,
    DependencyEdge, ModernizationRisk, MigrationPhase, SuggestedTest,
    ProductProfile, MetricCard
)


def assemble_modernization_report(
    project_name: str,
    file_inventory: List[Dict[str, Any]],
    static_results: Dict[str, Any],
    product_profile: ProductProfile,
    nodes: List[DependencyNode],
    edges: List[DependencyEdge],
    db_analysis: Dict[str, Any],
    rules: List[BusinessRule],
    risks: List[ModernizationRisk],
    phases: List[MigrationPhase],
    tests: List[SuggestedTest],
    arch: Any
) -> Dict[str, Any]:
    """Assemble final modernization report payload."""
    total_loc = static_results.get("total_loc", 0)
    top_langs = static_results.get("top_languages", "Unknown")

    exec_summary = (
        f"Autonomous modernization assessment completed for '{project_name}'. "
        f"Analyzed {len(file_inventory)} source files across {top_langs} totaling {total_loc:,} lines of code. "
        f"Identified {len(risks)} modernization risk boundaries, {len(rules)} business logic rules, "
        f"and mapped {len(edges)} cross-module dependency links with zero destructive code modifications."
    )

    limitations = [
        "Dynamic reflection and indirect RPC calls cannot be statically verified with 100% certainty; runtime telemetry is advised before retirement.",
        "Characterization tests should be executed against staging environment baselines to verify bit-level arithmetic parity.",
        "External batch orchestrators (e.g., cron jobs, mainframe scheduler) may invoke legacy scripts outside the repository scope."
    ]

    return {
        "summary": exec_summary,
        "limitations": limitations
    }


def generate_markdown_report(record: AnalysisRecord) -> str:
    """Format analysis record as a comprehensive executive Markdown report."""
    md = []
    md.append(f"# OmniStrat Modernization Report: {record.project_name}\n")
    md.append(f"**Analysis ID:** `{record.id}`  ")
    md.append(f"**Date:** {record.completed_at or record.created_at}  ")
    md.append(f"**AI Integration:** {'Enabled (Google Gemini)' if record.ai_enabled else 'Disabled (Static Heuristic Mode)'}\n")

    if record.product_profile:
        prof = record.product_profile
        md.append("## 1. Product Understanding & Profile\n")
        md.append(f"- **Product Type:** {prof.product_type}")
        md.append(f"- **Stated Purpose:** {prof.purpose}")
        md.append(f"- **Architectural Pattern:** {prof.architectural_pattern}")
        if prof.detected_frameworks:
            md.append(f"- **Detected Frameworks & Libraries:** {', '.join(prof.detected_frameworks)}")
        if prof.infrastructure:
            md.append(f"- **Infrastructure & Build Specs:** {', '.join(prof.infrastructure)}")
        if prof.entry_points:
            md.append("- **Discovered Entry Points:**")
            for ep in prof.entry_points:
                md.append(f"  * `{ep.get('file')}` — {ep.get('role')} ({ep.get('language')})")
        md.append("\n")

    if record.pipelines:
        md.append("## 2. Reconstructed Real Execution Pipelines\n")
        for pipe in record.pipelines:
            md.append(f"### Pipeline: {pipe.name}")
            md.append(f"**Purpose:** {pipe.purpose}  ")
            md.append(f"**Primary Entry:** `{pipe.entry_point}` | **Status:** {pipe.status}\n")
            md.append("| Step | Stage | Responsibilities | Inputs | Outputs | Evidence / Modules |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for st in pipe.stages:
                mods = ", ".join([f"`{m}`" for m in st.modules[:2]])
                md.append(f"| {st.order} | **{st.name}** | {st.responsibility} | {st.input} | {st.output} | {mods} |")
            md.append("\n")
            if pipe.alternate_workflows:
                md.append("**Alternate & Exception Workflows:**")
                for aw in pipe.alternate_workflows:
                    md.append(f"- {aw}")
                md.append("\n")

    md.append("## 3. Executive Summary\n")
    md.append(f"{record.executive_summary}\n")

    md.append("## 4. Key Metrics\n")
    md.append("| Metric | Value | Details |")
    md.append("| :--- | :--- | :--- |")
    for m in record.metrics:
        md.append(f"| {m.label} | **{m.value}** | {m.delta} |")
    md.append("\n")

    if record.findings:
        md.append("## 5. Code Intelligence & Deduplicated Evidence Findings\n")
        md.append("| ID | Category | Severity | Location | Confidence | Review | Evidence & Impact |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for f in record.findings:
            md.append(f"| **{f.id}** | {f.category} | `{f.severity}` | `{f.file}:{f.lines}` | {f.confidence}% | {f.review} | {f.evidence} — *{f.impact}* |")
        md.append("\n")

    md.append("## 6. Discovered Business Rules\n")
    for r in record.rules:
        md.append(f"### {r.id}: {r.name}")
        md.append(f"- **Category:** {r.category} | **Confidence:** {r.confidence}% | **Impact:** {r.impact}")
        md.append(f"- **Description:** {r.description}")
        md.append(f"- **Source Evidence:** `{r.source}`")
        if r.dependencies:
            md.append(f"- **Dependencies:** {', '.join(r.dependencies)}")
        if r.tests:
            md.append(f"- **Candidate Tests:** {', '.join(r.tests)}")
        md.append("")

    md.append("## 7. Modernization Risk Assessment\n")
    md.append("| Module | Risk Score | Severity | Criticality | Uncertainty | Action |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in record.risks:
        md.append(f"| {r.name} | {r.score}/100 | {r.severity} | {r.criticality} | {r.uncertainty} | {r.action} |")
    md.append("\n")

    if record.version_audit:
        md.append("## 8. Technology & Dependency Version Audit\n")
        md.append("| Component | Category | Current declared version | Resolved version | Recommended target version | Support status | Security status | Upgrade priority | Reason | Compatibility impact | Source evidence | Suggested action |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for v in record.version_audit:
            res_v = v.resolved_version or "N/A"
            md.append(f"| **{v.component}** | {v.category} | `{v.current_version}` | `{res_v}` | **{v.recommended_version}** | {v.support_status} | {v.security_status} | {v.upgrade_priority} | {v.reason} | {v.compatibility_impact} | `{v.source_evidence}` | **{v.suggested_action}** |")
        md.append("\n")

        # Upgrade order & summary
        critical_upgrades = [v for v in record.version_audit if v.upgrade_priority in ("Critical", "High")]
        stable_components = [v for v in record.version_audit if v.upgrade_priority == "No Upgrade Needed"]
        unverified_items = [v for v in record.version_audit if not v.verified]

        if critical_upgrades:
            md.append("### Recommended Upgrade Order (Dependency & Security Priority)\n")
            for idx, cu in enumerate(critical_upgrades, 1):
                md.append(f"{idx}. **{cu.component}** (`{cu.current_version}` -> `{cu.recommended_version}`): {cu.reason}")
            md.append("\n")

        if stable_components:
            md.append("### Supported Components (No Immediate Upgrade Needed)\n")
            md.append(", ".join([f"`{sc.component}` ({sc.current_version})" for sc in stable_components]))
            md.append("\n\n")

        if unverified_items:
            md.append("> [!NOTE]\n> **Version Verification Disclaimer:** Certain third-party dependencies are pinned without published security advisory metadata in project source files; team review is advised before version changes.\n\n")

    md.append("## 9. Database Analysis & Shared Table Contention\n")
    db_data = record.database_summary or {}
    shared = db_data.get("shared_tables", [])
    if shared:
        md.append("| Table | Writers | Readers | Risk |")
        md.append("| :--- | :--- | :--- | :--- |")
        for s in shared:
            md.append(f"| `{s['table']}` | {s['writers_count']} | {s['readers_count']} | {s['risk']} |")
        md.append("\n")
    else:
        md.append("No multi-writer database table contention detected.\n")

    if db_data.get("stored_procedures"):
        md.append(f"**Stored Procedures Discovered:** {', '.join(db_data['stored_procedures'])}\n\n")

    md.append("## 10. Phased Migration Roadmap\n")
    for p in record.phases:
        md.append(f"### {p.name}")
        md.append(f"- **Objective:** {p.objective}")
        md.append(f"- **Estimated Effort:** {p.effort} ({p.status})")
        md.append(f"- **Affected Modules:** {', '.join(p.modules)}")
        md.append(f"- **Prerequisites:** {p.prerequisites}")
        md.append(f"- **Risks & Mitigation:** {p.risks} — *{p.mitigation}*")
        md.append(f"- **Exit Criteria:** {p.criteria}")
        md.append(f"- **Rollback Plan:** {p.rollback}")
        md.append(f"- **Human Approval:** {p.approval}")
        md.append("")

    md.append("## 11. Suggested Regression Tests\n")
    for t in record.tests:
        md.append(f"- **[{t.priority}] {t.name}** (`{t.rule}`) in `{t.module}`: {t.behavior}")
    md.append("\n")

    if record.token_usage:
        tu = record.token_usage
        md.append("## 12. Gemini AI Token Usage Audit\n")
        md.append(f"- **Model:** {tu.model_name or 'N/A'}")
        md.append(f"- **Prompt Tokens:** {tu.prompt_tokens:,}")
        md.append(f"- **Candidate Output Tokens:** {tu.candidate_tokens:,}")
        md.append(f"- **Total Tokens Consumed:** {tu.total_tokens:,}")
        md.append(f"- **Tracking Accuracy:** {'Estimated Heuristic' if tu.estimated else 'Actual API Usage Metadata'}\n")

    md.append("## 13. Limitations & Disclaimers\n")
    for lim in record.limitations:
        md.append(f"- {lim}")
    md.append("\n---\n*Generated autonomously by OmniStrat.*")

    return "\n".join(md)


def generate_json_report(record: AnalysisRecord) -> Dict[str, Any]:
    """Serialize full analysis record to structured JSON format."""
    return {
        "analysis_id": record.id,
        "project_name": record.project_name,
        "created_at": record.created_at,
        "completed_at": record.completed_at,
        "ai_enabled": record.ai_enabled,
        "executive_summary": record.executive_summary,
        "findings": [f.model_dump() for f in record.findings],
        "business_rules": [r.model_dump() for r in record.rules],
        "dependency_modules": [m.model_dump() for m in record.modules],
        "dependency_edges": [e.model_dump(by_alias=True) for e in record.edges],
        "modernization_risks": [rk.model_dump() for rk in record.risks],
        "version_audit": [v.model_dump() for v in record.version_audit],
        "roadmap_phases": [p.model_dump() for p in record.phases],
        "regression_tests": [t.model_dump() for t in record.tests],
        "architecture_recommendations": record.architecture if isinstance(record.architecture, dict) else (record.architecture.model_dump() if hasattr(record.architecture, 'model_dump') else {}),
        "product_profile": record.product_profile.model_dump() if record.product_profile else {},
        "execution_pipelines": [p.model_dump() for p in record.pipelines],
        "metrics": [m.model_dump() for m in record.metrics],
        "token_usage": record.token_usage.model_dump() if record.token_usage else {},
        "limitations": record.limitations
    }
