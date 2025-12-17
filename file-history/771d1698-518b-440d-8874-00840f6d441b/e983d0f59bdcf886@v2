# Documentation Cleanup & Validation Removal Plan

## Overview
Update all documentation to reflect v2.1 dual database architecture changes and remove FK validations that no longer apply.

## Key Changes Summary
| Old | New | Status |
|-----|-----|--------|
| `/api/v1/requests` | `/api/v1/demands` | Renamed |
| `/api/v1/sub-groups` | `/api/v1/groups` | Renamed |
| `/api/v1/location-distances` | N/A | Removed |
| `location_distances` table | N/A | Doesn't exist in external DB |
| `calendars` table | N/A | Doesn't exist |
| `shift_templates` table | N/A | Doesn't exist |

## Phase 1: Remove Validations from API Routers

Remove only foreign key validations from teams and groups routers.

### Validations to REMOVE (only these 2):
1. **`api/routers/teams.py`** - Remove FK validation for region_id (lines 112-120, 180-190)
2. **`api/routers/groups.py`** - Remove FK validation for team_id (lines 110-117, 192-202), remove composite uniqueness check (lines 119-132)

### Validations to KEEP:
- 404 existence checks before UPDATE/DELETE (necessary)
- Required field checks for POST (necessary)
- Uniqueness checks in qualifications.py, regions.py, locations.py, divisions.py (keep)
- Constraints router 405 rejections (by design)

## Phase 2: Update Documentation Files

### 2.1 docs/API_ENDPOINTS.md (~3,400 lines)
**Actions:**
- Replace all `/api/v1/requests` → `/api/v1/demands`
- Replace all `/api/v1/sub-groups` → `/api/v1/groups`
- Delete Section 15: Location Distances entirely
- Remove `calendar_type` field references
- Keep port 8000 for deployed version (only use 8002 in local testing contexts)
- Add new endpoints: `/api/v1/divisions`, `/api/v1/demands-list`

### 2.2 docs/SQL_QUERIES_REFERENCE.md - COMPLETE REWRITE
**Purpose:** Comprehensive SQL reference for both databases (human readable + SQL agent compatible)

**New Structure:**
1. **Introduction** - Dual database overview
2. **External Database (150.241.245.65:5432/cff)** - Production data tables
3. **Internal Database (local container)** - Parameter tables
4. **Query Examples** - Organized by use case

**External Database Tables (13 core tables):**
| Table | Rows | Columns | Primary Key | Description |
|-------|------|---------|-------------|-------------|
| resources | 374 | 27 | resource_id | Personnel (internal/external) |
| demands | 50,896 | 34 | id | Maintenance demands (shifts) |
| assignments | 106,038 | 23 | id | Resource-to-demand assignments |
| absences | 6,190 | 13 | absence_id | Resource absences |
| regions | 3 | 7 | region_id | Regional hierarchy |
| teams | 61 | 8 | team_id | Team units |
| groups | 47 | 8 | group_id | Sub-groups within teams |
| divisions | 6 | 7 | division_id | Division organizational level |
| locations | 36 | 10 | location_id | Railway locations |
| qualifications | 101 | 10 | qualification_id | Skills/certifications |
| demands_list | 25,577 | 38 | id | Historical BSA records |
| operation_points | 761 | 10 | operation_points_id | Operational points |
| resource_category | 19 | 2 | id | Resource categories |

**Internal Database Tables:**
| Table | Purpose |
|-------|---------|
| legal_constraints | Swiss LDT (read-only) |
| company_policy_constraints | CFF policies |
| objective_weights | Optimization weights |
| utilization_targets | Efficiency targets |
| audit_log | Activity logging |

**Include for each table:**
- Complete column schema (name, type, nullable)
- Primary key and foreign keys
- Sample SELECT/INSERT/UPDATE/DELETE queries
- Common filtering patterns
- JOIN examples with related tables
- JSONB field queries (for availability_pattern, qualifications, assigned_resources)

### 2.3 docs/INTEGRATION_GUIDE.md (~2,234 lines)
**Actions:**
- Replace all `/requests` → `/demands`
- Replace all `/sub-groups` → `/groups`
- Update code examples with new endpoint names
- Keep port 8000 for deployed version (only use 8002 in local testing contexts)
- Remove location_distances integration examples

### 2.4 docs/DEPLOYMENT_GUIDE.md (~1,667 lines)
**Actions:**
- Keep port 8000 for deployed version
- Add external database configuration section
- Update environment variables documentation for dual DB

### 2.5 api/routers/ROUTER_SUMMARY.md
**Actions:**
- Rename "Sub-Groups Router" → "Groups Router"
- Rename "Requests Router" → "Demands Router"
- Update endpoint counts
- Remove location_distances references

## Phase 3: Test PUT/DELETE Operations

### Test Script (temp/test_crud.py)
Create a test script to verify:
1. GET all endpoints work
2. POST creates a test record
3. PUT updates the test record
4. DELETE removes the test record

### Endpoints to Test:
- `/api/v1/demands/` - PUT, DELETE
- `/api/v1/groups/` - PUT, DELETE
- `/api/v1/divisions/` - PUT, DELETE
- `/api/v1/resources/` - PUT, DELETE
- `/api/v1/assignments/` - PUT, DELETE
- `/api/v1/absences/` - PUT, DELETE

## Phase 4: Documentation Consolidation

### Files to DELETE:
1. **`PROJECT_COMPLETE.md`** - v2.0 completion doc, outdated
2. **`api/routers/QUICK_REFERENCE.md`** - Overlaps with API_ENDPOINTS.md
3. **`tests/TEST_SUITE_OVERVIEW.md`** - Overlaps with tests/README.md

### Files to UPDATE:
1. **`api/routers/ROUTER_SUMMARY.md`** - Update endpoint names (requests→demands, sub-groups→groups)

### Files to KEEP (after updates):
1. **`README.md`** - Main project docs (already updated)
2. **`docs/API_ENDPOINTS.md`** - Primary API reference
3. **`docs/DEPLOYMENT_GUIDE.md`** - Deployment instructions
4. **`docs/INTEGRATION_GUIDE.md`** - Client integration guide
5. **`docs/SQL_QUERIES_REFERENCE.md`** - Comprehensive SQL reference (both databases)
6. **`api/routers/ROUTER_SUMMARY.md`** - Router overview
7. **`tests/README.md`** - Test documentation
8. **`tests/QUICKSTART.md`** - Quick test guide
9. **`PACKAGING.md`** - Packaging info
10. **`sql_diagram/README.md`** - Schema visualization
11. **`core_data/README.md`** - Data documentation

## Execution Order

1. Remove FK validations from routers (teams.py, groups.py only)
2. Rebuild Docker container: `docker-compose up --build -d`
3. Test API endpoints work: verify GET endpoints
4. Create test script in temp/ folder for PUT/DELETE tests
5. Run PUT/DELETE tests on all endpoints
6. Update docs/API_ENDPOINTS.md (rename endpoints, remove location-distances, add divisions/demands-list)
7. Rewrite docs/SQL_QUERIES_REFERENCE.md (comprehensive dual DB reference)
8. Update docs/INTEGRATION_GUIDE.md (rename endpoints)
9. Update docs/DEPLOYMENT_GUIDE.md (add dual DB config)
10. Update api/routers/ROUTER_SUMMARY.md (rename endpoints)
11. Delete obsolete files (PROJECT_COMPLETE.md, QUICK_REFERENCE.md, TEST_SUITE_OVERVIEW.md)
12. Final verification: test all endpoints and docs accuracy

## Critical Files

### Routers to Modify (FK validation removal):
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/teams.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/groups.py`

### Docs to Update:
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/docs/API_ENDPOINTS.md`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/docs/SQL_QUERIES_REFERENCE.md`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/docs/INTEGRATION_GUIDE.md`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/docs/DEPLOYMENT_GUIDE.md`

### Files to Delete:
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/PROJECT_COMPLETE.md`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/QUICK_REFERENCE.md`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/tests/TEST_SUITE_OVERVIEW.md`

### Additional Docs to Update:
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/ROUTER_SUMMARY.md`
