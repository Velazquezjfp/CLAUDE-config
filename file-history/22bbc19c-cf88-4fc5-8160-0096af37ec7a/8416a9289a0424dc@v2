# ImpactPath / ESG-Hub

**Open-Source ESG Coach for SMEs**

> **Status: Planning & Conceptualization Stage**

## Problem Statement

Small and medium-sized enterprises (SMEs) face increasing pressure to demonstrate sustainability, human rights compliance, and good governance practices. Requirements come from large customers, supply chain partners, and regulatory bodies demanding ESG assessments (e.g., EcoVadis ratings).

**The challenge:** Most SMEs lack the time, expertise, and resources to translate abstract ESG requirements into concrete actions, responsibilities, and documentation. Existing solutions are typically proprietary, expensive, or heavily consulting-driven.

## Solution

ImpactPath/ESG-Hub is an AI-powered, self-hostable web platform that guides SMEs through ESG preparation via:

- **Dialog-based AI assistant** that explains requirements in plain language
- **Structured question flows** covering environment, social, and governance topics
- **Automated to-do generation** with prioritized action items
- **Document drafting** for core policies (e.g., Environmental Policy)
- **Full data sovereignty** through Docker-based self-hosting

## Repository Structure

| File | Purpose |
|------|---------|
| `frontend_draft.html` | Interactive UI/UX proof of concept demonstrating the platform's look and feel. Includes chat interface, to-do panel, document preview, and module navigation. |
| `architecture_diagram.md` | Technical architecture documentation with Mermaid diagrams showing system components, data flow, deployment architecture, and technology stack. |
| `Fragenkatalog_Prototyp_Umwelt.xlsx` | **Environment Module Question Catalog** - 32 structured questions covering environmental policy, organizational responsibility, energy, waste/resources, water, compliance, awareness, and planning. Used by the AI agent to guide users through the assessment. |
| `Fragenkatalog_EcoVadis_Prototyp.xlsx` | **EcoVadis-Aligned Question Catalog** - 22 questions structured by EcoVadis assessment criteria (Policy, Actions, Data, Results) with risk levels. Ensures generated to-dos and documents align with real certification requirements. |

### Question Catalogs (Excel Files)

The Excel files define the knowledge base that powers the AI dialog assistant:

**Fragenkatalog_Prototyp_Umwelt.xlsx** - Environment module with topics:
- `ENV_POLICY` - Environmental/sustainability policy basics
- `ORG_RESP` - Organizational responsibilities
- `ENERGY` - Energy consumption and measures
- `RESOURCES_WASTE` - Waste management and reduction
- `WATER` - Water usage (where relevant)
- `COMPLIANCE` - Legal/regulatory requirements
- `AWARENESS` - Employee training and awareness
- `PLANNING` - Priorities and support needs

**Fragenkatalog_EcoVadis_Prototyp.xlsx** - EcoVadis-structured questions:
- Categories: `POLICY`, `ACTIONS`, `DATA`, `RESULTS`
- Risk levels: `niedrig` (low), `mittel` (medium)
- Aligned with actual EcoVadis assessment structure

## Technology Stack (Planned)

| Component | Technology |
|-----------|------------|
| Frontend | React 18+, TypeScript |
| Backend | Python 3.11+, FastAPI |
| Database | PostgreSQL |
| Vector DB | ChromaDB / Qdrant |
| AI Agent | Google ADK + Gemma 3:12B (local) |
| RAG System | docling |
| Deployment | Docker, Docker Compose |

## Project Phases

**Stage 1 (6 months):** Environment module with question flow, to-do engine, and basic document generation.

**Stage 2 (4 months):** Social module (labor & human rights), memory-enhanced agent, user document processing (PDFs, scans).

## License

Open Source (license TBD)

## Team

- **Pia Roy Chowdhury** - ESG Expert
- **Javier Velazquez** - Software Development
- **Surja Bose** - Project Lead & Conception
