# ACTE Companion - Abhaengigkeiten Checkliste (v2)

> **Scope:** Nur ACTE Companion (Frontend + Backend) in **1 Docker-Container**.
> Anonymisierungsdienst und IDIRS Document Search sind NICHT enthalten (spaetere Phase).
> Zweck: Vergleich mit Artifactory-Verfuegbarkeit fuer gesicherte Umgebung.

**Datum:** 2026-04-14
**Architektur:** 1 Docker-Container (POC/Demo)
**LLM-Zugang:** Ueber LiteLLM Proxy (kein direkter Gemini SDK)
**Frontend-Build:** Extern (kein Node.js im Docker noetig)

---

## Architektur: 1 Docker Container

```
python:3.12-slim  (einziges Base Image)
  |
  ├── dist/             -->  React Build (extern gebaut, ins Image kopiert)
  ├── backend/          -->  FastAPI (10 REST Router + WebSocket Chat)
  └── Uvicorn Server    -->  Port 8000 (einziger Port)
```

**Frontend wird EXTERN gebaut** (auf Build-Rechner oder CI):
```
Build-Rechner:  node:20 + npm ci + npm run build  -->  dist/ Ordner
Docker-Build:   COPY dist/ /app/dist               -->  Nur statische Dateien kopieren
```

Dadurch braucht das Docker-Image **kein Node.js** und Artifactory braucht **kein node Image**.

---

## Kategorie 1: Docker Base Images

| # | Image | Version | Zweck | Benoetigt? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| D-01 | `python` | >= 3.12-slim | Runtime: Backend + Gesamtes Image | **Ja (Pflicht)** | [ ] In Bearbeitung |
| ~~D-02~~ | ~~`node`~~ | ~~>= 20~~ | ~~Build-Stage~~ | **Nein** (extern gebaut) | [x] Nicht noetig |

---

## Kategorie 2: Python Backend-Bibliotheken (pip)

> Quelle: `backend/requirements.txt`
> Alle werden per `pip install -r requirements.txt` im Docker-Build installiert.

### 2.1 Kern-Framework (Pflicht - FastAPI laeuft nicht ohne diese)

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| PY-01 | `fastapi` | 0.104.1 | Web-Framework (REST + WebSocket) | Nein | [ ] In Bearbeitung |
| PY-02 | `uvicorn` | 0.24.0 | ASGI Server (startet die App) | Nein | [ ] In Bearbeitung |
| PY-03 | `websockets` | 12.0 | WebSocket-Protokoll (Chat) | Nein | [ ] In Bearbeitung |
| PY-04 | `pydantic` | 2.5.2 | Datenvalidierung (FastAPI braucht es) | Nein | [ ] In Bearbeitung |
| PY-05 | `python-multipart` | 0.0.21 | Datei-Upload Support | Nein | [ ] In Bearbeitung |

### 2.2 KI-Integration (LiteLLM Proxy)

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| ~~PY-06~~ | ~~`google-generativeai`~~ | ~~0.3.1~~ | ~~Gemini SDK~~ | **Entfaellt** | [x] Nicht noetig |

> **Begruendung:** LiteLLM Proxy ist bereits in der Umgebung verfuegbar.
> Der Code wird angepasst: `GeminiService` nutzt `httpx` (PY-13) um LiteLLM
> ueber die OpenAI-kompatible REST API anzusprechen.
> Kein herstellerspezifisches SDK mehr noetig.

### 2.3 Dokumentenverarbeitung

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| PY-07 | `Pillow` | 10.2.0 | Bildverarbeitung | Nein | [ ] In Bearbeitung |
| PY-08 | `pdfplumber` | 0.11.0 | PDF-Textextraktion | Ja* | [ ] In Bearbeitung |
| PY-09 | `markdownify` | 1.2.2 | HTML-zu-Markdown (Chat-Antworten) | Ja* | [ ] In Bearbeitung |
| PY-10 | `beautifulsoup4` | 4.14.3 | HTML-Parsing (fuer markdownify) | Ja* | [ ] In Bearbeitung |
| PY-11 | `html2text` | 2024.2.26 | E-Mail-Verarbeitung (EML-Dateien) | Ja* | [ ] In Bearbeitung |
| PY-12 | `langdetect` | 1.0.9 | Spracherkennung in Dokumenten | Ja* | [ ] In Bearbeitung |

> \* `pdfplumber` -> Alternative: `PyMuPDF` (haeufiger in Artifactory).
> `markdownify` + `beautifulsoup4` -> koennte entfallen, dann werden LLM-Antworten nicht formatiert.
> `html2text` -> nur fuer E-Mail-Feature.
> `langdetect` -> nur fuer automatische Spracherkennung.

### 2.4 HTTP-Clients

| # | Paket | Version | Zweck | Jetzt aktiv? | Artifactory Status |
|---|-------|---------|-------|--------------|---|
| PY-13 | `httpx` | 0.28.1 | HTTP Client (LiteLLM + spaeter IDIRS) | **Ja (LiteLLM)** | [ ] In Bearbeitung |
| PY-14 | `aiohttp` | 3.9.1 | Async HTTP (spaeter Anonymisierung) | Nein* | [ ] In Bearbeitung |

> \* `aiohttp` wird aktuell nicht aktiv genutzt, aber der Code importiert es beim Start.
> **Optionen:**
> 1. Installieren (einfachste Loesung, Code laeuft ohne Aenderung)
> 2. Import zu lazy-import aendern (dann entfaellt es fuer Phase 1)
> 3. Durch `httpx` ersetzen (1 HTTP-Client statt 2, kleine Code-Aenderung)

### 2.5 Konfiguration

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| PY-15 | `python-dotenv` | 1.0.0 | `.env` Datei laden | Ja* | [ ] In Bearbeitung |

> \* Entfaellt in Kubernetes (ConfigMap/Secret). Aber Code ruft `load_dotenv()` auf.
> Einfachste Loesung: installieren und ignorieren (schadet nicht).

---

## Kategorie 3: Frontend-Bibliotheken (npm)

> **Diese Pakete werden EXTERN gebaut** (auf Build-Rechner, nicht im Docker).
> Das Ergebnis ist ein `dist/` Ordner (~2 MB) mit HTML, JS und CSS.
> Im Docker-Image und in Artifactory sind diese Pakete **NICHT noetig**.

> **Was muss auf dem Build-Rechner vorhanden sein:**
> - Node.js >= 20 LTS
> - npm (kommt mit Node.js)
> - Zugang zu npm Registry (direkt oder ueber Artifactory-Proxy)

### 3.1 Kern-Framework

| # | Paket | Version | Wo benoetigt |
|---|-------|---------|--------------|
| NPM-01 | `react` | ^18.3.1 | Nur Build-Rechner |
| NPM-02 | `react-dom` | ^18.3.1 | Nur Build-Rechner |
| NPM-03 | `react-router-dom` | ^6.30.1 | Nur Build-Rechner |
| NPM-04 | `typescript` | ^5.8.3 | Nur Build-Rechner |
| NPM-05 | `vite` | ^5.4.19 | Nur Build-Rechner |
| NPM-06 | `@vitejs/plugin-react-swc` | ^3.11.0 | Nur Build-Rechner |

### 3.2 UI-Komponenten

| # | Paket | Version | Wo benoetigt |
|---|-------|---------|--------------|
| NPM-07 | `@radix-ui/*` (22 Pakete) | diverse | Nur Build-Rechner |
| NPM-08 | `tailwindcss` | ^3.4.17 | Nur Build-Rechner |
| NPM-09 | `lucide-react` | ^0.462.0 | Nur Build-Rechner |
| NPM-10 | `class-variance-authority` | ^0.7.1 | Nur Build-Rechner |
| NPM-11 | `clsx` | ^2.1.1 | Nur Build-Rechner |
| NPM-12 | `tailwind-merge` | ^2.6.0 | Nur Build-Rechner |
| NPM-13 | `tailwindcss-animate` | ^1.0.7 | Nur Build-Rechner |

### 3.3 Funktionale Bibliotheken

| # | Paket | Version | Wo benoetigt |
|---|-------|---------|--------------|
| NPM-14 | `@tanstack/react-query` | ^5.83.0 | Nur Build-Rechner |
| NPM-15 | `i18next` | ^25.7.4 | Nur Build-Rechner |
| NPM-16 | `react-i18next` | ^16.5.2 | Nur Build-Rechner |
| NPM-17 | `i18next-browser-languagedetector` | ^8.2.0 | Nur Build-Rechner |
| NPM-18 | `pdfjs-dist` | ^5.4.530 | Nur Build-Rechner |
| NPM-19 | `react-pdf` | ^10.3.0 | Nur Build-Rechner |
| NPM-20 | `react-markdown` | ^10.1.0 | Nur Build-Rechner |
| NPM-21 | `remark-gfm` | ^4.0.1 | Nur Build-Rechner |
| NPM-22 | `react-hook-form` | ^7.61.1 | Nur Build-Rechner |
| NPM-23 | `@hookform/resolvers` | ^3.10.0 | Nur Build-Rechner |
| NPM-24 | `zod` | ^3.25.76 | Nur Build-Rechner |
| NPM-25 | `dompurify` | ^3.3.1 | Nur Build-Rechner |
| NPM-26 | `react-syntax-highlighter` | ^16.1.0 | Nur Build-Rechner |
| NPM-27 | `react-resizable-panels` | ^2.1.9 | Nur Build-Rechner |
| NPM-28 | `recharts` | ^2.15.4 | Nur Build-Rechner |
| NPM-29 | `date-fns` | ^3.6.0 | Nur Build-Rechner |
| NPM-30 | `embla-carousel-react` | ^8.6.0 | Nur Build-Rechner |
| NPM-31 | `sonner` | ^1.7.4 | Nur Build-Rechner |
| NPM-32 | `cmdk` | ^1.1.1 | Nur Build-Rechner |
| NPM-33 | `next-themes` | ^0.3.0 | Nur Build-Rechner |
| NPM-34 | `vaul` | ^0.9.9 | Nur Build-Rechner |
| NPM-35 | `input-otp` | ^1.4.2 | Nur Build-Rechner |
| NPM-36 | `react-day-picker` | ^8.10.1 | Nur Build-Rechner |

### 3.4 devDependencies (nur Build-Tools)

| # | Paket | Version | Wo benoetigt |
|---|-------|---------|--------------|
| NPM-37 | `eslint` | ^9.32.0 | Nur Build-Rechner |
| NPM-38 | `autoprefixer` | ^10.4.21 | Nur Build-Rechner |
| NPM-39 | `postcss` | ^8.5.6 | Nur Build-Rechner |
| NPM-40 | `@tailwindcss/typography` | ^0.5.16 | Nur Build-Rechner |
| NPM-41 | `@types/*` (5 Pakete) | diverse | Nur Build-Rechner |

---

## Kategorie 4: Hardware-Anforderungen (1 Container, POC)

| # | Ressource | Wert | Artifactory Status |
|---|-----------|------|--------------------|
| HW-01 | CPU | 1 - 1.5 vCPU | [ ] In Bearbeitung |
| HW-02 | RAM | 2Gi | [ ] In Bearbeitung |
| HW-03 | Dokumenten-Storage (PVC) | 1Gi | [ ] In Bearbeitung |
| HW-04 | Case-Daten-Storage (PVC) | 2Gi | [ ] In Bearbeitung |
| HW-05 | Replicas | 1 | [x] Erledigt |
| HW-06 | GPU | Nicht benoetigt | [x] Erledigt |
| HW-07 | Port | 8000 (TCP) | [x] Erledigt |

---

## Kategorie 5: Netzwerk / Externer Zugang

| # | Ziel | Protokoll | Port | Zweck | Benoetigt? | Artifactory Status |
|---|------|-----------|------|-------|------------|--------------------|
| NET-01 | LiteLLM Proxy (intern) | HTTP | konfigurierbar | LLM-Anfragen | **Ja (Laufzeit)** | [ ] In Bearbeitung |
| ~~NET-02~~ | ~~generativelanguage.googleapis.com~~ | ~~HTTPS~~ | ~~443~~ | ~~Gemini API direkt~~ | **Nein** (LiteLLM) | [x] Nicht noetig |
| ~~NET-03~~ | ~~npm Registry~~ | ~~HTTPS~~ | ~~443~~ | ~~npm Pakete~~ | **Nein** (extern gebaut) | [x] Nicht noetig |
| NET-04 | PyPI / Artifactory | HTTPS | 443 | pip Pakete (nur Build) | Ja (nur Build) | [ ] In Bearbeitung |
| NET-05 | Eingehend (Browser/Ingress) | HTTP | 8000 | ACTE App Zugang | **Ja (Laufzeit)** | [ ] In Bearbeitung |

---

## Zusammenfassung

### Was in Artifactory geprueft werden muss

| Kategorie | Anzahl | Was genau |
|-----------|--------|-----------|
| Docker Base Image | **1** | `python:3.12-slim` |
| Python pip Pakete | **14** | 5 Kern + 6 Doku + 2 HTTP + 1 Config |
| npm Pakete | **0** | Extern gebaut, nicht in Artifactory noetig |
| Hardware | **4** | CPU, RAM, 2x PVC Storage |
| Netzwerk (Laufzeit) | **2** | LiteLLM Proxy + eingehend Port 8000 |
| Netzwerk (nur Build) | **1** | PyPI / Artifactory fuer pip |

### Was NICHT mehr benoetigt wird

| Entfallen | Begruendung |
|-----------|-------------|
| `node` Docker Image | Frontend wird extern gebaut |
| `google-generativeai` Python SDK | LiteLLM Proxy ersetzt direkten Gemini-Zugang |
| npm Registry Zugang | Frontend wird extern gebaut |
| Google API Netzwerk-Zugang | LiteLLM Proxy ist intern |

### Artifactory-Pruefung: Nur diese 15 Punkte

```
Docker:
  [ ] python >= 3.12-slim

Python (pip):
  [ ] fastapi == 0.104.1
  [ ] uvicorn == 0.24.0
  [ ] websockets == 12.0
  [ ] pydantic == 2.5.2
  [ ] python-multipart == 0.0.21
  [ ] Pillow == 10.2.0
  [ ] pdfplumber == 0.11.0
  [ ] markdownify == 1.2.2
  [ ] beautifulsoup4 == 4.14.3
  [ ] html2text == 2024.2.26
  [ ] langdetect == 1.0.9
  [ ] httpx == 0.28.1
  [ ] aiohttp == 3.9.1
  [ ] python-dotenv == 1.0.0

Netzwerk:
  [ ] Zugang zu LiteLLM Proxy (HTTP, intern)
  [ ] Zugang zu PyPI/Artifactory (nur Build-Zeit)
```

---

**Naechster Schritt:** Diese 15 Punkte gegen Artifactory pruefen und Status aktualisieren zu:
- `[x] Verfuegbar`
- `[ ] Anfrage stellen`
- `[x] Nicht noetig`
