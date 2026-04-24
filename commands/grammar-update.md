---
description: Update existing grammar files after adding a new language, upgrading a framework version, or noticing that the code-graph extraction is missing constructs the grammars should catch. Reads the existing grammars, re-scans the codebase, and merges additions without discarding prior valid knowledge.
argument-hint: [optional: project name override]
---

# Update Project Grammars

Delegate to the **BO-project-grammar-builder** sub-agent via the Task tool to re-scan the codebase and update the existing grammar files.

**Project name override (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-project-grammar-builder` sub-agent with the following instruction:

> Perform an update of the project grammars.
>
> - Mode: **update** (the `./docs/{project}_grammars/` directory must already exist with prior grammar files; if missing or empty, stop and recommend `/grammar-build` instead).
> - Project name: use `$ARGUMENTS` if non-empty, otherwise derive from the working directory's parent folder name.
> - Read each existing grammar file first. Preserve the original `generated_at` (the first-run timestamp) and update `last_updated` to the current ISO-8601 time.
> - Re-scan the codebase topology and manifests. For each language:
>   - If new frameworks are detected, add them and query Context7 for their pattern syntax.
>   - If framework versions have changed (check lockfiles), re-verify the regex patterns via Context7 — pattern syntax may differ across versions.
>   - If a previously-detected framework is no longer in use, drop its entry from `frameworks` and remove its pattern group. Do not keep a `deprecated` array — git history carries the audit trail; grammar files describe only the current language surface.
> - Output: rewrite each affected grammar file with merged content. Do not touch grammar files for languages whose versions and frameworks are unchanged.
>
> Follow the agent's built-in workflow and refusal conditions (ambiguous state of the grammars directory, Context7 unavailability for changed frameworks, etc.).

## After the agent returns

Surface the agent's report verbatim. The report should summarize: languages added, languages with framework additions, languages with version changes triggering pattern updates, frameworks dropped (no longer in use), Context7 warnings, and files written vs. unchanged.