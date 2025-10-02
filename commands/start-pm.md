---
description: Analyze requirements and create prioritized implementation plan
argument-hint: 
---

# Project Management - Implementation Planning

Create a strategic implementation plan by analyzing the codebase, requirements, and dependencies.

## Instructions

1. **Read the codebase structure**
   - Read `docs/code-graph/code-graph.json`
   - Understand entities, relationships, and dependencies
   - Identify key modules and their interconnections

2. **Read all requirements**
   - Read `docs/requirements/requirements.md`
   - List all requirements (FR-XXX, NFR-XXX, DB-XXX, etc.)
   - Understand what each requirement aims to achieve
   - Note acceptance criteria and constraints

3. **Review test cases**
   - Read test files in `docs/tests/`
   - Understand expected behavior for each requirement
   - Identify validation rules and edge cases

4. **Analyze dependencies and relationships**
   - Identify which requirements are independent (can be done in parallel)
   - Identify which requirements depend on others (must be done in sequence)
   - Map requirements to affected code components
   - Determine if any requirements conflict or overlap

5. **Create implementation strategy**
   - Group independent requirements that can be worked on simultaneously
   - Order dependent requirements in the correct sequence
   - For each requirement, specify:
     - Priority level (must-have first, nice-to-have later)
     - Dependencies (what needs to be completed before this)
     - Affected files/modules from the code-graph
     - Estimated complexity (simple, moderate, complex)
   
6. **Define execution order**
   - Start with foundational requirements (database, core models)
   - Then infrastructure requirements (APIs, services)
   - Then feature requirements (business logic)
   - Finally integration and non-functional requirements
   - **Keep it simple**: choose the safest, most straightforward path

7. **Document the plan**
   - Save the implementation plan to `docs/implementation_plan.md`
   - Use clear structure:
     - **Phase 1**: Independent foundational requirements
     - **Phase 2**: Dependent feature requirements  
     - **Phase 3**: Integration and polish requirements
   - For each requirement, clearly state:
     - Requirement ID and brief description
     - File types to modify (e.g., "models only", "API routes + services", "database migrations")
     - Dependencies (which requirements must be completed first)
     - Rationale for this order

## Key Principles

- **Keep it simple**: Favor straightforward approaches over complex ones
- **Safety first**: Choose the safest execution path with minimal risk
- **Clear scope**: For independent requirements, precisely define which file types should be touched
- **No deviation**: Once file types are specified for a requirement, stick to that scope

## Output

Create `docs/implementation_plan.md` with a clear, actionable roadmap for implementing all requirements in the optimal order.
