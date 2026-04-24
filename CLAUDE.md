# Global Rules for Claude Code

## Core Principles

**Simplicity First (KISS)**
- Always choose the simplest solution that meets requirements
- Avoid complexity unless strictly necessary
- Clean up any temporary files created during development

**Quality Over Complexity**
- Build general-purpose solutions that handle all valid inputs
- Focus on the actual problem logic, not just passing tests
- "Production ready" means robustness and elegance, not feature bloat

**Maintainable Code**
- Write code other developers can easily understand
- Apply established best practices and design principles
- Prioritize clarity and readability

---

## Environment & Package Management

**Node.js**
- Always use `nvm` to manage Node versions — never `apt install nodejs`

**Python**
- Always verify a virtual environment is active before running any `pip install`
- If no venv is active: stop and tell the user — do not proceed with the installation
- Use `pytest` for testing, always within the current virtual environment

---

## Architecture & Patterns

- Prefer modular architecture: separate concerns, avoid monolithic functions or files
- Use FastAPI for Python backends

---

## Practices

**Never assume — always verify**
- Never assume endpoint URLs, resource paths, or API structures
- Always check the project context first; if not found, ask the user

**Dependency management**
- Use Context7 (MCP) to look up stable versions when adding or upgrading any dependency
- Prefer the latest stable release — avoid alphas, betas, or release candidates unless explicitly requested

**Secret files — read-only prohibition**
- Never read, print, or include content from secret files: `.env`, `.secrets`, `*.key`, `credentials.json`, or any file that appears to contain credentials or tokens
- If such a file is needed to understand the project, ask the user to share only the relevant non-sensitive keys/structure

**Be proactive — never delegate back**
- Do not hand work back to the user without first attempting to solve it or finding alternatives
- If blocked or uncertain, research the options yourself, form a recommendation, then ask: "I found X and Y — should I implement X, or would you prefer I explore Y first?"
- Asking for a decision is fine; asking the user to do the work for you is not

---

## Anti-Patterns to Avoid
- Over-engineering solutions
- Hard-coding values for specific test cases
- Unnecessary backward compatibility
- Premature optimization or feature creep
- Assuming infrastructure details not present in context
- Delegating problems back to the user without first attempting a solution

---

**Your goal: Build functional, simple, and robust software.**
