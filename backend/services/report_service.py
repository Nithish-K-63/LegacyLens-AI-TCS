"""Report generation service for JSON and Markdown downloads."""
import json
from typing import Dict, Any
from backend.schemas.models import AnalysisRecord


def generate_json_report(record: AnalysisRecord) -> str:
    """Format full analysis record as formatted JSON."""
    data = {
        "report_id": f"REP-{record.id}",
        "project_name": record.project_name,
        "analyzed_at": record.completed_at or record.created_at,
        "ai_enabled": record.ai_enabled,
        "product_profile": record.product_profile.model_dump() if record.product_profile else {},
        "discovered_pipelines": [p.model_dump() for p in record.pipelines],
        "token_usage": record.token_usage.model_dump() if record.token_usage else {},
        "metrics": [m.model_dump() for m in record.metrics],
        "executive_summary": record.executive_summary,
        "findings": [f.model_dump() for f in record.findings],
        "business_rules": [r.model_dump() for r in record.rules],
        "dependency_modules": [m.model_dump() for m in record.modules],
        "dependency_edges": [e.model_dump(by_alias=True) for e in record.edges],
        "modernization_risks": [r.model_dump() for r in record.risks],
        "database_dependencies": record.database_summary or {},
        "migration_phases": [p.model_dump() for p in record.phases],
        "suggested_tests": [t.model_dump() for t in record.tests],
        "target_architecture": record.architecture,
        "limitations": record.limitations
    }
    return json.dumps(data, indent=2)


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

    md.append("## 5. Discovered Business Rules\n")
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

    md.append("## 6. Modernization Risk Assessment\n")
    md.append("| Module | Risk Score | Severity | Criticality | Uncertainty | Action |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in record.risks:
        md.append(f"| {r.name} | {r.score}/100 | {r.severity} | {r.criticality} | {r.uncertainty} | {r.action} |")
    md.append("\n")

    md.append("## 7. Database Analysis & Shared Table Contention\n")
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

    md.append("## 8. Phased Migration Roadmap\n")
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

    md.append("## 9. Suggested Regression Tests\n")
    for t in record.tests:
        md.append(f"- **[{t.priority}] {t.name}** (`{t.rule}`) in `{t.module}`: {t.behavior}")
    md.append("\n")

    if record.token_usage:
        tu = record.token_usage
        md.append("## 10. Gemini AI Token Usage Audit\n")
        md.append(f"- **Model:** {tu.model_name or 'N/A'}")
        md.append(f"- **Prompt Tokens:** {tu.prompt_tokens:,}")
        md.append(f"- **Candidate Output Tokens:** {tu.candidate_tokens:,}")
        md.append(f"- **Total Tokens Consumed:** {tu.total_tokens:,}")
        md.append(f"- **Tracking Accuracy:** {'Estimated Heuristic' if tu.estimated else 'Actual API Usage Metadata'}\n")

    md.append("## 11. Limitations & Disclaimers\n")
    for lim in record.limitations:
        md.append(f"- {lim}")
    md.append("\n---\n*Generated autonomously by OmniStrat.*")

    return "\n".join(md)

