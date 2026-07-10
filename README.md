# AI Legal Aid — Multi-Agent System
## Powered by IBM WatsonX Granite-4

### Architecture

```
User ──► FastAPI Backend ──► Agent Orchestrator
                                │
                    ┌───────────┼───────────┐────────────┐
                    ▼           ▼           ▼            ▼
               Intake        Research   Document     Advisor
               Agent          Agent       Agent        Agent
                    │           │           │            │
                    └───────────┴───────────┴────────────┘
                                │
                         IBM WatsonX API
                      (granite-4-h-small)
```

### Agents

| Agent | Role |
|-------|------|
| **Intake** | Gathers facts, identifies legal area, produces intake summary |
| **Research** | Finds applicable laws, statutes, rights, deadlines |
| **Document** | Drafts letters, complaints, motions, and templates |
| **Advisor** | Synthesises everything into a step-by-step action plan |

### Quick Start

```bash
# 1. Set your IBM API key (already configured in config.py)

# 2. Install & run
python start.py

# 3. Open browser
http://localhost:8000
```

### Manual Start

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat/stream` | Full 4-agent pipeline via SSE |
| POST | `/api/chat/single` | Single agent call (`mode`: intake/research/document/advisor) |
| GET  | `/health` | Health check |
| GET  | `/` | Chat UI |

### Configuration

Edit `config.py` to change model, project, or endpoint.

### Disclaimer

This system provides general legal information only and does not constitute legal advice.
Consult a licensed attorney for advice specific to your situation.
