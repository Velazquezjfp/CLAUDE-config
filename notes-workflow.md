WOrkflow between documenters and code changes: 
write code → commit (code) → /code-graph-update → /api-doc-update → review → commit (docs) → push


Organizing:
docs/requirements/
├── sprint-042/
│   ├── _input.md                    # YOU write this: bullet list of raw requests
│   ├── F-001.md                     # agent writes: one polished requirement per file
│   ├── F-002.md
│   ├── NFR-001.md
│   ├── D-001.md
│   └── _index.md                    # agent writes: sprint-level summary (bounded)
├── sprint-043/
│   └── ...
└── _backlog.md                      # optional: cross-sprint parking lot (you own this)


For work on polishing requirements: 
./.claude/agents/BO-requirements-polisher.md
./.claude/commands/requirement-polish.md     ← /requirement-polish {sprint}
./.claude/commands/requirement-new.md        ← /requirement-new {sprint} "description"

use /intialize-sprint {number}
Use /requirement-polish {sprint}
And requirement-new {sprint} "description" --> so you dont hacve to go back to _input.md. 

After comes the PM slash command 

here using a skill: 
/start and /update in case requirements change I need to replan the roadmap. 

Then use the implement-requirement command, it will test and iterate until implementation is complete. Will also document. 



