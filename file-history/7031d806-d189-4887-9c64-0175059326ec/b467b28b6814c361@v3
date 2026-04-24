# BAMF ACTE Companion - Kubernetes Deployment Anforderungen

> Hypothetisches Deployment-Konzept zur Bereitstellung der BAMF ACTE Companion Anwendung
> in einer containerisierten Kubernetes-Umgebung.

**Datum:** 2026-04-09
**Version:** 2.0.0

---

## Inhaltsverzeichnis

1. [Hosting-Anforderungen](#1-hosting-anforderungen-containers-memory-cpu)
2. [Container-Anforderungen](#2-container-anforderungen)
3. [Netzwerk-System](#3-netzwerk-system)
4. [Hypothetischer Kubernetes-Zugang](#4-hypothetischer-kubernetes-zugang-ingress)
5. [System-Zusammenfassung](#5-system-zusammenfassung)
6. [Mermaid-Diagramm](#6-mermaid-diagramm)

---

## 1. Hosting-Anforderungen (Containers, Memory, CPU)

### 1.1 ACTE Companion - Interne Container

| Container | Min. CPU | Max. CPU | Min. RAM | Max. RAM | Storage | Replicas |
|-----------|----------|----------|----------|----------|---------|----------|
| **Frontend (React/NGINX)** | 100m | 500m | 128Mi | 256Mi | - | 2 |
| **Backend (FastAPI/Uvicorn)** | 250m | 1000m | 256Mi | 1Gi | - | 2 |
| **Dokumenten-PVC** | - | - | - | - | 10Gi (RWX) | 1 |
| **Case-Daten-PVC** | - | - | - | - | 5Gi (RWX) | 1 |

### 1.2 Anonymisierungsdienst (PII-Erkennung)

| Container | Min. CPU | Max. CPU | Min. RAM | Max. RAM | GPU | Storage | Replicas |
|-----------|----------|----------|----------|----------|-----|---------|----------|
| **Anonymisierung (Flask/PyTorch)** | 2000m | 4000m | 2Gi | 4Gi | Nein* | ~10Gi (Image) | 1 |

> \* Obwohl das Base-Image `pytorch/pytorch` CUDA-fähig ist, nutzt der Code nur **CPU-Inferenz** (OpenCV DNN Backend, SpaCy, EasyOCR). Kein GPU-Node erforderlich.

### 1.3 IDIRS Document Search (Hybride Suche & RAG)

Der IDIRS-Dienst besteht aus **3-4 Pods** (abhängig von der LLM-Option):

| Container | Min. CPU | Max. CPU | Min. RAM | Max. RAM | GPU | Storage | Typ |
|-----------|----------|----------|----------|----------|-----|---------|-----|
| **IDIRS API Server** | 500m | 2000m | 512Mi | 2Gi | Nein | - | Deployment |
| **IDIRS Data Pipeline** | 1000m | 4000m | 2Gi | 4Gi | Nein | Volume (PDFs + Ontologie) | Job (einmalig) |
| **OpenSearch** | 1000m | 2000m | 1Gi | 2Gi | Nein | 5-10Gi (PV) | StatefulSet |
| **Ollama (Option A)** | 2000m | 4000m | 12Gi | 16Gi | 1x NVIDIA 16GB VRAM | 15Gi (Modelle) | Deployment |

### 1.4 Cluster-Gesamtanforderungen

> **Wichtig:** Es gibt **zwei Optionen** fuer den LLM-Dienst des IDIRS-Suchsystems.
> Die Wahl beeinflusst die Cluster-Anforderungen erheblich.

#### Option A: Lokales LLM mit Ollama (Datensouveraenitaet)

Alle KI-Inferenz bleibt im Cluster. Erfordert GPU-Node.

| Ressource | Nur ACTE | + Anonymisierung | + IDIRS (Ollama) | **Gesamt** |
|-----------|----------|-------------------|-------------------|------------|
| **CPU** | 0.7 vCPU | + 2 vCPU | + 4.5 vCPU | **~7.2 vCPU** |
| **RAM** | 640Mi | + 2Gi | + 15.5Gi | **~18Gi** |
| **Storage** | 15Gi PVC | + 10Gi Image | + 30Gi | **~55Gi** |
| **GPU** | - | - | 1x NVIDIA 16GB | **1x NVIDIA 16GB** |
| **Nodes** | 1 | 1 | +1 GPU-Node | **2-3 Nodes** |

**Vorteile:** Keine Daten verlassen den Cluster, keine API-Kosten pro Request, volle Kontrolle.
**Nachteile:** GPU-Node teuer (~800-1500 EUR/Monat Cloud), hoher RAM-Bedarf, Modell-Verwaltung.

#### Option B: Externer LLM-API-Endpunkt (z.B. OpenAI, Anthropic)

IDIRS nutzt einen externen API-Endpunkt statt lokalem Ollama. Kein GPU-Node noetig.

| Ressource | Nur ACTE | + Anonymisierung | + IDIRS (Ext. API) | **Gesamt** |
|-----------|----------|-------------------|--------------------|------------|
| **CPU** | 0.7 vCPU | + 2 vCPU | + 3.5 vCPU | **~6.2 vCPU** |
| **RAM** | 640Mi | + 2Gi | + 3.5Gi | **~6.1Gi** |
| **Storage** | 15Gi PVC | + 10Gi Image | + 15Gi | **~40Gi** |
| **GPU** | - | - | - | **Keine** |
| **Nodes** | 1 | 1 | 1 | **1-2 Nodes** |

**Vorteile:** Kein GPU-Node noetig (Cluster viel guenstiger), einfachere Infrastruktur, leichtere Skalierung.
**Nachteile:** Latenz, Kosten pro Request, Daten verlassen den Cluster, Abhaengigkeit von externem Anbieter.
**Code-Aenderung:** `OLLAMA_BASE` Umgebungsvariable ersetzen durch API-URL + API-Key (Secret).

#### Vergleich auf einen Blick

| | Option A (Ollama) | Option B (Ext. API) |
|---|---|---|
| **CPU gesamt** | ~7.2 vCPU | ~6.2 vCPU |
| **RAM gesamt** | ~18Gi | ~6.1Gi |
| **GPU** | 1x NVIDIA 16GB VRAM | Keine |
| **Storage gesamt** | ~55Gi | ~40Gi |
| **Pods gesamt** | 8 | 7 |
| **Datensouveraenitaet** | Voll (alles im Cluster) | Teilweise (LLM-Anfragen extern) |
| **Monatl. Kosten (Cloud, geschaetzt)** | ~1500-2500 EUR | ~400-800 EUR + API-Kosten |

---

## 2. Container-Anforderungen

### 2.1 Frontend Container: React SPA mit NGINX

```
Base Image:     node:20-alpine (Build-Stage)
                nginx:1.25-alpine (Runtime-Stage)
Framework:      React 18.3 + TypeScript 5.8
Build Tool:     Vite 5.4
Node Version:   >= 20 LTS
Port:           80 (intern) -> NGINX dient statische Dateien
```

**Hypothetische Dockerfile-Struktur (Multi-Stage):**
```
Stage 1 - Build:
  - node:20-alpine
  - npm ci && npm run build
  - Output: /app/dist (statische Dateien)

Stage 2 - Runtime:
  - nginx:1.25-alpine
  - COPY dist -> /usr/share/nginx/html
  - NGINX Config mit API-Proxy Regeln
  - Exposed Port: 80
```

**Umgebungsvariablen (Build-Zeit):**
| Variable | Beschreibung | Standardwert |
|----------|--------------|--------------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000` |

**NGINX Proxy-Regeln (Laufzeit):**
- `/api/*` -> Backend Service (Port 8000)
- `/ws/*` -> Backend Service (WebSocket Upgrade)
- `/health` -> Backend Health-Check
- `/documents/*` -> Backend Static Files
- `/root_docs/*` -> Backend Static Files
- `/*` -> Statische SPA-Dateien (React Router)

**Wichtige Frontend-Abhaengigkeiten:**
- React 18.3.1, React DOM 18.3.1
- React Router DOM 6.30.1
- @tanstack/react-query 5.83.0
- i18next 25.7.4 (Internationalisierung DE/EN)
- pdfjs-dist 5.4.530 (PDF-Rendering)
- shadcn/ui Komponenten (Radix UI)

---

### 2.2 Backend Container: Python FastAPI

```
Base Image:     python:3.12-slim
Framework:      FastAPI 0.104.1
ASGI Server:    Uvicorn 0.24.0
Python Version: 3.12
Port:           8000
```

**Hypothetische Dockerfile-Struktur:**
```
Stage 1 - Build:
  - python:3.12-slim
  - COPY requirements.txt
  - pip install --no-cache-dir -r requirements.txt

Stage 2 - Runtime:
  - Gleiche Image
  - COPY backend/ /app/backend/
  - COPY root_docs/ /app/root_docs/ (falls statische Dokumente benoetigt)
  - Exposed Port: 8000
  - CMD: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Umgebungsvariablen (Laufzeit):**
| Variable | Beschreibung | Pflicht | Standardwert |
|----------|--------------|---------|--------------|
| `GEMINI_API_KEY` | Google Gemini API Schluessel | Ja | - |
| `ENABLE_CHAT_HISTORY` | Chat-Verlauf aktivieren | Nein | `false` |
| `MAX_CONVERSATION_HISTORY` | Max. Nachrichten pro Fall | Nein | `10` |
| `MAX_TOKENS_PER_REQUEST` | Max. Tokens pro API-Anfrage | Nein | `30000` |
| `TOKEN_ESTIMATE_PER_CHAR` | Token-Schaetzung pro Zeichen | Nein | `0.25` |
| `RESERVE_TOKENS` | Reservierte Tokens | Nein | `5000` |
| `DOCUMENTS_PATH` | Pfad fuer Dokumentenspeicher | Nein | `public/documents` |
| `IDIRS_BASE_URL` | IDIRS API Server URL | Nein | `http://idirs-api:8010` |
| `IDIRS_TIMEOUT` | IDIRS API Timeout (Sekunden) | Nein | `30` |
| `RAG_CONFIDENCE_THRESHOLD` | RAG-Konfidenz-Schwelle | Nein | `0.80` |
| `LOG_LEVEL` | Log-Level | Nein | `INFO` |
| `INIT_TEST_DOCS` | Testdokumente initialisieren | Nein | `false` |

**Python-Abhaengigkeiten (requirements.txt):**
| Paket | Version | Zweck |
|-------|---------|-------|
| fastapi | 0.104.1 | Web-Framework |
| uvicorn | 0.24.0 | ASGI Server |
| websockets | 12.0 | WebSocket-Support |
| google-generativeai | 0.3.1 | Gemini AI Integration |
| python-dotenv | 1.0.0 | Umgebungskonfiguration |
| pydantic | 2.5.2 | Datenvalidierung |
| python-multipart | 0.0.21 | Datei-Upload |
| aiohttp | 3.9.1 | Async HTTP (Anonymisierung) |
| httpx | 0.28.1 | HTTP Client (IDIRS Proxy) |
| Pillow | 10.2.0 | Bildverarbeitung (PII-Masking) |
| markdownify | 1.2.2 | HTML-zu-Markdown |
| beautifulsoup4 | 4.14.3 | HTML-Parsing |
| pdfplumber | 0.11.0 | PDF-Textextraktion |
| langdetect | 1.0.9 | Spracherkennung |
| html2text | 2024.2.26 | E-Mail-Verarbeitung |

**Volume Mounts:**
| Mount-Pfad (Container) | Zweck | Typ |
|-------------------------|-------|-----|
| `/app/data` | Case-Kontextdaten (JSON) | PVC (RWX) |
| `/app/documents` | Dokumentenspeicher (PDF, Bilder, E-Mails) | PVC (RWX) |

---

### 2.3 Anonymisierungsdienst (PII-Erkennung)

#### Uebersicht

```
Base Image:     docker.io/pytorch/pytorch (Ubuntu 22.04, CUDA-faehig)
Framework:      Flask 3.1.2
Python Version: 3.10.13
Port:           5000/TCP (POST /ai-analysis)
Image-Groesse:  ~8.4 GB
GPU:            NICHT benoetigt (nur CPU-Inferenz)
```

#### ML-Modelle (im Container eingebettet)

| Modell | Groesse | Typ |
|--------|---------|-----|
| model-best1 (SpaCy NER) | ~34 MB | Allgemeine Dokumente (24 Entity-Typen) |
| model-best-birthcert (SpaCy NER) | ~33 MB | Geburtsurkunden (21 Entity-Typen) |
| yolo/ (YOLOv4-tiny) | ~23 MB | Objekterkennung (4 Klassen) |
| yolo-birthcert/ (YOLOv4-tiny) | ~23 MB | Objekterkennung (7 Klassen) |
| frontalface.xml (Haar Cascade) | 1.2 MB | Gesichtserkennung |
| EasyOCR arabic.pth | 206 MB | Arabisch OCR Modell |
| EasyOCR craft_mlt_25k.pth | 80 MB | Text-Detektion |

> **Hinweis:** EasyOCR-Modelle werden beim ersten Aufruf nach `/root/.EasyOCR/` heruntergeladen.
> Fuer Kubernetes muessen diese **ins Image eingebacken** werden (kein Internet-Zugang im Pod).

#### Installierte Schluessel-Bibliotheken

| Paket | Version | Zweck |
|-------|---------|-------|
| torch | 2.2.1 | PyTorch (vom Base Image) |
| torchvision | 0.17.1 | (vom Base Image) |
| spacy | 3.8.11 | NER Modelle |
| easyocr | 1.7.2 | OCR (EN, AR, FA) |
| opencv-python-headless | 4.11.0.86 | Bildverarbeitung |
| opencv-contrib-python-headless | 4.11.0.86 | OpenCV extras |
| Flask | 3.1.2 | Web API |
| Levenshtein | 0.27.3 | String-Matching |
| pandas | 2.3.3 | Datenverarbeitung |
| numpy | 1.26.3 | Numerik |
| pillow | 10.2.0 | Bildformat-Support |
| scikit-image | 0.25.2 | (easyocr Dependency) |

#### RAM-Aufschluesselung

| Komponente | Geschaetzt |
|------------|-----------|
| PyTorch Runtime | ~500 MB |
| SpaCy Modelle (2x geladen) | ~200 MB |
| EasyOCR Modelle | ~400 MB |
| OpenCV Bildverarbeitung | ~200 MB |
| Flask + Overhead | ~100 MB |
| **Request (Minimum)** | **2 GB** |
| **Limit (Empfohlen)** | **4 GB** |

#### Kubernetes Resource Spec

```yaml
resources:
  requests:
    cpu: "2"
    memory: "2Gi"
  limits:
    cpu: "4"
    memory: "4Gi"
```

#### Wichtige Hinweise

- **Kein GPU noetig**: Obwohl `pytorch/pytorch` CUDA enthaelt, nutzt der Code nur CPU (OpenCV DNN Backend). Ein leichteres Base Image (z.B. `python:3.10-slim`) koennte die Image-Groesse von 8.4 GB auf ~3-4 GB reduzieren.
- **Stateless**: Keine Datenbank, kein persistenter Speicher noetig. Bilder werden nur temporaer unter `/usr/src/app/photo/` verarbeitet.
- **Skalierbar**: Mehrere Replicas moeglich, da zustandslos.
- **Authentifizierung**: SECRET_KEY ist im Backend hardcoded - sollte fuer Produktion als K8s-Secret konfiguriert werden.

---

### 2.4 IDIRS Document Search (Hybride Suche & RAG)

Der IDIRS-Dienst besteht aus **mehreren Pods**, die zusammen eine hybride Dokumentensuche ermoeglichen.

#### Pod 1: IDIRS API Server

```
Base Image:     python:3.12-slim
Framework:      FastAPI + Uvicorn
Port:           8010
```

| Ressource | Wert |
|-----------|------|
| Libraries | fastapi, uvicorn, opensearch-py, ollama (Python Client) |
| CPU | 0.5 - 2 Cores |
| RAM | 512Mi - 2Gi |
| GPU | Nein |
| Storage | - |
| Typ | Deployment |

**Endpunkte:**
- `POST /search` - Hybride Dokumentensuche (BM25 + kNN)
- `POST /rag` - RAG-Abfragen mit Chunk-Extraktion

#### Pod 2: IDIRS Data Pipeline

```
Base Image:     python:3.12-slim + system libs (libgl1, libglib2.0)
Typ:            Kubernetes Job (einmalig)
```

| Ressource | Wert |
|-----------|------|
| Libraries | docling, docling-graph, rdflib, pyshacl, opensearch-py, ollama |
| CPU | 1 - 4 Cores |
| RAM | 2 - 4Gi |
| GPU | Nein |
| Storage | Volume mit PDFs (`docs_1/`) + Ontologie-Dateien (`temp/*.jsonld`) |
| Typ | Job (einmalig, laeuft bei Daten-Ingestion) |

> **Hinweis:** Dieser Pod laeuft nur bei der initialen Datenaufnahme bzw. wenn neue Dokumente
> indiziert werden muessen. Im Normalbetrieb ist er nicht aktiv.

#### Pod 3: OpenSearch

```
Docker Image:   opensearchproject/opensearch:latest
Port:           9200
```

| Ressource | Wert |
|-----------|------|
| CPU | 1 - 2 Cores |
| RAM | 1 - 2Gi (JVM Heap: 512m) |
| GPU | Nein |
| Storage | 5 - 10Gi (PersistentVolume) |
| Typ | StatefulSet |

#### Pod 4: LLM Service - 2 Optionen

##### Option A: Ollama (Lokales LLM)

```
Docker Image:   ollama/ollama:latest
Port:           11434
```

| Ressource | Wert |
|-----------|------|
| CPU | 2 - 4 Cores |
| RAM | 12 - 16Gi |
| GPU | **1x NVIDIA, 16+ GB VRAM** |
| Storage | 15Gi (gemma3:12b ~10GB + nomic-embed-text ~274MB) |
| Cluster | **NVIDIA GPU Operator + Device Plugin erforderlich** |
| Typ | Deployment |

**Modelle:**
- `gemma3:12b` (~10 GB) - Generatives LLM fuer RAG-Antworten
- `nomic-embed-text` (~274 MB) - Embedding-Modell fuer kNN-Vektorsuche

##### Option B: Externer API-Endpunkt (z.B. OpenAI, Anthropic)

| Ressource | Wert |
|-----------|------|
| Docker Image | Keiner - kein Pod noetig |
| CPU / RAM / GPU | Entfaellt |
| Code-Aenderung | `OLLAMA_BASE` ersetzen durch API-URL + API-Key (K8s Secret) |

| | Vorteil | Nachteil |
|---|---|---|
| | Kein GPU-Node noetig | Latenz pro Request |
| | Cluster deutlich guenstiger | Kosten pro Request |
| | Einfachere Infrastruktur | Daten verlassen den Cluster |
| | Keine Modell-Verwaltung | Abhaengigkeit vom Anbieter |

#### IDIRS Gesamtverbrauch

| Ressource | Option A (Ollama) | Option B (Ext. API) |
|-----------|-------------------|---------------------|
| CPU | ~5-12 Cores | ~3-8 Cores |
| RAM | ~16-24Gi | ~4-8Gi |
| GPU | 1x NVIDIA 16GB VRAM | Keine |
| Storage | ~25Gi | ~10Gi |
| Pods | 4 | 3 |

---

### 2.5 Google Gemini API (Externe Cloud)

```
Typ:               Cloud-Service (kein Self-Hosting)
Modell:            gemini-2.5-flash
Authentifizierung: API Key (GEMINI_API_KEY)
Netzwerk:          Ausgehend HTTPS zu generativelanguage.googleapis.com
```

Keine Container-Bereitstellung noetig. Erfordert **ausgehenden Internetzugang** vom ACTE-Backend-Container.

> **Hinweis:** Gemini wird vom ACTE-Backend fuer Chat, Dokumentenanalyse, Formularextraktion,
> Uebersetzung und Validierung genutzt. Das IDIRS-System nutzt ein **separates** LLM (Ollama
> oder externen Anbieter) fuer RAG-Antworten und Embeddings.

---

## 3. Netzwerk-System

### 3.1 Kubernetes-internes Netzwerk

| Von | Nach | Protokoll | Port | Beschreibung |
|-----|------|-----------|------|--------------|
| Ingress | Frontend | HTTP | 80 | Statische SPA + Proxy |
| Frontend (NGINX) | Backend | HTTP/WS | 8000 | API + WebSocket Proxy |
| Backend | Anonymisierung | HTTP | 5000 | PII-Erkennung (POST /ai-analysis) |
| Backend | IDIRS API Server | HTTP | 8010 | Hybride Suche & RAG Proxy |
| IDIRS API Server | OpenSearch | HTTP | 9200 | Indizierung & Abfragen |
| IDIRS API Server | Ollama (Opt. A) | HTTP | 11434 | LLM-Inferenz & Embeddings |
| IDIRS Data Pipeline | OpenSearch | HTTP | 9200 | Daten-Ingestion |
| IDIRS Data Pipeline | Ollama (Opt. A) | HTTP | 11434 | Embedding-Generierung |
| Backend | Google Gemini API | HTTPS | 443 | KI-Anfragen (Egress) |

### 3.2 Kubernetes Services

```yaml
# ACTE Companion Services
Services:
  - acte-frontend          (ClusterIP, Port 80)
  - acte-backend           (ClusterIP, Port 8000)

# Anonymisierungsdienst
  - anonymization-svc      (ClusterIP, Port 5000)

# IDIRS Document Search
  - idirs-api              (ClusterIP, Port 8010)
  - idirs-opensearch       (ClusterIP, Port 9200)
  - idirs-ollama           (ClusterIP, Port 11434)   # Nur Option A
```

### 3.3 Konfiguration als Kubernetes Ressourcen

| Ressource | Typ | Inhalt |
|-----------|-----|--------|
| `acte-secrets` | Secret | GEMINI_API_KEY |
| `idirs-secrets` | Secret | OLLAMA_API_KEY (nur Option B) |
| `acte-config` | ConfigMap | Backend Env-Vars (nicht-sensibel) |
| `idirs-config` | ConfigMap | IDIRS Env-Vars (OLLAMA_BASE, OPENSEARCH_URL) |
| `acte-documents-pvc` | PersistentVolumeClaim | Dokumentenspeicher (10Gi, RWX) |
| `acte-data-pvc` | PersistentVolumeClaim | Case-Kontextdaten (5Gi, RWX) |
| `idirs-opensearch-pvc` | PersistentVolumeClaim | OpenSearch Index-Daten (10Gi, RWO) |
| `idirs-ollama-pvc` | PersistentVolumeClaim | LLM-Modelle (15Gi, RWO) - Nur Option A |

### 3.4 NetworkPolicy (Empfohlen)

```
Frontend:
  - Ingress: Nur vom Ingress-Controller
  - Egress:  Nur zum Backend-Service (Port 8000)

Backend (ACTE):
  - Ingress: Nur vom Frontend-Service
  - Egress:  Anonymisierung (5000), IDIRS API (8010), Google APIs (443)

Anonymisierungsdienst:
  - Ingress: Nur vom Backend-Service
  - Egress:  Kein externer Zugang (CPU-only, alle Modelle lokal)

IDIRS API Server:
  - Ingress: Nur vom Backend-Service
  - Egress:  OpenSearch (9200), Ollama (11434) oder Ext. API (443)

OpenSearch:
  - Ingress: Nur von IDIRS API Server und Data Pipeline
  - Egress:  Kein externer Zugang

Ollama (Nur Option A):
  - Ingress: Nur von IDIRS API Server und Data Pipeline
  - Egress:  Kein externer Zugang (Modelle lokal gespeichert)
```

---

## 4. Hypothetischer Kubernetes-Zugang (Ingress)

### 4.1 NGINX Ingress Controller (Empfohlen)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: acte-companion-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/websocket-services: "acte-backend"
    nginx.ingress.kubernetes.io/proxy-body-size: "15m"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - acte.bamf.internal
      secretName: acte-tls-secret
  rules:
    - host: acte.bamf.internal
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: acte-backend
                port:
                  number: 8000
          - path: /ws
            pathType: Prefix
            backend:
              service:
                name: acte-backend
                port:
                  number: 8000
          - path: /health
            pathType: Exact
            backend:
              service:
                name: acte-backend
                port:
                  number: 8000
          - path: /documents
            pathType: Prefix
            backend:
              service:
                name: acte-backend
                port:
                  number: 8000
          - path: /root_docs
            pathType: Prefix
            backend:
              service:
                name: acte-backend
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: acte-frontend
                port:
                  number: 80
```

### 4.2 Alternative Zugangssysteme

| Option | Beschreibung | Eignung |
|--------|--------------|---------|
| **NGINX Ingress** | Standard K8s Ingress, WebSocket Support | Empfohlen (einfach, ausgereift) |
| **Traefik** | Moderner Ingress mit Auto-TLS | Gut (komplexere Konfiguration) |
| **Istio Gateway** | Service Mesh mit mTLS | Fuer Produktionsumgebungen mit Zero-Trust |
| **HAProxy Ingress** | Hochperformanter Loadbalancer | Bei hohen Lastanforderungen |

### 4.3 Wichtige Ingress-Konfigurationen

- **WebSocket-Support**: Pflicht wegen `/ws/chat/{case_id}` Echtzeit-Chat
- **Proxy-Timeout**: >= 3600s fuer lang laufende WebSocket-Verbindungen
- **Body-Size**: >= 15MB wegen Datei-Upload (`/api/files/upload`)
- **TLS-Terminierung**: Am Ingress-Controller (interne Kommunikation HTTP)
- **Sticky Sessions**: Nicht zwingend (WebSocket-Verbindung ist zustandslos pro Request)

---

## 5. System-Zusammenfassung

### 5.1 Kurzbeschreibung

Der **BAMF ACTE Companion** ist ein KI-gestuetztes Fallverwaltungssystem zur Unterstuetzung von Sachbearbeitern im Asylverfahren. Das System besteht aus drei Hauptbereichen:

1. **ACTE Companion** (React Frontend + FastAPI Backend) - Die Kern-Anwendung mit KI-Chat, Dokumentenviewer, Formularverwaltung und Fallvalidierung.
2. **Anonymisierungsdienst** - PII-Erkennung und Schwaerzung in Identitaetsdokumenten mittels OCR, NER und Objekterkennung (CPU-only, kein GPU).
3. **IDIRS Document Search** - Hybride Dokumentensuche (BM25 + kNN-Vektoren) und RAG-Abfragen ueber OpenSearch mit lokalem oder externem LLM.

### 5.2 Microservices-Komponenten

| # | Komponente | Typ | Technologie | Port | Beschreibung |
|---|------------|-----|-------------|------|--------------|
| 1 | **Frontend** | Deployment | React 18 + NGINX | 80 | SPA: Dokumentenviewer, Chat, Formulare |
| 2 | **Backend** | Deployment | FastAPI + Uvicorn, Python 3.12 | 8000 | REST API (10 Router) + WebSocket-Chat |
| 3 | **Anonymisierung** | Deployment | Flask + PyTorch + SpaCy + EasyOCR, Python 3.10 | 5000 | PII-Erkennung und Schwaerzung (CPU-only) |
| 4 | **IDIRS API Server** | Deployment | FastAPI + Uvicorn, Python 3.12 | 8010 | Hybride Suche & RAG API |
| 5 | **IDIRS Data Pipeline** | Job | Python 3.12 + docling + rdflib | - | Einmalige Daten-Ingestion |
| 6 | **OpenSearch** | StatefulSet | opensearchproject/opensearch | 9200 | Suchindex (BM25 + kNN) |
| 7 | **Ollama** (Opt. A) | Deployment | ollama/ollama | 11434 | Lokales LLM + Embeddings |
| 8 | **Google Gemini** | Cloud-Service | Gemini 2.5 Flash API | 443 | KI fuer ACTE (Chat, Analyse, Uebersetzung) |
| - | **Dokumenten-PVC** | PVC (RWX) | Filesystem | - | PDF, Bilder, E-Mails (10Gi) |
| - | **Case-Daten-PVC** | PVC (RWX) | Filesystem | - | JSON Konfiguration (5Gi) |
| - | **OpenSearch-PVC** | PVC (RWO) | Filesystem | - | Suchindex-Daten (10Gi) |

### 5.3 Architektonische Merkmale

- **Zwei separate KI-Systeme**: ACTE nutzt Google Gemini (Cloud). IDIRS nutzt Ollama/Ext. API (lokal oder extern). Diese sind unabhaengig.
- **Stateless ACTE-Backend**: Keine Datenbank. Alle Daten in JSON-Dateien auf Shared Volumes.
- **WebSocket-Streaming**: Echtzeit-Chat mit Streaming-Antworten von Gemini AI.
- **Hierarchischer Kontext**: Intelligente Kontextladung (Fall > Ordner > Dokument) aus JSON-Konfigurationen.
- **Proxy-Architektur**: ACTE-Backend fungiert als Proxy fuer Anonymisierung und IDIRS.
- **CPU-only ML**: Der Anonymisierungsdienst nutzt trotz PyTorch-Image nur CPU-Inferenz (kein GPU erforderlich).

### 5.4 Deployment-Reihenfolge

```
Phase 1: Infrastruktur
  1. Namespace erstellen
  2. PersistentVolumeClaims anlegen (Dokumente, Case-Daten, OpenSearch)
  3. Secrets erstellen (GEMINI_API_KEY, ggf. OLLAMA_API_KEY)
  4. ConfigMaps erstellen

Phase 2: Datendienste
  5. OpenSearch deployen (StatefulSet, warten auf Ready)
  6. Ollama deployen (nur Option A, Modelle laden)

Phase 3: Anwendungsdienste
  7. IDIRS Data Pipeline ausfuehren (Job, Daten-Ingestion)
  8. IDIRS API Server deployen
  9. Anonymisierungsdienst deployen
  10. ACTE Backend deployen

Phase 4: Frontend & Zugang
  11. ACTE Frontend deployen
  12. Ingress konfigurieren
  13. TLS-Zertifikat einrichten
```

### 5.5 Wichtige Hinweise

- **Kein Docker vorhanden**: Die aktuelle ACTE-Loesung hat keine Dockerfiles. Diese muessen fuer das Kubernetes-Deployment erstellt werden.
- **Shared Volumes**: Da das ACTE-Backend Dateien auf dem Filesystem speichert, muessen alle Backend-Replicas auf dasselbe Volume zugreifen (ReadWriteMany).
- **Egress-Kontrolle**: ACTE-Backend benoetigt ausgehenden HTTPS-Zugang zu `generativelanguage.googleapis.com`. Bei Option B benoetigt IDIRS zusaetzlich Zugang zum externen LLM-Anbieter.
- **File-Upload-Limit**: Backend akzeptiert Dateien bis 15MB - Ingress und NGINX muessen entsprechend konfiguriert sein.
- **Image-Groesse Anonymisierung**: Das PyTorch-basierte Image ist ~8.4 GB gross. Node-Speicher und Registry-Kapazitaet beachten.
- **GPU-Operator (nur Option A)**: Fuer Ollama mit GPU wird der NVIDIA GPU Operator + Device Plugin im Cluster benoetigt.

---

## 6. Mermaid-Diagramm

Siehe: [deployment-diagram.mmd](./deployment-diagram.mmd)

---

**Dokument erstellt:** 2026-04-09
**Version:** 2.0.0
**Autor:** Automatisch generiert aus Codebase-Analyse + Dienst-Spezifikationen
