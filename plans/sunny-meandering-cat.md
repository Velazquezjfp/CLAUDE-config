# Plan: Always-Blocking Absence Calendar Types

## Context

Absences (vacations, sick leave, etc.) are currently stored in the `assignments` table with specific `calendar_type` values. The solver fetches these via `/resource-blocks/` API. Two problems exist:

1. **`lock_allocations=false`** → `all_blocks = []` → absences don't block resources (a resource on vacation could be assigned work)
2. **`lock_allocations=true`** → if FE puts absence types in `replannable_demand_type`, absences get excluded from blocking

**Goal:** A hardcoded list of calendar types representing TRUE absences must ALWAYS block resource availability, regardless of `lock_allocations` or `replannable_demand_type`.

**Long-term note:** This is transitional. Eventually absences will move to the dedicated `absences` table. The hardcoded list will be removed then.

---

## Approach: Solver-Side Only (No API Changes)

All changes stay within `solver_v2/`. The existing `/resource-blocks/` API is used as-is.

- When `lock_allocations=false`: Fetch all blocks from API, then **client-side filter** to keep only always-blocking types
- When `lock_allocations=true`: **Strip** always-blocking types from the replannable exclusion list before calling API, so they're never excluded

---

## Files to Modify

### 1. `solver_v2/config.py` — Add the constant

Add after line 157 (existing `ABSENCE_BLOCKED_TYPES = None`):

```python
# Calendar types that represent TRUE absences — ALWAYS block resource availability
# regardless of lock_allocations or replannable_demand_type settings.
# Values match exact DB assignments.calendar_type values (verified via changes-DB-March13-2026.md).
# Compared case-insensitively with .strip() at call sites for whitespace safety.
# TRANSITIONAL: Remove when absences fully migrate to the absences table.
ALWAYS_BLOCKING_CALENDAR_TYPES = [
    "Congés payés",            # 816 records in DB
    "CT Jour de compensation", # 22,822 records
    "Maladie",                 # 18 records
    "Pas disponible",          # 1,010 records
    "RT Jour de repos",        # 26,387 records
    "Service militaire / civil",  # 200 records
    "Vacances",                # 7,631 records
    "Vacances non payées",     # 30 records (note: accent on payées)
    "Visite médicale",         # 6 records
]
```

> **Note:** Values verified against actual `assignments.calendar_type` column in external DB. Case-insensitive + `.strip()` comparison used at all call sites for whitespace safety (DEV DB has trailing spaces on some values).

### 2. `solver_v2/api/data_pipeline.py` — Add helper functions

Add two helper functions (after existing imports, before `build_locked_assignments`). Centralizes the logic so it's not duplicated across `service.py` and `main.py`:

```python
from config import ALWAYS_BLOCKING_CALENDAR_TYPES

def get_always_blocking_set() -> set:
    """Return lowercase, stripped set of always-blocking calendar types."""
    return {t.strip().lower() for t in ALWAYS_BLOCKING_CALENDAR_TYPES}

def sanitize_replannable_types(replannable_types: list, logger=None) -> list:
    """Remove always-blocking absence types from replannable list.
    These types must NEVER be excluded from blocking."""
    if not replannable_types:
        return []
    always_blocking = get_always_blocking_set()
    overlap = [t for t in replannable_types if t.strip().lower() in always_blocking]
    safe = [t for t in replannable_types if t.strip().lower() not in always_blocking]
    if overlap and logger:
        logger.warning(f"replannable_demand_type contains always-blocking absences (protected): {overlap}")
    return safe

def filter_to_always_blocking(blocks: list) -> list:
    """Filter resource blocks to keep only always-blocking absence types.
    Used when lock_allocations=false to still enforce absences."""
    always_blocking = get_always_blocking_set()
    return [b for b in blocks if b.get('block_type', '').strip().lower() in always_blocking]
```

### 3. `solver_v2/api/service.py` — Main trigger path (lines 750-774)

Replace the current `if not lock_allocations: all_blocks = []` block:

```python
# --- 4D. Fetch resource blocks ---
replannable_types = job.request.replannable_demand_type
lock_allocations = job.request.lock_allocations

filter_resource_ids = list(sliced_resource_ids) if sliced_resource_ids else None
if filter_resource_ids:
    logger.info(f"Fetching resource blocks for {len(filter_resource_ids)} sliced resources only")

from api.data_pipeline import sanitize_replannable_types, filter_to_always_blocking

if not lock_allocations:
    # Even with lock_allocations=false, true absences must still block
    blocks_data = client.get_resource_blocks(
        category="all",
        start_date=start_date,
        end_date=end_date,
        resource_ids=filter_resource_ids
    )
    all_blocks = filter_to_always_blocking(blocks_data.get('data', []))
    logger.info(f"lock_allocations=false: kept {len(all_blocks)} always-blocking absence blocks "
                f"(from {blocks_data.get('total', 0)} total)")
else:
    safe_replannable = sanitize_replannable_types(replannable_types, logger)
    blocks_data = client.get_resource_blocks(
        category="all",
        start_date=start_date,
        end_date=end_date,
        exclude_calendar_types=safe_replannable if safe_replannable else None,
        resource_ids=filter_resource_ids
    )
    all_blocks = blocks_data.get('data', [])
    logger.info(f"lock_allocations=true: {len(all_blocks)} blocks "
                f"(replannable excluded: {safe_replannable or 'none'})")

absences_data = {'data': all_blocks, 'total': len(all_blocks)}
logger.info(f"Total resource blocks for solver: {len(all_blocks)}")
```

### 4. `solver_v2/api/service.py` — Pre-planning path (lines 1743-1756)

Same pattern:

```python
# Fetch resource blocks — always-blocking absences are protected
from api.data_pipeline import sanitize_replannable_types, filter_to_always_blocking

lock_allocations = request.lock_allocations if hasattr(request, 'lock_allocations') else True
replannable_types = request.replannable_demand_type if hasattr(request, 'replannable_demand_type') else []

if not lock_allocations:
    absences_response = client.get_resource_blocks(
        category="all",
        start_date=request.start_date,
        end_date=request.end_date,
    )
    absences_data = filter_to_always_blocking(absences_response.get('data', []))
else:
    safe_replannable = sanitize_replannable_types(replannable_types, logger)
    absences_response = client.get_resource_blocks(
        category="all",
        start_date=request.start_date,
        end_date=request.end_date,
        exclude_calendar_types=safe_replannable if safe_replannable else None
    )
    absences_data = absences_response.get('data', [])
```

### 5. `solver_v2/main.py` — Standalone mode (lines 39-70)

Protect env-var replannable types:

```python
replannable_types_env = os.environ.get('REPLANNABLE_DEMAND_TYPES', '')
replannable_types = [t.strip() for t in replannable_types_env.split(',') if t.strip()] if replannable_types_env else []

from api.data_pipeline import sanitize_replannable_types
safe_replannable = sanitize_replannable_types(replannable_types)
if safe_replannable:
    print(f"Replannable types (excluded from blocking): {safe_replannable}")

# Then use safe_replannable instead of replannable_types in get_resource_blocks calls
```

---

## Files NOT Modified

| File | Reason |
|------|--------|
| `data_pipeline.py:build_locked_assignments()` | Imported but never called in active flow |
| `constraints/hc_01_absence_blocking.py` | Consumes `absences_data` as-is — no changes needed |
| `preprocessing/data_processor.py` | Processes blocks regardless of type — no changes needed |
| `api/routers/resource_blocks.py` (API) | No API changes — solver handles filtering client-side |
| `api/client.py` | No changes to HTTP client |

---

## Verification

1. **Unit test helpers:** Call `sanitize_replannable_types(["Vacances", "Service de nuit"])` → returns `["Service de nuit"]`
2. **Unit test filter:** Call `filter_to_always_blocking([{"block_type": "Vacances"}, {"block_type": "Service de nuit"}])` → returns only the Vacances block
3. **Integration test — lock_allocations=false:** Trigger solver with `lock_allocations=false`, verify absence blocks appear in logs and resources on vacation are not assigned
4. **Integration test — lock_allocations=true + replannable override:** Trigger with `replannable_demand_type=["Vacances"]`, verify warning is logged and Vacances still blocks
5. **Docker rebuild:** `docker compose restart` for solver service, verify logs show new behavior
