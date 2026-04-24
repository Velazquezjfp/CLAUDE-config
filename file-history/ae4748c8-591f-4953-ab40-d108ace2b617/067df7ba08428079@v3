# Plan: Holistic Validation Run + Report (All 15 Constraints, CT/RT Replannable)

## Context

The CT/RT test suite is complete — 13/13 green under the minimal 4-constraint
profile (documented in `solver_v2/Planner_test/`). The production 15-constraint
stack is now active in the QA solver image (`config.py:206-225`) but has only
been smoke-verified (10s run, `PLAN-20260421143731`).

The user now wants a **holistic end-to-end report** covering:

1. **Accuracy** — Does the output plan respect all 15 enabled constraints?
2. **Objectives efficiency** — Are the configured weights/priorities actually
   driving planner decisions?
3. **Analyzers** — Does the summary (`/solver/status/{job_id}`) produce
   actionable, specific insights?

CT and RT are the feature of highest interest and will be replannable in the
trigger payload so they become part of the solver's decision space (not static
blockers).

**Key architectural facts discovered from exploration:**

- Objectives fetched at runtime from `GET /qa/ai/api/v1/objective-weights/`
  (`api/client.py:518`). Fallbacks at `config.py:277-283` apply only when a row
  is missing.
- 15 objectives are wired; weights combine via `Minimize(sum(terms))` in
  `solver/model.py:664-703`. Maximize-type objectives (coverage, continuity)
  use negative scaled weights.
- **Per-objective contributions are computed post-solve by
  `SolutionAnalyzer._analyze_objectives()` (`analysis/solution_analyzer.py:192`)
  but NOT surfaced to `/solver/status`** — only the aggregate `objective_value`
  scalar is exposed. This is the single biggest gap the report will flag.
- 14 of 15 constraints have dedicated analyzers. **`LC_06_rest_days_allocation`
  has NO analyzer** — RT/CT satisfaction is surfaced via
  `LC_08_monthly_rest_v2`'s Phase J `ct_rt_compliance_alerts` path only.
- Fetched input data is NOT persisted anywhere; must be reconstructed by
  re-querying cff_api with the same filters.

**User decisions (this session):**

- **Scope**: focused — 3 small teams (7557, 7566, 7549), 30-day cross-month
  `2026-04-27 → 2026-05-30`. Exercises partitioning, Phase I carryover,
  sub-partition path, and all 15 constraints with strong signal-to-noise.
- **Fetch capture**: re-query cff_api + mine docker logs. No code changes.
- **Report location**: `solver_v2/planner_dev/`.

---

## Strategy: 6 stages with defensive checkpoints

The report hinges on tying three independent data surfaces together:
(a) what the solver *fetched*, (b) what the solver *decided*, (c) what the
analyzers *reported*. Each stage validates one linkage. If a stage fails, we
stop and diagnose before proceeding — otherwise downstream analysis is
compounded on bad inputs.

```
Stage 0 — Pre-flight & snapshot                        [~5 min]
      │   baseline objective weights, constraint values,
      │   replannable types, container health
      ▼
Stage 1 — Trigger + monitor                            [~10-30 min]
      │   POST trigger, poll status every 30s,
      │   tail solver logs for fetch/preprocess/solve phases
      ▼
Stage 2 — Fetch reconstruction                         [~3 min]
      │   re-query /demands, /resources, /resource-blocks
      │   with identical filters; persist to /tmp
      ▼
Stage 3 — Output extraction                            [~5 min]
      │   pull analysis_summary, planner_output, all
      │   paginated assignments; persist to /tmp
      ▼
Stage 4 — Cross-analysis                               [~10 min]
      │   accuracy (input vs output per constraint),
      │   objective efficiency (weights vs achievement),
      │   analyzer quality (sample insights, gaps)
      ▼
Stage 5 — Report synthesis                             [~10 min]
            write holistic report to planner_dev/
```

Total budget: ~45-60 minutes. Hard cap on Stage 1 solver time: 1800s (set via
`options.time_limit_seconds`). Stall detection at 120s-no-improvement keeps
effective search controlled.

---

## Stage 0 — Pre-flight & baseline snapshot

**Goal:** capture the "rules of the game" before triggering so the report can
compare "weights going in" vs "decisions coming out" apples-to-apples.

Commands (all read-only):

1. Verify `solver-api-qa` and `api-qa` containers healthy:
   `docker ps --filter name=solver-api-qa --filter name=cff_api_qa`.
2. Snapshot current configuration to `/tmp/holistic_baseline.json` — fetch
   and persist each:
   - `GET http://localhost:8003/qa/ai/api/v1/objective-weights/` →
     all active weights + categories
   - `GET http://localhost:8003/qa/ai/api/v1/legal-constraints/` → enforced
     constraint values (max weekly hours, min rest hours, etc.)
   - `GET http://localhost:8003/qa/ai/api/v1/replannable-demand-types/` →
     the 14+ types (sanity check for RT/CT presence)
3. Snapshot `config.py::ENABLED_CONSTRAINTS` contents (15 items) into the
   same baseline file for the report to display alongside weights.
4. Verify test teams exist and have resources:
   `GET /qa/ai/api/v1/resources/?team_id=7557&per_page=1` — expect `total>0`;
   repeat for 7566, 7549.
5. Record timestamps, solver container ID, and solver image SHA into
   baseline.

Artifact: `/tmp/holistic_baseline.json` with keys
`{weights, constraint_values, replannable_types, enabled_constraints,
container_info, test_teams}`.

---

## Stage 1 — Trigger + monitor

**Goal:** run the job with full visibility into each phase.

Payload (`/tmp/holistic_trigger.json`):
```json
{
  "user_id": "javi_test",
  "test_mode": false,
  "use_mock_data": false,
  "plan_range": {"start_date": "2026-04-27", "end_date": "2026-05-30"},
  "target_team_ids": [7557, 7566, 7549],
  "target_group_ids": [],
  "lock_allocations": true,
  "locked_date_ranges": [
    {"start": "2026-04-27", "end": "2026-05-30", "reason": "Holistic validation run"}
  ],
  "replannable_demand_type": ["RT Jour de repos", "CT Jour de compensation"],
  "options": {"time_limit_seconds": 1800}
}
```

Procedure:

1. `SUBMIT_TS=$(date +%s)` — record for log windowing.
2. `POST http://localhost:8005/qa/planner/api/v1/solver/trigger` with
   payload.
3. Capture `job_id` + `plan_id` immediately from response.
4. Launch a background tail:
   `docker logs -f --since $SUBMIT_TS cff-solver-qa | tee /tmp/holistic_solver.log`
5. Poll `GET /qa/planner/api/v1/solver/status/{job_id}` every 30s until
   `status in {complete, failed, cancelled}`. Cap: 1900s.
6. While polling, note the phase transitions:
   `fetching_data → preprocessing → solving → postprocessing → saving → complete`.
7. When complete, grep the log for expected signatures:
   - Fetch: `Fetching demands for date range: 2026-04-27 to 2026-05-30`,
     `Actual counts: X demands, Y resources`, `Total resource blocks for
     solver: Z`.
   - Partitioning: `Auto-partitioning: X demands > 500 threshold`,
     `Created N partitions`, `[DATE-OVERLAP]` (should be zero),
     `Saved N normalized assignments ... by type: {DEMAND: ..., RT: ...,
     CT: ...}`.
   - LC-06/LC-08: `LC-06: partition range …`, `LC-08 v2 SKIPPED`
     (expected when RT/CT are replannable — LC-06 takes over).
   - Phase J: `ct_rt_compliance_alerts` emissions.

Artifact: `/tmp/holistic_solver.log` + captured status payload at
`/tmp/holistic_status.json` (the FINAL complete-status response).

---

## Stage 2 — Fetch reconstruction

**Goal:** rebuild the exact input space the solver saw, so accuracy claims
have ground truth.

For each category, call cff_api with the same filters as the job and persist:

- `/qa/ai/api/v1/demands/?start_date=2026-04-27&end_date=2026-05-30&
  per_page=200&page=*` → `/tmp/holistic_input_demands.json` (all pages
  concatenated)
- `/qa/ai/api/v1/resources/?team_id=7557|7566|7549&per_page=200&page=*`
  → `/tmp/holistic_input_resources.json`
- `/qa/ai/api/v1/resource-blocks/?category=all&start_date=2026-04-27&
  end_date=2026-05-30&exclude_calendar_types=RT+Jour+de+repos,CT+Jour+de+
  compensation&per_page=1000&page=*` →
  `/tmp/holistic_input_blocks.json`. Note: CT/RT excluded from blocks because
  they're replannable — this mirrors what `_fetch_and_preprocess_sync` does
  for this payload.

Sanity check: counts in reconstruction should match within ±5% of the
`Actual counts:` line in Stage 1 logs. If wider drift → flag as reconstruction
limitation in the report (not a solver bug).

---

## Stage 3 — Output extraction

**Goal:** capture every surface that the report will cross-reference.

1. `GET /qa/ai/api/v1/planner-output/plan/{plan_id}` → full output record
   (includes `assignments` JSONB, `objective_value`, `num_violations`,
   `fetch_rt`, `fetch_ct`, `coverage_percentage`).
   Persist to `/tmp/holistic_output_plan.json`.
2. Paginate `GET /qa/ai/api/v1/planner-output/assignments/?plan_id={plan_id}
   &per_page=200&page={n}` until `data=[]`. Concatenate all rows into
   `/tmp/holistic_output_assignments.json` — this is the normalized row set
   with `assignment_type` distinguishing DEMAND / RT / CT.
3. The `analysis_summary` is already in `/tmp/holistic_status.json` from
   Stage 1 (the final `status=complete` payload). Extract and save its
   `key_insights`, `top_recommendations`, `ct_rt_compliance`, violation
   counts to `/tmp/holistic_analysis.json` for easier referencing.

---

## Stage 4 — Cross-analysis

This is the heart of the report. Three independent checks feed three report
sections.

### 4a. Accuracy (per constraint)

For each of the 15 enabled constraints, compute an observed-vs-expected check
from the input+output artifacts. Examples:

| Constraint | Check | Source |
|---|---|---|
| `HC_01_absence_blocking` | 0 assignments overlap an absence window | input_blocks + output_assignments |
| `LC_01_max_weekly_hours_v2` | No resource exceeds `max_weekly_hours` value from baseline | output_assignments, group by resource × 7d rolling |
| `LC_04_min_rest_between_shifts` | Every pair of consecutive assignments per resource has ≥ `min_rest_hours` gap | output_assignments sorted per resource |
| `LC_06_rest_days_allocation` | Each resource × segment meets RT≥4, CT≥2, combined≥6 (pro-rated) | output_assignments filtered to `assignment_type in (RT, CT)` + segment_breakdown from analysis_summary |
| `LC_05_weekend_frequency` | Each resource has ≥1 free weekend per rolling 5 weeks | output_assignments weekend filter |
| `CP_02_qualification_matching` | Every assigned resource has the demand's required category | input_demands × input_resources × output_assignments |
| `OC_01_min_category_activity` | Per-category activity meets DB-defined floor (best-effort; target may not be set for short ranges) | |
| ... | ... | ... |

For each row, report PASS / FAIL / N/A with an example violation if FAIL.
**This is the Accuracy table.**

### 4b. Objectives efficiency

Build a table with one row per objective from the baseline weights snapshot:

| Objective | Weight | Category | Signal in output? | Evidence |
|---|---|---|---|---|
| `maximize_coverage` | 3.0 | coverage | YES if coverage_percentage ≥ 95% | analysis_summary.coverage |
| `balance_workload` | 1.5 | balance | YES if workload_variance low | analysis_summary.workload_balance |
| `maintain_function_continuity` | 1.0 (fallback) | continuity | UNKNOWN (no surfaced metric) | — |
| ... | | | | |

**Gap to explicitly call out in the report**: per-objective satisfaction rates
(`achievement_rate`, `performance_category`) are computed by
`SolutionAnalyzer._analyze_objectives` but NOT returned via
`/solver/status`. For this report we will surface what is observable
(`objective_value` scalar, coverage %, workload spread) and label the rest
as "instrumentation gap — recommend surfacing in future iteration".

Optional verification: docker exec into the solver container and run
`python -c "from analysis.solution_analyzer import SolutionAnalyzer; ..."`
against the plan_id if direct inspection of `objective_performance` is
needed. (Defer unless the observable metrics are inconclusive.)

### 4c. Analyzer quality

Score each of the analyzer outputs in `analysis_summary`:

- For every insight in `key_insights`, judge:
  - Specific? (names resource/demand/date)
  - Actionable? (tells user what to fix)
  - Quantified? (includes severity/count/magnitude)
- For every recommendation in `top_recommendations`, same check.
- For `ct_rt_compliance`, verify `alerts_total`, `severity`, and
  `segment_breakdown` align with the RT/CT distribution in
  output_assignments.

**Explicit gap to call out**: `LC_06_rest_days_allocation` has no dedicated
analyzer — RT/CT failures only surface through LC-08's Phase J path. If the
Phase J alerts are missing or empty when the data says otherwise, that's a
report finding.

---

## Stage 5 — Report synthesis

Write `solver_v2/planner_dev/holistic_validation_report-2026-04-21.md`.

**Sections (fixed order):**

1. **Executive summary** — 3-5 bullets: PASS / PARTIAL / FAIL verdicts per
   section, headline numbers (coverage %, violations, RT/CT filled).
2. **Run parameters** — payload, plan_id, job_id, runtime, partition count,
   solver image SHA.
3. **Baseline snapshot** — weights table, constraint values table, enabled
   constraints list.
4. **Input dataset** — demand count, resource count, block count,
   reconstruction drift vs solver's `Actual counts:`.
5. **Accuracy** — per-constraint PASS/FAIL table (4a output).
6. **Objectives efficiency** — per-objective table (4b output) + explicit
   gap section for the missing per-objective-metric surface.
7. **Analyzers** — insight/recommendation quality table (4c output),
   sample strings quoted verbatim, gap called out (no LC-06 analyzer,
   aggregate-only objective_value).
8. **CT/RT deep dive** — per-segment RT/CT distribution, comparison with
   LC-06 target (4+2 min, ceil-pro-rated for partial months),
   `ct_rt_compliance` alerts.
9. **Findings & recommendations** — ranked list:
   - What works well
   - Instrumentation gaps (per-objective metrics, LC-06 analyzer)
   - Data-quality observations
   - Suggested next-iteration improvements
10. **Appendix** — links to `/tmp/` artifacts (note: ephemeral), plan_id
    for DB re-query, log window timestamps.

---

## Files involved (all READ-ONLY except the report)

| File | Role | Edited? |
|---|---|---|
| `solver_v2/config.py` | Source of ENABLED_CONSTRAINTS + fallback weights | No |
| `solver_v2/api/client.py` | Reference for endpoint URLs | No |
| `solver_v2/api/service.py` | `_fetch_and_preprocess_sync` for fetch semantics | No |
| `solver_v2/solver/model.py` | Objective assembly reference | No |
| `solver_v2/analysis/solution_analyzer.py` | Summary assembly reference | No |
| `solver_v2/analysis/constraint_analyzers/*` | Insight string reference | No |
| `mock_data_v2/database_application_v2/database/schema_planner_assignments.sql` | Row-shape reference | No |
| `mock_data_v2/database_application_v2/api/routers/*` | Endpoint reference | No |
| `/tmp/holistic_*.json` | Run artifacts | Written |
| `/tmp/holistic_solver.log` | Log capture | Written |
| **`solver_v2/planner_dev/holistic_validation_report-2026-04-21.md`** | **Final deliverable** | **Written (new file)** |

---

## Verification — how to know the report is good

1. Every table has real data (no placeholders).
2. The 15 enabled constraints are each accounted for in §5 with PASS/FAIL
   backed by an observable check, or an explicit "N/A — cannot verify
   without X" note.
3. Each of the 10+ active objectives has either (a) an observable metric
   showing its effect, or (b) an explicit "unobserved — instrumentation gap"
   note.
4. Every `key_insight` and `top_recommendation` from the analysis_summary is
   classified in §7.
5. RT/CT segment distribution in §8 matches the LC-06 4+2/6 targets
   (pro-rated where the segment is a partial month).
6. Gaps section in §9 surfaces at least:
   - per-objective metrics not in API response
   - LC-06 has no dedicated analyzer
   - fetched input data is not persisted
7. The report is self-contained — a reader can understand the state of the
   planner without opening the solver codebase.

---

## Out of scope

- Changing any solver code, constraint, or objective weight.
- Rebuilding containers.
- Adding new analyzers or surfacing additional metrics (these are findings,
  not deliverables).
- Load or performance testing beyond the focused 3-team / 30-day run.
- Frontend integration testing.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Solver times out at 1800s | Stall detection (120s) caps effective search; will report partial solution + flag |
| Input reconstruction drifts vs actual fetch | Compare against `Actual counts:` log line; report drift as limitation |
| `ct_rt_compliance` empty in analysis_summary | Still have raw `output_assignments` filtered to RT/CT types — deep dive survives |
| Sub-partition duplicates regress | Fix A+B dedupe + DATE-OVERLAP log; grep log for `[DATE-OVERLAP]` — any match is a report finding |
| One of the 3 test teams has zero qualifying resources for the plan_range | Stage 0 step 4 verifies upfront; if so, drop team and note in §2 |
