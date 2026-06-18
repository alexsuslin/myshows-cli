# Contributing

This document describes the expected delivery workflow for `myshows-cli`.

It is written for:

- maintainers
- external contributors
- AI coding agents

The goal is to keep the project predictable, reviewable, and release-friendly without adding unnecessary process.

## Principles

- Keep `main` stable and releasable.
- Prefer small, short-lived branches.
- Use pull requests for almost all changes.
- Keep code, tests, docs, and changelog in sync.
- Separate feature delivery from release preparation.

## Source of truth

When working on code or release tasks, use these files together:

- `AGENTS.md` for project rules
- `docs/agent-cli.md` for the agent-facing CLI contract
- `CHANGELOG.md` for release notes history
- this file for contribution and release workflow

## Recommended model

Use a lightweight trunk-based workflow:

- one permanent branch: `main`
- short-lived feature branches
- PR-based merges back into `main`
- releases created from `main`

## Issue-first workflow

Whenever practical, start with a GitHub Issue.

Use Issues for:

- features
- bugs
- docs work
- release tasks
- refactors with behavioral impact

Good defaults:

- create one issue per user-visible change
- link PRs to issues with `Closes #<number>`
- use milestones for release planning

## Branch naming

Prefer short branch names with an issue number when available.

Examples:

- `codex/12-unmark-command`
- `codex/18-xdg-config-support`
- `docs/22-release-workflow`

If there is no issue yet, create one first when the work is more than a trivial typo fix.

## Day-to-day development flow

Standard flow:

1. Create or pick a GitHub Issue.
2. Switch from `main` to a new branch.
3. Implement the change.
4. Add or update tests.
5. Update docs when the user-facing behavior changes.
6. Add changelog notes to `Unreleased` if the change is release-worthy.
7. Run validation locally.
8. Push the branch.
9. Open a PR.
10. Merge after CI passes and review is complete.

## Required updates when behavior changes

When a change affects users, maintainers, or agents, update the relevant docs in the same PR.

Common files:

- `README.md`
- `docs/agent-cli.md`
- `docs/skill.md`
- `AGENTS.md`
- `CHANGELOG.md`

## Testing expectations

Use TDD for user-facing features whenever practical.

Minimum expectations for code changes:

- add or update tests
- keep `pytest` green
- keep `ruff` green
- ensure the package still builds

Recommended local checks:

```bash
python -m pytest
python -m ruff check .
python -m build
python -m compileall src tests
```

Or:

```bash
make check
```

## Pull request workflow

PRs should be:

- focused
- small enough to review
- linked to an issue when possible
- accompanied by updated tests and docs

Recommended PR structure:

- summary of the change
- why it is needed
- testing performed
- linked issue

Suggested PR body pattern:

```text
## Summary
- add ...
- update ...

## Testing
- pytest
- python -m ruff check .
- python -m build

Closes #123
```

## Merge policy

Preferred merge style: `squash`.

Why:

- keeps `main` history compact
- makes release notes easier to read
- avoids noisy branch-level commit history

Recommended rules:

- no direct pushes to `main`
- merge only after green CI
- use PR review for non-trivial changes

## Solo maintainer workflow

If you are working alone, still prefer PRs for most changes.

Why:

- CI runs naturally
- diffs stay reviewable
- release preparation is easier
- project history stays cleaner

Acceptable exceptions:

- typo-only docs fix
- emergency fix where speed matters more than ceremony

Even then, prefer a branch if the change touches code.

## Multi-developer workflow

When several people or agents contribute:

- require PRs for all code changes
- avoid direct pushes to `main`
- use issues to claim work
- keep branches short-lived
- prefer one change per PR

Recommended collaboration rules:

- feature work starts from an issue
- every PR has a clear owner
- every PR includes validation results
- release work happens separately from feature work

## AI agent workflow

AI agents should follow the same branch-and-PR model as humans.

Agent expectations:

- do not push directly to `main`
- do not change version numbers for ordinary feature PRs
- do not prepare a release unless explicitly asked
- update docs when behavior changes
- update tests together with code
- mention assumptions and risks in the PR description when relevant

## Versioning policy

Use semantic versioning.

For this project:

- patch: compatible fix or operational improvement
- minor: new compatible CLI capability
- major: breaking CLI or response contract changes

Examples:

- config aliases: patch
- XDG config support: patch
- new command like `unmark`: minor
- changing JSON response structure incompatibly: major

## Changelog policy

Use `CHANGELOG.md` continuously.

During normal feature work:

- add release-worthy notes under `Unreleased`

During release preparation:

- convert `Unreleased` notes into a versioned section
- keep the release notes concise and user-facing

## Release workflow

Do not bump the version in every feature PR.

Preferred release flow:

1. Merge feature PRs into `main`.
2. Review `CHANGELOG.md`.
3. Decide the next version.
4. Update version in:
   - `pyproject.toml`
   - `src/myshows_cli/__init__.py`
5. Finalize release notes in `CHANGELOG.md`.
6. Run validation:
   - `pytest`
   - `ruff`
   - `build`
7. Create a release commit.
8. Create an annotated git tag `vX.Y.Z`.
9. Push `main`.
10. Push the tag.
11. Create the GitHub Release.

## GitHub CLI examples

Create an issue:

```bash
gh issue create --title "Add unmark command" --label feature
```

Create a branch:

```bash
git switch -c codex/12-unmark-command
```

Push a branch:

```bash
git push -u origin codex/12-unmark-command
```

Open a PR:

```bash
gh pr create --fill
```

Merge a PR:

```bash
gh pr merge --squash --delete-branch
```

Create a release:

```bash
git switch main
git pull
git add pyproject.toml src/myshows_cli/__init__.py CHANGELOG.md
git commit -m "Release v0.1.2"
git tag -a v0.1.2 -m "Release v0.1.2"
git push origin main
git push origin v0.1.2
gh release create v0.1.2 --notes-file CHANGELOG.md
```

## GitHub issue and milestone suggestions

Recommended labels:

- `feature`
- `bug`
- `docs`
- `refactor`
- `release`

Recommended milestone usage:

- create a milestone for each planned release
- assign feature issues to the target release milestone
- create a dedicated release issue when preparing the release

## Suggested release issue checklist

- review merged PRs
- update `CHANGELOG.md`
- bump version
- run tests, lint, and build
- create release commit
- create and push tag
- create GitHub Release

## Direct push policy

Avoid direct pushes to `main`.

Allowed only for exceptional cases such as:

- repository bootstrapping
- urgent hotfixes
- administrative repo maintenance

If a direct push happens, still update tests, docs, and changelog as needed.

## In short

Normal change:

`Issue -> Branch -> Code + Tests + Docs -> PR -> CI -> Merge`

Release:

`Merged work on main -> Version bump -> Changelog finalization -> Tag -> GitHub Release`
