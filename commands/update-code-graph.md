---
description: Review recent git changes and update the code graph if needed
argument-hint: <summary of changes>
---

# Update Code Graph

Review the latest git commit changes and determine if the code graph needs updating.

**Summary of changes:** $ARGUMENTS

## Instructions

1. **Analyze the latest commit**
   - Run `git log -1 --stat` to see changed files
   - Run `git diff HEAD~1` to review the actual changes
   - Identify the nature of changes (new classes, functions, modules, relationships)

2. **Review current code graph**
   - Read `docs/code-graph/code-graph.json`
   - Understand the existing structure and entities

3. **Determine update requirements**
   - Check if changes introduce:
     - New entities (classes, functions, modules)
     - Modified relationships between entities
     - Removed entities
     - Updated dependencies or imports
   - Assess impact on the existing graph structure

4. **Delegate to bone-code-graph-builder**
   - If updates are needed, use the bone-code-graph-builder sub-agent to:
     - Add new entities and relationships
     - Update modified entities
     - Remove obsolete entities
     - Ensure consistency with existing graph structure
     - Validate the updated graph structure

5. **Report results**
   - Provide a clear summary of what was updated
   - If no updates were needed, confirm the graph is still accurate
   - List specific entities/relationships that were added, modified, or removed
