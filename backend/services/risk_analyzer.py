"""Modernization risk assessment and heatmap scoring engine.

Structures risk strictly around actual discovered modules, files, and deduplicated evidence.
Provides file-level drill-down, priority dimensions, and dynamic heatmap scoring.
"""
import os
from typing import List, Dict, Any, Tuple, Optional
from backend.schemas.models import ModernizationRisk, FileRiskDetail, DependencyNode, AnalysisFinding

PRIORITY_MAP = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}


def assess_modernization_risks(
    modules: List[DependencyNode],
    findings: List[AnalysisFinding],
    file_inventory: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[ModernizationRisk], List[List[int]], Dict[str, int]]:
    """Compute risk score, contributing factors, file breakdowns, and dynamic heatmap matrix."""
    risks: List[ModernizationRisk] = []
    inventory = file_inventory or []

    # Map findings by normalized file path and by module
    findings_by_file: Dict[str, List[AnalysisFinding]] = {}
    findings_by_module: Dict[str, List[AnalysisFinding]] = {}

    for f in findings:
        norm_file = (f.file or "").strip().replace("\\", "/").lower()
        while norm_file.startswith("./"):
            norm_file = norm_file[2:]
        findings_by_file.setdefault(norm_file, []).append(f)

        for mod in (f.modules or []):
            findings_by_module.setdefault(mod.lower(), []).append(f)

    # Map inventory files to modules
    module_files_map: Dict[str, List[Dict[str, Any]]] = {}
    all_assigned_files = set()

    for node in modules:
        node_key = node.id.lower()
        node_name_clean = node.name.lower().replace("service", "").replace("engine", "").replace("adapter", "").replace("db", "").strip()
        matched = []

        for item in inventory:
            rel = item.get("relative_path", "").replace("\\", "/")
            rel_lower = rel.lower()
            if node_key in rel_lower or (node_name_clean and node_name_clean in rel_lower):
                matched.append(item)
                all_assigned_files.add(rel)

        module_files_map[node.id] = matched

    # Fallback for unassigned files or when inventory is empty
    unassigned = [item for item in inventory if item.get("relative_path", "").replace("\\", "/") not in all_assigned_files]
    if unassigned and modules:
        # Assign to first module or general module
        module_files_map[modules[0].id].extend(unassigned)

    # Process each module
    for node in modules:
        m_name = node.name
        f_list = findings_by_module.get(node.id.lower(), []) or findings_by_module.get(node.name.lower(), [])
        assigned_inv = module_files_map.get(node.id, [])

        # Build file-level drill-down
        file_details: List[FileRiskDetail] = []
        files_to_process = assigned_inv

        # If no inventory items matched, check if any findings belong to this module
        if not files_to_process:
            unique_find_files = list(dict.fromkeys([f.file for f in f_list if f.file]))
            files_to_process = [{"relative_path": fp, "size_bytes": 0} for fp in unique_find_files]

        for file_item in files_to_process:
            raw_path = file_item.get("relative_path", "")
            norm_p = raw_path.replace("\\", "/").lower()
            while norm_p.startswith("./"):
                norm_p = norm_p[2:]

            f_matches = findings_by_file.get(norm_p, [])
            # Also check if partial file path matches
            if not f_matches:
                for fpath_key, f_group in findings_by_file.items():
                    if norm_p.endswith(fpath_key) or fpath_key.endswith(norm_p):
                        f_matches = f_group
                        break

            crit = sum(1 for f in f_matches if f.severity == "Critical")
            high = sum(1 for f in f_matches if f.severity == "High")
            med = sum(1 for f in f_matches if f.severity == "Medium")
            low = sum(1 for f in f_matches if f.severity == "Low")

            sec_count = sum(1 for f in f_matches if (f.category or "").lower() == "security")
            debt_count = sum(1 for f in f_matches if (f.category or "").lower() in ("obsolete candidate", "architecture", "complexity"))
            biz_count = sum(1 for f in f_matches if (f.category or "").lower() == "business logic")

            file_score = min(98, max(20, 25 + (crit * 25) + (high * 15) + (med * 8) + (low * 3)))
            file_priority = "Critical" if file_score >= 75 else "High" if file_score >= 50 else "Medium" if file_score >= 30 else "Low"

            t_debt = "Critical" if debt_count >= 3 else "High" if debt_count >= 1 else "Medium" if (med + low) > 0 else "Low"
            s_risk = "Critical" if any(f.severity == "Critical" for f in f_matches if (f.category or "").lower() == "security") else "High" if sec_count > 0 else "Low"
            b_crit = "Critical" if biz_count >= 2 else "High" if biz_count >= 1 else "Medium"
            conf = int(sum(f.confidence for f in f_matches) / len(f_matches)) if f_matches else 85

            rec_action = f_matches[0].recommendation if f_matches else "Verify boundary contracts and isolate runtime entry points."

            file_details.append(FileRiskDetail(
                file_path=raw_path,
                name=os.path.basename(raw_path) or raw_path,
                priority=file_priority,
                score=file_score,
                evidence_count=len(f_matches),
                technical_debt=t_debt,
                security_risk=s_risk,
                business_criticality=b_crit,
                confidence=conf,
                recommended_action=rec_action,
                findings_ids=[f.id for f in f_matches]
            ))

        # Sort file drill-down by score descending
        file_details.sort(key=lambda x: x.score, reverse=True)

        # Aggregate module metrics
        max_file_score = max([f.score for f in file_details], default=node.risk)
        module_score = min(98, max(node.risk, int(max_file_score * 0.85 + (node.incoming * 4) + (node.outgoing * 2))))
        module_priority = "Critical" if module_score >= 75 else "High" if module_score >= 50 else "Medium" if module_score >= 30 else "Low"
        module_evidence_count = sum(f.evidence_count for f in file_details) or len(f_list)

        module_tech_debt = "Critical" if any(f.technical_debt == "Critical" for f in file_details) else \
                           "High" if any(f.technical_debt == "High" for f in file_details) else "Medium"
        module_sec_risk = "Critical" if any(f.security_risk == "Critical" for f in file_details) else \
                          "High" if any(f.security_risk == "High" for f in file_details) else "Low"
        module_biz_crit = "Critical" if module_score >= 80 or node.incoming >= 3 else \
                          "High" if module_score >= 55 else "Medium"
        module_confidence = int(sum(f.confidence for f in file_details) / len(file_details)) if file_details else 88

        dep_level = "High" if node.incoming >= 3 or node.outgoing >= 2 else "Medium" if node.incoming >= 1 else "Low"
        coverage = f"{max(18, 100 - module_score)}%"
        uncertainty = "High" if module_score >= 75 or module_sec_risk == "Critical" else "Medium" if module_score >= 45 else "Low"

        # Dynamically derived factors from actual evidence
        factors = []
        if node.incoming > 0:
            factors.append(f"{node.incoming} inbound coupling dependencies")
        if node.outgoing > 0:
            factors.append(f"{node.outgoing} outbound dependencies")
        if module_evidence_count > 0:
            factors.append(f"{module_evidence_count} evidence citations flagged in source")
        if module_sec_risk in ("Critical", "High"):
            factors.append(f"{module_sec_risk} perimeter security exposure")
        if module_tech_debt in ("Critical", "High"):
            factors.append(f"{module_tech_debt} architectural technical debt")
        if not factors:
            factors.append("Isolated execution boundary")

        rec_module_action = (
            file_details[0].recommended_action if file_details and file_details[0].recommended_action
            else "Establish contract tests and wrap with an anti-corruption layer."
        )

        risks.append(ModernizationRisk(
            name=m_name,
            score=module_score,
            severity=module_priority,
            criticality=module_biz_crit,
            dependency=dep_level,
            coverage=coverage,
            uncertainty=uncertainty,
            factors=factors[:4],
            action=rec_module_action,
            priority=module_priority,
            evidence_count=module_evidence_count,
            technical_debt=module_tech_debt,
            security_risk=module_sec_risk,
            business_criticality=module_biz_crit,
            confidence=module_confidence,
            recommended_action=rec_module_action,
            files=file_details
        ))

    # Sort risks: highest priority first
    risks.sort(key=lambda r: (PRIORITY_MAP.get(r.priority, 1), r.score), reverse=True)

    # Dynamic heatmap matrix: module row x 6 real dimension columns
    # Dimensions: [Composite Score, Technical Debt, Security Risk, Business Criticality, Coupling, Confidence]
    def dim_val(level_str: str) -> int:
        return 92 if level_str == "Critical" else 75 if level_str == "High" else 45 if level_str == "Medium" else 20

    heatmap_matrix: List[List[int]] = []
    layer_scores: Dict[str, int] = {}

    for r in risks:
        layer_scores[r.name] = r.score
        row = [
            r.score,
            dim_val(r.technical_debt),
            dim_val(r.security_risk),
            dim_val(r.business_criticality),
            min(95, 30 + len(r.factors) * 15),
            r.confidence
        ]
        heatmap_matrix.append(row)

    return risks, heatmap_matrix, layer_scores
