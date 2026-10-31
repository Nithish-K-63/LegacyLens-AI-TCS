"""Unit tests for OmniStrat features: evidence deduplication, dynamic heatmap, and repository tree evidence counting."""
import pytest
from backend.schemas.models import AnalysisFinding, BusinessRule, DependencyNode
from backend.services.deduplicator import deduplicate_findings, deduplicate_business_rules
from backend.services.risk_analyzer import assess_modernization_risks
from backend.services.product_analyzer import build_module_tree


def test_evidence_deduplication_exact_and_semantic():
    """Verify duplicates are merged into one canonical record with max confidence and highest severity."""
    findings = [
        AnalysisFinding(
            id="FIND-1",
            category="Security",
            severity="Medium",
            file="src/auth/token.js",
            lines="45-48",
            evidence="Dynamic code evaluation: eval(payload)",
            confidence=80,
            language="JavaScript",
            review="Unreviewed",
            classification="NEEDS_INVESTIGATION",
            impact="Dynamic code evaluation exposes application.",
            modules=["Auth Module"],
            recommendation="Replace eval with parser.",
            method="regex_conservative"
        ),
        # Near-duplicate with different diagnostic prefix, higher severity, and different review status
        AnalysisFinding(
            id="FIND-2",
            category="Security",
            severity="Critical",
            file="src/auth/token.js",
            lines="45-48",
            evidence="eval(payload) execution detected in source",
            confidence=95,
            language="JavaScript",
            review="Verified",
            classification="BUSINESS_CRITICAL",
            impact="Arbitrary code execution risk and impedes static dead-code tree shaking.",
            modules=["Security Perimeter"],
            recommendation="Replace dynamic eval with declarative dispatch.",
            method="ast"
        ),
        # Distinct finding in different file
        AnalysisFinding(
            id="FIND-3",
            category="Business Logic",
            severity="High",
            file="src/pricing/discount.js",
            lines="100-110",
            evidence="Tier discount calculation applied before tax",
            confidence=90,
            language="JavaScript",
            review="Unreviewed",
            classification="BUSINESS_CRITICAL",
            impact="Changes invoice calculations",
            modules=["Pricing Engine"],
            recommendation="Maintain calculation order",
            method="regex_conservative"
        )
    ]

    deduped = deduplicate_findings(findings)
    assert len(deduped) == 2, "Expected 2 findings after deduplicating the two eval findings"

    # Inspect merged canonical record
    auth_finding = next(f for f in deduped if "auth/token.js" in f.file)
    assert auth_finding.severity == "Critical", "Should retain highest severity"
    assert auth_finding.confidence == 95, "Should retain max confidence"
    assert auth_finding.review == "Verified", "Should retain strongest review status"
    assert auth_finding.classification == "BUSINESS_CRITICAL"
    assert "Auth Module" in auth_finding.modules and "Security Perimeter" in auth_finding.modules
    assert auth_finding.id.startswith("OMNI-")

    # Distinct finding must be preserved
    pricing_finding = next(f for f in deduped if "pricing/discount.js" in f.file)
    assert pricing_finding.category == "Business Logic"


def test_business_rules_deduplication():
    """Verify business rules are deduplicated by name and condition while merging dependencies."""
    rules = [
        BusinessRule(
            id="BR-1",
            name="Loyalty Tier Discount Calculation",
            category="Pricing",
            description="Short desc",
            source="src/order/discount.js:45",
            confidence=85,
            impact="Invoice variance",
            critical=True,
            dependencies=["TaxService"],
            conditions=["customer.tier == 'GOLD'"]
        ),
        BusinessRule(
            id="BR-2",
            name="Loyalty Tier Discount Calculation",
            category="Pricing",
            description="Longer more detailed rule description for customer tier",
            source="src/order/discount.js:45",
            confidence=95,
            impact="Invoice variance",
            critical=True,
            dependencies=["CustomerDB"],
            conditions=["customer.tier == 'GOLD'"]
        )
    ]

    deduped_rules = deduplicate_business_rules(rules)
    assert len(deduped_rules) == 1
    r = deduped_rules[0]
    assert r.confidence == 95
    assert "TaxService" in r.dependencies and "CustomerDB" in r.dependencies
    assert "Longer more detailed" in r.description


def test_dynamic_heatmap_structure_and_file_drilldown():
    """Verify modernization risks derive file breakdowns and priority dimensions dynamically."""
    modules = [
        DependencyNode(id="order", name="Order Service", type="Service", risk=80, incoming=3, outgoing=2, reason="Order core"),
        DependencyNode(id="pricing", name="Pricing Engine", type="Module", risk=40, incoming=1, outgoing=1, reason="Pricing logic")
    ]
    findings = [
        AnalysisFinding(
            id="OMNI-SEC-1001",
            category="Security",
            severity="Critical",
            file="src/order/Checkout.js",
            lines="12",
            evidence="Insecure direct eval",
            confidence=94,
            language="JavaScript",
            review="Needs Investigation",
            classification="BUSINESS_CRITICAL",
            impact="Code injection",
            modules=["Order Service"],
            recommendation="Remove eval",
            method="ast"
        ),
        AnalysisFinding(
            id="OMNI-OBS-1002",
            category="Obsolete Candidate",
            severity="Medium",
            file="src/order/LegacyHelper.js",
            lines="50",
            evidence="Uncalled utility",
            confidence=70,
            language="JavaScript",
            review="Unreviewed",
            classification="LIKELY_OBSOLETE",
            impact="Dead code",
            modules=["Order Service"],
            recommendation="Deprecate helper",
            method="ast"
        )
    ]
    inventory = [
        {"relative_path": "src/order/Checkout.js", "size_bytes": 4500, "language": "JavaScript"},
        {"relative_path": "src/order/LegacyHelper.js", "size_bytes": 1200, "language": "JavaScript"},
        {"relative_path": "src/pricing/Calculator.js", "size_bytes": 3100, "language": "JavaScript"}
    ]

    risks, matrix, layer_scores = assess_modernization_risks(modules, findings, file_inventory=inventory)
    assert len(risks) == 2
    order_risk = next(r for r in risks if r.name == "Order Service")
    assert order_risk.priority in ("Critical", "High")
    assert len(order_risk.files) >= 2
    # Verify file-level dimensions
    checkout_file = next(f for f in order_risk.files if "Checkout.js" in f.file_path)
    assert checkout_file.evidence_count == 1
    assert checkout_file.security_risk == "Critical"
    assert checkout_file.score >= 50
    # Verify dynamic matrix
    assert len(matrix) == 2
    assert len(matrix[0]) == 6


def test_repository_module_tree_evidence_counting():
    """Verify module tree nodes calculate evidence counts and folder size rollups."""
    inventory = [
        {"relative_path": "src/components/App.js", "size_bytes": 2048, "language": "JavaScript"},
        {"relative_path": "src/components/Header.js", "size_bytes": 1024, "language": "JavaScript"},
        {"relative_path": "src/utils/math.js", "size_bytes": 512, "language": "JavaScript"}
    ]
    findings = [
        AnalysisFinding(
            id="OMNI-1",
            category="Security",
            severity="High",
            file="src/components/App.js",
            lines="10",
            evidence="Insecure innerHTML",
            confidence=90,
            language="JavaScript",
            review="Unreviewed",
            classification="NEEDS_INVESTIGATION",
            impact="XSS",
            modules=["components"],
            recommendation="Escape input",
            method="ast"
        )
    ]

    tree = build_module_tree("", inventory, findings=findings)
    assert len(tree) > 0
    # Locate src/components folder
    src_node = next(n for n in tree if n["name"] == "src")
    assert src_node["evidence_count"] == 1
    assert src_node["size_bytes"] == 3584
