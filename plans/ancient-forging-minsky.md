# Fix: Event Loop Blocking Causes Cancel 404 (JobManager Amnesia)

## Context

The cancel endpoint returns 404 for running jobs on QA. Root cause chain:

1. `_execute_solver_job()` calls synchronous `httpx.Client` methods directly from the async event loop
2. Data fetching blocks the event loop for 10-30+ seconds (confirmed: 2 consecutive 10s health probe timeouts)
3. Docker healthcheck (`timeout: 10s, retries: 3`) → 3 consecutive failures → container restart
4. New container → fresh `JobManager` → empty `jobs` dict → cancel returns 404

## Full Blocking I/O Audit

Audited ALL solver subsystems. Results:

| Module | HTTP calls? | Called inside executor? | Action |
|--------|-------------|----------------------|--------|
| `api/client.py` (data fetch) | YES — get_demands, get_resources, get_blocks, get_op_points | NO — blocks event loop 10-30s | **WRAP** |
| `preprocessing/constraints.py` | YES — ~12 HTTP calls via get_client() | NO — blocks event loop ~3s | **WRAP** |
| `preprocessing/objectives.py` | YES — 1 HTTP call via get_client() | NO — blocks event loop ~0.3s | **WRAP** |
| `preprocessing/data_processor.py` | No HTTP — pure data transform | N/A (safe) | Include in wrapper for free |
| `constraints/` (20+ files) | **No HTTP** — pure CP-SAT model building | YES (inside solve_sync) | No change |
| `objectives/` (14 files) | **No HTTP** — pure CP-SAT objective building | YES (inside solve_sync) | No change |
| `solver/model.py` | **No HTTP** — OR-Tools CP-SAT | YES (inside solve_sync) | No change |
| `analysis/solution_analyzer.py` | **No HTTP** — pure computation | NO but safe (no I/O) | No change |
| `analysis/constraint_analyzers/` | **No HTTP** — pure computation | NO but safe (no I/O) | No change |
| `analysis/objective_analyzers/` | **No HTTP** — pure computation | NO but safe (no I/O) | No change |
| `analysis/recommendations/` | **No HTTP** — pure computation | NO but safe (no I/O) | No change |
| `postprocessing/` | **No HTTP** — pure data transform | Not currently invoked | No change |
| Result saving (post_planner_*) | YES — 3-5 HTTP calls | NO — blocks ~2-5s | **WRAP** |

**Conclusion**: Only 3 phases make HTTP calls outside executor: data-fetch, constraint/objective fetch, and result-saving. The plan wraps all three. Everything else (constraints, objectives, analysis, postprocessing) is pure computation with zero network calls.

## Safety Review

Verified these concerns are NOT issues:
- **No input mutation**: `PreprocessedData.__init__` reads from `requests_data['data']` but does NOT mutate input dicts — stores references in `self.raw_*` and builds new structures
- **Singleton safe**: `MAX_CONCURRENT_JOBS=1`, one job at a time. `get_client()` singleton accessed sequentially from same executor thread
- **`_check_cancelled` unaffected**: Stays in async function as closure over `job`, used between `await` points
- **`main.py` unaffected**: Standalone CLI entry, not Docker entry
- **Analysis phase safe**: `SolutionAnalyzer` and all sub-analyzers (constraint_analyzers/, objective_analyzers/, recommendations/) make zero HTTP calls — pure in-memory computation
- **Solver constraints/objectives safe**: All 34+ files in `constraints/` and `objectives/` are pure CP-SAT builders with no network I/O

## Approach

Extract all blocking sync I/O into sync helpers, call via `loop.run_in_executor()`. Follows the existing `solve_sync()` + `run_in_executor` pattern at service.py:1014.

## File Modified

**`solver_v2/api/service.py`** — 3 changes

### Change 1: Extract data-fetch + preprocess into sync helper for `_execute_solver_job()`

**New function: `_fetch_and_preprocess_sync(job)`** (add before `_execute_solver_job`, ~line 565)

This is a **pure extraction** — code body moves unchanged. No logic changes.

What moves INTO the sync helper (current lines ~625-859):
- Client creation: `get_client(env=CURRENT_ENV, user_id=...)` (line 627)
- Deprecation warnings (lines 629-633)
- All data fetching: `client.get_demands()`, `client.get_resources()`, `client.get_operation_points()`, `client.get_resource_blocks()` (lines 635-824)
- All filtering: teams, groups, categories, territory, test mode slicing (lines 638-789)
- `absences_data` construction (lines 823-824)
- `fetch_constraint_values()` and `fetch_objective_weights()` (lines 843, 849)
- `preprocess_data()` call and `targeted_request_ids = None` (lines 855, 859)

What the sync helper sets on `job` (thread-safe simple assignments):
- `job.num_demands`, `job.num_resources` (lines 827-828)

Returns 7 values used by rest of function:
```python
return (client, requests_data, resources_data, absences_data,
        preprocessed_data, constraint_values, objective_weights)
```

**Replacement in `_execute_solver_job()`** (lines ~619-861 become ~15 lines):

```python
# Step 2: Fetch data & preprocess (in thread pool to keep event loop free)
job.update_progress(SolverStep.FETCHING_DATA)
await job_manager.broadcast_progress(job.job_id, job.progress_history[-1])

if _check_cancelled("fetching_data"): return

loop = asyncio.get_event_loop()
(client, requests_data, resources_data, absences_data,
 preprocessed_data, constraint_values, objective_weights
) = await loop.run_in_executor(None, _fetch_and_preprocess_sync, job)

if _check_cancelled("after_fetching_data"): return

await send_webhook(job, "RUNNING", 15.0, current_step="preprocessing")

job.update_progress(SolverStep.PREPROCESSING, {
    'requests_count': job.num_demands,
    'resources_count': job.num_resources
})
await job_manager.broadcast_progress(job.job_id, job.progress_history[-1])

if _check_cancelled("before_solving"): return
```

The `loop` variable is reused later by `solve_sync()` (line ~1014).

Intermediate progress steps (FETCHING_CONSTRAINTS, FETCHING_OBJECTIVES, PREPROCESSING) are consolidated into a single FETCHING_DATA → PREPROCESSING update. These sub-steps complete in <1s each — the user can't meaningfully act on them.

### Change 2: Wrap result-saving phase in executor

The analysis phase (SolutionAnalyzer) is safe — **zero HTTP calls**, pure computation. But the result-saving phase (lines ~1073-1200) makes 3-5 sync HTTP calls:
- `client.get_teams()`, `client.get_groups()` (enrichment)
- `client.post_planner_output()` (main save)
- `client.post_planner_assignments_bulk()` (normalized save)
- `client.post_planner_uncovered_demands_bulk()` (gaps save)

Extract into `_save_results_sync(client, job, model, analysis_report, requests_data, resources_data, preprocessed_data, cp)` and call via `run_in_executor`.

The analysis phase (lines ~1028-1062) stays inline — it's pure computation, no blocking.

### Change 3: Wrap sync calls in `_execute_solver_job_from_preplan()`

Lines 1940-1953 (3 blocking sync calls) → wrap in inline closure + `run_in_executor`:

```python
loop = asyncio.get_event_loop()

def _preplan_preprocess_sync():
    cv = fetch_constraint_values(planning_mode="Balanced", user_id=job.request.user_id)
    ow = fetch_objective_weights(user_id=job.request.user_id)
    pd = preprocess_data(requests_data, resources_data, absences_data)
    pd.targeted_request_ids = None
    return (pd, cv, ow)

(preprocessed_data, constraint_values, objective_weights) = await loop.run_in_executor(
    None, _preplan_preprocess_sync
)
```

Note: `_execute_solver_job_from_preplan` does NOT have a result-saving phase (no `client.post_*` calls), so no additional wrapping needed there.

## What does NOT change

- `solver_v2/api/client.py` — stays synchronous (runs in thread pool now)
- `solver_v2/preprocessing/constraints.py`, `objectives.py`, `data_processor.py` — no changes
- `solver_v2/api/data_pipeline.py` — pure filtering functions, no changes
- `solver_v2/constraints/` (20+ files) — pure CP-SAT builders, no HTTP, no changes
- `solver_v2/objectives/` (14 files) — pure CP-SAT builders, no HTTP, no changes
- `solver_v2/analysis/` (all sub-dirs) — pure computation, no HTTP, no changes
- `solver_v2/postprocessing/` — pure data transform, not invoked, no changes
- `solver_v2/solver/model.py` — already in executor, no changes
- `solver_v2/main.py` — standalone CLI, not Docker entry, no changes
- Docker healthcheck config — no changes (fix prevents the timeout)
- Cancel endpoint — already works, this prevents the 404 by keeping container alive

## Risk Assessment

| Concern | Status | Reason |
|---------|--------|--------|
| Thread safety | SAFE | `MAX_CONCURRENT_JOBS=1`, one job at a time, singleton sequential |
| Input mutation | SAFE | `PreprocessedData` reads but doesn't mutate input dicts |
| Variable flow | VERIFIED | 7 return values cover all downstream usage (solve, analyze, save) |
| Cancellation checks | SAFE | `_check_cancelled` stays in async function, checks between await points |
| Error propagation | SAFE | Exceptions from executor propagate to existing try/except |
| Constraints/objectives modules | SAFE | Zero HTTP calls — pure CP-SAT model operations |
| Analysis modules | SAFE | Zero HTTP calls — pure in-memory computation |
| Logging | SAFE | All logger calls thread-safe, output unchanged |
| Progress granularity | MINOR TRADE-OFF | Sub-steps consolidated — acceptable UX trade-off |

## Verification

1. **Health endpoint responsive during fetch**: Trigger job, probe `/health` every 2s → all <100ms (was 10s+ timeouts)
2. **Cancel works during fetch**: Trigger job, cancel during data fetch → 200 (was blocked/404)
3. **Cancel works during save**: Trigger job, cancel after solver → 200
4. **Functional correctness**: Same team-6127 job → same solver result (FEASIBLE, same counts)
5. **WebSocket responsive**: Keepalive pings arrive on time during fetch
6. **Error handling**: Trigger job with invalid data → same error behavior as before
