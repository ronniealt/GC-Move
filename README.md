# Gold Coast Move OS

An AI-powered Family Decision Intelligence Platform for relocation decisions.

---

## What This Is

Gold Coast Move OS helps families choose a better life — not just a better house. It evaluates properties, suburbs, and schools through the lens of what actually matters: community, lifestyle, school culture, and long-term family outcomes.

The platform acts as a trusted relocation advisor. You paste a property URL, and it tells you — honestly — whether that home and suburb will improve your family's life in five years.

**This is not a property portal.** It sits above Domain and realestate.com.au as the decision layer.

---

## Scoring Model

Every property is evaluated across five dimensions:

| Dimension | Weight |
|---|---|
| Community | 25% |
| Lifestyle | 20% |
| School ecosystem | 20% |
| Property quality | 20% |
| Financial outcome | 15% |

The result is a **Family Fit Score** (0–100) and a recommendation: Prioritise Immediately / Inspect / Monitor / Ignore.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL 15 + Redis |
| Auth | Clerk |
| AI | OpenAI GPT-4o |
| Property data | Apify (REA + Domain scrapers) |
| Hosting | Vercel (frontend) + Railway (backend) |

---

## Project Structure

```
gc-move-os/
├── apps/
│   ├── web/        # Next.js frontend
│   └── api/        # FastAPI backend
├── docs/           # Architecture specifications
├── CLAUDE.md       # Claude Code project guide
└── README.md
```

---

## Architecture Docs

All specifications are in `/docs`:

- `GC-Move-OS-Build-Pack.md` — implementation guide and task breakdown
- `GC-Move-OS-PRD.md` — product requirements and user stories
- `GC-Move-OS-UX-Spec.md` — screen specs and UX flows
- `GC-Move-OS-Technical-Architecture.md` — system design and API contracts
- `GC-Move-OS-AI-Architecture.md` — AI pipeline and prompt engineering
- `GC-Move-OS-Data-Architecture.md` — data sources and pipelines
- `GC-Move-OS-Database-Design.md` — PostgreSQL schema and seed data

---

## Getting Started (Local Development)

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15
- Redis
- pnpm

### Setup

```bash
# Clone the repo
git clone https://github.com/ronniealt/GC-Move.git
cd GC-Move

# Install frontend dependencies
cd apps/web && pnpm install

# Install backend dependencies
cd ../api && pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Fill in your API keys — see docs/GC-Move-OS-Build-Pack.md

# Run database migrations
alembic upgrade head

# Start frontend (localhost:3000)
pnpm dev

# Start backend (localhost:8000)
uvicorn app.main:app --reload
```

---

## Status

🚧 In active development — Phase 0 (foundation) in progress.
