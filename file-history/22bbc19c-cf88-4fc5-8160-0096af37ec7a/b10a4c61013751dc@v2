# ImpactPath / ESG-Hub - Technical Architecture

## System Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["🌐 Client Layer"]
        Browser["Web Browser"]
    end

    subgraph Frontend["📱 Frontend Container (Docker)"]
        React["React 18+<br/>TypeScript<br/>Tailwind CSS"]
        ChatUI["Dialog UI Component"]
        TodoUI["To-do List Component"]
        DocUI["Document Preview Component"]
        UploadUI["File Upload<br/>(Images, PDFs)"]

        React --> ChatUI
        React --> TodoUI
        React --> DocUI
        React --> UploadUI
    end

    subgraph Backend["⚙️ Backend Container (Docker)"]
        FastAPI["FastAPI<br/>Python 3.11+<br/>REST API"]

        subgraph Services["Core Services"]
            DialogService["Dialog Service<br/>(Question Flow)"]
            TodoEngine["To-do Engine<br/>(Priority Logic)"]
            DocGenerator["Document Generator<br/>(Templates)"]
            ExportService["Export Service<br/>(PDF/Markdown)"]
        end

        subgraph AgentLayer["🤖 AI Agent Layer"]
            ADK["Google ADK<br/>(Agent Framework)"]
            Gemma["Gemma 3:12B<br/>(Local LLM, min 8B)"]
            MultiModal["Multimodal Processing<br/>(Text + Images)"]
            MemoryLayer["Memory Layer<br/>(Stage 2)"]
        end

        FastAPI --> Services
        FastAPI --> AgentLayer
        ADK --> Gemma
        ADK --> MultiModal
        ADK --> MemoryLayer
    end

    subgraph RAGSystem["📚 RAG System Container (Docker)"]
        Docling["docling<br/>(Document Parser)"]
        Embeddings["Embedding Model<br/>(Local)"]
        RAGPipeline["RAG Pipeline<br/>(Context Retrieval)"]

        Docling --> RAGPipeline
        Embeddings --> RAGPipeline
    end

    subgraph Databases["🗄️ Data Layer"]
        subgraph PostgreSQL["PostgreSQL 15+"]
            UserAnswers[("User Answers")]
            Tasks[("Tasks/To-dos")]
            Documents[("Generated Documents")]
            Sessions[("User Sessions")]
        end

        subgraph VectorDB["Vector Database<br/>(ChromaDB/Qdrant)"]
            ComplianceDocs[("Compliance Documents<br/>(PDFs, Guidelines)")]
            Standards[("ESG Standards<br/>(EcoVadis, ISO)")]
            Templates[("Document Templates")]
        end
    end

    subgraph DocumentStore["📄 Document Storage"]
        PDFStore["PDF Storage<br/>(Compliance Docs)"]
        UserDocs["User Uploads<br/>(Stage 2)"]
        ExportDocs["Generated Exports"]
    end

    subgraph ExternalOpt["☁️ Optional External (API Fallback)"]
        CloudLLM["Cloud LLM API<br/>(Fallback for limited HW)"]
    end

    %% Connections
    Browser <-->|HTTPS| React
    React <-->|REST API| FastAPI

    FastAPI <--> PostgreSQL
    FastAPI <--> VectorDB
    FastAPI <--> DocumentStore

    AgentLayer <-->|Context Query| RAGPipeline
    RAGPipeline <--> VectorDB

    Docling --> PDFStore
    DocGenerator --> ExportDocs

    AgentLayer -.->|Optional| CloudLLM

    UploadUI -->|Stage 2| UserDocs

    %% Styling
    classDef frontend fill:#3B82F6,stroke:#1D4ED8,color:white
    classDef backend fill:#10B981,stroke:#059669,color:white
    classDef database fill:#8B5CF6,stroke:#6D28D9,color:white
    classDef ai fill:#F59E0B,stroke:#D97706,color:white
    classDef storage fill:#EC4899,stroke:#BE185D,color:white
    classDef external fill:#6B7280,stroke:#374151,color:white

    class React,ChatUI,TodoUI,DocUI,UploadUI frontend
    class FastAPI,DialogService,TodoEngine,DocGenerator,ExportService backend
    class PostgreSQL,VectorDB,UserAnswers,Tasks,Documents,Sessions,ComplianceDocs,Standards,Templates database
    class ADK,Gemma,MultiModal,MemoryLayer,Docling,Embeddings,RAGPipeline ai
    class PDFStore,UserDocs,ExportDocs storage
    class CloudLLM external
```

## Component Details

### Frontend (React)
- **Technology**: React 18+ with TypeScript
- **Styling**: Tailwind CSS / CSS Modules
- **Key Components**:
  - Dialog Chat Interface
  - To-do List Management
  - Document Preview & Export
  - Multimodal File Upload (Images, PDFs)

### Backend (FastAPI)
- **Technology**: Python 3.11+ with FastAPI
- **API**: RESTful endpoints
- **Core Services**:
  - **Dialog Service**: Manages question flow and user interactions
  - **To-do Engine**: Generates prioritized action items
  - **Document Generator**: Creates templates (Environmental Policy, etc.)
  - **Export Service**: PDF/Markdown generation

### AI Agent Layer
- **Google ADK**: Agent orchestration framework
- **Gemma 3:12B**: Local LLM (minimum 8B for limited hardware)
- **Multimodal**: Text and image processing capabilities
- **Memory Layer** (Stage 2): Persistent context across sessions

### RAG System
- **docling**: PDF and document parsing
- **Embeddings**: Local embedding model for semantic search
- **Pipeline**: Context retrieval from compliance documents

### Databases
- **PostgreSQL**: Structured data (answers, tasks, documents, sessions)
- **Vector DB (ChromaDB/Qdrant)**: Embeddings for RAG system
  - Compliance documents
  - ESG standards and guidelines
  - Document templates

### Infrastructure
- **Docker**: Containerized deployment
- **Self-Hosting**: Full data sovereignty
- **Optional Cloud Fallback**: API-based LLM for limited hardware

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Agent as AI Agent (ADK + Gemma)
    participant RAG as RAG System (docling)
    participant VDB as Vector Database
    participant PG as PostgreSQL

    U->>FE: Start Environment Module
    FE->>API: Initialize Session
    API->>PG: Create Session Record
    API->>Agent: Start Dialog Flow

    Agent->>RAG: Query Compliance Context
    RAG->>VDB: Semantic Search
    VDB-->>RAG: Relevant Documents
    RAG-->>Agent: Context Retrieved

    Agent-->>API: First Question + Explanation
    API-->>FE: Display Question
    FE-->>U: Show AI Message

    U->>FE: Submit Answer
    FE->>API: POST /answers
    API->>PG: Store Answer
    API->>Agent: Process Answer

    Agent->>Agent: Analyze Response
    Agent->>API: Generate To-do Items
    API->>PG: Store To-dos

    Agent-->>API: Next Question
    API-->>FE: Update UI
    FE-->>U: Show To-dos + Next Question

    Note over Agent,PG: Repeat for all questions

    U->>FE: Request Document Generation
    FE->>API: POST /documents/generate
    API->>Agent: Generate Environmental Policy
    Agent->>RAG: Get Template Context
    RAG-->>Agent: Template + Guidelines
    Agent-->>API: Draft Document
    API->>PG: Store Document
    API-->>FE: Document Preview
    FE-->>U: Display Draft for Review

    U->>FE: Export as PDF
    FE->>API: GET /documents/export/pdf
    API-->>FE: PDF File
    FE-->>U: Download PDF
```

---

## Module Architecture

```mermaid
flowchart LR
    subgraph Stage1["Stage 1 - Environment Module"]
        ENV_Q["Question Catalog<br/>(Climate, Energy, Resources)"]
        ENV_T["To-do Templates"]
        ENV_D["Environmental Policy<br/>Document Templates"]
    end

    subgraph Stage2["Stage 2 - Extensions"]
        SOC_Q["Social Module<br/>(Labor & Human Rights)"]
        SOC_T["Social To-do Templates"]
        SOC_D["Social Policy Templates"]

        MEM["Memory Enhancement"]
        DOC_PROC["User Document<br/>Processing (PDFs, Scans)"]
    end

    subgraph Future["Future - Governance"]
        GOV_Q["Governance Module"]
        GOV_T["Governance Templates"]
        GOV_D["Governance Documents"]
    end

    Stage1 --> Stage2
    Stage2 --> Future

    classDef s1 fill:#10B981,stroke:#059669,color:white
    classDef s2 fill:#3B82F6,stroke:#1D4ED8,color:white
    classDef future fill:#8B5CF6,stroke:#6D28D9,color:white

    class ENV_Q,ENV_T,ENV_D s1
    class SOC_Q,SOC_T,SOC_D,MEM,DOC_PROC s2
    class GOV_Q,GOV_T,GOV_D future
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18+, TypeScript, Tailwind CSS | Modern responsive UI |
| **Backend** | Python 3.11+, FastAPI | REST API, Business Logic |
| **Database** | PostgreSQL 15+ | Structured data storage |
| **Vector DB** | ChromaDB / Qdrant | RAG embeddings storage |
| **AI Agent** | Google ADK | Agent orchestration |
| **LLM** | Gemma 3:12B (local) | Dialog generation, explanations |
| **RAG** | docling | Document parsing & retrieval |
| **Container** | Docker, Docker Compose | Deployment & isolation |
| **Export** | WeasyPrint / Pandoc | PDF/Markdown generation |

---

## Deployment Architecture

```mermaid
flowchart TB
    subgraph Docker["Docker Compose Environment"]
        subgraph FE_Container["frontend:latest"]
            Nginx["Nginx"]
            ReactBuild["React Build"]
        end

        subgraph BE_Container["backend:latest"]
            Uvicorn["Uvicorn ASGI"]
            FastAPIApp["FastAPI App"]
            AgentRuntime["Agent Runtime"]
        end

        subgraph DB_Container["postgres:15"]
            PostgresDB["PostgreSQL"]
        end

        subgraph Vector_Container["chromadb:latest"]
            ChromaDB["ChromaDB"]
        end

        subgraph LLM_Container["ollama:latest"]
            Ollama["Ollama"]
            GemmaModel["Gemma 3:12B"]
        end
    end

    Internet["Internet"] --> Nginx
    Nginx --> FastAPIApp
    FastAPIApp --> PostgresDB
    FastAPIApp --> ChromaDB
    AgentRuntime --> Ollama

    classDef container fill:#0EA5E9,stroke:#0284C7,color:white
    class FE_Container,BE_Container,DB_Container,Vector_Container,LLM_Container container
```
