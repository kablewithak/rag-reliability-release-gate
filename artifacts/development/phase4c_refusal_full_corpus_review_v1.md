# Phase 4C Refusal Full-Corpus Semantic Review V1

Audit Markdown SHA256: `0429b8842a29e62312b59b85c353a8071acc2f8fbde094da3b543cd8ba591693`

## Verdict summary

- `SUPPORTED_REFUSAL=7`
- `ANSWERABLE_ELSEWHERE=0`
- `AMBIGUOUS_NEEDS_REWORDING=3`
- `ALLOCATION_SURVIVES=true`
- `ALLOCATION_FROZEN=false`

## `dev-api-version-after-2026-03-10`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `guidance:docs-api-versions`
- role: `evaluation_development_case`
- candidate count: `1209`
- cross-gold candidate count: `1172`
- rewrite required: `false`

**Final claim**

The frozen corpus does not establish the identity or release date of an API version after 2026-03-10.

**Rationale**

The surfaced evidence establishes current and historical version material but does not establish a later version identity or release date.

## `dev-add-assignees-silent-ignore-cause`

- verdict: `AMBIGUOUS_NEEDS_REWORDING`
- cluster: `openapi-pair:issues/add-assignees`
- role: `evaluation_development_case`
- candidate count: `175`
- cross-gold candidate count: `163`
- rewrite required: `true`

**Final claim**

Given only a successful add-assignees outcome and no request or response detail, the frozen evidence cannot establish which requested login, if any, was ignored.

**Rationale**

The operation itself documents the push-access condition, so the refusal must target the unknown instance-specific login rather than treat the documented condition as unknown.

## `dev-create-issue-silent-drop-cause`

- verdict: `AMBIGUOUS_NEEDS_REWORDING`
- cluster: `openapi-pair:issues/create`
- role: `evaluation_development_case`
- candidate count: `278`
- cross-gold candidate count: `253`
- rewrite required: `true`

**Final claim**

Given only a successful create-issue outcome and no response details or caller identity, the frozen evidence cannot establish which optional requested fields were silently dropped or identify the caller.

**Rationale**

The operation documents that lack of push access can silently drop optional assignments, labels, or milestone changes, so permission deficiency must not be treated as universally unknown.

## `dev-remove-reviewers-422-cause`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `openapi-pair:pulls/remove-requested-reviewers`
- role: `evaluation_development_case`
- candidate count: `64`
- cross-gold candidate count: `57`
- rewrite required: `false`

**Final claim**

A 422 response from removing requested reviewers does not by itself establish the exact validation cause.

**Rationale**

The operation and shared validation contract establish validation failure but do not identify the concrete cause from status alone.

## `tuning-get-pull-mergeable-null`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `openapi-pair:pulls/get`
- role: `intervention_tuning_case`
- candidate count: `74`
- cross-gold candidate count: `72`
- rewrite required: `false`

**Final claim**

mergeable=null does not establish whether the pull request is mergeable because computation may still be pending.

**Rationale**

The operation explicitly states that null can mean the background mergeability computation has not completed.

## `tuning-update-pull-422-cause`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `openapi-pair:pulls/update`
- role: `intervention_tuning_case`
- candidate count: `74`
- cross-gold candidate count: `69`
- rewrite required: `false`

**Final claim**

A 422 response from updating a pull request does not by itself establish the exact validation cause.

**Rationale**

The status and generic validation schema do not identify the exact failed field or condition without response detail.

## `tuning-create-in-org-451-cause`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `openapi-pair:repos/create-in-org`
- role: `intervention_tuning_case`
- candidate count: `53`
- cross-gold candidate count: `47`
- rewrite required: `false`

**Final claim**

A 451 response from creating an organization repository does not by itself establish the exact triggering cause.

**Rationale**

The current operation exposes the response but the surfaced frozen evidence does not establish its exact triggering condition.

## `heldout-last-known-timezone`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `guidance:docs-timezones`
- role: `held_out_release_case`
- candidate count: `1`
- cross-gold candidate count: `0`
- rewrite required: `false`

**Final claim**

Without observed user state, the authenticated user's last-known timezone cannot be inferred.

**Rationale**

The documentation defines timezone precedence, but the actual last-known timezone is user state rather than a fact contained in the corpus.

## `heldout-blocked-by-failure-cause`

- verdict: `AMBIGUOUS_NEEDS_REWORDING`
- cluster: `openapi-pair:issues/add-blocked-by-dependency`
- role: `held_out_release_case`
- candidate count: `215`
- cross-gold candidate count: `185`
- rewrite required: `true`

**Final claim**

A 404 response from adding a blocked-by dependency does not by itself identify which relevant resource or access condition caused the request to fail.

**Rationale**

The original generic-error wording was too weak to be diagnostic. A specific 404 preserves the insufficiency test without pretending the exact cause is known.

## `heldout-list-pulls-422-cause`

- verdict: `SUPPORTED_REFUSAL`
- cluster: `openapi-pair:pulls/list`
- role: `held_out_release_case`
- candidate count: `230`
- cross-gold candidate count: `211`
- rewrite required: `false`

**Final claim**

A 422 response from listing pull requests does not by itself establish the exact validation cause.

**Rationale**

The operation exposes several query dimensions and a generic validation failure; status alone does not identify the exact failed condition.
