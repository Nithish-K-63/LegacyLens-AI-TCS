# OmniStrat — Autonomous Legacy Modernization Agent

> **Visual Reference:** Matches the exact design and user experience of [Solar Glade Figma Reference](https://solar-glade-31108544.figma.site/).

OmniStrat is an end-to-end autonomous legacy modernization intelligence platform that analyzes legacy codebases (Python, Java, COBOL, SQL, XML/WSDL, JavaScript, TypeScript) safely without runtime execution. It extracts core business rules, maps observed and inferred module dependencies, assesses modernization risk, visualizes heatmaps with file-level drill-down, deduplicates evidence across static and AI stages, and proposes phased strangler migration roadmaps and regression test specifications.

---

## 1. Architecture Overview

- **Frontend:** React 19, Vite, JavaScript, custom animated SVG visualizations, and high-fidelity styling preserving the Figma UI.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2.
- **Static Code Analysis:** Python AST for Python source, conservative language-aware pattern parsers for Java, COBOL, SQL, and XML.
- **Graph & Topology:** NetworkX directed graph analysis for dependency coupling, centrality, and risk scoring.
- **AI Integration:** Google Gemini API via official `google-genai` SDK with prompt injection defenses, secret redaction, and deterministic static fallback.
- **Security:** Sandbox archive extraction (anti-Zip Slip, bomb limits, symlink protection), GitHub URL validation, and untrusted code containment.

---

## 2. Project Directory Structure

```text
LegacyLens AI/
├── backend/
│   ├── main.py                     # FastAPI application & REST endpoints
│   ├── requirements.txt            # Python dependencies
│   ├── schemas/
│   │   └── models.py               # Pydantic v2 data models
│   ├── services/
│   │   ├── security.py             # Validation, Zip Slip prevention & secret redaction
│   │   ├── ingestion.py            # Shallow git clone & safe archive unpacking
│   │   ├── static_analyzer.py      # Python AST visitor & multi-language parsers
│   │   ├── dependency_analyzer.py  # NetworkX graph builder
│   │   ├── database_analyzer.py    # SQL CRUD, tables & stored procs
│   │   ├── business_rules.py       # Business rule discovery & preservation
│   │   ├── risk_analyzer.py        # Heatmap matrix & risk scoring
│   │   ├── architecture.py         # Strangler roadmap & test generator
│   │   ├── gemini_service.py       # Google Gen AI integration & fallback
│   │   └── report_service.py       # JSON & Markdown report generation
│   └── tests/
│       ├── test_api.py             # API, security, & upload tests
│       └── test_analyzer.py        # AST visitor & parser tests
├── frontend/
│   ├── index.html                  # HTML5 entry with fonts and metadata
│   ├── package.json                # React 19 & Vite dependencies
│   ├── vite.config.js              # Vite server & backend API proxy
│   ├── public/
│   │   └── favicon.svg             # Project mark
│   └── src/
│       ├── main.jsx                # React DOM root mounting
│       ├── App.jsx                 # Full UI navigation, pages, drawers & visualizers
│       ├── index.css               # Exact styling matching Figma design
│       └── api/
│           └── client.js           # Centralized API client
├── sample-legacy-project/          # Realistic legacy test codebase
│   ├── src/
│   │   ├── order/discount_engine.py
│   │   ├── auth/permission_map.py
│   │   ├── inventory/warehouse_client.py
│   │   └── util/legacy_date_util.py
│   ├── legacy/
│   │   ├── db/schema.sql
│   │   └── cbl/CUSTREC.cbl
│   └── interfaces/
│       └── warehouse.wsdl
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
└── README.md                       # Complete documentation
```

---

## 3. Quickstart & Verification

### Unified One-Command Startup (Frontend + Backend)

From the project root `D:\LegacyLens AI`:

```bash
npm run dev
```

This single command automatically starts both servers concurrently with live reload:
- **Frontend:** `http://localhost:5173` (Vite + React 19)
- **Backend:** `http://localhost:8000` (FastAPI + Uvicorn)
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)

Both processes display their labeled logs (`[frontend]` and `[backend]`) in the same terminal. If either process terminates with an error, `concurrently` shuts down the partner process cleanly.

### Individual Process Execution (Optional)

If you prefer running frontend and backend in separate terminals:

```powershell
# Backend (from project root)
node scripts/start-backend.js
# or: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (from frontend directory)
cd frontend
npm run dev
```

---

## 4. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Returns server status, version, and Gemini integration mode. |
| `POST` | `/api/analyze/repository` | Ingests a public GitHub repository URL and begins background static analysis. |
| `POST` | `/api/analyze/upload` | Ingests an uploaded ZIP archive or source code file and queues pipeline. |
| `GET` | `/api/analysis/{analysis_id}` | Returns current stage (`inventory`, `dependencies`, `business_rules`, `risk_assessment`, `report_generation`), percentage progress, and completed record. |
| `GET` | `/api/analysis/{analysis_id}/report` | Downloads full decision-ready modernization report (`?format=json` or `?format=markdown`). |
| `GET` | `/api/analysis/{analysis_id}/graph` | Returns NetworkX nodes, in/out degrees, and observed vs inferred edges. |
| `GET` | `/api/analysis/{analysis_id}/heatmap` | Returns module modernization risk matrix and layer-by-layer pressure scores. |

---

## 5. Security Protections

1. **No Code Execution:** All analysis is conducted strictly through Python AST, token inspection, and regular expressions. Uploaded code is never run, imported, or executed.
2. **SSRF & URL Hardening:** Only public HTTPS `github.com` URLs are accepted. Local IP addresses (`127.0.0.1`, `localhost`, CIDR ranges) and URLs containing credentials (`user:pass@host`) are strictly rejected.
3. **Zip Slip Protection:** Every entry in uploaded ZIP files is verified to prevent directory traversal (`..`) out of the temporary extraction target. Symlinks are explicitly skipped to prevent link traversal.
4. **Decompression Bomb Protection:** Hard limits of 2,000 files, 100 MB maximum upload size, and 250 MB maximum uncompressed size are enforced.
5. **Secret Redaction:** High-entropy tokens, passwords, bearer tokens, private keys, and API keys are redacted with `[REDACTED_SECRET]` before any external AI processing.
6. **Automatic Cleanup:** Temporary git clones and unpacked archives are deleted in `finally` blocks upon completion or failure.

---

## 6. Testing with `sample-legacy-project`

You can test the full upload and analysis pipeline using the included multi-language legacy sample:

1. In the LegacyLens AI UI at `http://localhost:5173`, click **Upload** in the sidebar.
2. Under **Source archive**, drag and drop a ZIP archive of `sample-legacy-project` (or run `Compress-Archive -Path sample-legacy-project/* -DestinationPath sample.zip` in PowerShell).
3. Click **Continue to analysis**.
4. Watch the animated agent convergence visual and 5-stage pipeline progress in real-time.
5. Explore the extracted business rules (e.g., Gold loyalty discount ordering, credit override policies), interactive dependency graph, risk heatmap, and target architecture.
6. Click **Export report** to download the Markdown or JSON report.

---

## 7. Limitations & Honest Disclosures

- **Static vs Dynamic:** Static analysis detects syntactic structures, declared decorators, and known query formats. Dynamic dispatch, runtime reflection, and dynamic code generation require human verification.
- **Effort Projections:** Phase effort timelines (e.g. "3–4 weeks") are heuristic planning estimates, not delivery guarantees.
- **Suggested Tests:** Generated regression tests represent behavioral specifications that must be confirmed by domain owners and executed against dedicated test environments.

