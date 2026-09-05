# RAG Reliability Release Gate

Local-first reliability harness for evaluating whether a named RAG configuration
remains semantically reliable and operationally stable under controlled context
pressure, corpus drift, dependency faults, and traffic load.

The system is designed to produce reproducible release evidence and a final:

- PASS
- CONDITIONAL_PASS
- FAIL

The public Context Rot RAG Chaos Lab is a static evidence viewer, not a live
inference or chaos-testing product.

See `PRD.md` for the authoritative product requirements.
