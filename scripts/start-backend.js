/**
 * Cross-platform Python FastAPI backend launcher for LegacyLens AI.
 * Automatically resolves virtual environment or system Python.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

function resolvePython() {
  const isWin = process.platform === 'win32';
  const candidates = [
    // Project root .venv / venv
    path.join(rootDir, '.venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
    path.join(rootDir, 'venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
    path.join(rootDir, 'backend', '.venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
    path.join(rootDir, 'backend', 'venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
  ];

  if (process.env.VIRTUAL_ENV) {
    const venvPython = path.join(
      process.env.VIRTUAL_ENV,
      isWin ? 'Scripts/python.exe' : 'bin/python'
    );
    if (fs.existsSync(venvPython)) {
      console.log(`[backend] Using active virtual environment: ${venvPython}`);
      return venvPython;
    }
  }

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      console.log(`[backend] Using detected virtual environment: ${candidate}`);
      return candidate;
    }
  }

  // System fallback
  const fallback = process.env.PYTHON || (isWin ? 'python' : 'python3');
  console.log(`[backend] Using Python executable: ${fallback}`);
  return fallback;
}

const pythonExe = resolvePython();
const host = process.env.HOST || '0.0.0.0';
const port = process.env.PORT || '8000';

console.log(`[backend] Starting FastAPI application on http://${host}:${port} (cwd: ${rootDir})...`);

const args = [
  '-m',
  'uvicorn',
  'backend.main:app',
  '--host',
  host,
  '--port',
  String(port),
  '--reload'
];

const child = spawn(pythonExe, args, {
  cwd: rootDir,
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONPATH: rootDir,
    PYTHONUNBUFFERED: '1'
  },
  shell: process.platform === 'win32'
});

child.on('error', (err) => {
  console.error('\n======================================================');
  console.error(`[backend-error] Failed to start backend using '${pythonExe}':`);
  console.error(`  ${err.message}`);
  console.error('======================================================\n');
  process.exit(1);
});

child.on('close', (code) => {
  if (code !== null && code !== 0) {
    console.error(`[backend] Server process exited with code ${code}`);
    process.exit(code);
  }
});

// Handle termination signals cleanly
process.on('SIGINT', () => {
  child.kill('SIGINT');
  process.exit(0);
});
process.on('SIGTERM', () => {
  child.kill('SIGTERM');
  process.exit(0);
});

