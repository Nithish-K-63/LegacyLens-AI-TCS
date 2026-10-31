"""OmniStrat - FastAPI Application Entry Point."""
import os
import re
import json
import uuid
import datetime
import tempfile
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

# Load local environment variables from root or backend .env if present
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_root_dir, ".env"))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
load_dotenv()

from backend.schemas.models import (
    HealthResponse, RepositoryAnalysisRequest, AnalysisStatusResponse,
    GraphResponse, HeatmapResponse, AnalysisRecord, MetricCard,
    GeminiConfigRequest, GeminiTestResponse, GeminiSettingsResponse,
    DatabaseAnalysisResponse, AnalysisFinding
)
from backend.services.security import (
    validate_github_url, sanitize_analysis_id, MAX_UPLOAD_SIZE_BYTES
)
from backend.services.ingestion import (
    clone_github_repository, ingest_zip_archive, scan_file_inventory, cleanup_directory
)
from backend.services.static_analyzer import analyze_codebase
from backend.services.dependency_analyzer import build_dependency_graph, _default_topology
from backend.services.database_analyzer import analyze_database_interactions
from backend.services.business_rules import extract_business_rules, _default_business_rules
from backend.services.risk_analyzer import assess_modernization_risks
from backend.services.architecture import generate_modernization_roadmap
from backend.services.gemini_service import gemini_service, SUPPORTED_MODELS
from backend.services.report_service import generate_json_report, generate_markdown_report
from backend.services.product_analyzer import (
    analyze_product_profile, reconstruct_product_pipelines, build_module_tree
)
from backend.services.token_tracker import TokenTracker
from backend.services.deduplicator import deduplicate_findings, deduplicate_business_rules

app = FastAPI(
    title="OmniStrat API",
    description="Autonomous Legacy Modernization Agent Backend",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for analyses (Hackathon-ready simple persistence)
ANALYSES_DB: Dict[str, AnalysisRecord] = {}


def _create_demo_record() -> AnalysisRecord:
    """Pre-load the Northstar Commerce synthetic demo record matching Figma."""
    nodes, edges = _default_topology()
    rules = _default_business_rules()
    demo_findings = [
        AnalysisFinding(
            id="OMNI-BIZ-1001",
            category="Business Logic",
            severity="Critical",
            file="src/order/DiscountEngine.java",
            lines="118–146",
            evidence="Loyalty discount is applied after regional tax calculation.",
            confidence=96,
            language="Java",
            review="Unreviewed",
            classification="BUSINESS_CRITICAL",
            impact="Changing operation order may alter invoice totals for loyalty customers.",
            modules=["Order Service", "Pricing Engine"],
            recommendation="Preserve operation order and verify with historical invoices.",
            method="regex_conservative"
        ),
        AnalysisFinding(
            id="OMNI-DAT-1002",
            category="Data Access",
            severity="High",
            file="legacy/db/CUSTREC.cbl",
            lines="442–501",
            evidence="Direct writes to CUSTOMER_CREDIT bypass the service layer.",
            confidence=89,
            language="COBOL",
            review="Needs Investigation",
            classification="NEEDS_INVESTIGATION",
            impact="Credit limits may diverge across systems during migration.",
            modules=["Credit Batch", "Customer DB"],
            recommendation="Trace nightly job consumers before introducing an API boundary.",
            method="regex_conservative"
        ),
        AnalysisFinding(
            id="OMNI-OBS-1003",
            category="Obsolete Candidate",
            severity="Medium",
            file="src/util/LegacyDateUtil.java",
            lines="12–94",
            evidence="No static call sites found; reflection usage could not be excluded.",
            confidence=62,
            language="Java",
            review="Needs Investigation",
            classification="LIKELY_OBSOLETE",
            impact="Removal could break dynamically loaded month-end reports.",
            modules=["Reporting"],
            recommendation="Instrument runtime use for one reporting cycle before removal.",
            method="ast"
        ),
        AnalysisFinding(
            id="OMNI-SEC-1004",
            category="Security",
            severity="High",
            file="src/auth/PermissionMap.java",
            lines="71–103",
            evidence="ADMIN_OVERRIDE grants approval above configured order limit.",
            confidence=92,
            language="Java",
            review="Verified",
            classification="BUSINESS_CRITICAL",
            impact="Required exception path for regulated manual approvals.",
            modules=["Authorization", "Order Service"],
            recommendation="Model as an explicit policy with immutable audit logging.",
            method="regex_conservative"
        ),
        AnalysisFinding(
            id="OMNI-INT-1005",
            category="Integration",
            severity="Medium",
            file="interfaces/warehouse.wsdl",
            lines="204–232",
            evidence="Warehouse reservation timeout is interpreted as pending.",
            confidence=84,
            language="XML",
            review="Unreviewed",
            classification="BUSINESS_CRITICAL",
            impact="Treating timeout as failure can cause duplicate reservations.",
            modules=["Warehouse Adapter"],
            recommendation="Preserve idempotency key and pending reconciliation behavior.",
            method="regex_conservative"
        )
    ]
    risks, matrix, layer_scores = assess_modernization_risks(nodes, demo_findings)
    phases, tests, arch = generate_modernization_roadmap(rules, risks)

    return AnalysisRecord(
        id="demo",
        project_name="Northstar Commerce",
        status="completed",
        progress=100,
        stage="completed",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ai_enabled=gemini_service.is_configured(),
        repo_url="https://github.com/demo/northstar-legacy",
        metrics=[
            MetricCard(label="Files analyzed", value="1,284", delta="COBOL, Java, SQL"),
            MetricCard(label="Modules discovered", value="86", delta="12 tightly coupled"),
            MetricCard(label="Dependencies", value="312", delta="47 inferred"),
            MetricCard(label="Business rules", value="64", delta="18 undocumented"),
            MetricCard(label="High-risk findings", value="9", delta="3 need review")
        ],
        findings=demo_findings,
        rules=rules,
        modules=nodes,
        edges=edges,
        risks=risks,
        phases=phases,
        tests=tests,
        architecture=arch,
        database_summary={
            "tables": {
                "CUSTOMER_CREDIT": {"writers": ["legacy/db/CUSTREC.cbl", "src/order/DiscountEngine.java"], "readers": ["src/order/OrderService.java"]},
                "ORDERS": {"writers": ["src/order/OrderService.java"], "readers": ["src/reporting/ReportEngine.java"]},
                "AUDIT_TRAIL": {"writers": ["src/auth/PermissionMap.java"], "readers": ["src/security/Compliance.java"]}
            },
            "shared_tables": [
                {
                    "table": "CUSTOMER_CREDIT",
                    "writers_count": 2,
                    "readers_count": 1,
                    "writers": ["legacy/db/CUSTREC.cbl", "src/order/DiscountEngine.java"],
                    "risk": "High direct-write contention across independent modules"
                }
            ],
            "stored_procedures": ["PROCESS_MONTHLY_INTEREST"],
            "total_tables": 3
        },
        product_profile={
            "product_type": "Enterprise Order Processing & Billing System",
            "purpose": "Processes commercial order lifecycles, customer credit scoring, pricing tiers, and warehouse inventory.",
            "detected_frameworks": ["Java EE", "COBOL Batch", "SOAP WSDL", "SQL Relational DB"],
            "detected_languages": {"Java": 42, "COBOL": 18, "SQL": 12, "XML": 8},
            "entry_points": [
                {"file": "src/order/DiscountEngine.java", "role": "Pricing & Discount Engine", "language": "Java"},
                {"file": "legacy/cbl/CUSTREC.cbl", "role": "Nightly Credit Batch Processor", "language": "COBOL"},
                {"file": "interfaces/warehouse.wsdl", "role": "External Warehouse SOAP Interface", "language": "XML"}
            ],
            "architectural_pattern": "Layered Core Banking & Commerce Monolith",
            "infrastructure": ["Relational DB Schema", "Batch JCL Scripts"],
            "total_files": 86,
            "total_loc": 28400
        },
        pipelines=[
            {
                "id": "PIPE-DEMO-01",
                "name": "Order Intake & Credit Ledger Reconciliation Pipeline",
                "purpose": "End-to-end execution path from customer order creation to credit deduction and warehouse allocation.",
                "status": "Complete",
                "entry_point": "src/order/DiscountEngine.java",
                "stages": [
                    {
                        "id": "STAGE-01",
                        "name": "Request Validation & Policy Override",
                        "order": 1,
                        "responsibility": "Validates order limits and enforces mandatory audit reasons for credit hold exceptions.",
                        "input": "Order Payload + User Security Token",
                        "output": "Authorized Order Context",
                        "modules": ["src/auth/PermissionMap.java"],
                        "data_passed": "Validated Customer Identity & Order Limits",
                        "dependencies": ["Identity Provider", "Audit Trail"],
                        "failure_points": ["Missing audit justification on administrative override"],
                        "bottlenecks": ["Synchronous authorization verification"],
                        "confidence": 94,
                        "evidence": "ADMIN_OVERRIDE security check at lines 71-103."
                    },
                    {
                        "id": "STAGE-02",
                        "name": "Pricing Calculation & Tax Resolution",
                        "order": 2,
                        "responsibility": "Evaluates customer loyalty tier (Gold/Silver) and applies discounts after tax region resolution.",
                        "input": "Authorized Order Context",
                        "output": "Priced Order Summary",
                        "modules": ["src/order/DiscountEngine.java"],
                        "data_passed": "Line item totals and calculated discounts",
                        "dependencies": ["Tax Calculation Service"],
                        "failure_points": ["Operation ordering dependency altering invoice totals"],
                        "bottlenecks": ["Complex conditional branching on large orders"],
                        "confidence": 96,
                        "evidence": "DiscountEngine tier calculations at lines 118-146."
                    },
                    {
                        "id": "STAGE-03",
                        "name": "Shared Ledger Update & Batch Synchronization",
                        "order": 3,
                        "responsibility": "Synchronizes customer credit balance across online API service and nightly batch runs.",
                        "input": "Priced Order Total",
                        "output": "Updated Credit Ledger + Transaction ID",
                        "modules": ["legacy/db/CUSTREC.cbl", "legacy/db/schema.sql"],
                        "data_passed": "Committed Transaction Token",
                        "dependencies": ["CUSTOMER_CREDIT database table"],
                        "failure_points": ["Direct write contention between batch and service layers"],
                        "bottlenecks": ["Table locks during monthly interest calculation batch"],
                        "confidence": 92,
                        "evidence": "EXEC SQL direct write statements in CUSTREC.cbl."
                    },
                    {
                        "id": "STAGE-04",
                        "name": "Warehouse Allocation & Timeout Reconciliation",
                        "order": 4,
                        "responsibility": "Reserves warehouse inventory via SOAP interface with non-terminal timeout handling.",
                        "input": "Confirmed Transaction Token + SKU List",
                        "output": "Warehouse Allocation or Pending Ticket",
                        "modules": ["interfaces/warehouse.wsdl"],
                        "data_passed": "Order Completion Response",
                        "dependencies": ["External Warehouse Adapter"],
                        "failure_points": ["Warehouse timeout treated as hard failure causing duplicate orders"],
                        "bottlenecks": ["External SOAP latency"],
                        "confidence": 88,
                        "evidence": "WSDL timeout configuration at lines 204-232."
                    }
                ],
                "alternate_workflows": [
                    "Manual administrative override workflow",
                    "Warehouse timeout asynchronous reconciliation loop"
                ]
            }
        ],
        module_tree=[
            {"name": "src", "path": "src", "type": "folder", "children": [
                {"name": "order", "path": "src/order", "type": "folder", "children": [
                    {"name": "DiscountEngine.java", "path": "src/order/DiscountEngine.java", "type": "file", "size_bytes": 14200, "language": "Java", "role": "Business Logic"}
                ]},
                {"name": "auth", "path": "src/auth", "type": "folder", "children": [
                    {"name": "PermissionMap.java", "path": "src/auth/PermissionMap.java", "type": "file", "size_bytes": 8400, "language": "Java", "role": "Security Boundary"}
                ]}
            ]},
            {"name": "legacy", "path": "legacy", "type": "folder", "children": [
                {"name": "cbl", "path": "legacy/cbl", "type": "folder", "children": [
                    {"name": "CUSTREC.cbl", "path": "legacy/cbl/CUSTREC.cbl", "type": "file", "size_bytes": 22100, "language": "COBOL", "role": "Batch Processor"}
                ]},
                {"name": "db", "path": "legacy/db", "type": "folder", "children": [
                    {"name": "schema.sql", "path": "legacy/db/schema.sql", "type": "file", "size_bytes": 4800, "language": "SQL", "role": "Database Schema"}
                ]}
            ]},
            {"name": "interfaces", "path": "interfaces", "type": "folder", "children": [
                {"name": "warehouse.wsdl", "path": "interfaces/warehouse.wsdl", "type": "file", "size_bytes": 11300, "language": "WSDL", "role": "External Integration"}
            ]}
        ],
        token_usage={
            "prompt_tokens": 1420,
            "candidate_tokens": 580,
            "total_tokens": 2000,
            "model_name": "gemini-2.5-flash",
            "stage_breakdown": {
                "executive_summary": {"prompt_tokens": 820, "candidate_tokens": 340, "total_tokens": 1160, "model": "gemini-2.5-flash", "is_estimate": False},
                "business_rules": {"prompt_tokens": 600, "candidate_tokens": 240, "total_tokens": 840, "model": "gemini-2.5-flash", "is_estimate": False}
            },
            "estimated": False
        },
        executive_summary="Northstar Commerce is a tightly coupled order-processing system with valuable, partially undocumented behavior spanning pricing, credit approval, and warehouse reservation.",
        limitations=[
            "Static analysis discovers structure and patterns without code execution.",
            "Dynamic behavior (reflection, runtime plugins, environment routing) requires human verification.",
            "Effort estimates and risk scores are prioritization aids, not commitments.",
            "Suggested regression tests must be executed in a dedicated staging environment."
        ]
    )

# Seed with demo
ANALYSES_DB["demo"] = _create_demo_record()


@app.get("/api/health", response_model=HealthResponse)
def get_health():
    """Health check endpoint showing backend state and Gemini integration."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        gemini_configured=gemini_service.is_configured(),
        model=gemini_service.model_name,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


def _execute_analysis_pipeline(analysis_id: str, working_dir: str, project_name: str, repo_url: Optional[str] = None):
    """Background task executing the end-to-end static & architectural analysis."""
    record = ANALYSES_DB[analysis_id]
    token_tracker = TokenTracker(analysis_id, model_name=gemini_service.model_name)
    try:
        # Step 1: Inventory & Root Identification
        record.stage = "inventory"
        record.progress = 15
        inventory = scan_file_inventory(working_dir)

        # Step 2: Static Analysis & Deduplication
        record.stage = "dependencies"
        record.progress = 35
        static_res = analyze_codebase(working_dir, inventory)
        # Deduplicate static findings
        raw_findings = static_res.get("findings", [])
        deduped_findings = deduplicate_findings(raw_findings)
        static_res["findings"] = deduped_findings

        # Step 3: Technology & Product Understanding
        record.stage = "product_understanding"
        record.progress = 50
        profile = analyze_product_profile(
            working_dir,
            inventory,
            static_res["language_distribution"],
            static_res["total_loc"]
        )

        # Step 4: Real Pipeline Reconstruction & Module Tree
        record.stage = "pipeline_reconstruction"
        record.progress = 65
        pipelines = reconstruct_product_pipelines(
            working_dir, inventory, static_res, profile
        )
        module_tree = build_module_tree(working_dir, inventory, findings=deduped_findings)

        # Step 5: Dependencies & Database Contention
        record.stage = "business_rules"
        record.progress = 75
        nodes, edges = build_dependency_graph(inventory, static_res)
        db_res = analyze_database_interactions(inventory, deduped_findings)

        # Step 6: Business Rules Extraction & Modernization Risks
        record.stage = "risk_assessment"
        record.progress = 85
        raw_rules = extract_business_rules(inventory, static_res)
        rules = deduplicate_business_rules(raw_rules)
        risks, matrix, layer_scores = assess_modernization_risks(nodes, deduped_findings, file_inventory=inventory)
        phases, tests, arch = generate_modernization_roadmap(rules, risks)

        # Step 7: Report & AI Summary with Token Tracking
        record.stage = "report_generation"
        record.progress = 95
        
        # Calculate metric cards
        total_files = static_res["total_files"] or len(inventory)
        total_modules = len(nodes)
        total_rules = len(rules)
        high_risk_count = sum(1 for f in deduped_findings if f.severity in ("Critical", "High"))
        
        metrics = [
            MetricCard(label="Files analyzed", value=f"{total_files:,}", delta=static_res["top_languages"]),
            MetricCard(label="Modules discovered", value=str(total_modules), delta=f"{sum(1 for n in nodes if n.risk >= 70)} high risk"),
            MetricCard(label="Dependencies", value=str(len(edges)), delta=f"{sum(1 for e in edges if e.inferred)} inferred"),
            MetricCard(label="Business rules", value=str(total_rules), delta=f"{sum(1 for r in rules if r.critical)} critical"),
            MetricCard(label="High-risk findings", value=str(high_risk_count), delta=f"{sum(1 for f in deduped_findings if f.review == 'Needs Investigation')} need review")
        ]

        # Generate AI summary and capture real token metadata
        exec_summary = gemini_service.generate_executive_summary(
            project_name=project_name,
            metrics=[m.model_dump() for m in metrics],
            findings=deduped_findings,
            rules=rules,
            token_tracker=token_tracker
        )

        # Update completed record
        record.metrics = metrics
        record.findings = deduped_findings
        record.rules = rules
        record.modules = nodes
        record.edges = edges
        record.risks = risks
        record.phases = phases
        record.tests = tests
        record.architecture = arch
        record.database_summary = db_res
        record.product_profile = profile
        record.pipelines = pipelines
        record.module_tree = module_tree
        record.token_usage = token_tracker.to_schema()
        record.executive_summary = exec_summary
        record.ai_enabled = gemini_service.is_configured()
        record.limitations = [
            "Source analyzed without code execution using AST and conservative parsing.",
            "Dynamic calls and reflection require runtime confirmation.",
            "Effort estimates are heuristic planning projections.",
            "AI recommendations require human architectural sign-off."
        ]
        record.progress = 100
        record.stage = "completed"
        record.status = "completed"
        record.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    except Exception as e:
        record.status = "failed"
        record.stage = "failed"
        record.error = f"Analysis pipeline error: {str(e)}"
    finally:
        # Secure cleanup of temporary workspace
        cleanup_directory(working_dir)


@app.post("/api/analyze/repository")
def analyze_repository(req: RepositoryAnalysisRequest, background_tasks: BackgroundTasks):
    """Initiate analysis of a public GitHub repository."""
    is_valid, repo_url_or_err = validate_github_url(req.repo_url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=repo_url_or_err)

    repo_url = repo_url_or_err
    project_name = req.project_name or repo_url.split("/")[-1].replace(".git", "")
    analysis_id = f"LL-{uuid.uuid4().hex[:8]}"

    # Clone repository shallowly
    success, temp_dir, err = clone_github_repository(repo_url, req.branch)
    if not success:
        raise HTTPException(status_code=400, detail=err)

    # Initialize analysis tracking record
    record = AnalysisRecord(
        id=analysis_id,
        project_name=project_name,
        status="analyzing",
        progress=10,
        stage="inventory",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        repo_url=repo_url
    )
    ANALYSES_DB[analysis_id] = record

    # Schedule background worker
    background_tasks.add_task(
        _execute_analysis_pipeline,
        analysis_id=analysis_id,
        working_dir=temp_dir,
        project_name=project_name,
        repo_url=repo_url
    )

    return {
        "analysis_id": analysis_id,
        "project_name": project_name,
        "status": "analyzing",
        "message": "Analysis started successfully"
    }


@app.post("/api/analyze/upload")
async def analyze_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_name: Optional[str] = Form(None)
):
    """Initiate analysis of an uploaded ZIP archive or source code."""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    p_name = project_name or file.filename.rsplit(".", 1)[0]
    analysis_id = f"LL-{uuid.uuid4().hex[:8]}"

    # Validate file size and write to temporary file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    try:
        bytes_read = 0
        while chunk := await file.read(1024 * 1024):
            bytes_read += len(chunk)
            if bytes_read > MAX_UPLOAD_SIZE_BYTES:
                temp_zip.close()
                os.unlink(temp_zip.name)
                raise HTTPException(status_code=400, detail="Uploaded file exceeds 100 MB limit")
            temp_zip.write(chunk)
        temp_zip.close()

        # Unpack securely
        success, temp_dir, msg, fcount = ingest_zip_archive(temp_zip.name)
        if not success:
            raise HTTPException(status_code=400, detail=msg)

    finally:
        if os.path.exists(temp_zip.name):
            try:
                os.unlink(temp_zip.name)
            except Exception:
                pass

    record = AnalysisRecord(
        id=analysis_id,
        project_name=p_name,
        status="analyzing",
        progress=10,
        stage="inventory",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    ANALYSES_DB[analysis_id] = record

    background_tasks.add_task(
        _execute_analysis_pipeline,
        analysis_id=analysis_id,
        working_dir=temp_dir,
        project_name=p_name
    )

    return {
        "analysis_id": analysis_id,
        "project_name": p_name,
        "status": "analyzing",
        "file_count": fcount,
        "message": "Archive extracted and analysis queued"
    }


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisStatusResponse)
def get_analysis_status(analysis_id: str):
    """Retrieve current status or completed record for an analysis ID."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID format")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis ID not found")

    return AnalysisStatusResponse(
        id=record.id,
        project_name=record.project_name,
        status=record.status,
        progress=record.progress,
        stage=record.stage,
        error=record.error,
        completed_at=record.completed_at,
        record=record if record.status == "completed" else None
    )


@app.get("/api/analysis/{analysis_id}/graph", response_model=GraphResponse)
def get_analysis_graph(analysis_id: str):
    """Retrieve dependency nodes and edges for graph visualization."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return GraphResponse(
        analysis_id=record.id,
        nodes=record.modules,
        edges=record.edges
    )


@app.get("/api/analysis/{analysis_id}/heatmap", response_model=HeatmapResponse)
def get_analysis_heatmap(analysis_id: str):
    """Retrieve modernization risk scores and dynamic heatmap matrix."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if record.risks:
        modules = record.risks
        layer_scores = {r.name: r.score for r in modules}
        matrix = [[r.score, 80, 70, 75, 60, r.confidence] for r in modules]
    else:
        modules, matrix, layer_scores = assess_modernization_risks(record.modules, record.findings)

    return HeatmapResponse(
        analysis_id=record.id,
        modules=modules,
        matrix=matrix,
        layer_scores=layer_scores
    )


@app.get("/api/settings/gemini", response_model=GeminiSettingsResponse)
def get_gemini_settings():
    """Retrieve Gemini provider status, masked key, and supported models."""
    return GeminiSettingsResponse(
        provider="Google Gemini",
        configured=gemini_service.is_configured(),
        model=gemini_service.model_name,
        masked_key=gemini_service.get_masked_key(),
        supported_models=SUPPORTED_MODELS
    )


@app.post("/api/settings/gemini/test", response_model=GeminiTestResponse)
def test_gemini_connection(req: GeminiConfigRequest):
    """Test connection to Gemini with provided or existing API key."""
    result = gemini_service.test_connection(api_key=req.api_key, model_name=req.model)
    return GeminiTestResponse(
        success=result["success"],
        message=result["message"],
        model=result.get("model", gemini_service.model_name),
        masked_key=result.get("masked_key", gemini_service.get_masked_key()),
        timestamp=result.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())
    )


@app.post("/api/settings/gemini/configure", response_model=GeminiTestResponse)
def configure_gemini(req: GeminiConfigRequest):
    """Configure and test Gemini API key in backend runtime."""
    if not req.api_key or not req.api_key.strip():
        raise HTTPException(status_code=400, detail="API key is required.")

    result = gemini_service.configure(api_key=req.api_key.strip(), model_name=req.model)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return GeminiTestResponse(
        success=True,
        message=result["message"],
        model=gemini_service.model_name,
        masked_key=gemini_service.get_masked_key(),
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


@app.get("/api/analysis/{analysis_id}/database", response_model=DatabaseAnalysisResponse)
def get_analysis_database(analysis_id: str):
    """Retrieve database tables, shared write contention, and stored procedures."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db_data = record.database_summary or {
        "tables": {},
        "shared_tables": [],
        "stored_procedures": [],
        "total_tables": 0
    }

    return DatabaseAnalysisResponse(
        analysis_id=record.id,
        tables=db_data.get("tables", {}),
        shared_tables=db_data.get("shared_tables", []),
        stored_procedures=db_data.get("stored_procedures", []),
        total_tables=db_data.get("total_tables", len(db_data.get("tables", {})))
    )


@app.get("/api/analysis/{analysis_id}/report")
def get_analysis_report(analysis_id: str, format: str = Query("json", pattern="^(json|markdown|md)$")):
    """Download full decision-ready modernization report in JSON or Markdown."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if format in ("markdown", "md"):
        content = generate_markdown_report(record)
        return PlainTextResponse(content, media_type="text/markdown")
    else:
        content = generate_json_report(record)
        return JSONResponse(content=json.loads(content), media_type="application/json")


@app.get("/api/analysis/{analysis_id}/pipeline")
def get_analysis_pipeline(analysis_id: str):
    """Retrieve discovered real product execution pipelines and stages."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "analysis_id": record.id,
        "project_name": record.project_name,
        "pipelines": [p.model_dump() for p in record.pipelines]
    }


@app.get("/api/analysis/{analysis_id}/modules")
def get_analysis_modules(analysis_id: str):
    """Retrieve interactive folder/file hierarchy tree with component roles."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "analysis_id": record.id,
        "project_name": record.project_name,
        "module_tree": record.module_tree or []
    }


@app.get("/api/analysis/{analysis_id}/tokens")
def get_analysis_tokens(analysis_id: str):
    """Retrieve real Gemini API token usage audit metrics."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    token_data = record.token_usage.model_dump() if record.token_usage else {
        "prompt_tokens": 0,
        "candidate_tokens": 0,
        "total_tokens": 0,
        "model_name": gemini_service.model_name,
        "stage_breakdown": {},
        "estimated": False
    }

    return {
        "analysis_id": record.id,
        "token_usage": token_data
    }


@app.get("/api/analysis/{analysis_id}/profile")
def get_analysis_profile(analysis_id: str):
    """Retrieve product understanding profile, detected frameworks, and entry points."""
    if not sanitize_analysis_id(analysis_id):
        raise HTTPException(status_code=400, detail="Invalid analysis ID")

    record = ANALYSES_DB.get(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    profile_data = record.product_profile.model_dump() if record.product_profile else {
        "product_type": "Software Application",
        "purpose": "Product profile not yet generated.",
        "detected_frameworks": [],
        "detected_languages": {},
        "entry_points": [],
        "architectural_pattern": "Modular System",
        "infrastructure": [],
        "total_files": 0,
        "total_loc": 0
    }

    return {
        "analysis_id": record.id,
        "profile": profile_data
    }
