---
description: Query Knowledge Graph for information relevant to your question
argument-hint: [your_question_or_topic]
allowed-tools: Bash
---

# Knowledge Graph Query

You need to read and analyze the Knowledge Graph located at `/mnt/c/Users/Javie/.knowledge_graph/graph.json` to answer: **$ARGUMENTS**

## Process:
1. **Load Knowledge Graph**: Read the JSON file from the specified Windows mount path
2. **Parse and Search**: Extract entities, relations, and observations relevant to the query
3. **Context Analysis**: Find connections and patterns related to the question
4. **Synthesize Answer**: Provide comprehensive response based on graph data

## Implementation:
Use the analysis tool to:
- Load the JSON file from `/mnt/c/Users/Javie/.knowledge_graph/graph.json`
- Search through entities, relationships, and observations
- Filter results based on relevance to the query
- Present findings in a structured, actionable format

## Output Format:
1. **Direct Answer**: Clear response to the original question
2. **Supporting Evidence**: Relevant entities and relationships from the graph
3. **Additional Context**: Related information that might be useful
4. **Recommendations**: Actionable insights based on the data

Start by loading the Knowledge Graph and then analyzing it for information relevant to the query.
