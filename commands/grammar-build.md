---
description: Generate grammar files for the project from scratch. Scans the codebase, detects languages and framework versions (using Context7 MCP for accuracy), and writes one JSON file per language under docs/{project}_grammars/. Run this once at project start, and re-run via /grammar-update when you introduce new languages or upgrade major framework versions.
argument-hint: [optional: project name override]
---

# Build Project Grammars

Delegate to the **BO-project-grammar-builder** sub-agent via the Task tool to scan the codebase and generate regex-based grammar files.

**Project name override (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-project-grammar-builder` sub-agent with the following instruction:

> Perform a full build of the project grammars.
>
> - Mode: **initialize** (the `./docs/{project}_grammars/` directory should not exist or be empty; if it has content, stop and ask whether to use `/grammar-update` instead).
> - Project name: use `$ARGUMENTS` if non-empty, otherwise derive from the working directory's parent folder name.
> - Output: create `./docs/{project}_grammars/` and write one `{language}.json` per detected language. Frameworks fold into their host language file (React into `javascript.json` or `typescript.json`, FastAPI into `python.json`, etc.).
>
> Follow the agent's built-in workflow: topology pass → manifest and lockfile reading for version detection → minimal source sampling (1–3 files per language) to confirm which frameworks are in use → Context7 MCP queries to confirm version-accurate regex syntax for each framework → emit grammar files with the `patterns` dictionary schema.
>
> Do not emit `relational_constructs`, file paths, symbol names, or any codebase-specific instance. This is a pattern dictionary, not a code graph.

## After the agent returns

Surface the agent's report verbatim. The report should list: project name, mode, languages detected with runtime versions, frameworks detected with versions, Context7 enrichment status per framework, and files written. Pass any warnings (Context7 unavailable for specific libraries, languages detected without clear version info) through unchanged.
