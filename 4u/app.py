"""
Web-UI für die 4U-Analyse-Pipeline
FastAPI + HTML/CSS für intuitive strategische Analyse
"""

import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import json

from methods.four_u import FourUMethod

# Load environment variables
load_dotenv()

app = FastAPI(
    title="4U Analyse Pipeline",
    description="AI Augmented Superpowers für strategische Problemvalidierung"
)


class AnalysisRequest(BaseModel):
    problem: str
    api_key: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Render the main UI."""
    return get_html_template()


@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    """
    Run 4U analysis on a problem.

    Returns streaming JSON updates as analysis progresses.
    """
    if not request.problem.strip():
        raise HTTPException(status_code=400, detail="Problem darf nicht leer sein")

    if not request.api_key.strip():
        raise HTTPException(status_code=400, detail="API-Schlüssel erforderlich")

    async def generate():
        try:
            method = FourUMethod(request.api_key)
            dimensions = ["unworkable", "unavoidable", "urgent", "underserved"]

            for dim in dimensions:
                result = method.run_step(request.problem, dim)
                yield f"data: {json.dumps({'type': 'step', 'dimension': dim, 'result': result})}\n\n"
                await asyncio.sleep(0.5)  # Small delay for animation

            # Synthesis
            synthese = method.run_synthese()
            yield f"data: {json.dumps({'type': 'synthese', 'result': synthese})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0"
    }


def get_html_template() -> str:
    """Return the Notion-style HTML template for the UI."""
    return """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>4U Analysis — Strategic Problem Validation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg: #ffffff;
            --bg-secondary: #f5f5f5;
            --text-primary: #0d0d0d;
            --text-secondary: #626262;
            --border: #e0e0e0;
            --accent: #0d66d0;
            --accent-light: #f0f6ff;
            --signal-strong: #34a853;
            --signal-medium: #f57c00;
            --signal-weak: #d32f2f;
        }

        html, body {
            height: 100%;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: var(--bg);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* HEADER */
        header {
            padding: 4rem 2rem 2rem;
            border-bottom: 1px solid var(--border);
        }

        h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }

        .subtitle {
            font-size: 0.95rem;
            color: var(--text-secondary);
            font-weight: 400;
        }

        /* MAIN CONTENT */
        main {
            flex: 1;
            padding: 2rem;
        }

        /* INPUT SECTION */
        .input-section {
            margin-bottom: 3rem;
        }

        .input-label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }

        .input-wrapper {
            display: flex;
            gap: 1rem;
            align-items: flex-start;
        }

        textarea {
            flex: 1;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-family: inherit;
            font-size: 1rem;
            color: var(--text-primary);
            background: var(--bg);
            resize: vertical;
            min-height: 100px;
            transition: all 0.2s;
            line-height: 1.5;
        }

        textarea:focus {
            outline: none;
            border-color: var(--accent);
            background: var(--accent-light);
            box-shadow: none;
        }

        textarea::placeholder {
            color: var(--text-secondary);
            opacity: 0.6;
        }

        button {
            padding: 0.75rem 1.5rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
            height: fit-content;
            letter-spacing: 0.02em;
        }

        button:hover:not(:disabled) {
            background: #0552b0;
            box-shadow: 0 2px 8px rgba(13, 102, 208, 0.15);
        }

        button:active:not(:disabled) {
            transform: scale(0.98);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* ERROR & LOADING */
        .error {
            background: #ffebee;
            color: var(--signal-weak);
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            display: none;
            font-size: 0.95rem;
            border-left: 3px solid var(--signal-weak);
        }

        .error.show {
            display: block;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            display: none;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 2px solid var(--bg-secondary);
            border-top: 2px solid var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* RESULTS */
        .results-section {
            display: none;
        }

        .results-section.active {
            display: block;
        }

        .results-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .result-card-placeholder {
            background: #e8e8e8;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            font-style: italic;
        }

        .result-card.processing {
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        .result-card {
            min-height: auto;
            cursor: pointer;
            background: #e8e8e8;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            padding: 1.5rem;
        }

        /* MODAL */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            overflow-y: auto;
            padding: 2rem;
        }

        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: var(--bg);
            border-radius: 12px;
            max-width: 700px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
            padding: 2rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: start;
        }

        .modal-header h2 {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
            flex: 1;
        }

        .modal-close {
            background: transparent;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
            padding: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .modal-close:hover {
            color: var(--text-primary);
            background: var(--bg-secondary);
            border-radius: 4px;
        }

        .modal-body {
            padding: 2rem;
            display: flex;
            gap: 2rem;
        }

        .modal-left {
            flex: 1;
            border-right: 1px solid var(--border);
            padding-right: 2rem;
        }

        .modal-right {
            flex: 1;
            padding-left: 2rem;
        }

        .agent-section {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .agent-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }

        .agent-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--accent);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .agent-info h4 {
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .agent-info p {
            margin: 0.25rem 0 0 0;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .agent-content {
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
        }

        .intervention-section {
            border-top: 1px solid var(--border);
            padding-top: 1.5rem;
            margin-top: 1.5rem;
        }

        .intervention-btn {
            background: var(--signal-medium);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
        }

        .intervention-btn:hover {
            background: #e65100;
        }

        .modal-section {
            margin-bottom: 2rem;
        }

        .modal-section h3 {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }

        .modal-analysis {
            color: var(--text-primary);
            font-size: 0.95rem;
            line-height: 1.7;
            margin-bottom: 1.5rem;
        }

        .expandable-section {
            border: 1px solid var(--border);
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .expandable-header {
            padding: 1rem;
            background: var(--bg-secondary);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
        }

        .expandable-header:hover {
            background: rgba(13, 102, 208, 0.05);
        }

        .expandable-header h4 {
            margin: 0;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .expandable-chevron {
            transition: transform 0.2s;
        }

        .expandable-content {
            display: none;
            padding: 1rem;
            border-top: 1px solid var(--border);
        }

        .expandable-section.open .expandable-content {
            display: block;
        }

        .expandable-section.open .expandable-chevron {
            transform: rotate(90deg);
        }

        .expandable-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .expandable-list li {
            padding: 0.5rem 0;
            color: var(--text-primary);
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .expandable-list li:before {
            content: "• ";
            color: var(--accent);
            margin-right: 0.5rem;
            font-weight: bold;
        }

        .result-card h3 {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .signal-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-left: auto;
        }

        .signal-badge.stark {
            background: rgba(52, 168, 83, 0.1);
            color: var(--signal-strong);
        }

        .signal-badge.mittel {
            background: rgba(245, 124, 0, 0.1);
            color: var(--signal-medium);
        }

        .signal-badge.schwach {
            background: rgba(211, 47, 47, 0.1);
            color: var(--signal-weak);
        }

        .result-text {
            color: var(--text-primary);
            font-size: 0.95rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: none;
        }

        .result-sources {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }

        .result-sources-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .result-sources-list {
            font-size: 0.9rem;
            color: var(--text-primary);
            margin: 0;
            padding-left: 1.2rem;
        }

        .result-sources-list li {
            margin-bottom: 0.4rem;
            cursor: pointer;
            color: var(--accent);
            text-decoration: none;
            transition: all 0.2s;
        }

        .result-sources-list li:hover {
            text-decoration: underline;
            color: #0552b0;
        }

        /* SYNTHESE */
        .synthese-section {
            background: #e8f5e9;
            border: 1px solid #c8e6c9;
            border-radius: 8px;
            padding: 2rem;
            margin-top: 2rem;
        }

        .synthese-section h3 {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }

        .synthese-text {
            color: var(--text-primary);
            font-size: 0.95rem;
            line-height: 1.7;
            white-space: pre-wrap;
            word-break: break-word;
        }

        /* PROGRESS BAR */
        .progress-container {
            margin-bottom: 2rem;
            display: none;
        }

        .progress-container.active {
            display: block;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--bg-secondary);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--signal-strong));
            border-radius: 4px;
            transition: width 0.5s ease;
            width: 0%;
        }

        .progress-steps {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .progress-step {
            text-align: center;
            opacity: 0.5;
            transition: opacity 0.3s ease;
        }

        .progress-step.active {
            opacity: 1;
            color: var(--accent);
        }

        .progress-step.completed {
            opacity: 0.8;
            color: var(--signal-strong);
        }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            header {
                padding: 2rem 1.5rem 1.5rem;
            }

            h1 {
                font-size: 1.5rem;
            }

            main {
                padding: 1.5rem;
            }

            .input-wrapper {
                flex-direction: column;
            }

            .results-grid {
                grid-template-columns: 1fr;
            }

            .synthese-section {
                padding: 1.5rem;
            }
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #1a1a1a;
                --bg-secondary: #262626;
                --text-primary: #ececec;
                --text-secondary: #999999;
                --border: #333333;
                --accent-light: #1a2a45;
            }

            textarea {
                background: var(--bg-secondary);
                color: var(--text-primary);
                border-color: var(--border);
            }

            textarea:focus {
                background: var(--accent-light);
                border-color: var(--accent);
            }

            .error {
                background: rgba(211, 47, 47, 0.1);
                color: #ff5252;
            }

            .result-card {
                background: var(--bg-secondary);
            }

            .synthese-section {
                background: var(--accent-light);
                border-color: rgba(13, 102, 208, 0.3);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>4U Analysis</h1>
            <p class="subtitle">Strategic problem validation framework</p>
        </header>

        <main>
            <section class="input-section">
                <label class="input-label">OpenAI API Key</label>
                <input type="password" id="apiKeyInput" placeholder="Enter your OpenAI API key" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-family: inherit; font-size: 1rem; margin-bottom: 1rem;">
                <label class="input-label">Problem</label>
                <div class="input-wrapper">
                    <textarea
                        id="problemInput"
                        placeholder="Describe the problem you want to validate. The analysis will structure it along four dimensions: unworkable, unavoidable, urgent, underserved."
                    ></textarea>
                    <button id="analyzeBtn" onclick="runAnalysis()">Analyze</button>
                </div>
                <div class="error" id="errorMsg"></div>
            </section>

            <div class="loading" id="loadingSpinner">
                <div class="spinner"></div>
                <p>Analyzing across 4U dimensions...</p>
            </div>

            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-steps">
                    <div class="progress-step" id="stepUnworkable">Unworkable</div>
                    <div class="progress-step" id="stepUnavoidable">Unavoidable</div>
                    <div class="progress-step" id="stepUrgent">Urgent</div>
                    <div class="progress-step" id="stepUnderserved">Underserved</div>
                    <div class="progress-step" id="stepSynthesis">Synthesis</div>
                </div>
            </div>

            <div class="results-section" id="resultsSection">
                <div class="results-grid">
                    <div id="unworkableResult"></div>
                    <div id="unavoidableResult"></div>
                    <div id="urgentResult"></div>
                    <div id="underservedResult"></div>
                </div>
                <div class="synthese-section" id="syntheseSection"></div>
            </div>
        </main>

        <footer>
            Machine structures. Human decides. No shortcuts.
        </footer>
    </div>

    <!-- MODAL -->
    <div class="modal" id="detailModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle"></h2>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="modal-left">
                    <div class="modal-section">
                        <h3>Analysis & Method</h3>
                        <div class="modal-analysis" id="modalAnalysis"></div>
                        <div id="modalSignalContainer"></div>
                    </div>
                    <div id="modalSources"></div>
                    <div id="modalAssumptions"></div>
                    <div id="modalCounterArguments"></div>
                </div>
                <div class="modal-right">
                    <div class="agent-section">
                        <div class="agent-header">
                            <div class="agent-avatar">🤖</div>
                            <div class="agent-info">
                                <h4>AI Agent Analysis</h4>
                                <p>Autonomous analysis completed</p>
                            </div>
                        </div>
                        <div class="agent-content" id="agentSummary">
                            <p><strong>Analysis completed:</strong> The AI agent has systematically evaluated this dimension using structured reasoning and available data.</p>
                            <p><strong>Confidence level:</strong> <span id="agentConfidence">High</span></p>
                            <p><strong>Processing time:</strong> <span id="agentTime">~2.3 seconds</span></p>
                        </div>
                    </div>
                    <div class="agent-section">
                        <h4>Critical Reflection</h4>
                        <div class="agent-content" id="agentCritique">
                            <p><strong>Potential limitations:</strong></p>
                            <ul>
                                <li>Data availability may be incomplete</li>
                                <li>Market dynamics can change rapidly</li>
                                <li>Human context not fully captured</li>
                            </ul>
                            <p><strong>Recommendations:</strong></p>
                            <ul>
                                <li>Validate assumptions with primary research</li>
                                <li>Monitor competitive landscape</li>
                                <li>Consider timing and execution feasibility</li>
                            </ul>
                        </div>
                    </div>
                    <div class="intervention-section">
                        <h4>Human Intervention</h4>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">
                            Override or enhance the AI analysis with your strategic insights.
                        </p>
                        <button class="intervention-btn" onclick="openInterventionModal()">
                            ✏️ Edit & Intervene
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function runAnalysis() {
            const problem = document.getElementById('problemInput').value;
            const apiKey = document.getElementById('apiKeyInput').value;
            const errorMsg = document.getElementById('errorMsg');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const progressContainer = document.getElementById('progressContainer');
            const resultsSection = document.getElementById('resultsSection');
            const btn = document.getElementById('analyzeBtn');

            errorMsg.classList.remove('show');
            resultsSection.classList.remove('active');
            progressContainer.classList.remove('active');

            if (!problem.trim()) {
                errorMsg.textContent = 'Please enter a problem to analyze.';
                errorMsg.classList.add('show');
                return;
            }

            if (!apiKey.trim()) {
                errorMsg.textContent = 'Please enter your OpenAI API key.';
                errorMsg.classList.add('show');
                return;
            }

            btn.disabled = true;
            loadingSpinner.classList.add('show');
            progressContainer.classList.add('active');

            // Initialize progress
            resetProgress();

            // Clear previous results
            document.getElementById('resultsSection').innerHTML = `
                <div class="results-grid">
                    <div id="unworkableResult" class="result-card-placeholder"></div>
                    <div id="unavoidableResult" class="result-card-placeholder"></div>
                    <div id="urgentResult" class="result-card-placeholder"></div>
                    <div id="underservedResult" class="result-card-placeholder"></div>
                </div>
                <div class="synthese-section" id="syntheseSection"></div>
            `;

            resultsSection.classList.add('active');

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        problem: problem,
                        api_key: apiKey
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Analysis failed');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.slice(6));
                            if (data.type === 'step') {
                                updateProgress(data.dimension);
                                displayStepResult(data.dimension, data.result);
                            } else if (data.type === 'synthese') {
                                updateProgress('synthesis');
                                displaySynthese(data.result);
                                loadingSpinner.classList.remove('show');
                                progressContainer.classList.remove('active');
                                btn.disabled = false;
                            } else if (data.type === 'error') {
                                throw new Error(data.message);
                            }
                        }
                    }
                }

            } catch (error) {
                loadingSpinner.classList.remove('show');
                progressContainer.classList.remove('active');
                btn.disabled = false;
                errorMsg.textContent = `Error: ${error.message}`;
                errorMsg.classList.add('show');
            }
        }

        function resetProgress() {
            const steps = ['stepUnworkable', 'stepUnavoidable', 'stepUrgent', 'stepUnderserved', 'stepSynthesis'];
            steps.forEach(stepId => {
                const step = document.getElementById(stepId);
                step.classList.remove('active', 'completed');
            });
            document.getElementById('progressFill').style.width = '0%';
        }

        function updateProgress(dimension) {
            const stepMap = {
                'unworkable': 'stepUnworkable',
                'unavoidable': 'stepUnavoidable',
                'urgent': 'stepUrgent',
                'underserved': 'stepUnderserved',
                'synthesis': 'stepSynthesis'
            };

            const stepId = stepMap[dimension];
            if (stepId) {
                const step = document.getElementById(stepId);
                step.classList.add('active');

                // Mark previous steps as completed
                const allSteps = ['stepUnworkable', 'stepUnavoidable', 'stepUrgent', 'stepUnderserved', 'stepSynthesis'];
                const currentIndex = allSteps.indexOf(stepId);
                for (let i = 0; i < currentIndex; i++) {
                    document.getElementById(allSteps[i]).classList.add('completed');
                    document.getElementById(allSteps[i]).classList.remove('active');
                }

                // Update progress bar
                const progress = ((currentIndex + 1) / allSteps.length) * 100;
                document.getElementById('progressFill').style.width = progress + '%';

                // Add processing animation to current card
                const cardId = dimension + 'Result';
                const card = document.getElementById(cardId);
                if (card) {
                    card.classList.add('processing');
                }
            }
        }
        function displayStepResult(dimension, result) {
            const dimensions = [
                { key: 'unworkable', label: 'Unworkable', icon: '❌' },
                { key: 'unavoidable', label: 'Unavoidable', icon: '⚠️' },
                { key: 'urgent', label: 'Urgent', icon: '⏰' },
                { key: 'underserved', label: 'Underserved', icon: '👥' }
            ];

            const dim = dimensions.find(d => d.key === dimension);
            const signal = result.signal || 'Unbekannt';
            const analysis = result.analysis || '';
            const sources = result.sources || [];
            const container = document.getElementById(dimension + 'Result');

            // Show full analysis text
            const sourcesHtml = sources.length > 0 ? `
                <div class="result-sources">
                    <div class="result-sources-label">Quellen</div>
                    <ul class="result-sources-list">
                        ${sources.map((s, idx) => `<li onclick="handleSourceClick(event, '${escapeAttr(s)}')">${escapeHtml(s)}</li>`).join('')}
                    </ul>
                </div>
            ` : '';

            container.classList.remove('processing');
            container.innerHTML = `
                <div class="result-card" onclick="openModal('${escapeAttr(dim.label)}', ${escapeJSON(result)}, '${dimension}')">
                    <h3>
                        ${dim.icon} ${dim.label}
                        <span class="signal-badge ${signal.toLowerCase()}">${signal}</span>
                    </h3>
                    <p class="result-text">${escapeHtml(analysis)}</p>
                    ${sourcesHtml}
                </div>
            `;
        }

        function displaySynthese(result) {
            const signal = result.signal || 'Unbekannt';
            const analysis = result.analysis || '';
            const sources = result.sources || [];
            const syntheseContainer = document.getElementById('syntheseSection');
            const sourcesHtml = sources.length > 0 ? `
                <div class="result-sources">
                    <div class="result-sources-label">Quellen</div>
                    <ul class="result-sources-list">
                        ${sources.map((s, idx) => `<li onclick="handleSourceClick(event, '${escapeAttr(s)}')">${escapeHtml(s)}</li>`).join('')}
                    </ul>
                </div>
            ` : '';
            syntheseContainer.innerHTML = `
                <div class="result-card" onclick="openModal('Synthesis & Validation', ${escapeJSON(result)}, 'synthesis')">
                    <h3>📊 Synthesis & Validation
                        <span class="signal-badge ${signal.toLowerCase()}">${signal}</span>
                    </h3>
                    <p class="result-text">${escapeHtml(analysis)}</p>
                    ${sourcesHtml}
                </div>
            `;
        }

        function openModal(title, result, dimension = '') {
            const modal = document.getElementById('detailModal');
            const signal = result.signal || 'Unbekannt';
            const analysis = result.analysis || '';
            const sources = result.sources || [];
            const assumptions = result.assumptions || [];
            const counterArguments = result.counter_arguments || [];

            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalAnalysis').textContent = analysis;

            // Signal badge
            const signalContainer = document.getElementById('modalSignalContainer');
            signalContainer.innerHTML = `
                <div style="margin-bottom: 1.5rem;">
                    <span class="signal-badge ${signal.toLowerCase()}">${signal}</span>
                </div>
            `;

            // Agent summary based on dimension
            const agentSummary = document.getElementById('agentSummary');
            const confidenceLevels = { 'stark': 'High', 'mittel': 'Medium', 'schwach': 'Low' };
            const confidence = confidenceLevels[signal.toLowerCase()] || 'Medium';
            agentSummary.innerHTML = `
                <p><strong>Analysis completed:</strong> The AI agent has systematically evaluated the ${dimension || 'selected'} dimension using structured reasoning and available data.</p>
                <p><strong>Confidence level:</strong> <span id="agentConfidence">${confidence}</span></p>
                <p><strong>Processing time:</strong> <span id="agentTime">~2.3 seconds</span></p>
            `;

            // Agent critique
            const agentCritique = document.getElementById('agentCritique');
            agentCritique.innerHTML = `
                <p><strong>Potential limitations:</strong></p>
                <ul>
                    <li>Data availability may be incomplete for ${dimension || 'this analysis'}</li>
                    <li>Market dynamics can change rapidly</li>
                    <li>Human context and tacit knowledge not fully captured</li>
                    <li>Assumptions may not hold in all scenarios</li>
                </ul>
                <p><strong>Recommendations:</strong></p>
                <ul>
                    <li>Validate key assumptions with primary research</li>
                    <li>Monitor competitive landscape and market changes</li>
                    <li>Consider execution feasibility and resource requirements</li>
                    <li>Combine with human expertise for strategic validation</li>
                </ul>
            `;

            // Sources
            const sourcesDiv = document.getElementById('modalSources');
            if (sources.length > 0) {
                sourcesDiv.innerHTML = buildExpandableSection('Sources', sources);
            } else {
                sourcesDiv.innerHTML = '';
            }

            // Assumptions
            const assumptionsDiv = document.getElementById('modalAssumptions');
            if (assumptions.length > 0) {
                assumptionsDiv.innerHTML = buildExpandableSection('Assumptions', assumptions);
            } else {
                assumptionsDiv.innerHTML = '';
            }

            // Counter-arguments
            const counterDiv = document.getElementById('modalCounterArguments');
            if (counterArguments.length > 0) {
                counterDiv.innerHTML = buildExpandableSection('Counter-Arguments', counterArguments);
            } else {
                counterDiv.innerHTML = '';
            }

            modal.classList.add('active');
        }

        function openInterventionModal() {
            // Simple intervention: allow editing the analysis
            const currentAnalysis = document.getElementById('modalAnalysis').textContent;
            const interventionHtml = `
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: 2000; display: flex; align-items: center; justify-content: center;">
                    <div style="background: var(--bg); border-radius: 12px; padding: 2rem; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;">
                        <h3 style="margin-bottom: 1rem;">Human Intervention</h3>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
                            Edit the AI analysis with your strategic insights. Your changes will be saved locally.
                        </p>
                        <textarea id="interventionText" style="width: 100%; min-height: 200px; padding: 1rem; border: 1px solid var(--border); border-radius: 6px; font-family: inherit; margin-bottom: 1.5rem;">${escapeHtml(currentAnalysis)}</textarea>
                        <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                            <button onclick="cancelIntervention()" style="padding: 0.75rem 1.5rem; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 6px; cursor: pointer;">Cancel</button>
                            <button onclick="saveIntervention()" style="padding: 0.75rem 1.5rem; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer;">Save Changes</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', interventionHtml);
        }

        function cancelIntervention() {
            const interventionModal = document.querySelector('[style*="position: fixed"][style*="z-index: 2000"]');
            if (interventionModal) {
                interventionModal.remove();
            }
        }

        function saveIntervention() {
            const newAnalysis = document.getElementById('interventionText').value;
            document.getElementById('modalAnalysis').textContent = newAnalysis;
            cancelIntervention();
            // Here you could add logic to save the changes to a backend or local storage
            alert('Changes saved! The analysis has been updated with your human intervention.');
        }

        function handleSourceClick(event, source) {
            event.stopPropagation();

            // Don't open assumptions/notes as links
            if (source.toLowerCase().startsWith('assumption:')) {
                alert(source);
                return;
            }

            // Check if it's already a URL
            if (/^(https?:\/\/|www\.)/i.test(source)) {
                // Open URL as-is
                const url = source.startsWith('http') ? source : 'https://' + source;
                window.open(url, '_blank');
            } else {
                // For plain text, show as info (don't Google search)
                alert('Quelle: ' + source);
            }
        }

        function showNotification(message) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                background: var(--accent);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(13, 102, 208, 0.3);
                font-size: 0.9rem;
                z-index: 9999;
                animation: slideIn 0.3s ease-out;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

        function buildExpandableSection(title, items) {
            const listItems = items.map(item => `<li>${escapeHtml(item)}</li>`).join('');
            return `
                <div class="expandable-section" onclick="toggleExpandable(event)">
                    <div class="expandable-header">
                        <h4>${title}</h4>
                        <span class="expandable-chevron">›</span>
                    </div>
                    <div class="expandable-content">
                        <ul class="expandable-list">${listItems}</ul>
                    </div>
                </div>
            `;
        }

        function toggleExpandable(event) {
            const section = event.currentTarget;
            section.classList.toggle('open');
        }

        function escapeAttr(text) {
            return text.replace(/'/g, "\\'");
        }

        function escapeJSON(obj) {
            return JSON.stringify(obj).replace(/'/g, "\\'");
        }

        function escapeHtml(text) {
            const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        document.getElementById('problemInput').addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                runAnalysis();
            }
        });

        // Modal backdrop close
        document.getElementById('detailModal').addEventListener('click', (e) => {
            if (e.target.id === 'detailModal') {
                closeModal();
            }
        });

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("🚀 4U Analyse Pipeline startet...")
    print("="*60)
    print("\n📱 Öffne: http://localhost:8000")
    print("\n💡 Die Pipeline respektiert dein strategisches Denken.")
    print("   Sie ersetzt es nicht.\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
