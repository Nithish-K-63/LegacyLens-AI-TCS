"""Evidence and business-rule deduplication engine.

Deduplicates static, architectural, AST, and AI findings using stable fingerprints
based on category, normalized source file path, line range, and semantic core.
Merges duplicates into a canonical record with highest confidence, strongest evidence,
and union of affected modules.
"""
import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from backend.schemas.models import AnalysisFinding, BusinessRule

SEVERITY_WEIGHT = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

CLASSIFICATION_WEIGHT = {
    "BUSINESS_CRITICAL": 4,
    "NEEDS_INVESTIGATION": 3,
    "LIKELY_OBSOLETE": 2,
    "SAFE_DEPRECATION": 1
}

REVIEW_WEIGHT = {
    "Verified": 3,
    "Needs Investigation": 2,
    "Unreviewed": 1
}

COMMON_STOPWORDS = {
    "code", "detected", "source", "pattern", "line", "lines",
    "check", "function", "module", "execution", "rule", "found",
    "site", "sites", "used", "using", "into", "from", "with"
}


def normalize_path(path: str) -> str:
    """Normalize file path for stable fingerprinting."""
    if not path:
        return ""
    p = path.strip().replace("\\", "/").lower()
    while p.startswith("./"):
        p = p[2:]
    return p


def normalize_lines(lines_str: str) -> str:
    """Normalize line representation (e.g. '15-18' or '15–18' or '15')."""
    if not lines_str:
        return "0"
    cleaned = re.sub(r'[\s–—]+', '-', str(lines_str).strip())
    parts = cleaned.split('-')
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}-{parts[1]}"
    if parts[0].isdigit():
        return parts[0]
    return cleaned


def are_findings_duplicate(f1: AnalysisFinding, f2: AnalysisFinding) -> bool:
    """Determine whether two findings are duplicate or semantically identical."""
    # 1. Must be in the exact same source file
    if normalize_path(f1.file) != normalize_path(f2.file):
        return False

    # 2. Must share compatible categories
    c1 = (f1.category or "General").strip().lower()
    c2 = (f2.category or "General").strip().lower()
    if c1 != c2:
        compat_pairs = [
            ("security", "security"),
            ("obsolete", "obsolete"),
            ("business", "business"),
            ("debt", "obsolete"),
            ("obsolete", "debt")
        ]
        if not any(p[0] in c1 and p[1] in c2 for p in compat_pairs):
            return False

    # 3. Check line location proximity
    l1 = normalize_lines(f1.lines)
    l2 = normalize_lines(f2.lines)
    s1 = int(l1.split("-")[0]) if l1.split("-")[0].isdigit() else 0
    s2 = int(l2.split("-")[0]) if l2.split("-")[0].isdigit() else 0

    # If both have line numbers, must be within 3 lines of each other
    if s1 > 0 and s2 > 0 and abs(s1 - s2) > 3 and l1 != l2:
        return False

    # 4. Check semantic token overlap
    tokens1 = set(re.findall(r'[a-zA-Z0-9_]{3,}', (f1.evidence or "").lower())) - COMMON_STOPWORDS
    tokens2 = set(re.findall(r'[a-zA-Z0-9_]{3,}', (f2.evidence or "").lower())) - COMMON_STOPWORDS

    if not tokens1 or not tokens2:
        return True

    # If they share any key identifier (eval, innerhtml, tax, override, etc.)
    overlap = tokens1 & tokens2
    if overlap:
        return True

    return False


def merge_two_findings(f1: AnalysisFinding, f2: AnalysisFinding) -> AnalysisFinding:
    """Merge duplicate findings into a single canonical record."""
    # Retain highest confidence
    canonical_confidence = max(f1.confidence or 0, f2.confidence or 0)

    # Retain highest severity
    w1 = SEVERITY_WEIGHT.get(f1.severity, 1)
    w2 = SEVERITY_WEIGHT.get(f2.severity, 1)
    canonical_severity = f1.severity if w1 >= w2 else f2.severity

    # Retain strongest review status
    rw1 = REVIEW_WEIGHT.get(f1.review, 1)
    rw2 = REVIEW_WEIGHT.get(f2.review, 1)
    canonical_review = f1.review if rw1 >= rw2 else f2.review

    # Retain highest classification
    cw1 = CLASSIFICATION_WEIGHT.get(f1.classification, 1)
    cw2 = CLASSIFICATION_WEIGHT.get(f2.classification, 1)
    canonical_classification = f1.classification if cw1 >= cw2 else f2.classification

    # Evidence: keep longer, more detailed description
    canonical_evidence = f1.evidence if len(f1.evidence or "") >= len(f2.evidence or "") else f2.evidence

    # Impact: keep longer, more comprehensive statement
    canonical_impact = f1.impact if len(f1.impact or "") >= len(f2.impact or "") else f2.impact

    # Recommendation: keep more actionable recommendation
    canonical_recommendation = (
        f1.recommendation if len(f1.recommendation or "") >= len(f2.recommendation or "") else f2.recommendation
    )

    # Union of modules
    merged_modules = list(dict.fromkeys((f1.modules or []) + (f2.modules or [])))

    # Use clearer line definition
    canonical_lines = f1.lines if len(str(f1.lines)) >= len(str(f2.lines)) else f2.lines

    return AnalysisFinding(
        id=f1.id,  # Preserve canonical ID
        category=f1.category,
        severity=canonical_severity,
        file=f1.file,
        lines=canonical_lines,
        evidence=canonical_evidence,
        confidence=canonical_confidence,
        language=f1.language or f2.language or "Unknown",
        review=canonical_review,
        classification=canonical_classification,
        impact=canonical_impact,
        modules=merged_modules,
        recommendation=canonical_recommendation,
        method=f1.method or f2.method or "static"
    )


def deduplicate_findings(findings: List[AnalysisFinding]) -> List[AnalysisFinding]:
    """Audit and deduplicate findings across static, AST, regex, and AI stages.
    
    Returns a clean list of canonical findings with unique IDs and merged metadata.
    """
    if not findings:
        return []

    canonical_list: List[AnalysisFinding] = []

    for f in findings:
        matched_idx = -1
        for idx, existing in enumerate(canonical_list):
            if are_findings_duplicate(f, existing):
                matched_idx = idx
                break

        if matched_idx >= 0:
            canonical_list[matched_idx] = merge_two_findings(canonical_list[matched_idx], f)
        else:
            canonical_list.append(f)

    # Renumber IDs sequentially to ensure 100% uniqueness without collisions
    category_counts: Dict[str, int] = {}
    final_findings: List[AnalysisFinding] = []
    for f in canonical_list:
        cat_key = (f.category or "GEN").upper()[:3]
        category_counts[cat_key] = category_counts.get(cat_key, 1000) + 1
        new_id = f"OMNI-{cat_key}-{category_counts[cat_key]}"
        f_copy = f.model_copy(update={"id": new_id})
        final_findings.append(f_copy)

    return final_findings


def deduplicate_business_rules(rules: List[BusinessRule]) -> List[BusinessRule]:
    """Deduplicate extracted business rules by normalized rule name, condition, and source."""
    if not rules:
        return []

    groups: Dict[str, List[BusinessRule]] = {}
    for r in rules:
        norm_name = re.sub(r'[^\w]', '', (r.name or "").lower())
        norm_source = normalize_path(r.source)
        fp = f"{norm_name}::{norm_source}"
        groups.setdefault(fp, []).append(r)

    deduped_rules: List[BusinessRule] = []
    rule_idx = 1001
    for fp, group in groups.items():
        canonical = group[0]
        # Merge subsequent duplicates
        for dup in group[1:]:
            # Max confidence
            canonical.confidence = max(canonical.confidence, dup.confidence)
            # Critical flag
            canonical.critical = canonical.critical or dup.critical
            # Union of dependencies
            canonical.dependencies = list(dict.fromkeys(canonical.dependencies + dup.dependencies))
            # Union of tests
            canonical.tests = list(dict.fromkeys(canonical.tests + dup.tests))
            # Union of db references
            canonical.db_references = list(dict.fromkeys(canonical.db_references + dup.db_references))
            # Union of conditions
            canonical.conditions = list(dict.fromkeys(canonical.conditions + dup.conditions))
            # Longest description
            if len(dup.description or "") > len(canonical.description or ""):
                canonical.description = dup.description

        # Reassign clean canonical ID
        canonical.id = f"RULE-{rule_idx}"
        rule_idx += 1
        deduped_rules.append(canonical)

    return deduped_rules
