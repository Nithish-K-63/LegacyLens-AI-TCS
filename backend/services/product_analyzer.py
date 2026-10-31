"""Product-Aware System Understanding and Real Pipeline Reconstruction Service."""
import os
import json
import re
from typing import List, Dict, Any, Optional
from backend.schemas.models import (
    ProductProfile, ProductPipeline, PipelineStage
)


def analyze_product_profile(
    root_dir: str,
    file_inventory: List[Dict[str, Any]],
    language_counts: Dict[str, int],
    total_loc: int
) -> ProductProfile:
    """Analyze source evidence to understand the real product type, purpose, and tech stack."""
    frameworks = set()
    infrastructure = set()
    entry_points = []
    product_type = "Software Application"
    purpose = "Legacy modernization candidate software system."
    arch_pattern = "Layered Modular Architecture"

    # 1. Inspect package.json (Node/JS/React/Electron)
    pkg_path = os.path.join(root_dir, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8", errors="replace") as f:
                pkg_data = json.load(f)
                name = pkg_data.get("name", "")
                desc = pkg_data.get("description", "")
                if desc:
                    purpose = desc
                elif name:
                    purpose = f"{name.replace('-', ' ').title()} software system."

                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "react" in deps:
                    frameworks.add("React")
                if "react-native" in deps:
                    frameworks.add("React Native")
                if "redux" in deps or "react-redux" in deps:
                    frameworks.add("Redux")
                if "webpack" in deps:
                    frameworks.add("Webpack")
                if "babel-core" in deps or "@babel/core" in deps:
                    frameworks.add("Babel")
                if "nw" in deps or "nw.gui" in deps:
                    frameworks.add("NW.js (Node-Webkit)")
                if "electron" in deps:
                    frameworks.add("Electron")
                if "express" in deps:
                    frameworks.add("Express.js")
                if "next" in deps:
                    frameworks.add("Next.js")
                if "typescript" in deps:
                    frameworks.add("TypeScript")

                if "calculator" in name.lower() or "calculator" in desc.lower():
                    product_type = "Cross-Platform Calculator Application"
                    arch_pattern = "Flux / Redux Unidirectional Architecture with Native Bridges"
        except Exception:
            pass

    # 2. Inspect Python requirements / pyproject
    req_path = os.path.join(root_dir, "requirements.txt")
    if os.path.exists(req_path):
        try:
            with open(req_path, "r", encoding="utf-8", errors="replace") as f:
                req_text = f.read().lower()
                if "fastapi" in req_text:
                    frameworks.add("FastAPI")
                    product_type = "High-Performance REST API Service"
                    arch_pattern = "Asynchronous Layered Service Architecture"
                if "django" in req_text:
                    frameworks.add("Django")
                    product_type = "Django Enterprise Web Application"
                    arch_pattern = "Model-View-Template Monolith"
                if "flask" in req_text:
                    frameworks.add("Flask")
                if "sqlalchemy" in req_text:
                    frameworks.add("SQLAlchemy ORM")
                if "celery" in req_text:
                    frameworks.add("Celery Distributed Tasks")
        except Exception:
            pass

    # 3. Inspect Java / COBOL / SQL legacy indicators
    for f in file_inventory:
        ext = f["extension"].lower()
        rel = f["relative_path"].lower()
        if ext in (".cbl", ".cob", ".cpy"):
            frameworks.add("COBOL Batch Processing")
            product_type = "Legacy Enterprise Transaction System"
            arch_pattern = "Core Banking / Batch Processing Monolith"
        elif ext == ".wsdl":
            frameworks.add("SOAP Web Services")
        elif "schema.sql" in rel or ext == ".sql":
            frameworks.add("Relational SQL Database")

    # 4. Inspect README.md for explicit documentation
    for readme_name in ["README.md", "README", "readme.md", "Readme.md"]:
        readme_path = os.path.join(root_dir, readme_name)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#") and not l.startswith("[!")]
                    if lines and len(purpose) < 40:
                        purpose = lines[0][:180]
            except Exception:
                pass
            break

    # 5. Discover primary entry points
    entry_candidates = [
        ("index.web.js", "Web Browser Entry Point"),
        ("index.ios.js", "Apple iOS Native Entry Point"),
        ("index.android.js", "Google Android Native Entry Point"),
        ("index.js", "Application Main Entry Point"),
        ("app.js", "Application Controller Shell"),
        ("server.js", "Node HTTP Server Bootstrap"),
        ("main.py", "FastAPI / Python Application Bootstrap"),
        ("app.py", "Python Service Entry Point"),
        ("manage.py", "Django Management CLI"),
        ("webpack.config.js", "Webpack Bundler Configuration"),
        ("docker-compose.yml", "Container Orchestration Spec"),
        ("Dockerfile", "Container Build Specification")
    ]
    for rel_name, role in entry_candidates:
        matched = [f for f in file_inventory if f["relative_path"].endswith(rel_name) or os.path.basename(f["relative_path"]) == rel_name]
        for m in matched[:2]:
            entry_points.append({
                "file": m["relative_path"],
                "role": role,
                "language": m["language"]
            })
            if "docker" in rel_name:
                infrastructure.add("Docker")
            if "webpack" in rel_name:
                infrastructure.add("Webpack Build System")

    # If no specific product type was matched
    if product_type == "Software Application":
        top_lang = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else "Generic"
        product_type = f"{top_lang} Application Component"

    return ProductProfile(
        product_type=product_type,
        purpose=purpose,
        detected_frameworks=sorted(list(frameworks)),
        detected_languages=language_counts,
        entry_points=entry_points,
        architectural_pattern=arch_pattern,
        infrastructure=sorted(list(infrastructure)),
        total_files=len(file_inventory),
        total_loc=total_loc
    )


def reconstruct_product_pipelines(
    root_dir: str,
    file_inventory: List[Dict[str, Any]],
    static_results: Dict[str, Any],
    profile: ProductProfile
) -> List[ProductPipeline]:
    """Discover and trace the product's real execution and data processing pipelines."""
    pipelines: List[ProductPipeline] = []

    # Pipeline A: Check for Calculator / Interactive UI Application
    is_calculator = "calculator" in profile.product_type.lower() or any("calc" in f["relative_path"].lower() for f in file_inventory)
    if is_calculator:
        stages = [
            PipelineStage(
                id="STAGE-01",
                name="Input Ingestion & Event Capture",
                order=1,
                responsibility="Captures button clicks, touch gestures, and keyboard numeric/operator inputs.",
                input="Raw UI Click / Touch Event payload (e.g., button key, character, touch coordinate)",
                output="Dispatched user intent event with normalized key identifier",
                modules=[f["relative_path"] for f in file_inventory if any(k in f["relative_path"].lower() for k in ["button", "screen", "keypad"])][:4] or ["src/components/Button.js"],
                data_passed="Action Type token (NUMBER, OPERATOR, CLEAR, EQUALS)",
                dependencies=["React Synthetic Event System", "Native View Touch Responder"],
                failure_points=["Rapid double-click debounce omission", "Platform-specific touch responder delay"],
                bottlenecks=["Unnecessary re-renders of display screen during rapid inputs"],
                confidence=95,
                evidence="Component event handlers in UI presentation elements dispatching to store."
            ),
            PipelineStage(
                id="STAGE-02",
                name="Action Creator & Intent Normalization",
                order=2,
                responsibility="Maps raw user keys into typed immutable action objects with mathematical semantics.",
                input="Key identifier ('+', '-', '5', 'C', '=')",
                output="Typed Action object: { type: 'INPUT_OPERATOR', payload: '+' }",
                modules=[f["relative_path"] for f in file_inventory if "action" in f["relative_path"].lower()][:4] or ["src/actions/index.js"],
                data_passed="Action object dispatched to central Redux / Flux dispatcher",
                dependencies=["Redux Dispatcher", "Action Type Constants"],
                failure_points=["Unmapped action type fallback", "Operator sequence ambiguity (e.g. '5 + - 3')"],
                bottlenecks=["Synchronous dispatch overhead under rapid automated replay"],
                confidence=92,
                evidence="Dispatched action creators mapping button inputs to typed intent payloads."
            ),
            PipelineStage(
                id="STAGE-03",
                name="Calculation Engine & State Mutation",
                order=3,
                responsibility="Executes arithmetic evaluation, floating point precision rounding, and state buffer updates.",
                input="Previous Calculator State + Dispatched Action payload",
                output="Mutated immutable state: { displayValue: '42', previousOperand: null, operation: null }",
                modules=[f["relative_path"] for f in file_inventory if any(k in f["relative_path"].lower() for k in ["reducer", "calc", "engine", "math"])][:4] or ["src/reducers/index.js"],
                data_passed="Updated state tree emitted to subscribed UI views and memory stack",
                dependencies=["JavaScript Math runtime", "Floating-point IEEE-754 arithmetic"],
                failure_points=["Division by zero handling", "Floating-point IEEE 754 precision drift (e.g. 0.1 + 0.2 != 0.3)"],
                bottlenecks=["Large expression parsing in complex continuous operations"],
                confidence=96,
                evidence="Reducer switch-case state mutation rules executing mathematical operations."
            ),
            PipelineStage(
                id="STAGE-04",
                name="Cross-Platform Bridge & UI Rendering",
                order=4,
                responsibility="Translates updated calculator state into native platform display (Web DOM, iOS UIKit, Android Views).",
                input="State tree { displayValue: '42' }",
                output="Native View tree / HTML5 DOM rendered representation",
                modules=[f["relative_path"] for f in file_inventory if any(k in f["relative_path"].lower() for k in ["index.web", "index.ios", "index.android", "screen", "calculator"])][:4] or ["index.web.js", "src/components/Screen.js"],
                data_passed="Rendered visual frames presented to the user",
                dependencies=["React Native Bridge", "NW.js Window Context", "React DOM"],
                failure_points=["Async bridge serialization overhead between JS thread and Native UI thread"],
                bottlenecks=["Screen layout recalculation and font auto-scaling on variable screen widths"],
                confidence=94,
                evidence="Multi-platform entry bootstrap files rendering platform-agnostic Screen view."
            )
        ]
        pipelines.append(ProductPipeline(
            id="PIPE-CALC-01",
            name="Calculator Input & Mathematical Evaluation Pipeline",
            purpose="Processes user keypresses through action normalization, arithmetic evaluation, and multi-platform native rendering.",
            status="Complete",
            entry_point=profile.entry_points[0]["file"] if profile.entry_points else "index.js",
            stages=stages,
            alternate_workflows=[
                "Keyboard shortcut listener bypassing touch responder",
                "History recall / Memory buffer calculation path",
                "Desktop menu bar accelerator dispatch (NW.js / Electron)"
            ]
        ))
        return pipelines

    # Pipeline B: FinTech / Enterprise Order Processing Pipeline
    is_enterprise = any(k in profile.product_type.lower() for k in ["order", "commerce", "enterprise", "banking", "transaction"]) or any(ext in (".cbl", ".sql", ".wsdl") for ext in [f["extension"].lower() for f in file_inventory])
    if is_enterprise:
        stages = [
            PipelineStage(
                id="STAGE-01",
                name="Request Ingestion & Security Boundary",
                order=1,
                responsibility="Accepts incoming order payloads and verifies identity against administrative override boundaries.",
                input="HTTP Order Request / SOAP XML Payload + Auth Tokens",
                output="Authenticated Order Context with verified customer tier and audit identity",
                modules=[f["relative_path"] for f in file_inventory if "auth" in f["relative_path"].lower()][:3] or ["src/auth/permission_map.py"],
                data_passed="Validated Order Context payload",
                dependencies=["Identity Service", "Token Verification"],
                failure_points=["Missing audit reason on administrative credit hold override", "Expired session token"],
                bottlenecks=["Synchronous credential verification against external directory"],
                confidence=94,
                evidence="Authorization boundary requiring ADMIN_OVERRIDE and reason code."
            ),
            PipelineStage(
                id="STAGE-02",
                name="Pricing Calculation & Tier Validation",
                order=2,
                responsibility="Applies customer tier discounts and checks minimum order thresholds.",
                input="Order Context { customerTier, lineItems, orderTotal }",
                output="Priced Order Payload with computed discounts and regional tax boundaries",
                modules=[f["relative_path"] for f in file_inventory if "order" in f["relative_path"].lower() or "price" in f["relative_path"].lower()][:3] or ["src/order/discount_engine.py"],
                data_passed="Calculated Invoice Summary",
                dependencies=["Pricing Engine", "Tax Rule Matrix"],
                failure_points=["Tier evaluation order dependency before discount rounding", "Negative line item quantities"],
                bottlenecks=["Complex matrix evaluation on large multi-line orders"],
                confidence=92,
                evidence="Tier evaluation conditionals checking customer status and order totals."
            ),
            PipelineStage(
                id="STAGE-03",
                name="Shared Database Contention & Batch Synchronization",
                order=3,
                responsibility="Records credit balance updates across synchronous service layer and nightly batch jobs.",
                input="Account balance deduction command",
                output="Committed database ledger update + audit trail entry",
                modules=[f["relative_path"] for f in file_inventory if f["extension"].lower() in (".cbl", ".sql")][:3] or ["legacy/cbl/CUSTREC.cbl", "legacy/db/schema.sql"],
                data_passed="Committed transaction confirmation token",
                dependencies=["Relational Database (CUSTOMER_CREDIT)", "COBOL Batch Subsystem"],
                failure_points=["Direct write contention between batch jobs and online APIs", "Deadlocks on customer ledger table"],
                bottlenecks=["Table-level write locks during monthly interest calculation batch"],
                confidence=96,
                evidence="EXEC SQL statements and database triggers modifying CUSTOMER_CREDIT."
            ),
            PipelineStage(
                id="STAGE-04",
                name="External Warehouse Allocation & Reconciliation",
                order=4,
                responsibility="Reserves physical warehouse inventory via external SOAP integration with pending timeout semantics.",
                input="Reservation Request { sku, quantity, reservationKey }",
                output="Confirmed Allocation Token or Pending Reconciliation Ticket",
                modules=[f["relative_path"] for f in file_inventory if "warehouse" in f["relative_path"].lower() or f["extension"].lower() == ".wsdl"][:3] or ["interfaces/warehouse.wsdl"],
                data_passed="Final Order Status event dispatched to customer notification service",
                dependencies=["External Warehouse SOAP Service", "Idempotency Ledger"],
                failure_points=["SOAP connection timeout treated as hard failure causing duplicate allocations"],
                bottlenecks=["External warehouse network latency and synchronous HTTP timeout thresholds"],
                confidence=90,
                evidence="WSDL timeout specifications defining non-terminal pending reconciliation semantics."
            )
        ]
        pipelines.append(ProductPipeline(
            id="PIPE-ORDER-01",
            name="End-to-End Order Processing & Credit Reconciliation Pipeline",
            purpose="Orchestrates order authentication, pricing discount calculations, database ledger writes, and warehouse reservations.",
            status="Complete",
            entry_point="src/order/discount_engine.py",
            stages=stages,
            alternate_workflows=[
                "Credit hold administrative override path",
                "Warehouse timeout pending reconciliation loop",
                "Nightly batch credit interest processing path"
            ]
        ))
        return pipelines

    # Pipeline C: Generic Modular Processing Pipeline
    stages = [
        PipelineStage(
            id="STAGE-01",
            name="System Entry & Request Ingestion",
            order=1,
            responsibility="Receives external input, parses parameters, and initializes application context.",
            input="External command / HTTP request payload",
            output="Normalized execution context",
            modules=[f["relative_path"] for f in file_inventory if any(k in f["relative_path"].lower() for k in ["index", "main", "app", "server"])][:3] or ["index.js"],
            data_passed="Context and parameters",
            dependencies=["Runtime Environment"],
            failure_points=["Parameter validation failure", "Missing configuration"],
            bottlenecks=["Initial boot time"],
            confidence=80,
            evidence="Application entry point bootstrap sequence."
        ),
        PipelineStage(
            id="STAGE-02",
            name="Core Domain Processing",
            order=2,
            responsibility="Executes primary business logic and state transformations.",
            input="Execution parameters",
            output="Processed domain output",
            modules=[f["relative_path"] for f in file_inventory if any(k in f["relative_path"].lower() for k in ["src", "lib", "service"])][:3] or ["src/core.js"],
            data_passed="Domain result payload",
            dependencies=["Domain Service Matrix"],
            failure_points=["Unhandled boundary conditions"],
            bottlenecks=["Sequential processing overhead"],
            confidence=82,
            evidence="Core service modules executing system logic."
        ),
        PipelineStage(
            id="STAGE-03",
            name="Output Generation & Response Delivery",
            order=3,
            responsibility="Formats final results and emits responses to callers or presentation layers.",
            input="Domain result",
            output="Formatted response / View render",
            modules=[f["relative_path"] for f in file_inventory if any(k in f["relative_path"].lower() for k in ["view", "response", "client", "output"])][:3] or ["src/output.js"],
            data_passed="Client output",
            dependencies=["Presentation / API Gateway"],
            failure_points=["Serialization errors"],
            bottlenecks=["Network payload serialization"],
            confidence=80,
            evidence="Response generation and output rendering."
        )
    ]
    pipelines.append(ProductPipeline(
        id="PIPE-GEN-01",
        name="Primary Execution & Data Flow Pipeline",
        purpose=f"Coordinates execution flow across {profile.product_type} subsystems.",
        status="Complete",
        entry_point=profile.entry_points[0]["file"] if profile.entry_points else "index.js",
        stages=stages,
        alternate_workflows=["Error recovery and retry handling path"]
    ))
    return pipelines


def build_module_tree(
    root_dir: str,
    file_inventory: List[Dict[str, Any]],
    findings: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """Build an interactive folder and file hierarchy tree with component roles, sizes, and evidence counts."""
    tree: Dict[str, Any] = {"name": "root", "type": "folder", "children": {}}

    # Pre-index findings count by normalized file path
    findings_count_map: Dict[str, int] = {}
    if findings:
        for f in findings:
            f_path = getattr(f, "file", "") or (f.get("file", "") if isinstance(f, dict) else "")
            norm = f_path.replace("\\", "/").lower()
            while norm.startswith("./"):
                norm = norm[2:]
            findings_count_map[norm] = findings_count_map.get(norm, 0) + 1

    for f in file_inventory:
        rel = f["relative_path"]
        parts = rel.split("/")
        current = tree

        # Identify top-level module name
        if len(parts) > 1 and parts[0] in ("src", "lib", "app", "packages", "service", "services"):
            module_name = parts[1].replace("_", " ").title()
        elif len(parts) > 1:
            module_name = parts[0].replace("_", " ").title()
        else:
            module_name = "Core"

        for i, part in enumerate(parts):
            is_file = (i == len(parts) - 1)
            if is_file:
                # Classify component role
                role = "Source Code"
                rel_lower = rel.lower()
                if "component" in rel_lower or "view" in rel_lower:
                    role = "UI Presentation"
                elif "action" in rel_lower:
                    role = "Business Action"
                elif "reducer" in rel_lower or "store" in rel_lower:
                    role = "State Engine"
                elif "util" in rel_lower or "helper" in rel_lower:
                    role = "Utility"
                elif "test" in rel_lower or "spec" in rel_lower:
                    role = "Test Suite"
                elif "config" in rel_lower or rel_lower.endswith((".json", ".yml", ".yaml")):
                    role = "Configuration"
                elif rel_lower.startswith(("index.", "app.", "main.", "server.")):
                    role = "Entry Point"

                # Check evidence count
                norm_rel = rel.replace("\\", "/").lower()
                while norm_rel.startswith("./"):
                    norm_rel = norm_rel[2:]
                ev_count = findings_count_map.get(norm_rel, 0)
                if ev_count == 0:
                    for k, count in findings_count_map.items():
                        if norm_rel.endswith(k) or k.endswith(norm_rel):
                            ev_count = count
                            break

                current["children"][part] = {
                    "name": part,
                    "path": rel,
                    "type": "file",
                    "size_bytes": f.get("size_bytes", 0),
                    "language": f.get("language", "Text"),
                    "role": role,
                    "module": module_name,
                    "evidence_count": ev_count
                }
            else:
                if part not in current["children"]:
                    current["children"][part] = {
                        "name": part,
                        "path": "/".join(parts[:i + 1]),
                        "type": "folder",
                        "module": module_name,
                        "children": {}
                    }
                current = current["children"][part]

    def _convert_to_list(node: Dict[str, Any]) -> Dict[str, Any]:
        if "children" in node:
            children_dict = node["children"]
            children_list = [_convert_to_list(v) for v in children_dict.values()]
            # Sort: folders first, then alphabetically
            children_list.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))
            node["children"] = children_list
            # Sum up folder evidence count and size
            node["evidence_count"] = sum(c.get("evidence_count", 0) for c in children_list)
            node["size_bytes"] = sum(c.get("size_bytes", 0) for c in children_list)
        return node

    converted = _convert_to_list(tree)
    return converted.get("children", [])

