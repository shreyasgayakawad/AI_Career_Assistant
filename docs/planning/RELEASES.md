# RELEASES

No versioned release has been cut yet. Development proceeds on `main` and the
version marker remains v0.1.0 across planning documents.

## Proposed release criteria

A version may be tagged only when:

- All shipped phases are recorded in `PHASES.md` and `CHANGELOG.md`
- Full test suite is green (`python -m scripts.run_all_tests`)
- No unresolved high-severity regressions
- Working tree clean; annotated tag created at the release commit
