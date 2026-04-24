---
description: Review recent git changes and update database documentation if needed
argument-hint: <summary of changes>
---

# Update Database Documentation

Review the latest git commit changes and determine if the database documentation needs updating.

**Summary of changes:** $ARGUMENTS

## Instructions

1. **Analyze the latest commit**
   - Run `git log -1 --stat` to see changed files
   - Run `git diff HEAD~1` to review the actual changes
   - Identify database-related changes:
     - New tables or collections
     - Modified schemas or column definitions
     - Changed indexes or constraints
     - New or updated migrations
     - Modified relationships (foreign keys, references)
     - Changed stored procedures or functions
     - Updated triggers or views

2. **Review current database documentation**
   - Read files in `docs/database/` directory
   - Understand the existing documentation structure
   - Identify which database docs correspond to the changed code

3. **Determine update requirements**
   - Check if changes affect:
     - Table/collection schemas
     - Entity Relationship Diagrams (ERDs)
     - Column descriptions and data types
     - Indexes and performance considerations
     - Foreign key relationships
     - Database constraints and validations
     - Migration history
     - Data model descriptions

4. **Delegate to bone-database-documenter sub-agent**
   - If updates are needed, use the bone-database-documenter sub-agent to:
     - Add documentation for new tables/collections
     - Update modified schema definitions
     - Remove documentation for deprecated tables
     - Update ERD diagrams if schema relationships changed
     - Document new migrations and their purpose
     - Update data dictionary entries
     - Ensure consistency with actual database structure
     - Validate that all tables and relationships are properly documented

5. **Report results**
   - Provide a clear summary of what was updated in `docs/database/`
   - If no updates were needed, confirm the documentation is still accurate
   - List specific files and sections that were added, modified, or removed
