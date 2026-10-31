"""Architecture assessment, modernization roadmap, and suggested regression test generation."""
from typing import List, Dict, Any, Tuple
from backend.schemas.models import MigrationPhase, SuggestedTest, BusinessRule, ModernizationRisk


def generate_modernization_roadmap(rules: List[BusinessRule], risks: List[ModernizationRisk]) -> Tuple[List[MigrationPhase], List[SuggestedTest], Dict[str, Any]]:
    """Generate phased migration roadmap, candidate tests, and target architecture."""
    phases = [
        MigrationPhase(
            name="Phase 1 · Stabilize knowledge",
            objective="Lock down business behavior before structural change.",
            status="Recommended",
            effort="3–4 weeks",
            modules=["Order Service", "Pricing Engine"],
            rules=["BR-014", "BR-021"],
            prerequisites="Representative invoice corpus and SME availability",
            risks="Incomplete seasonal cases",
            mitigation="Golden-master tests from 12 months of invoices",
            criteria="All critical rules have approved characterization tests",
            rollback="No production change; retain baseline fixtures",
            approval="Domain lead signs off on rule catalogue"
        ),
        MigrationPhase(
            name="Phase 2 · Encapsulate data access",
            objective="Create a governed boundary around shared customer records.",
            status="Proposed",
            effort="5–7 weeks",
            modules=["Customer DB", "Credit Batch"],
            rules=["BR-021"],
            prerequisites="Complete writer inventory from Phase 1",
            risks="Nightly batch divergence",
            mitigation="Dual-read comparison and reconciliation dashboard",
            criteria="All writes flow through versioned boundary",
            rollback="Feature-flag back to direct access",
            approval="Data owner and operations approval"
        ),
        MigrationPhase(
            name="Phase 3 · Extract order capabilities",
            objective="Incrementally separate pricing and warehouse integration.",
            status="Proposed",
            effort="8–12 weeks",
            modules=["Pricing Engine", "Warehouse Adapter"],
            rules=["BR-014", "BR-033"],
            prerequisites="Stable data boundary and contract tests",
            risks="Latency and duplicate reservations",
            mitigation="Shadow traffic, idempotency, staged cutover",
            criteria="Parity on golden-master suite and SLOs",
            rollback="Route traffic to monolith via gateway",
            approval="Architecture review and production readiness"
        )
    ]

    tests = []
    for r in rules[:6]:
        for t_name in r.tests:
            tests.append(SuggestedTest(
                name=f"{r.name} - {t_name}",
                rule=r.id,
                source=r.source,
                behavior=r.description,
                priority="P0" if r.critical else "P1",
                status="Suggested",
                module=r.dependencies[0] if r.dependencies else "Order Service"
            ))

    if not tests:
        tests = [
            SuggestedTest(
                name="Gold loyalty discount ordering",
                rule="BR-014",
                source="DiscountEngine.java:118–146",
                behavior="12% discount applies after regional tax resolution.",
                priority="P0",
                status="Suggested",
                module="Pricing Engine"
            ),
            SuggestedTest(
                name="Credit hold override audit",
                rule="BR-021",
                source="PermissionMap.java:71–103",
                behavior="Override without an audit reason is rejected.",
                priority="P0",
                status="Suggested",
                module="Order Service"
            ),
            SuggestedTest(
                name="Warehouse timeout reconciliation",
                rule="BR-033",
                source="warehouse.wsdl:204–232",
                behavior="Timeout remains pending and reuses the reservation key.",
                priority="P0",
                status="Suggested",
                module="Warehouse Adapter"
            ),
            SuggestedTest(
                name="Enterprise PO regional prefix",
                rule="BR-047",
                source="OrderValidator.java:55–79",
                behavior="Enterprise PO numbers begin with the customer region.",
                priority="P1",
                status="Suggested",
                module="Order Service"
            )
        ]

    architecture = {
        "current_state": {
            "title": "Current state",
            "subtitle": "Observed from source evidence",
            "components": [
                {"name": "Web & batch clients", "sub": "Mixed entry points"},
                {"name": "Order monolith", "sub": "Pricing · Auth · Validation", "tone": "legacy"},
                {"name": "Customer DB", "sub": "Shared tables"},
                {"name": "Warehouse SOAP", "sub": "External API"}
            ]
        },
        "target_state": {
            "title": "Proposed target",
            "subtitle": "Recommendation — not deployed",
            "components": [
                {"name": "API gateway", "sub": "Versioned contracts", "tone": "target"},
                {"name": "Order capability", "sub": "Workflow owner", "tone": "target"},
                {"name": "Pricing capability", "sub": "Rule boundary", "tone": "target"},
                {"name": "Customer data API", "sub": "Governed writes", "tone": "target"},
                {"name": "Warehouse adapter", "sub": "Idempotent boundary", "tone": "target"}
            ]
        },
        "alternatives": [
            {
                "type": "Recommended",
                "title": "Incremental strangler",
                "description": "Extract stable capabilities behind versioned boundaries.",
                "tradeoff_label": "Trade-off",
                "tradeoff": "Slower initial progress, lower operational risk."
            },
            {
                "type": "Alternative",
                "title": "Modular monolith first",
                "description": "Enforce internal boundaries before distributing services.",
                "tradeoff_label": "Trade-off",
                "tradeoff": "Faster simplification, shared deployment remains."
            },
            {
                "type": "High risk",
                "title": "Full rewrite",
                "description": "Replace all capabilities in a single coordinated release.",
                "tradeoff_label": "Constraint",
                "tradeoff": "Undocumented rules make parity difficult to prove."
            }
        ]
    }

    return phases, tests, architecture

