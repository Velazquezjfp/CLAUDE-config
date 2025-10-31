---
description: Analyze impact and dependencies of file changes using code-graph knowledge base
allowed-tools:
  - mcp__knowledge-graph-custom-path
argument-hint: <filepath> or <filepath1> <filepath2> ...
---

You are analyzing the impact of potential changes to code files using the knowledge graph at `./docs/code-graph/code-graph.json`.

## Files to Analyze
The user provided: $ARGUMENTS

Parse this as either:
- Single file: `src/api/python.py`
- Multiple files: `src/api/python.py src/api/python_2.py`

## Your Task

1. **Initialize the Knowledge Graph MCP**
   - Connect to the knowledge graph at `./docs/code-graph/code-graph.json`

2. **Query Each File**
   For each file provided:
   - Search for entities matching the filepath pattern in the knowledge graph
   - Use `search_nodes` or `open_nodes` to find the file entity
   - Query all relations connected to this entity
   - Focus on: imports, dependencies, database interactions, API endpoints, consumers

3. **Generate Risk Assessment**
   Provide a concise, scannable summary with:
   
   **🎯 Breaking Change Risk**: [HIGH/MEDIUM/LOW]
   
   **💾 Database Impact**:
   - What tables/schemas are directly accessed or modified
   - Any FK relationships or constraints affected
   
   **🔌 API Dependencies**:
   - Which endpoints or methods are exposed
   - What external services or clients consume this
   
   **📦 Downstream Consumers**:
   - Which files/modules import or depend on this
   - Any critical workflows that would break
   
   **⚠️ Required Updates**:
   - Brief list of files that need changes if this file changes
   - Documentation or config files to update

4. **Keep it Actionable**
   - Use bullet points for clarity
   - Focus on WHAT could break, not implementation details
   - Help planning, not exhaustive documentation
   - Max 10-15 lines total per file

## Example Output Format
```
📊 Impact Analysis: src/api/python.py

🎯 Breaking Change Risk: MEDIUM

💾 Database Impact:
- Queries: users, user_sessions tables
- Modifies: user_sessions.last_active column

🔌 API Dependencies:
- Exposes: /api/v1/users, /api/v1/auth endpoints
- Consumed by: web frontend, mobile app

📦 Downstream Consumers:
- src/services/auth_service.py
- tests/integration/test_users.py

⚠️ Required Updates:
- Update API spec: docs/openapi.yaml
- Sync frontend types: web/src/types/user.ts
```
