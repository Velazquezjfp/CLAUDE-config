# ACTE Companion - Abhaengigkeiten Checkliste

> **Scope:** Nur ACTE Companion (Frontend + Backend) in **1 Docker-Container**.
> Anonymisierungsdienst und IDIRS Document Search sind NICHT enthalten (spaetere Phase).
> Zweck: Vergleich mit Artifactory-Verfuegbarkeit fuer gesicherte Umgebung.

**Datum:** 2026-04-14
**Architektur:** 1 Docker-Container (POC/Demo)

---

## Architektur: 1 Docker Container

```
python:3.12-slim  (Runtime - finales Image)
  + node:20       (nur Build-Stage, NICHT im finalen Image)
  |
  ├── React Build (dist/)  -->  FastAPI StaticFiles
  ├── FastAPI Backend       -->  10 REST Router + WebSocket Chat
  └── Uvicorn Server        -->  Port 8000 (einziger Port)
```

**Warum 1 Container:**
- POC/Demo: Einfachheit bevorzugt
- 1 Docker-Image in Artifactory statt 2-3
- Kein NGINX noetig
- Kein Container-Networking noetig
- FastAPI serviert Frontend-Dateien direkt

---

## Kategorie 1: Docker Base Images

| # | Image | Version | Zweck | Im finalen Image? | Artifactory Status |
|---|-------|---------|-------|--------------------|--------------------|
| D-01 | `python` | >= 3.12-slim | Runtime: Backend + Gesamtes Image | **Ja** | [ ] In Bearbeitung |
| D-02 | `node` | >= 20 LTS | Build-Stage: `npm ci && npm run build` | **Nein** (nur Build) | [ ] In Bearbeitung |

> **Hinweis zu D-02:** Falls `node` nicht in Artifactory verfuegbar ist, kann die React-App
> auch **ausserhalb von Docker** gebaut werden. Dann kopiert man nur den fertigen `dist/`
> Ordner ins Python-Image. In dem Fall ist D-02 nicht noetig.

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

### 2.2 KI-Integration (Pflicht - Gemini-Verbindung)

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| PY-06 | `google-generativeai` | 0.3.1 | Gemini API SDK | Ja* | [ ] In Bearbeitung |

> \* Ersetzbar durch direkten HTTPS-Call mit `httpx`. Der Code nutzt nur `generate_content(prompt)`.
> Aber: mehr Aufwand, fuer POC ist das SDK einfacher.

### 2.3 Dokumentenverarbeitung (Pflicht - im Code importiert)

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| PY-07 | `Pillow` | 10.2.0 | Bildverarbeitung | Nein | [ ] In Bearbeitung |
| PY-08 | `pdfplumber` | 0.11.0 | PDF-Textextraktion | Ja* | [ ] In Bearbeitung |
| PY-09 | `markdownify` | 1.2.2 | HTML-zu-Markdown (Chat-Antworten) | Ja* | [ ] In Bearbeitung |
| PY-10 | `beautifulsoup4` | 4.14.3 | HTML-Parsing (fuer markdownify) | Ja* | [ ] In Bearbeitung |
| PY-11 | `html2text` | 2024.2.26 | E-Mail-Verarbeitung (EML-Dateien) | Ja* | [ ] In Bearbeitung |
| PY-12 | `langdetect` | 1.0.9 | Spracherkennung in Dokumenten | Ja* | [ ] In Bearbeitung |

> \* `pdfplumber` -> Alternative: `PyMuPDF` (haeufiger in Artifactory).
> `markdownify` + `beautifulsoup4` -> koennte entfallen, dann werden Gemini-Antworten nicht formatiert.
> `html2text` -> nur fuer E-Mail-Feature, koennte fuer POC entfallen.
> `langdetect` -> nur fuer automatische Spracherkennung, koennte fuer POC entfallen.

### 2.4 HTTP-Clients (Im Code importiert - fuer spaetere Dienste)

| # | Paket | Version | Zweck | Jetzt aktiv genutzt? | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|----------------------|------------|--------------------|
| PY-13 | `httpx` | 0.28.1 | HTTP Client (IDIRS Proxy Code) | Nein (IDIRS spaeter) | Ja* | [ ] In Bearbeitung |
| PY-14 | `aiohttp` | 3.9.1 | Async HTTP (Anonymisierung Code) | Nein (Anon. spaeter) | Ja* | [ ] In Bearbeitung |

> \* Diese beiden Pakete werden **aktuell nicht aktiv genutzt** da Anonymisierung und IDIRS
> noch nicht bereitgestellt werden. ABER: Der Backend-Code importiert sie beim Start.
> **Optionen:**
> 1. Beide installieren (einfachste Loesung, Code laeuft ohne Aenderung)
> 2. Imports im Code zu lazy-imports aendern (dann entfallen beide fuer Phase 1)
> 3. Nur `httpx` behalten und `aiohttp` durch `httpx` ersetzen (1 Paket statt 2)

### 2.5 Konfiguration

| # | Paket | Version | Zweck | Ersetzbar? | Artifactory Status |
|---|-------|---------|-------|------------|--------------------|
| PY-15 | `python-dotenv` | 1.0.0 | `.env` Datei laden | Ja* | [ ] In Bearbeitung |

> \* Entfaellt in Kubernetes (Umgebungsvariablen ueber ConfigMap/Secret).
> Aber: Der Code ruft `load_dotenv()` beim Start auf. Einfachste Loesung: installieren.

---

## Kategorie 3: Frontend-Bibliotheken (npm)

> **Wichtig:** npm-Pakete sind nur in der **Build-Stage** noetig.
> Das finale Docker-Image enthaelt nur kompilierte Dateien (`dist/` = HTML, JS, CSS).
> Diese Pakete sind NICHT im laufenden Container.

> **Artifactory-Strategie fuer npm:**
> - Option A: npm-Registry in Artifactory als Proxy konfigurieren -> alle Pakete automatisch
> - Option B: `npm ci` lokal ausfuehren, `dist/` ins Image kopieren -> kein npm in Docker noetig

### 3.1 Kern-Framework

| # | Paket | Version | Zweck | Artifactory Status |
|---|-------|---------|-------|--------------------|
| NPM-01 | `react` | ^18.3.1 | UI Framework | [ ] In Bearbeitung |
| NPM-02 | `react-dom` | ^18.3.1 | React DOM Rendering | [ ] In Bearbeitung |
| NPM-03 | `react-router-dom` | ^6.30.1 | Client-Side Routing | [ ] In Bearbeitung |
| NPM-04 | `typescript` | ^5.8.3 | Typsystem (devDep) | [ ] In Bearbeitung |
| NPM-05 | `vite` | ^5.4.19 | Build Tool (devDep) | [ ] In Bearbeitung |
| NPM-06 | `@vitejs/plugin-react-swc` | ^3.11.0 | React Compiler (devDep) | [ ] In Bearbeitung |

### 3.2 UI-Komponenten

| # | Paket | Version | Zweck | Artifactory Status |
|---|-------|---------|-------|--------------------|
| NPM-07 | `@radix-ui/*` (22 Pakete) | diverse | shadcn/ui Basis-Komponenten | [ ] In Bearbeitung |
| NPM-08 | `tailwindcss` | ^3.4.17 | CSS Framework (devDep) | [ ] In Bearbeitung |
| NPM-09 | `lucide-react` | ^0.462.0 | Icons | [ ] In Bearbeitung |
| NPM-10 | `class-variance-authority` | ^0.7.1 | CSS Varianten (shadcn) | [ ] In Bearbeitung |
| NPM-11 | `clsx` | ^2.1.1 | CSS Klassen-Merge | [ ] In Bearbeitung |
| NPM-12 | `tailwind-merge` | ^2.6.0 | Tailwind Klassen-Merge | [ ] In Bearbeitung |
| NPM-13 | `tailwindcss-animate` | ^1.0.7 | Animationen | [ ] In Bearbeitung |

### 3.3 Funktionale Bibliotheken

| # | Paket | Version | Zweck | Artifactory Status |
|---|-------|---------|-------|--------------------|
| NPM-14 | `@tanstack/react-query` | ^5.83.0 | Async State Management | [ ] In Bearbeitung |
| NPM-15 | `i18next` | ^25.7.4 | Internationalisierung (DE/EN) | [ ] In Bearbeitung |
| NPM-16 | `react-i18next` | ^16.5.2 | React i18n Binding | [ ] In Bearbeitung |
| NPM-17 | `i18next-browser-languagedetector` | ^8.2.0 | Sprache erkennen | [ ] In Bearbeitung |
| NPM-18 | `pdfjs-dist` | ^5.4.530 | PDF-Rendering im Browser | [ ] In Bearbeitung |
| NPM-19 | `react-pdf` | ^10.3.0 | PDF-Viewer Komponente | [ ] In Bearbeitung |
| NPM-20 | `react-markdown` | ^10.1.0 | Markdown Rendering (Chat) | [ ] In Bearbeitung |
| NPM-21 | `remark-gfm` | ^4.0.1 | GitHub Markdown Tabellen | [ ] In Bearbeitung |
| NPM-22 | `react-hook-form` | ^7.61.1 | Formular-Verwaltung | [ ] In Bearbeitung |
| NPM-23 | `@hookform/resolvers` | ^3.10.0 | Formular-Validierung | [ ] In Bearbeitung |
| NPM-24 | `zod` | ^3.25.76 | Schema-Validierung | [ ] In Bearbeitung |
| NPM-25 | `dompurify` | ^3.3.1 | HTML Sanitizer (XSS-Schutz) | [ ] In Bearbeitung |
| NPM-26 | `react-syntax-highlighter` | ^16.1.0 | Code-Highlighting (Chat) | [ ] In Bearbeitung |
| NPM-27 | `react-resizable-panels` | ^2.1.9 | Teilbare Workspace-Panels | [ ] In Bearbeitung |
| NPM-28 | `recharts` | ^2.15.4 | Diagramme/Charts | [ ] In Bearbeitung |
| NPM-29 | `date-fns` | ^3.6.0 | Datumsformatierung | [ ] In Bearbeitung |
| NPM-30 | `embla-carousel-react` | ^8.6.0 | Karussell | [ ] In Bearbeitung |
| NPM-31 | `sonner` | ^1.7.4 | Toast-Benachrichtigungen | [ ] In Bearbeitung |
| NPM-32 | `cmdk` | ^1.1.1 | Command-Palette | [ ] In Bearbeitung |
| NPM-33 | `next-themes` | ^0.3.0 | Theme (Dark/Light) | [ ] In Bearbeitung |
| NPM-34 | `vaul` | ^0.9.9 | Drawer-Komponente | [ ] In Bearbeitung |
| NPM-35 | `input-otp` | ^1.4.2 | OTP-Eingabe | [ ] In Bearbeitung |
| NPM-36 | `react-day-picker` | ^8.10.1 | Datumsauswahl | [ ] In Bearbeitung |

### 3.4 devDependencies (nur Build-Tools)

| # | Paket | Version | Zweck | Artifactory Status |
|---|-------|---------|-------|--------------------|
| NPM-37 | `eslint` | ^9.32.0 | Code-Linting | [ ] In Bearbeitung |
| NPM-38 | `autoprefixer` | ^10.4.21 | CSS Autoprefixer | [ ] In Bearbeitung |
| NPM-39 | `postcss` | ^8.5.6 | CSS Verarbeitung | [ ] In Bearbeitung |
| NPM-40 | `@tailwindcss/typography` | ^0.5.16 | Typografie-Plugin | [ ] In Bearbeitung |
| NPM-41 | `@types/react` | ^18.3.23 | TypeScript Typen | [ ] In Bearbeitung |
| NPM-42 | `@types/react-dom` | ^18.3.7 | TypeScript Typen | [ ] In Bearbeitung |
| NPM-43 | `@types/dompurify` | ^3.0.5 | TypeScript Typen | [ ] In Bearbeitung |
| NPM-44 | `@types/node` | ^22.16.5 | TypeScript Typen | [ ] In Bearbeitung |
| NPM-45 | `@types/react-syntax-highlighter` | ^15.5.13 | TypeScript Typen | [ ] In Bearbeitung |

---

## Kategorie 4: Hardware-Anforderungen (1 Container)

| # | Ressource | Minimum (POC) | Empfohlen | Artifactory Status |
|---|-----------|---------------|-----------|-------|
| HW-01 | CPU | 350m (0.35 vCPU) | 1.5 vCPU | [ ] In Bearbeitung |
| HW-02 | RAM | 384Mi | 1.25Gi | [ ] In Bearbeitung |
| HW-03 | Dokumenten-Storage (PVC) | 5Gi | 10Gi | [ ] In Bearbeitung |
| HW-04 | Case-Daten-Storage (PVC) | 2Gi | 5Gi | [ ] In Bearbeitung |
| HW-05 | Replicas | 1 | 1 (POC) | [x] Erledigt |
| HW-06 | GPU | Nicht benoetigt | - | [x] Erledigt |
| HW-07 | Port | 8000 (TCP) | 8000 | [x] Erledigt |

---

## Kategorie 5: Netzwerk / Externer Zugang

| # | Ziel | Protokoll | Port | Zweck | Richtung | Artifactory Status |
|---|------|-----------|------|-------|----------|--------------------|
| NET-01 | `generativelanguage.googleapis.com` | HTTPS | 443 | Google Gemini API | Ausgehend | [ ] In Bearbeitung |
| NET-02 | npm Registry / Artifactory | HTTPS | 443 | npm Pakete (nur Build) | Ausgehend | [ ] In Bearbeitung |
| NET-03 | PyPI / Artifactory | HTTPS | 443 | pip Pakete (nur Build) | Ausgehend | [ ] In Bearbeitung |
| NET-04 | Eingehend (Browser/Ingress) | HTTP | 8000 | ACTE App Zugang | Eingehend | [ ] In Bearbeitung |

> **NET-01** ist die einzige Laufzeit-Abhaengigkeit nach aussen.
> NET-02 und NET-03 werden nur beim Docker-Image-Build benoetigt und koennen
> ueber Artifactory als Proxy laufen.

---

## Zusammenfassung

| Kategorie | Anzahl | Bemerkung |
|-----------|--------|-----------|
| Docker Base Images | 2 | `python:3.12-slim` (Pflicht) + `node:20` (nur Build) |
| Python pip Pakete | 15 | 5 Kern + 1 KI + 6 Doku + 2 HTTP* + 1 Config |
| npm Pakete | ~45 | Nur Build-Stage, nicht im finalen Image |
| Hardware-Ressourcen | 7 | 1 Container, kein GPU, Port 8000 |
| Netzwerk | 4 | 1 Laufzeit (Gemini API), 3 nur Build |
| **Gesamt Abhaengigkeiten** | **~73** | |

> \* `httpx` und `aiohttp` sind im Code importiert (fuer spaetere IDIRS/Anonymisierung).
> Muessen installiert werden damit der Code startet, werden aber aktuell nicht aktiv genutzt.

---

**Naechster Schritt:** Artifactory-Inhalt pruefen und `[ ] In Bearbeitung` aktualisieren zu:
- `[x] Verfuegbar` - In Artifactory vorhanden
- `[ ] Anfrage stellen` - Muss in Artifactory angefragt werden
- `[x] Nicht noetig` - Kann umgangen werden (z.B. lokaler Build)
