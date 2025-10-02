---
description: Create implementation plan and todo list for a specific requirement
argument-hint: <requirement-id>
---

# Start Requirement Implementation

Create a detailed implementation plan and todo list for requirement: **$ARGUMENTS**

## Instructions

1. **Read the implementation plan**
   - Open and read `docs/implementation_plan.md`
   - Locate requirement $ARGUMENTS in the plan
   - Check for:
     - Dependencies (which requirements must be completed first)
     - Specific file types allowed for this requirement
     - Scope restrictions and what NOT to do
     - Phase/priority assignment
     - Any special instructions or constraints

2. **Read the requirement specification**
   - Open and read `docs/requirements/requirements.md`
   - Locate the requirement ID: $ARGUMENTS
   - Extract all details about:
     - Requirement description and objectives
     - Acceptance criteria
     - Dependencies on other requirements
     - Constraints and business rules
     - Expected behavior

3. **Understand the codebase structure**
   - Read `docs/code-graph/code-graph.json`
   - Identify relevant entities, modules, and classes
   - Map out relationships and dependencies
   - Understand the architecture affected by this requirement
   - Identify which components need to be modified or created

4. **Review test cases for context**
   - Read test cases in `docs/tests/$ARGUMENTS/`
   - Understand expected inputs and outputs
   - Identify edge cases and validation rules
   - Note the expected behavior from test scenarios
   - **Important:** Focus on understanding expected results, NOT on implementing tests

5. **Analyze impact and dependencies**
   - Verify prerequisite requirements are completed (from implementation plan)
   - Identify which files and modules need changes
   - Determine if new entities need to be created
   - Check for potential breaking changes
   - Identify integration points with existing code
   - Review database schema changes if needed
   - Check API modifications if applicable
   - **Strictly adhere to file type restrictions** from implementation plan

6. **Create detailed todo list**
   - Break down the requirement into actionable tasks
   - Order tasks by dependencies (what needs to be done first)
   - For each task, specify:
     - The file(s) to modify or create
     - The type of change (new function, modify existing, refactor)
     - Key considerations or gotchas
   - Focus **strictly on implementation tasks**, not testing
   - Include tasks for updating documentation if schema/API changes
   - **Do not deviate** from scope defined in implementation plan

7. **Present the implementation plan**
   - Show the todo list in a clear, numbered format
   - Highlight critical dependencies between tasks
   - Note any risks or areas requiring special attention
   - Confirm adherence to implementation plan constraints
   - Suggest the order of implementation
   - Be ready to start implementing once the plan is approved

## Output Format

Present the plan as:
- **Implementation Plan Notes**: Key constraints and dependencies from the plan
- **Requirement Summary**: Brief overview of what needs to be implemented
- **Affected Components**: List of modules/files that will change
- **Implementation Todo List**: Numbered, ordered list of tasks
- **Key Considerations**: Important notes, risks, or dependencies
