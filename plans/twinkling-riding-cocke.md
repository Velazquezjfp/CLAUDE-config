# Plan: Integration Test — Category Priority & BSA-ID Category Consistency

## Context

We just implemented two new solver objectives (OBJ-08 `category_priority`, OBJ-09 `bsa_category_consistency`) and need to validate they work correctly against real QA data. The QA solver container already has the new code deployed. However, the **seed data for the two new objectives is NOT in the QA database** (only 9 original objectives present). The solver will fall back to `OBJECTIVE_FALLBACK_DEFAULTS` (`category_priority: 1.5`, `bsa_category_consistency: 2.0`), which is fine for this test — it proves the fallback path works.

**QA environment status** (verified):
- `cff-solver-qa` on port 8005 — healthy, 0 active jobs, has both new `.py` files
- `cff_api_qa` on port 8003 — healthy, 9 objectives in DB (no new ones yet)
- May 2026 data: **1483 demands**, **374 active resources**

## Test Steps

### Step 1: Trigger QA Solver Job for May 2026

`POST http://localhost:8005/qa/planner/api/v1/solver/trigger`

```json
{
    "user_id": "javi_test",
    "test_mode": false,
    "test_requests": 50,
    "test_resources": 80,
    "use_mock_data": false,
    "plan_range": {"start_date": "2026-05-01", "end_date": "2026-05-30"},
    "target_team_ids": [],
    "target_group_ids": [],
    "lock_allocations": true,
    "locked_date_ranges": [{"start": "2026-05-01", "end": "2026-05-30", "reason": "Sprint freeze"}],
    "replannable_demand_type": ["Service de nuit"],
    "options": {"time_limit_seconds": 7200}
}
```

Capture `job_id` and `websocket_url` from response.

### Step 2: Monitor Logs in Real-Time

Two approaches in parallel:
1. **Docker logs** (primary — captures all solver print output including our new objectives):
   ```bash
   docker logs -f cff-solver-qa 2>&1 | tee /tmp/solver_qa_may_test.log
   ```
2. **Poll status endpoint** every ~30s:
   ```bash
   curl http://localhost:8005/qa/planner/api/v1/solver/status/{job_id}
   ```

**What to look for in logs** (proves objectives loaded):
- `[CATEGORY PRIORITY] Adding category priority objective...` — confirms OBJ-08 loaded
- `Backend weight:` or `[WARNING] Objective 'category_priority' not in backend, using default: 1.5` — confirms fallback weight used
- `Created N penalty terms:` with index distribution — shows non-trivial penalty count
- `[BSA CATEGORY CONSISTENCY] Adding BSA-ID category consistency objective...` — confirms OBJ-09 loaded
- `BSA-IDs with mixed categories: N` — shows how many BSA-IDs have mixed-category demands
- `Created N BSA-ID category switch detection variables` — shows BoolVars created

**Red flags**:
- `ImportError` or `ModuleNotFoundError` — missing file in container
- `Weight is 0 or negative, skipping` — objective accidentally disabled
- `No demands with bsa_id found` — data pipeline issue
- Any Python traceback from the new modules

### Step 3: Wait for Completion

Job will run through partitioning (May = 1 month, likely 1 partition or sub-partitioned if >200 demands per partition). Expected time: 5-15 minutes depending on partition count.

Capture from completion:
- `plan_id` from status response
- Final solver status (`OPTIMAL` or `FEASIBLE`)
- Coverage rate
- Total assignments

### Step 4: Retrieve and Inspect Results

#### 4a. Get plan assignments
```
GET http://localhost:8003/qa/ai/api/v1/planner-output/assignments/?plan_id={plan_id}&per_page=200
```
Page through all results. Key fields: `resource_id`, `resource_category`, `bsa_id`, `request_id`.

#### 4b. Get uncovered demands
```
GET http://localhost:8003/qa/ai/api/v1/planner-output/uncovered-demands/?plan_id={plan_id}&per_page=200
```

#### 4c. Get resource data (for category order verification)
```
GET http://localhost:8003/qa/ai/api/v1/resources/?status_filter=Actif&per_page=200
```
Page through all 374 resources. Build lookup: `{resource_id: resource_categories_list}`.

#### 4d. Get demand data (for BSA-ID cross-reference)
```
GET http://localhost:8003/qa/ai/api/v1/demands/?start_date=2026-05-01&end_date=2026-05-30&per_page=200
```
Page through all 1483 demands. Build lookup: `{demand_id: {bsa_id, resource_category}}`.

### Step 5: Analyze Category Priority (OBJ-08)

Write a Python analysis script that:

1. **For each assignment**, look up the resource's ordered `resource_categories` list and find the index of the assigned `resource_category`
2. **Count**: primary (idx=0), secondary (idx=1), tertiary+ (idx>=2), unknown
3. **Calculate primary rate**: `primary_count / total_categorized * 100`
4. **Find worst offenders**: Resources with the most non-primary assignments
5. **Spot-check**: Pick 3-5 resources with secondary assignments — did they have a primary-category demand available that went to another resource? (This validates the objective is working)

**Pass criteria**:
- Primary rate > 80% (given real data constraints)
- The solver log shows `Created N penalty terms` with N > 0
- No resources are exclusively in tertiary+ categories when primary demands exist

### Step 6: Analyze BSA-ID Consistency (OBJ-09)

Write a Python analysis script that:

1. **Group assignments by (resource_id, bsa_id)** → collect set of `resource_category` per pair
2. **Count**: consistent pairs (1 category), inconsistent pairs (>1 category)
3. **Calculate consistency rate**: `consistent / total * 100`
4. **Find switches**: List all (resource, bsa_id) pairs where the resource switched categories
5. **Cross-reference with demands**: For each switch, check if the BSA-ID actually had demands in multiple categories (expected if solver had no choice)

**Pass criteria**:
- Consistency rate > 90%
- The solver log shows `BSA-IDs with mixed categories: N` with N > 0
- Switches only occur where coverage would otherwise be lost

### Step 7: Coverage Regression Check

Compare coverage rate against expectations:
- Coverage should be >= 60% for a full May run (1483 demands, 374 resources)
- Category priority must NOT reduce coverage — if coverage drops below expected, the penalty weights are too high

### Step 8: Seed Data Insertion (Post-Test, Optional)

If the test passes and we want the FE to show the new objectives:
```sql
-- Run against QA internal DB (port 5436)
INSERT INTO objective_weights (objective_name, objective_category, weight_coefficient, weight_min, weight_max, description, active) VALUES
('category_priority', 'quality', 1.5, 0.5, 3.0, 'Prefer assigning resources to their primary (highest-priority) category', TRUE),
('bsa_category_consistency', 'quality', 2.0, 0.5, 3.0, 'Keep same resource in same category on same construction site (BSA-ID)', TRUE);
```
Then verify via `GET /objective-weights/` that 11 objectives are returned.

## Key Files

| File | Role in Test |
|------|-------------|
| `solver_v2/objectives/category_priority.py` | OBJ-08 in solver container |
| `solver_v2/objectives/bsa_category_consistency.py` | OBJ-09 in solver container |
| `solver_v2/config.py:219-225` | Fallback defaults (what solver uses when DB has no entry) |
| `solver_v2/solver/model.py:574-593` | Where both objectives are registered |

## Verification Summary

| Check | What Proves It Works |
|-------|---------------------|
| Solver logs show `[CATEGORY PRIORITY]` block | Module loaded, no import errors |
| Logs show `Created N penalty terms` (N > 0) | Objective is generating meaningful penalties |
| Solver logs show `[BSA CATEGORY CONSISTENCY]` block | Module loaded, no import errors |
| Logs show `BSA-IDs with mixed categories: N` (N > 0) | BSA grouping logic works on real data |
| Primary category rate > 80% in assignments | Solver prefers primary categories |
| BSA consistency rate > 90% in assignments | Solver avoids category switches on same site |
| Coverage rate unchanged vs expectations | New objectives don't hurt coverage |
| No Python tracebacks in solver logs | Clean execution |
