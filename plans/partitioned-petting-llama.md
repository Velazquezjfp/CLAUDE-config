# Database Migration Plan: Split Internal/External Architecture

## Overview
Migrate the CFF Personnel Planning API to use a split database architecture:
- **Internal DB** (current PostgreSQL): User-modifiable parameters only
- **External DB** (150.241.245.65:5432/cff): Hard data (resources, demands, assignments, etc.)

---

## 1. Database Comparison

### Tables in External Database (qa_database @ 150.241.245.65:5432/cff)
| Table | Rows | Description |
|-------|------|-------------|
| absences | 6,190 | Resource absences with `family_name` column |
| assignments | 106,038 | Coverage mappings (different columns than current) |
| cff_roles | 1 | Role definitions |
| cff_user_activations | 0 | User activation tokens |
| cff_user_roles | 1 | User-role mappings |
| cff_users | 1 | Application users |
| **demands** | 50,896 | **Renamed from `requests`** - resource demands |
| demands_list | 25,577 | Historical demand records (BSA data) |
| **divisions** | 6 | **NEW** - Division organizational level |
| **groups** | 47 | **Renamed from `sub_groups`** |
| import_job_details | 7 | Data import history |
| import_job_logs | 28 | Import error logs |
| locations | 36 | Location reference data |
| operation_points | 761 | Operational locations |
| qualifications | 101 | Skills and certifications |
| regions | 3 | Regional hierarchy |
| resource_category | 19 | Resource type classifications |
| resources | 374 | Personnel (internal/external) |
| teams | 56 | Team units |

### Tables in Current Internal Database (schema.sql)
| Table | Purpose | Action Required |
|-------|---------|-----------------|
| regions | Organizational | **MOVE TO EXTERNAL** |
| teams | Organizational | **MOVE TO EXTERNAL** |
| sub_groups | Organizational | **MOVE TO EXTERNAL** (now `groups`) |
| resources | Personnel | **MOVE TO EXTERNAL** |
| absences | Personnel | **MOVE TO EXTERNAL** |
| requests | Demands | **MOVE TO EXTERNAL** (now `demands`) |
| assignments | Coverage | **MOVE TO EXTERNAL** |
| locations | Reference | **MOVE TO EXTERNAL** |
| location_distances | Travel calc | **NOT IN EXTERNAL** - Remove |
| qualifications | Reference | **MOVE TO EXTERNAL** |
| **legal_constraints** | Parameters | **KEEP INTERNAL** |
| **company_policy_constraints** | Parameters | **KEEP INTERNAL** |
| **operational_preferences** | Parameters | **KEEP INTERNAL** |
| **objective_weights** | Parameters | **KEEP INTERNAL** |
| **utilization_targets** | Parameters | **KEEP INTERNAL** |
| calendars | Reference | **NOT IN EXTERNAL** - TBD |
| shift_templates | Reference | **NOT IN EXTERNAL** - TBD |
| audit_log | Logging | **KEEP INTERNAL** |

---

## 2. Column Differences by Table

### 2.1 `resources` Table

| Column | Current Schema | External DB | Notes |
|--------|----------------|-------------|-------|
| resource_id | VARCHAR(20) PK | INTEGER PK | **TYPE CHANGE** |
| type | resource_type ENUM | NOT IN DB | **REMOVED** |
| first_name | VARCHAR(100) | VARCHAR | Same |
| last_name | VARCHAR(100) | VARCHAR | Same |
| email | VARCHAR(255) | VARCHAR | Same |
| phone | VARCHAR(30) | VARCHAR | Same |
| region_id | INTEGER FK | INTEGER FK | Same |
| team_id | INTEGER FK | INTEGER FK | Same |
| sub_group_id | INTEGER FK | N/A | **RENAMED to group_id** |
| group_id | N/A | INTEGER FK | **NEW** |
| home_location | VARCHAR(100) | VARCHAR | Same |
| contract | contract_type ENUM | VARCHAR | Same (as string) |
| shift_pref | shift_preference ENUM | shift_preference VARCHAR | Same |
| weekly_hours | INTEGER | INTEGER | Same |
| cost_per_hour | DECIMAL(10,2) | NUMERIC | Same |
| resource_category | VARCHAR(100) | N/A | **REPLACED by resource_categories JSONB** |
| resource_categories | N/A | JSONB | **NEW** (array) |
| qualifications | JSONB | JSONB | Same |
| availability_pattern | JSONB | JSONB | Same |
| hire_date | DATE | DATE | Same |
| status | resource_status ENUM | VARCHAR | Same (as string) |
| user_name | N/A | VARCHAR NOT NULL | **NEW** |
| address | N/A | VARCHAR | **NEW** |
| npa | N/A | VARCHAR | **NEW** |
| number | N/A | VARCHAR | **NEW** |
| team_salon_hr | N/A | VARCHAR | **NEW** |
| created_by | N/A | VARCHAR | **NEW** |
| updated_by | N/A | VARCHAR | **NEW** |

### 2.2 `demands` Table (was `requests`)

| Column | Current (requests) | External (demands) | Notes |
|--------|-------------------|-------------------|-------|
| id | N/A | INTEGER PK | **NEW** - composite with bsa_id |
| request_id | VARCHAR(30) PK | N/A | **REMOVED** |
| bsa_id | VARCHAR(20) | VARCHAR PK | Same (now part of composite PK) |
| task_name | VARCHAR(255) | VARCHAR | Same |
| status | request_status ENUM | N/A | **REMOVED** |
| assignment_status | VARCHAR(50) | VARCHAR | Same |
| resource_category | VARCHAR(100) | VARCHAR | Same |
| resource_category_group | N/A | VARCHAR | **NEW** |
| technical_service | VARCHAR(100) | VARCHAR | Same |
| branch | VARCHAR(100) | VARCHAR | Same |
| start_datetime | TIMESTAMP | N/A | **REPLACED** |
| end_datetime | TIMESTAMP | N/A | **REPLACED** |
| shift_start_time | N/A | VARCHAR | **NEW** |
| shift_finish_time | N/A | VARCHAR | **NEW** |
| shift | shift_type ENUM | VARCHAR | Same (as string) |
| shift_service_type | VARCHAR(100) | N/A | **REMOVED** |
| start_location | VARCHAR(100) | VARCHAR | Same |
| end_location | VARCHAR(100) | VARCHAR | Same |
| start_location_code | VARCHAR(50) | VARCHAR | Same |
| end_location_code | VARCHAR(50) | VARCHAR | Same |
| people_needed | INTEGER | INTEGER | Same |
| personnel | N/A | VARCHAR | **NEW** |
| required_qualifications | JSONB | JSONB | Same |
| work_type | TEXT | TEXT | Same |
| responsible_person | VARCHAR(100) | VARCHAR | Same |
| isp_amgt | VARCHAR(50) | VARCHAR | Same |
| psp | VARCHAR(50) | VARCHAR | Same |
| priority | priority_level ENUM | VARCHAR | Same (as string) |
| locked | BOOLEAN | BOOLEAN | Same |
| assigned_resources | JSONB | JSONB | Same |
| ir_er | N/A | VARCHAR | **NEW** |
| comments | N/A | VARCHAR | **NEW** |
| work_operation_type1 | N/A | VARCHAR | **NEW** |
| work_operation_type2 | N/A | VARCHAR | **NEW** |
| team_id | N/A | INTEGER FK | **NEW** |

### 2.3 `assignments` Table

| Column | Current Schema | External DB | Notes |
|--------|----------------|-------------|-------|
| assignment_id | VARCHAR(30) PK | N/A | **REMOVED** |
| id | N/A | INTEGER PK | **NEW** |
| resource_id | VARCHAR(20) FK | VARCHAR | Same |
| request_id | VARCHAR(30) FK | VARCHAR | Same |
| bsa_id | N/A | VARCHAR | **NEW** |
| type | VARCHAR(20) | N/A | **REMOVED** |
| status | assignment_status ENUM | N/A | **REMOVED** |
| start_date | DATE | N/A | **REMOVED** |
| end_date | DATE | N/A | **REMOVED** |
| calendar_start | N/A | VARCHAR | **NEW** |
| calendar_end | N/A | VARCHAR | **NEW** |
| enterprise | VARCHAR(100) | VARCHAR | Same |
| calendar_type | VARCHAR(50) | VARCHAR | Same |
| qualifications | TEXT | N/A | **REMOVED** |
| region | VARCHAR(100) | N/A | **REMOVED** |
| team | VARCHAR(100) | N/A | **REMOVED** |
| sub_group | VARCHAR(50) | N/A | **REMOVED** |
| meeting_location | VARCHAR(100) | VARCHAR | Same |
| meeting_time | TIME | VARCHAR | Same (format change) |
| family_name | N/A | VARCHAR | **NEW** |
| responsible | VARCHAR(100) | VARCHAR | Same |
| required_skills | TEXT | VARCHAR | Same |
| notes | TEXT | TEXT | Same |
| resource_category | VARCHAR(100) | VARCHAR | Same |
| billing_number | N/A | VARCHAR | **NEW** |
| tour_manager | N/A | VARCHAR | **NEW** |
| work_site | N/A | VARCHAR | **NEW** |
| rdm_comments | N/A | VARCHAR | **NEW** |
| work_type | VARCHAR(100) | N/A | **REMOVED** |
| pe_from | VARCHAR(50) | N/A | **REMOVED** |
| pe_to | VARCHAR(50) | N/A | **REMOVED** |
| external_company | VARCHAR(100) | N/A | **REMOVED** |
| estimated_cost_chf | DECIMAL(12,2) | N/A | **REMOVED** |
| mandate_name | VARCHAR(255) | N/A | **REMOVED** |
| technical_service | VARCHAR(100) | N/A | **REMOVED** |
| branch | VARCHAR(100) | N/A | **REMOVED** |
| personnel_count | INTEGER | N/A | **REMOVED** |

### 2.4 `absences` Table

| Column | Current Schema | External DB | Notes |
|--------|----------------|-------------|-------|
| absence_id | VARCHAR(20) PK | INTEGER PK | **TYPE CHANGE** |
| resource_id | VARCHAR(20) FK | VARCHAR | Same |
| type | absence_type ENUM | VARCHAR | Same (as string) |
| start_date | DATE | TIMESTAMP | Same |
| end_date | DATE | TIMESTAMP | Same |
| number_of_days | INTEGER GENERATED | INTEGER | Same (but not auto) |
| status | absence_status ENUM | VARCHAR | Same (as string) |
| notes | TEXT | VARCHAR | Same |
| approved_by | VARCHAR(100) | N/A | **REMOVED** |
| created_date | DATE | N/A | **REMOVED** |
| family_name | N/A | VARCHAR NOT NULL | **NEW** |

### 2.5 `groups` Table (was `sub_groups`)

| Column | Current (sub_groups) | External (groups) | Notes |
|--------|---------------------|-------------------|-------|
| sub_group_id | SERIAL PK | N/A | **RENAMED** |
| group_id | N/A | INTEGER PK | **NEW name** |
| sub_group_name | VARCHAR(50) | N/A | **RENAMED** |
| group_name | N/A | VARCHAR NOT NULL | **NEW name** |
| team_id | INTEGER FK | INTEGER FK | Same |
| color_code | VARCHAR(20) | VARCHAR | Same |

---

## 3. Tables to KEEP in Internal Database

These tables remain in the current app's database (user-modifiable parameters):

1. **legal_constraints** - Swiss LDT constraints (immutable)
2. **company_policy_constraints** - CFF policies
3. **operational_preferences** - Soft constraints for optimization
4. **objective_weights** - Multi-objective optimization weights
5. **utilization_targets** - Resource efficiency targets
6. **audit_log** - Keep for internal audit trail

---

## 4. Tables NOT in External Database (CONFIRMED DECISIONS)

**Decision: REMOVE ENTIRELY**
1. ~~**location_distances**~~ - Remove table and API endpoints
2. ~~**calendars**~~ - Remove table and API endpoints
3. ~~**shift_templates**~~ - Remove table and API endpoints

---

## 5. New Tables in External Database

**Decision: Create API endpoints for divisions + demands_list only**

1. **divisions** - 6 rows (new organizational level) - **CREATE ENDPOINTS**
2. **demands_list** - 25,577 rows (historical BSA data) - **CREATE ENDPOINTS**
3. ~~cff_users / cff_roles / cff_user_roles / cff_user_activations~~ - **IGNORE (separate service)**

**Decision: get_bsa_details_json() function - LOW PRIORITY (follow up later)**

---

## 6. Implementation Plan

### Phase 1: Database Configuration
1. Update `config.py` to support dual database connections:
   ```python
   # Internal DB (parameters - same server)
   INTERNAL_DB_HOST: str = "postgres"  # or localhost in production
   INTERNAL_DB_PORT: int = 5432
   INTERNAL_DB_NAME: str = "cff_planning"

   # External DB (data)
   EXTERNAL_DB_HOST: str = "150.241.245.65"  # dev, will be internal docker in prod
   EXTERNAL_DB_PORT: int = 5432
   EXTERNAL_DB_NAME: str = "cff"
   EXTERNAL_DB_USER: str = "cffdev"
   EXTERNAL_DB_PASSWORD: str = "cffdev"
   ```
2. Update `database.py` to create two connection pools:
   - `get_internal_db()` - for parameter tables
   - `get_external_db()` - for data tables
3. Create environment variables in `.env` for both connections

### Phase 2: Update Schema (Internal DB)
1. Remove tables that move to external:
   - regions, teams, sub_groups, resources, absences
   - requests, assignments, locations, qualifications
2. Remove tables that don't exist in external:
   - location_distances, calendars, shift_templates
3. Keep parameter tables only:
   - legal_constraints, company_policy_constraints
   - operational_preferences, objective_weights, utilization_targets
   - audit_log

### Phase 3: Update API Routers (External DB)
1. **resources.py** - Point to external DB, update columns
2. **requests.py** - Rename to demands, update columns
3. **assignments.py** - Point to external DB, update columns
4. **absences.py** - Point to external DB, update columns
5. **regions.py** - Point to external DB
6. **teams.py** - Point to external DB
7. **sub_groups.py** - Rename to groups, point to external DB
8. **locations.py** - Point to external DB
9. **qualifications.py** - Point to external DB

### Phase 4: Update API Routers (Internal DB - No Changes)
- constraints.py
- company_policies.py
- objective_weights.py
- utilization_targets.py

### Phase 5: Remove Unused Code
1. Remove routers for tables that no longer exist:
   - location_distances.py (REMOVE)
   - Remove calendar-related code if any
   - Remove shift_template-related code if any
2. Update models.py to match new schemas
3. Remove ENUM types that are now strings in external DB

### Phase 6: Add New API Endpoints (External DB)
1. Create `divisions.py` router for divisions table
2. Create `demands_list.py` router for demands_list table (historical BSA data)

### Phase 7: Docker/Deployment Configuration
1. Update docker-compose to support dual database connections
2. Configure internal DB to point to localhost (same server)
3. Configure external DB connection for deployment

---

## 7. Files to Modify

### Configuration Files
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/config.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/database.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/.env.example`

### Router Files (External DB)
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/resources.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/requests.py` (→ demands)
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/assignments.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/absences.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/regions.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/teams.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/sub_groups.py` (→ groups)
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/locations.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/qualifications.py`

### Router Files to REMOVE
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/location_distances.py`

### Router Files to CREATE
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/divisions.py` (NEW)
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/demands_list.py` (NEW)

### Model Files
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/models.py`

### Schema Files
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/database/schema.sql`

### Main Application & Router Index
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/main.py`
- `/home/javiervel/clients/CFF/mock_data_v2/database_application_v2/api/routers/__init__.py`

---

## 8. External Database Connection Details

```
Host: 150.241.245.65 (development/testing)
Port: 5432
Database: cff
Username: cffdev
Password: cffdev
```

**Production**: Same server, internal Docker network connection

---

## 9. Confirmed User Decisions

| Decision | Choice |
|----------|--------|
| calendars, shift_templates, location_distances | **REMOVE ENTIRELY** |
| New tables (divisions, demands_list) | **CREATE ENDPOINTS** |
| cff_users tables | **IGNORE (separate service)** |
| get_bsa_details_json() function | **LOW PRIORITY (follow up later)** |

---

## 10. Summary of API Changes

### Endpoints MOVING to External DB (update queries)
- `GET/POST/PUT/DELETE /api/v1/resources`
- `GET/POST/PUT/DELETE /api/v1/demands` (was requests)
- `GET/POST/PUT/DELETE /api/v1/assignments`
- `GET/POST/PUT/DELETE /api/v1/absences`
- `GET/POST/PUT/DELETE /api/v1/regions`
- `GET/POST/PUT/DELETE /api/v1/teams`
- `GET/POST/PUT/DELETE /api/v1/groups` (was sub_groups)
- `GET/POST/PUT/DELETE /api/v1/locations`
- `GET/POST/PUT/DELETE /api/v1/qualifications`

### Endpoints STAYING on Internal DB (no changes)
- `GET /api/v1/constraints` (legal_constraints - read-only)
- `GET/POST/PUT/DELETE /api/v1/company-policies`
- `GET/POST/PUT/DELETE /api/v1/objective-weights`
- `GET/POST/PUT/DELETE /api/v1/utilization-targets`

### NEW Endpoints (External DB)
- `GET/POST/PUT/DELETE /api/v1/divisions`
- `GET/POST/PUT/DELETE /api/v1/demands-list`

### Endpoints to REMOVE
- ~~`/api/v1/location-distances`~~
