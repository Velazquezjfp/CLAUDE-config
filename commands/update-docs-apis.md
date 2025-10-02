---
description: Review recent git changes and update API documentation if needed
argument-hint: <summary of changes>
---

# Update API Documentation

Review the latest git commit changes and determine if the API documentation needs updating.

**Summary of changes:** $ARGUMENTS

## Instructions

1. **Analyze the latest commit**
   - Run `git log -1 --stat` to see changed files
   - Run `git diff HEAD~1` to review the actual changes
   - Identify API-related changes:
     - New endpoints or routes
     - Modified request/response schemas
     - Changed parameters or query strings
     - Updated authentication/authorization requirements
     - New or modified data models
     - Changed error responses

2. **Review current API documentation**
   - Read files in `docs/apis/` directory
   - Understand the existing documentation structure
   - Identify which API docs correspond to the changed code

3. **Determine update requirements**
   - Check if changes affect:
     - Endpoint definitions (method, path, description)
     - Request/response examples
     - Parameter specifications
     - Authentication methods
     - Status codes and error messages
     - Data type definitions
     - API versioning information

4. **Delegate to bone-api-documenter sub-agent**
   - If updates are needed, use the bone-api-documenter sub-agent to:
     - Add documentation for new endpoints
     - Update modified endpoint specifications
     - Remove documentation for deprecated endpoints
     - Update examples to reflect current behavior
     - Ensure consistency with OpenAPI/Swagger specs if applicable
     - Update changelog or version notes
     - Validate that all endpoints are properly documented

5. **Report results**
   - Provide a clear summary of what was updated in `docs/apis/`
   - If no updates were needed, confirm the documentation is still accurate
   - List specific files and sections that were added, modified, or removed
