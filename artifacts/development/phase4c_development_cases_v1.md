# Phase 4C DEVELOPMENT Canonical Case Candidate V1

**State:** authored candidate; not yet frozen and not baseline-authorized.

## Quotas

- cases: `24`
- clusters: `12`
- current single-source: `7`
- current multi-evidence: `5`
- version freshness: `5`
- authority/scope: `3`
- must-refuse: `4`

## `phase4-dev-api-version-current-contract`

- cluster: `guidance:docs-api-versions`
- family: `cross_cutting_rest_guidance`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy runbook says 2022-11-28 is still the newest GitHub REST API version. Under the frozen current docs, what newer supported version is listed, what version do requests without X-GitHub-Api-Version default to, and what happens if a specified version is no longer supported?

**Gold facts**

- The supported-version list includes 2026-03-10, which is newer than 2022-11-28.
- Requests without X-GitHub-Api-Version default to 2022-11-28.
- A specified API version that is no longer supported returns 410 Gone.

**Required evidence IDs**

- `chunk-983a0027263f77cae71fe270dd205876fd7df230c10e5b64d2d069352dc1e97d`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-api-version-future-unknown`

- cluster: `guidance:docs-api-versions`
- family: `cross_cutting_rest_guidance`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

What is the exact GitHub REST API version that will replace 2026-03-10, and on what exact date will GitHub release that future version?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: The frozen corpus does not establish the identity or release date of an API version after 2026-03-10.

## `phase4-dev-breaking-sarif-content-type-current`

- cluster: `guidance:docs-breaking-changes`
- family: `cross_cutting_rest_guidance`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy integration expects a SARIF response requested with Accept: application/sarif+json to come back with Content-Type application/json+sarif. Under the 2026-03-10 breaking-change guidance, what Content-Type should the response use instead?

**Gold facts**

- The prior response Content-Type application/json+sarif was incorrect.
- The corrected SARIF response Content-Type is application/sarif+json.

**Required evidence IDs**

- `chunk-099035e853588f6d8e3d3e13466602b62f7366fe77f3f99d48f8a53c0fd435ce`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-breaking-version-migration`

- cluster: `guidance:docs-breaking-changes`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

Compare the current breaking-change guidance for 2022-11-28 and 2026-03-10: did 2022-11-28 introduce breaking changes, and how should an integration migrate away from the deprecated rate property in the rate-limit endpoint?

**Gold facts**

- Version 2022-11-28 is the first date-based GitHub REST API version and includes no breaking changes.
- For 2026-03-10, the deprecated rate property is removed from the rate-limit endpoint.
- Integrations should read the equivalent rate-limit information from resources.core.

**Required evidence IDs**

- `chunk-099035e853588f6d8e3d3e13466602b62f7366fe77f3f99d48f8a53c0fd435ce`
- `chunk-cf790cc8a7edd6efb9809f062aa0c37c593a47c61d41148a5ff769aecdc1d919`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-pagination-manual-link-loop`

- cluster: `guidance:docs-pagination`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

I am implementing GitHub REST pagination without a built-in pagination helper. How does the link header tell me whether another page exists, and how should the manual collection loop know when to stop?

**Gold facts**

- Paginated responses use the link header to expose URLs for additional pages.
- The next-page URL is identified by the next relationship in the link header.
- A manual pagination loop follows the next-page URL repeatedly and stops when no next-page link remains.
- The manual implementation must handle paginated data returned as either an array or an object containing the array.

**Required evidence IDs**

- `chunk-181c3fb39ae34ec7ece304c0896c9e1c80ebe919cb47ee0beb7d43a1795e9e12`
- `chunk-b549d8c7ee35b3cadf0a2abfd4e82db27c7d4de5876a2a6f401ac5fc469da40b`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-pagination-helper-vs-manual`

- cluster: `guidance:docs-pagination`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

A paginated endpoint can return items inside an object, and a request can also return no data. Compare octokit.paginate() with a custom paginator: what result shape does the helper provide, and what normalization must custom code perform before accumulating items?

**Gold facts**

- octokit.paginate() returns an array of items even when the raw paginated response wraps the items in an object.
- A custom paginator should normalize a no-data response to an empty array.
- When the raw data is an object, custom code must extract the actual items array before accumulating results.

**Required evidence IDs**

- `chunk-181c3fb39ae34ec7ece304c0896c9e1c80ebe919cb47ee0beb7d43a1795e9e12`
- `chunk-b549d8c7ee35b3cadf0a2abfd4e82db27c7d4de5876a2a6f401ac5fc469da40b`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-troubleshooting-method-and-rate-limit`

- cluster: `guidance:docs-troubleshooting`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

A GitHub REST request first returns 404 because the client used an unsupported HTTP method, and repeated requests later hit a 403 or 429 rate-limit response. Explain both behaviours and the safe retry sequence.

**Gold facts**

- Using an HTTP method that the endpoint does not support can return 404 Not Found instead of 405 Method Not Allowed.
- A primary or secondary rate-limit failure may return 403 or 429.
- If retry-after is present, the client should wait that many seconds before retrying.
- If x-ratelimit-remaining is zero, the client should wait until x-ratelimit-reset.
- Otherwise the client should wait at least one minute and use increasing backoff for repeated secondary-limit failures.

**Required evidence IDs**

- `chunk-6fc744dee58c1b47dfa67cf1f3c95bc4e791320346e08158a29f8be891afc752`
- `chunk-c302e7937061f7efe865d21345a74967955cdd60c1d86e84e99966fca1bd9440`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-troubleshooting-private-resource-and-version`

- cluster: `guidance:docs-troubleshooting`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

One request to a private resource that is known to exist returns 404 Not Found, while another request specifies an API version that does not exist and returns 400 Bad Request. What should the client infer and check in each case?

**Gold facts**

- A private resource can return 404 Not Found instead of 403 Forbidden when the request is not properly authenticated.
- For a known existing private resource, the client should check authentication, token scopes or permissions, and resource access.
- Specifying an API version that does not exist returns 400 Bad Request with a message that the version is not supported.
- The client should use X-GitHub-Api-Version with a supported API version.

**Required evidence IDs**

- `chunk-6fc744dee58c1b47dfa67cf1f3c95bc4e791320346e08158a29f8be891afc752`
- `chunk-8dd06f9776710075a0304ff05e06d9c104a0eea6e99e20b7be4e1ac5187d4f27`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-actions-org-registration-token`

- cluster: `openapi-pair:actions/create-registration-token-for-org`
- family: `actions`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current GitHub REST contract, which endpoint creates a self-hosted runner registration token for an organization, how long is the token valid, and what is the successful response status?

**Gold facts**

- The operation is POST /orgs/{org}/actions/runners/registration-token.
- The registration token expires after one hour.
- The successful response status is 201.

**Required evidence IDs**

- `chunk-d694c138d0b2408b36c58947d94949887320b133b604f83157627a3d458410c7`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-actions-org-registration-scope`

- cluster: `openapi-pair:actions/create-registration-token-for-org`
- family: `actions`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

Who is authorized to create an organization self-hosted runner registration token, and which classic personal access token or OAuth scope is required?

**Gold facts**

- The caller must have organization administrator access.
- OAuth app tokens and classic personal access tokens require the admin:org scope for this operation.

**Required evidence IDs**

- `chunk-d694c138d0b2408b36c58947d94949887320b133b604f83157627a3d458410c7`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-actions-repo-remove-token`

- cluster: `openapi-pair:actions/create-remove-token-for-repo`
- family: `actions`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

Which current GitHub REST endpoint creates a removal token for a repository self-hosted runner, how long does that token remain valid, and what success status does the operation return?

**Gold facts**

- The operation is POST /repos/{owner}/{repo}/actions/runners/remove-token.
- The removal token expires after one hour.
- The successful response status is 201.

**Required evidence IDs**

- `chunk-9367992c420cc80d42b78e7129457783f233c67f35787f35c04d1096f8f5f99b`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-actions-repo-remove-scope`

- cluster: `openapi-pair:actions/create-remove-token-for-repo`
- family: `actions`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

What access level is required to create a self-hosted runner removal token for a repository, and which classic personal access token or OAuth scope is required?

**Gold facts**

- The caller must have administrator access to the repository.
- OAuth app tokens and classic personal access tokens require the repo scope.

**Required evidence IDs**

- `chunk-9367992c420cc80d42b78e7129457783f233c67f35787f35c04d1096f8f5f99b`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-issues-add-assignees`

- cluster: `openapi-pair:issues/add-assignees`
- family: `issues`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

Under the current Add assignees to an issue contract, how many assignees may be added, what happens to existing assignees, and what happens when the caller lacks push access?

**Gold facts**

- The operation can add up to 10 assignees.
- Users already assigned to the issue are not replaced.
- Only users with push access can add assignees.
- Assignees are silently ignored when the required push access is absent.

**Required evidence IDs**

- `chunk-db26bf1f3b7de296c0851a148250427f380b5c18b32e5662922d579b158be8bb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-issues-add-assignees-instance-refusal`

- cluster: `openapi-pair:issues/add-assignees`
- family: `issues`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

An Add assignees request returned a generic successful outcome. I have no request body, response body, or user permission state. Tell me exactly which requested login, if any, was silently ignored.

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: Given only a successful add-assignees outcome and no request or response detail, the frozen evidence cannot establish which requested login, if any, was ignored.

## `phase4-dev-issues-create-current-assignees`

- cluster: `openapi-pair:issues/create`
- family: `issues`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A 2022 integration still sends the singular assignee property when creating an issue. Under the current 2026-03-10 operation contract, is that singular field still part of the request schema?

**Gold facts**

- The current 2026-03-10 Create an issue request schema no longer contains the singular assignee field.
- The current contract uses the assignees array for assigning users.

**Required evidence IDs**

- `chunk-818a2d7af95a38d5ffd8d96869fbd8198cb399d3e2e8c55900c85770cf07a1d9`

**Forbidden evidence IDs**

- `chunk-a6f2c249acaf3aadd70ac7964297edb46071d6ab5d2fed98384b39ba0e34862f`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-dev-issues-create-instance-refusal`

- cluster: `openapi-pair:issues/create`
- family: `issues`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

An issue was created successfully, but I do not have the response details or caller identity. Tell me exactly which optional requested fields were silently dropped and identify the caller who made the request.

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: Given only a successful create-issue outcome and no response details or caller identity, the frozen evidence cannot establish which optional requested fields were silently dropped or identify the caller.

## `phase4-dev-pulls-create-contract`

- cluster: `openapi-pair:pulls/create`
- family: `pull_requests`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current Create a pull request operation, which base and head information must be supplied, how may a head branch be qualified with an owner, and when is head_repo required?

**Gold facts**

- The request requires base and head information.
- The head value can identify the source as username:branch.
- head_repo is required for a cross-repository pull request when both repositories are owned by the same organization.

**Required evidence IDs**

- `chunk-e8fc96fbaa45f2c119f5c6ebb463aa1f2185ef34a62d159f349d65c167f4caca`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-pulls-create-authority`

- cluster: `openapi-pair:pulls/create`
- family: `pull_requests`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

What repository access and organization-membership conditions apply when creating a pull request from its head or source branch?

**Gold facts**

- The caller needs write access to the head or source branch used for the pull request.
- For organization-owned repositories, the caller must be a member of the organization that owns the repository.

**Required evidence IDs**

- `chunk-e8fc96fbaa45f2c119f5c6ebb463aa1f2185ef34a62d159f349d65c167f4caca`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-pulls-remove-reviewers-contract`

- cluster: `openapi-pair:pulls/remove-requested-reviewers`
- family: `pull_requests`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For Remove requested reviewers from a pull request, which HTTP method and endpoint are used, what does the required reviewers field contain, and how are teams identified?

**Gold facts**

- The operation uses DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers.
- The reviewers request field is required and contains user logins.
- team_reviewers contains team slugs.
- The operation documents 200 and 422 responses.

**Required evidence IDs**

- `chunk-dfd55afaa0a00a80b6074c48a0605b597cb4aabe4060b7d06eb3020d245a0dcb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-pulls-remove-reviewers-422-refusal`

- cluster: `openapi-pair:pulls/remove-requested-reviewers`
- family: `pull_requests`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

A Remove requested reviewers request returned only HTTP 422. I do not have the response body or validation errors. What exact validation condition caused this request to fail?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: A 422 response from removing requested reviewers does not by itself establish the exact validation cause.

## `phase4-dev-repos-accept-invitation-current`

- cluster: `openapi-pair:repos/accept-invitation-for-authenticated-user`
- family: `repositories_and_repository_webhooks`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

An older 2022 contract for accepting a repository invitation did not list HTTP 451. Under the current 2026-03-10 operation contract, is 451 now a documented response?

**Gold facts**

- The current 2026-03-10 contract includes HTTP 451 as a documented response for accepting a repository invitation.

**Required evidence IDs**

- `chunk-ede821e5fd4be2c5bc48ef65d813c5b920a05a004a017e5efbe55fde9b584d89`

**Forbidden evidence IDs**

- `chunk-0c19021a77142567363f0be9647755d3aef4e2b61df218536ab5b6a8e9f676fd`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-dev-repos-accept-invitation-success`

- cluster: `openapi-pair:repos/accept-invitation-for-authenticated-user`
- family: `repositories_and_repository_webhooks`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current Accept a repository invitation operation, which HTTP method and endpoint are used, and what status indicates success?

**Gold facts**

- The operation uses PATCH /user/repository_invitations/{invitation_id}.
- A successful Accept a repository invitation operation returns HTTP 204.

**Required evidence IDs**

- `chunk-ede821e5fd4be2c5bc48ef65d813c5b920a05a004a017e5efbe55fde9b584d89`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-dev-repos-get-content-current-submodule`

- cluster: `openapi-pair:repos/get-content`
- family: `repositories_and_repository_webhooks`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy integration expects submodules returned in a repository directory listing to have type file. Under the current 2026-03-10 Get repository content contract, what type should a submodule have?

**Gold facts**

- Under the current 2026-03-10 contract, a submodule in a directory listing has type submodule rather than type file.

**Required evidence IDs**

- `chunk-04e27893cade7a2cb64b06cc387db4cefb1c887db971ddfdc6082b8c136a206b`

**Forbidden evidence IDs**

- `chunk-f81fe01e0fd1af16f295885b6ad3405931469127e81de12ef9c0861b6ce04066`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-dev-repos-get-content-size-contract`

- cluster: `openapi-pair:repos/get-content`
- family: `repositories_and_repository_webhooks`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For Get repository content, what happens when ref is omitted, and what restrictions apply to files between 1 MB and 100 MB and to files larger than 100 MB?

**Gold facts**

- If ref is omitted, the endpoint uses the repository's default branch.
- For files between 1 MB and 100 MB, only the raw or object custom media types are supported.
- For the object media type in that size range, content is an empty string and encoding is none.
- Files larger than 100 MB are not supported by this endpoint.

**Required evidence IDs**

- `chunk-04e27893cade7a2cb64b06cc387db4cefb1c887db971ddfdc6082b8c136a206b`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.
