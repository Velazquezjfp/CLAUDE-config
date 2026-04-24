#!/usr/bin/env python3
"""
Sprint planner: parse polished requirement files, build a dependency graph,
compute parallelizable waves, detect conflicts and cycles, emit JSON.

Called from the /sprint-roadmap-build and /sprint-roadmap-update slash commands.

Usage:
    python plan.py <sprint_number>

Reads:
    docs/requirements/sprint-{NNN}/*.md (excluding _input.md, _index.md, _roadmap.md)

Writes:
    docs/requirements/sprint-{NNN}/_dep-graph.json

Exits non-zero on fatal errors (missing sprint folder, no requirement files,
unparseable files, dependency cycle). Warnings are embedded in the JSON.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Resource:
    """A single resource entry in affected_surface, e.g. `table: orders`."""
    type: str  # table | endpoint | env_var | file | class | function | component | selector | constant
    name: str
    is_new: bool = False


@dataclass
class Requirement:
    id: str
    title: str
    type: str  # functional | non-functional | data
    status: str
    sprint: str
    path: str  # filesystem path, for traceability
    creates: list[Resource] = field(default_factory=list)
    modifies: list[Resource] = field(default_factory=list)
    reads: list[Resource] = field(default_factory=list)
    deletes: list[Resource] = field(default_factory=list)
    semantic_dependencies: list[str] = field(default_factory=list)


@dataclass
class Edge:
    from_id: str
    to_id: str
    kind: str       # "semantic" | "structural" | "conflict"
    reason: str     # human-readable


@dataclass
class Warning:
    level: str      # "warn" | "error"
    code: str       # machine-readable category
    message: str


# ---------------------------------------------------------------------------
# Constants — must match requirements-polisher vocabulary exactly
# ---------------------------------------------------------------------------


VALID_RESOURCE_TYPES = {
    "table", "endpoint", "env_var", "file", "class",
    "function", "component", "selector", "constant",
}

VALID_REQ_TYPES = {"functional", "non-functional", "data"}

VERBS = ("Creates", "Modifies", "Reads", "Deletes")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
RESOURCE_LINE_RE = re.compile(
    r"^\s*-\s*(?P<type>\w+)\s*:\s*(?P<name>[^\s(]+(?:\s+[^\s(]+)*?)\s*(?P<new>\(new\))?\s*$"
)
SEMDEP_LINE_RE = re.compile(r"^\s*-\s*(?P<id>S\d{3}-[A-Z]+-\d{3})\b")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse a minimal subset of YAML frontmatter: key: value per line."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def parse_resource_line(line: str) -> Optional[Resource]:
    m = RESOURCE_LINE_RE.match(line)
    if not m:
        return None
    rtype = m.group("type").strip()
    if rtype not in VALID_RESOURCE_TYPES:
        return None
    return Resource(
        type=rtype,
        name=m.group("name").strip(),
        is_new=bool(m.group("new")),
    )


def parse_affected_surface(body: str) -> tuple[list[Resource], list[Resource], list[Resource], list[Resource]]:
    """Extract creates/modifies/reads/deletes from the Affected surface section."""
    creates: list[Resource] = []
    modifies: list[Resource] = []
    reads: list[Resource] = []
    deletes: list[Resource] = []

    # Find the Affected surface section
    lines = body.splitlines()
    in_section = False
    current_bucket: Optional[list[Resource]] = None

    for line in lines:
        stripped = line.strip()

        if re.match(r"^##\s+Affected surface\s*$", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            # next section
            break
        if not in_section:
            continue

        # Subsection headers like **Creates:** or **Creates**: or **Creates**
        m = re.match(r"^\*\*(Creates|Modifies|Reads|Deletes):?\*\*\s*:?\s*$",
                     stripped, re.IGNORECASE)
        if m:
            verb = m.group(1).lower()
            current_bucket = {
                "creates": creates, "modifies": modifies,
                "reads": reads, "deletes": deletes,
            }[verb]
            continue

        if current_bucket is None:
            continue

        res = parse_resource_line(line)
        if res is not None:
            current_bucket.append(res)

    return creates, modifies, reads, deletes


def parse_semantic_dependencies(body: str) -> list[str]:
    deps: list[str] = []
    lines = body.splitlines()
    in_section = False

    for line in lines:
        if re.match(r"^##\s+Semantic dependencies\s*$", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if not in_section:
            continue
        m = SEMDEP_LINE_RE.match(line)
        if m:
            deps.append(m.group("id"))

    return deps


def parse_requirement(path: Path) -> tuple[Optional[Requirement], list[Warning]]:
    """Parse a single S###-T-NNN.md file. Returns (requirement, warnings)."""
    warnings: list[Warning] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        warnings.append(Warning("error", "unreadable",
                                f"Could not read {path}: {exc}"))
        return None, warnings

    fm = parse_frontmatter(text)
    required_keys = {"id", "title", "type", "status", "sprint"}
    missing = required_keys - fm.keys()
    if missing:
        warnings.append(Warning(
            "error", "bad_frontmatter",
            f"{path.name}: missing frontmatter keys: {sorted(missing)}",
        ))
        return None, warnings

    if fm["type"] not in VALID_REQ_TYPES:
        warnings.append(Warning(
            "warn", "unknown_type",
            f"{path.name}: type '{fm['type']}' is not in {sorted(VALID_REQ_TYPES)}; treating as functional",
        ))
        fm["type"] = "functional"

    body = strip_frontmatter(text)
    creates, modifies, reads, deletes = parse_affected_surface(body)
    sem_deps = parse_semantic_dependencies(body)

    if not (creates or modifies or reads or deletes):
        warnings.append(Warning(
            "warn", "empty_surface",
            f"{fm['id']}: affected_surface is empty — this requirement will appear in Wave 1 "
            f"with no dependencies and no conflicts. Verify this is intentional.",
        ))

    req = Requirement(
        id=fm["id"],
        title=fm["title"],
        type=fm["type"],
        status=fm["status"],
        sprint=fm["sprint"],
        path=str(path),
        creates=creates,
        modifies=modifies,
        reads=reads,
        deletes=deletes,
        semantic_dependencies=sem_deps,
    )
    return req, warnings


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def resource_key(r: Resource) -> tuple[str, str]:
    """Normalized key for resource equality. Case-insensitive on name."""
    return (r.type, r.name.lower())


def build_edges(reqs: list[Requirement]) -> tuple[list[Edge], list[Warning]]:
    """Build structural and semantic edges. Conflicts are detected later.

    Rules:
      * Semantic: declared in requirement text.
      * Structural writer-before-reader: A creates X, B reads X => B depends on A.
      * Structural writer-before-writer: A creates X, B modifies X => B depends on A.
      * Deletes-last: A deletes X, B reads or modifies X => A depends on B.
    """
    edges: list[Edge] = []
    warnings: list[Warning] = []
    by_id = {r.id: r for r in reqs}

    # Index resources by type
    creators: dict[tuple[str, str], list[str]] = {}
    readers: dict[tuple[str, str], list[str]] = {}
    modifiers: dict[tuple[str, str], list[str]] = {}
    deleters: dict[tuple[str, str], list[str]] = {}

    for req in reqs:
        for r in req.creates:
            creators.setdefault(resource_key(r), []).append(req.id)
        for r in req.reads:
            readers.setdefault(resource_key(r), []).append(req.id)
        for r in req.modifies:
            modifiers.setdefault(resource_key(r), []).append(req.id)
        for r in req.deletes:
            deleters.setdefault(resource_key(r), []).append(req.id)

    # Duplicate creators: two requirements cannot both claim to create the same resource.
    # One creates it, the others should either read/modify/delete it, or the duplicate
    # should be removed entirely.
    for key, creator_ids in creators.items():
        if len(creator_ids) > 1:
            rtype, rname = key
            warnings.append(Warning(
                "error", "duplicate_creator",
                f"{rtype} '{rname}' is declared as created by multiple requirements: "
                f"{sorted(set(creator_ids))}. Only one requirement can be the creator. "
                f"For the others, either remove the entry or move it to modifies/reads.",
            ))

    # Semantic dependencies
    for req in reqs:
        for dep_id in req.semantic_dependencies:
            if dep_id not in by_id:
                warnings.append(Warning(
                    "warn", "unresolved_semantic_dep",
                    f"{req.id}: semantic dependency {dep_id} not found in this sprint. "
                    f"Cross-sprint deps are noted but not enforced in this roadmap.",
                ))
                continue
            edges.append(Edge(
                from_id=dep_id,
                to_id=req.id,
                kind="semantic",
                reason=f"{req.id} declares a semantic dependency on {dep_id}",
            ))

    # Structural: create → read, create → modify
    for key, creator_ids in creators.items():
        rtype, rname = key
        for creator in creator_ids:
            # readers depend on creator
            for reader in readers.get(key, []):
                if reader == creator:
                    continue
                edges.append(Edge(
                    from_id=creator,
                    to_id=reader,
                    kind="structural",
                    reason=f"{reader} reads {rtype} '{rname}' which {creator} creates",
                ))
            # modifiers depend on creator
            for modifier in modifiers.get(key, []):
                if modifier == creator:
                    continue
                edges.append(Edge(
                    from_id=creator,
                    to_id=modifier,
                    kind="structural",
                    reason=f"{modifier} modifies {rtype} '{rname}' which {creator} creates",
                ))

    # Structural: deletes-last
    for key, deleter_ids in deleters.items():
        rtype, rname = key
        for deleter in deleter_ids:
            for reader in readers.get(key, []):
                if reader == deleter:
                    continue
                edges.append(Edge(
                    from_id=reader,
                    to_id=deleter,
                    kind="structural",
                    reason=f"{deleter} deletes {rtype} '{rname}' which {reader} reads — delete after reads",
                ))
            for modifier in modifiers.get(key, []):
                if modifier == deleter:
                    continue
                edges.append(Edge(
                    from_id=modifier,
                    to_id=deleter,
                    kind="structural",
                    reason=f"{deleter} deletes {rtype} '{rname}' which {modifier} modifies — delete after mods",
                ))

    # Mutual semantic dependencies: if A declares a semantic dep on B AND B declares
    # one on A, that's always an authoring error — one must come before the other.
    # Emit a targeted error before the general cycle detector sees it, so the message
    # points directly at the two files to edit.
    semantic_pairs = {(e.from_id, e.to_id) for e in edges if e.kind == "semantic"}
    reported: set[frozenset[str]] = set()
    for (a, b) in semantic_pairs:
        if (b, a) in semantic_pairs:
            key = frozenset((a, b))
            if key in reported:
                continue
            reported.add(key)
            warnings.append(Warning(
                "error", "mutual_semantic_dependency",
                f"{a} and {b} declare each other as semantic dependencies. "
                f"Exactly one of these declarations is wrong — remove the entry "
                f"from whichever requirement logically comes first "
                f"(its `## Semantic dependencies` section should not list the later one).",
            ))

    return edges, warnings


def dedupe_edges(edges: list[Edge]) -> list[Edge]:
    """Collapse duplicate edges. Keep the strongest-reasoned one (semantic > structural > conflict)."""
    priority = {"semantic": 0, "structural": 1, "conflict": 2}
    best: dict[tuple[str, str], Edge] = {}
    for e in edges:
        k = (e.from_id, e.to_id)
        if k not in best or priority[e.kind] < priority[best[k].kind]:
            best[k] = e
    return sorted(best.values(), key=lambda e: (e.from_id, e.to_id))


# ---------------------------------------------------------------------------
# Cycle detection and topological sort
# ---------------------------------------------------------------------------


def detect_cycles(reqs: list[Requirement], edges: list[Edge]) -> list[list[str]]:
    """Tarjan-esque DFS to find all cycles. Returns list of cycles (each a list of IDs)."""
    graph: dict[str, list[str]] = {r.id: [] for r in reqs}
    for e in edges:
        if e.from_id in graph and e.to_id in graph:
            graph[e.from_id].append(e.to_id)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in graph}
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        color[node] = GRAY
        stack.append(node)
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                idx = stack.index(neighbor)
                cycles.append(stack[idx:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor)
        stack.pop()
        color[node] = BLACK

    for node in sorted(graph):
        if color[node] == WHITE:
            dfs(node)

    return cycles


def compute_base_waves(reqs: list[Requirement], edges: list[Edge]) -> list[list[str]]:
    """Kahn's algorithm: iteratively peel nodes with in-degree 0."""
    in_degree: dict[str, int] = {r.id: 0 for r in reqs}
    adj: dict[str, list[str]] = {r.id: [] for r in reqs}
    for e in edges:
        if e.from_id in in_degree and e.to_id in in_degree:
            adj[e.from_id].append(e.to_id)
            in_degree[e.to_id] += 1

    waves: list[list[str]] = []
    remaining = dict(in_degree)

    while remaining:
        # Nodes with no remaining incoming edges
        ready = sorted([n for n, d in remaining.items() if d == 0])
        if not ready:
            # Cycle — shouldn't happen if cycle detection ran first, but defend
            break
        waves.append(ready)
        for n in ready:
            del remaining[n]
            for m in adj[n]:
                if m in remaining:
                    remaining[m] -= 1

    return waves


def resolve_file_conflicts(
    waves: list[list[str]],
    reqs_by_id: dict[str, Requirement],
) -> tuple[list[list[str]], list[Edge]]:
    """For each wave, if two requirements modify the same file, keep the lower-ID
    one in the current wave and push the other to the next wave. Records the
    resolution as conflict edges for traceability."""
    new_waves: list[list[str]] = []
    conflict_edges: list[Edge] = []
    overflow: list[str] = []

    i = 0
    while i < len(waves) or overflow:
        current = sorted((waves[i] if i < len(waves) else []) + overflow)
        overflow = []

        # Group by modified-file to find conflicts
        files_in_wave: dict[str, list[str]] = {}
        for req_id in current:
            for res in reqs_by_id[req_id].modifies:
                if res.type == "file":
                    files_in_wave.setdefault(res.name.lower(), []).append(req_id)

        # Mark reqs that conflict with something earlier in the wave
        to_defer: set[str] = set()
        for file_name, req_ids in files_in_wave.items():
            if len(req_ids) < 2:
                continue
            sorted_ids = sorted(set(req_ids))
            keeper = sorted_ids[0]
            for losing in sorted_ids[1:]:
                to_defer.add(losing)
                conflict_edges.append(Edge(
                    from_id=keeper,
                    to_id=losing,
                    kind="conflict",
                    reason=f"both modify file '{file_name}' — {losing} deferred to avoid parallel-edit collision",
                ))

        kept = [r for r in current if r not in to_defer]
        deferred = [r for r in current if r in to_defer]

        new_waves.append(kept)
        overflow = deferred
        i += 1

    # Drop empty trailing waves (shouldn't happen, but safe)
    while new_waves and not new_waves[-1]:
        new_waves.pop()

    return new_waves, conflict_edges


def label_phase(wave: list[str], reqs_by_id: dict[str, Requirement]) -> str:
    """Assign a dominant-phase label to a wave. Pure heuristic, not load-bearing."""
    types = [reqs_by_id[r].type for r in wave]
    # If any data requirement exists, that dominates (foundation).
    if any(t == "data" for t in types):
        return "Foundational"
    if all(t == "non-functional" for t in types):
        return "Integration"
    return "Feature"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def load_sprint(sprint_dir: Path) -> tuple[list[Requirement], list[Warning]]:
    """Load all S###-*.md files from the sprint directory."""
    all_warnings: list[Warning] = []
    reqs: list[Requirement] = []

    if not sprint_dir.is_dir():
        all_warnings.append(Warning(
            "error", "no_sprint_dir",
            f"Sprint directory does not exist: {sprint_dir}",
        ))
        return [], all_warnings

    pattern = re.compile(r"^S\d{3}-[A-Z]+-\d{3}\.md$")
    for path in sorted(sprint_dir.iterdir()):
        if not path.is_file():
            continue
        if not pattern.match(path.name):
            continue
        req, warnings = parse_requirement(path)
        all_warnings.extend(warnings)
        if req is not None:
            reqs.append(req)

    if not reqs:
        all_warnings.append(Warning(
            "error", "no_requirements",
            f"No polished requirement files found in {sprint_dir}. "
            f"Expected files matching S###-TYPE-###.md.",
        ))

    return reqs, all_warnings


def build_graph(sprint: str, sprint_dir: Path) -> dict:
    """Run the full pipeline and return a JSON-serializable dict."""
    reqs, warnings = load_sprint(sprint_dir)

    if any(w.level == "error" for w in warnings):
        return {
            "sprint": sprint,
            "generated_at_unix": int(__import__("time").time()),
            "ok": False,
            "requirements": [],
            "edges": [],
            "waves": [],
            "cycles": [],
            "warnings": [asdict(w) for w in warnings],
        }

    reqs_by_id = {r.id: r for r in reqs}

    edges, edge_warnings = build_edges(reqs)
    warnings.extend(edge_warnings)
    edges = dedupe_edges(edges)

    # Errors from build_edges (duplicate_creator, mutual_semantic_dependency) block
    # wave computation. mutual_semantic_dependency will also trip the cycle detector,
    # but we want the targeted message surfaced regardless.
    if any(w.level == "error" for w in warnings):
        return {
            "sprint": sprint,
            "generated_at_unix": int(__import__("time").time()),
            "ok": False,
            "requirements": [req_to_dict(r) for r in reqs],
            "edges": [asdict(e) for e in edges],
            "waves": [],
            "cycles": [],
            "warnings": [asdict(w) for w in warnings],
        }

    cycles = detect_cycles(reqs, edges)
    if cycles:
        for cyc in cycles:
            warnings.append(Warning(
                "error", "cycle",
                f"Dependency cycle detected: {' -> '.join(cyc)}",
            ))
        return {
            "sprint": sprint,
            "generated_at_unix": int(__import__("time").time()),
            "ok": False,
            "requirements": [req_to_dict(r) for r in reqs],
            "edges": [asdict(e) for e in edges],
            "waves": [],
            "cycles": cycles,
            "warnings": [asdict(w) for w in warnings],
        }

    base_waves = compute_base_waves(reqs, edges)
    final_waves, conflict_edges = resolve_file_conflicts(base_waves, reqs_by_id)
    all_edges = dedupe_edges(edges + conflict_edges)

    # Attach phase labels to each wave
    wave_entries = []
    for idx, wave in enumerate(final_waves, start=1):
        wave_entries.append({
            "wave": idx,
            "phase": label_phase(wave, reqs_by_id),
            "requirements": wave,
        })

    return {
        "sprint": sprint,
        "generated_at_unix": int(__import__("time").time()),
        "ok": True,
        "requirements": [req_to_dict(r) for r in reqs],
        "edges": [asdict(e) for e in all_edges],
        "waves": wave_entries,
        "cycles": [],
        "warnings": [asdict(w) for w in warnings],
    }


def req_to_dict(r: Requirement) -> dict:
    """Compact requirement dict for the JSON output."""
    return {
        "id": r.id,
        "title": r.title,
        "type": r.type,
        "status": r.status,
        "path": r.path,
        "surface": {
            "creates": [asdict(x) for x in r.creates],
            "modifies": [asdict(x) for x in r.modifies],
            "reads": [asdict(x) for x in r.reads],
            "deletes": [asdict(x) for x in r.deletes],
        },
        "semantic_dependencies": r.semantic_dependencies,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: plan.py <sprint_number>", file=sys.stderr)
        return 2

    try:
        sprint_num = int(sys.argv[1])
    except ValueError:
        print(f"sprint number must be an integer, got {sys.argv[1]!r}", file=sys.stderr)
        return 2

    sprint = f"{sprint_num:03d}"
    sprint_dir = Path.cwd() / "docs" / "requirements" / f"sprint-{sprint}"

    result = build_graph(sprint, sprint_dir)

    out_path = sprint_dir / "_dep-graph.json"
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n",
                            encoding="utf-8")
    except OSError as exc:
        print(f"could not write {out_path}: {exc}", file=sys.stderr)
        return 1

    # Always emit a one-line summary to stdout for the slash command to parse
    err_count = sum(1 for w in result["warnings"] if w["level"] == "error")
    warn_count = sum(1 for w in result["warnings"] if w["level"] == "warn")
    status = "ok" if result["ok"] else "failed"
    wave_count = len(result["waves"])
    print(f"[plan] status={status} sprint={sprint} "
          f"requirements={len(result['requirements'])} "
          f"waves={wave_count} edges={len(result['edges'])} "
          f"errors={err_count} warnings={warn_count} out={out_path}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())