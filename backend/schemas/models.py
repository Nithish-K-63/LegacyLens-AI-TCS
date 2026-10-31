"""Pydantic data schemas for LegacyLens AI backend."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    gemini_configured: bool
    model: str
    timestamp: str


class GeminiConfigRequest(BaseModel):
    api_key: Optional[str] = Field(None, description="Google Gemini API key")
    model: Optional[str] = Field(None, description="Gemini model name (e.g. gemini-2.5-flash)")


class GeminiTestResponse(BaseModel):
    success: bool
    message: str
    model: str
    masked_key: Optional[str] = None
    timestamp: str


class GeminiSettingsResponse(BaseModel):
    provider: str = "Google Gemini"
    configured: bool
    model: str
    masked_key: Optional[str] = None
    supported_models: List[str] = Field(default_factory=list)
    setup_url: str = "https://aistudio.google.com/app/apikey"
    instructions: str = (
        "Obtain a Gemini API key from Google AI Studio. "
        "Keys configured via the UI are kept in secure backend process memory. "
        "For permanent storage, configure GEMINI_API_KEY in your local .env file."
    )


class DatabaseAnalysisResponse(BaseModel):
    analysis_id: str
    tables: Dict[str, Any]
    shared_tables: List[Dict[str, Any]]
    stored_procedures: List[str]
    total_tables: int


class RepositoryAnalysisRequest(BaseModel):
    repo_url: str = Field(..., description="Public GitHub repository URL")
    project_name: Optional[str] = Field(None, description="Display name for the project")
    branch: Optional[str] = Field(None, description="Optional branch or tag to clone")


class AnalysisFinding(BaseModel):
    id: str
    category: str
    severity: str  # Critical, High, Medium, Low
    file: str
    lines: str
    evidence: str
    confidence: int  # 0 - 100
    language: str
    review: str = "Unreviewed"  # Unreviewed, Verified, Needs Investigation
    classification: str = "BUSINESS_CRITICAL"  # BUSINESS_CRITICAL, NEEDS_INVESTIGATION, LIKELY_OBSOLETE
    impact: str
    modules: List[str] = Field(default_factory=list)
    recommendation: str
    method: str = "ast"  # ast, regex_conservative, ai_inferred


class BusinessRule(BaseModel):
    id: str
    name: str
    category: str
    description: str
    source: str
    confidence: int
    impact: str
    review: str = "Unreviewed"
    critical: bool = True
    dependencies: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    classification: str = "Confirmed in source"
    inputs: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    db_references: List[str] = Field(default_factory=list)


class DependencyNode(BaseModel):
    id: str
    name: str
    type: str  # Service, Module, Database, API
    risk: int
    incoming: int
    outgoing: int
    x: int = 50
    y: int = 50
    reason: str


class DependencyEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    inferred: bool = False


class FileRiskDetail(BaseModel):
    file_path: str
    name: str
    priority: str = "Medium"  # Critical, High, Medium, Low
    score: int = 50
    evidence_count: int = 0
    technical_debt: str = "Low"
    security_risk: str = "Low"
    business_criticality: str = "Medium"
    confidence: int = 85
    recommended_action: str = ""
    findings_ids: List[str] = Field(default_factory=list)


class ModernizationRisk(BaseModel):
    name: str
    score: int
    severity: str
    criticality: str
    dependency: str
    coverage: str
    uncertainty: str
    factors: List[str] = Field(default_factory=list)
    action: str
    priority: str = "Medium"
    evidence_count: int = 0
    technical_debt: str = "Low"
    security_risk: str = "Low"
    business_criticality: str = "Medium"
    confidence: int = 85
    recommended_action: str = ""
    files: List[FileRiskDetail] = Field(default_factory=list)


class MigrationPhase(BaseModel):
    name: str
    objective: str
    status: str
    effort: str
    modules: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    prerequisites: str
    risks: str
    mitigation: str
    criteria: str
    rollback: str
    approval: str


class SuggestedTest(BaseModel):
    name: str
    rule: str
    source: str
    behavior: str
    priority: str  # P0, P1, P2
    status: str = "Suggested"
    module: str


class MetricCard(BaseModel):
    label: str
    value: str
    delta: str


class PipelineStage(BaseModel):
    id: str
    name: str
    order: int
    responsibility: str
    input: str
    output: str
    modules: List[str] = Field(default_factory=list)
    data_passed: str
    dependencies: List[str] = Field(default_factory=list)
    failure_points: List[str] = Field(default_factory=list)
    bottlenecks: List[str] = Field(default_factory=list)
    confidence: int = 85
    evidence: str = ""


class ProductPipeline(BaseModel):
    id: str
    name: str
    purpose: str
    status: str = "Complete"  # Complete, Partial, Inferred
    entry_point: str
    stages: List[PipelineStage] = Field(default_factory=list)
    alternate_workflows: List[str] = Field(default_factory=list)


class ProductProfile(BaseModel):
    product_type: str
    purpose: str
    detected_frameworks: List[str] = Field(default_factory=list)
    detected_languages: Dict[str, int] = Field(default_factory=dict)
    entry_points: List[Dict[str, str]] = Field(default_factory=list)
    architectural_pattern: str
    infrastructure: List[str] = Field(default_factory=list)
    total_files: int
    total_loc: int


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    candidate_tokens: int = 0
    total_tokens: int = 0
    model_name: str = ""
    stage_breakdown: Dict[str, Any] = Field(default_factory=dict)
    estimated: bool = False


class AnalysisRecord(BaseModel):
    id: str
    project_name: str
    status: str  # queued, analyzing, completed, failed
    progress: int = 0
    stage: str = "queued"
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    ai_enabled: bool = False
    repo_url: Optional[str] = None
    metrics: List[MetricCard] = Field(default_factory=list)
    findings: List[AnalysisFinding] = Field(default_factory=list)
    rules: List[BusinessRule] = Field(default_factory=list)
    modules: List[DependencyNode] = Field(default_factory=list)
    edges: List[DependencyEdge] = Field(default_factory=list)
    risks: List[ModernizationRisk] = Field(default_factory=list)
    phases: List[MigrationPhase] = Field(default_factory=list)
    tests: List[SuggestedTest] = Field(default_factory=list)
    architecture: Dict[str, Any] = Field(default_factory=dict)
    database_summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    product_profile: Optional[ProductProfile] = None
    pipelines: List[ProductPipeline] = Field(default_factory=list)
    module_tree: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    executive_summary: str = ""
    limitations: List[str] = Field(default_factory=list)


class AnalysisStatusResponse(BaseModel):
    id: str
    project_name: str
    status: str
    progress: int
    stage: str
    error: Optional[str] = None
    completed_at: Optional[str] = None
    record: Optional[AnalysisRecord] = None


class GraphResponse(BaseModel):
    analysis_id: str
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]


class HeatmapResponse(BaseModel):
    analysis_id: str
    modules: List[ModernizationRisk]
    matrix: List[List[int]]
    layer_scores: Dict[str, int]
