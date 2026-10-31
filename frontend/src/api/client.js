/**
 * Centralized API Client for LegacyLens AI Backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

/**
 * Check backend health and Gemini status.
 */
export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch Gemini provider settings, masked key, and supported models.
 */
export async function getGeminiSettings() {
  const res = await fetch(`${API_BASE}/api/settings/gemini`);
  if (!res.ok) {
    throw new Error(`Failed to fetch Gemini settings: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Test Gemini API connection.
 */
export async function testGeminiConnection(apiKey, model) {
  const res = await fetch(`${API_BASE}/api/settings/gemini/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey || undefined, model: model || undefined })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Connection test failed");
  }
  return res.json();
}

/**
 * Configure and save Gemini API key in backend memory.
 */
export async function configureGemini(apiKey, model) {
  const res = await fetch(`${API_BASE}/api/settings/gemini/configure`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, model: model || undefined })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Configuration failed");
  }
  return res.json();
}

/**
 * Fetch database dependencies and shared table writers.
 */
export async function getDatabaseAnalysis(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/database`);
  if (!res.ok) {
    throw new Error(`Failed to fetch database analysis: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Start repository analysis.
 */
export async function analyzeRepository(repoUrl, projectName, branch) {
  const res = await fetch(`${API_BASE}/api/analyze/repository`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      repo_url: repoUrl,
      project_name: projectName || undefined,
      branch: branch || undefined
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to start repository analysis");
  }
  return res.json();
}

/**
 * Upload ZIP archive or source code file for analysis.
 */
export async function analyzeUpload(file, projectName) {
  const formData = new FormData();
  formData.append("file", file);
  if (projectName) {
    formData.append("project_name", projectName);
  }

  const res = await fetch(`${API_BASE}/api/analyze/upload`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to upload and start analysis");
  }
  return res.json();
}

/**
 * Poll current analysis status or get completed record.
 */
export async function getAnalysisStatus(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to get analysis status");
  }
  return res.json();
}

/**
 * Fetch dependency graph nodes and edges.
 */
export async function getGraph(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/graph`);
  if (!res.ok) {
    throw new Error(`Failed to fetch dependency graph: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch modernization risk heatmap.
 */
export async function getHeatmap(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/heatmap`);
  if (!res.ok) {
    throw new Error(`Failed to fetch heatmap: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch discovered real product execution pipelines and stages.
 */
export async function getPipeline(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/pipeline`);
  if (!res.ok) {
    throw new Error(`Failed to fetch pipeline: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch interactive folder and file hierarchy tree with component roles.
 */
export async function getModuleTree(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/modules`);
  if (!res.ok) {
    throw new Error(`Failed to fetch module tree: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch Gemini API token usage audit metrics.
 */
export async function getTokenUsage(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/tokens`);
  if (!res.ok) {
    throw new Error(`Failed to fetch token usage: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch product profile, detected frameworks, and entry points.
 */
export async function getProductProfile(analysisId) {
  const res = await fetch(`${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/profile`);
  if (!res.ok) {
    throw new Error(`Failed to fetch product profile: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Download or fetch full report in json or markdown format.
 */
export async function downloadReport(analysisId, format = "json", projectName = "omnistrat") {
  const url = `${API_BASE}/api/analysis/${encodeURIComponent(analysisId)}/report?format=${format}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to download report: ${res.statusText}`);
  }

  const blob = await res.blob();
  const downloadUrl = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = downloadUrl;
  a.download = `${projectName.toLowerCase().replace(/[\s_]+/g, "-")}-report.${format === "markdown" || format === "md" ? "md" : "json"}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(downloadUrl);
}

