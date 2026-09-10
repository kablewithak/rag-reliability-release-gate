# Phase 4C HELD_OUT Canonical Case Candidate V1

**State:** authored candidate; not yet frozen and not baseline-authorized.

## Quotas

- cases: `18`
- clusters: `9`
- current single-source: `5`
- current multi-evidence: `4`
- version freshness: `4`
- authority/scope: `2`
- must-refuse: `3`

## `phase4-heldout-best-practices-poll-cache`

- cluster: `guidance:docs-best-practices`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

An integration cannot use webhooks and must poll the GitHub REST API. Under the frozen current best-practices guidance, how should it control polling frequency and x-poll-interval, use conditional authenticated requests, and keep requests stable so unchanged resources are more likely to return HTTP 304 without consuming primary rate-limit budget?

**Gold facts**

- When polling is unavoidable, poll only as often as needed on a fixed schedule.
- If x-poll-interval is returned, wait at least that many seconds before polling the same endpoint again.
- Correctly authorized conditional requests that return HTTP 304 do not count against the primary rate limit.
- Request only the data needed and keep the request stable and specific so unchanged data is more likely to return HTTP 304.
- Repeated polls of the same data should use the same parameters, because changing page size, page number, or filters produces a different response and etag.

**Required evidence IDs**

- `chunk-4822abf057b571cf16b0e79561614b306b380042a4e8f09996404099bc026e31`
- `chunk-ae6500530a333bc9c4e22391d66658e15a22d8b95500170cbc0ae422fb2cf66f`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-best-practices-repeated-errors`

- cluster: `guidance:docs-best-practices`
- family: `cross_cutting_rest_guidance`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

A polling integration repeatedly receives HTTP 404 from a resource that the operator believes exists. What does the frozen current best-practices guidance say about the possible authorization meaning of 404 and how the integration should behave instead of continually retrying?

**Gold facts**

- A 404 does not always mean the resource is absent, because GitHub may return 404 instead of 403 for some private resources when credentials lack access.
- The integration should first verify that the 404 is not caused by authentication or authorization.
- After credentials are confirmed, the integration should wait much longer before checking again or retry only when there is reason to believe the resource exists.
- Repeatedly requesting a missing resource wastes rate limit and can trigger a secondary rate limit.

**Required evidence IDs**

- `chunk-4822abf057b571cf16b0e79561614b306b380042a4e8f09996404099bc026e31`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-getting-started-request-contract`

- cluster: `guidance:docs-getting-started`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

A developer is constructing a REST request from the current GitHub guidance. Which request elements are always present, how do path, body, and query parameters differ, and which version and media-type headers does the guidance describe?

**Gold facts**

- Every REST API request includes an HTTP method and a path.
- Path parameters modify the endpoint path and are required where the endpoint defines them.
- Body parameters send additional data and may be optional or required depending on the endpoint.
- Query parameters control what data is returned and are usually optional.
- The X-GitHub-Api-Version header specifies the REST API version for the request.
- Most REST endpoints recommend Accept: application/vnd.github+json.

**Required evidence IDs**

- `chunk-016bb9166542c2ba4bbd33a1aeb8d10d0cc889e5a0c2276d00dc5a5e88f4cb07`
- `chunk-3c499f1990ac0c066d520f07851659dcd0fdb7821fde7a966223a22b8038e1fd`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-getting-started-request-inspection`

- cluster: `guidance:docs-getting-started`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

Using the frozen getting-started guidance, explain the key method/header controls for making requests with GitHub CLI or curl and how a caller can inspect the returned HTTP status code and headers.

**Gold facts**

- GitHub CLI uses the api subcommand and allows the HTTP method to be supplied with --method.
- The examples send Accept and X-GitHub-Api-Version headers.
- For curl, the request method can be supplied with --request or -X and the full API URL with --url.
- An authenticated curl request sends the access token in the Authorization header.
- The --include or --i option can be used to display the response status code and headers.

**Required evidence IDs**

- `chunk-26b602928020bab70748654dd84106df4188f1d8bd4ce038b8dab607c8201215`
- `chunk-f62c569b11e1f8f3e5f767abb6c1aee7161d6090ea5eb37948ea2c59cee855e9`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-timezones-current-precedence`

- cluster: `guidance:docs-timezones`
- family: `cross_cutting_rest_guidance`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy runbook says GitHub always generates request timestamps in UTC unless the timestamp itself contains an offset. Under the frozen current timezone guidance, what precedence is actually used for applicable API calls when determining timezone information?

**Gold facts**

- An explicitly supplied ISO 8601 timestamp with timezone information has highest priority.
- If an explicit timestamp does not determine it, a Time-Zone header can provide the timezone.
- Without a Time-Zone header, an authenticated request uses the authenticated user's last known timezone.
- UTC is the fallback when no other timezone information is available.

**Required evidence IDs**

- `chunk-cd0e87ca852080c49fd723c0efd6e0225afeae8be7ed5ec25df339ed1e8807bb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-timezones-last-known-refusal`

- cluster: `guidance:docs-timezones`
- family: `cross_cutting_rest_guidance`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

No Time-Zone header or explicit timezone was provided, and I have no observed user state. What exact last-known timezone will GitHub use for this authenticated user?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: Without observed user state, the authenticated user's last-known timezone cannot be inferred.

## `phase4-heldout-actions-remove-token-authority`

- cluster: `openapi-pair:actions/create-remove-token-for-org`
- family: `actions`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

Under the current organization self-hosted-runner remove-token operation, what organization authority must the authenticated user have and what organization scope is required for OAuth tokens or classic personal access tokens?

**Gold facts**

- The authenticated user must have admin access to the organization.
- OAuth tokens and classic personal access tokens need the admin:org scope.

**Required evidence IDs**

- `chunk-8cf27b1c1eb50de277026c4b7e29b3c23eb562dd3a0659630cea4fe56bf9ed70`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-actions-remove-token-contract`

- cluster: `openapi-pair:actions/create-remove-token-for-org`
- family: `actions`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current GitHub REST operation that creates a self-hosted-runner remove token for an organization, what HTTP method and endpoint are used, how long is the token valid, and what successful status is documented?

**Gold facts**

- The operation uses POST /orgs/{org}/actions/runners/remove-token.
- The token expires after one hour.
- The successful response status is HTTP 201.

**Required evidence IDs**

- `chunk-8cf27b1c1eb50de277026c4b7e29b3c23eb562dd3a0659630cea4fe56bf9ed70`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-blocked-by-404-refusal`

- cluster: `openapi-pair:issues/add-blocked-by-dependency`
- family: `issues`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

An Add blocked-by dependency request returns HTTP 404, but I have no further request, resource, credential, or response details. Which exact resource or access condition caused this particular failure?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: A 404 response from adding a blocked-by dependency does not by itself identify which relevant resource or access condition caused the request to fail.

## `phase4-heldout-blocked-by-contract`

- cluster: `openapi-pair:issues/add-blocked-by-dependency`
- family: `issues`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current Add blocked-by dependency operation, what method and endpoint are used, which request-body field is required, what does that field identify, and what successful response status is documented?

**Gold facts**

- The operation uses POST /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by.
- The request body requires issue_id.
- issue_id identifies the issue that blocks the current issue.
- The successful response status is HTTP 201.

**Required evidence IDs**

- `chunk-54218cead5dc4d96ffc452ff1dbd07d9b0f4dab0236c0d3ab315168d9f0d4124`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-issues-update-assignee-freshness`

- cluster: `openapi-pair:issues/update`
- family: `issues`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy Update issue request schema contains a singular assignee field marked as closing down. Under the frozen current 2026-03-10 request contract, is that singular assignee field still present, and what plural field is available for replacing or clearing assignees?

**Gold facts**

- The current request schema does not contain the legacy singular assignee field.
- The current request schema contains the plural assignees field.
- Passing one or more logins to assignees replaces the set of assignees.
- Passing an empty assignees array clears all assignees.

**Required evidence IDs**

- `chunk-cd375411d841104feb9b2825d17e637b92b9d817f6f22d1c52d0fbce134f328d`

**Forbidden evidence IDs**

- `chunk-a1a6a71a7bf60ff978907f1339ae3ce7cc900759a29c6114fdff63e37a492421`
- `chunk-db4f7149fb4f7e84d0de4a79830ed8a35e793d967bbf7c60f5d4f35fad88f118`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-heldout-issues-update-suggestions`

- cluster: `openapi-pair:issues/update`
- family: `issues`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current Update issue contract, who may edit an issue, and how do request-side suggestion metadata and the response-side suggestions object represent proposed or ignored changes?

**Gold facts**

- Issue owners and users with push access or the Triage role can edit an issue.
- Suggestible request fields can carry metadata such as confidence, rationale, and suggest.
- When suggest is true, the requested change is stored as a pending suggestion for human review rather than being applied directly.
- The response suggestions object reports pending suggestions for suggestible fields touched by the request.
- Items marked ignored echo request inputs that were not persisted as pending suggestions.

**Required evidence IDs**

- `chunk-2a1b7e2dd72157f835c63422ef3416992ea7a3c25b55460ada39cd66ca0d6f3f`
- `chunk-cd375411d841104feb9b2825d17e637b92b9d817f6f22d1c52d0fbce134f328d`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-pulls-list-422-refusal`

- cluster: `openapi-pair:pulls/list`
- family: `pull_requests`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

A List pull requests call returns HTTP 422, but I have no request parameters or response body. Which exact query parameter or validation condition caused this failure?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: A 422 response from listing pull requests does not by itself establish the exact validation cause.

## `phase4-heldout-pulls-list-filters`

- cluster: `openapi-pair:pulls/list`
- family: `pull_requests`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current List pull requests operation, what is the default state filter, how is the head filter formatted, what does the base filter identify, and what are the documented sort and direction defaults?

**Gold facts**

- The state filter accepts open, closed, or all and defaults to open.
- The head filter uses the form user:ref-name or organization:ref-name.
- The base filter identifies the base branch name.
- The sort parameter defaults to created.
- Direction defaults to desc when sort is created or unspecified, and otherwise defaults to asc.

**Required evidence IDs**

- `chunk-0d1569942ce3eb27dd225f5c465d8d55795c6773041393e19ff2e8ff40b9e5b3`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-create-user-repo-451-freshness`

- cluster: `openapi-pair:repos/create-for-authenticated-user`
- family: `repositories_and_repository_webhooks`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy Create a repository for the authenticated user contract does not list HTTP 451. Under the frozen current 2026-03-10 operation contract, is HTTP 451 documented and how is that response represented?

**Gold facts**

- The current operation documents HTTP 451.
- The HTTP 451 response references the shared validation_failed response contract.

**Required evidence IDs**

- `chunk-0a98ac5e1a4daa0e51e91dc08bb8787b274704ce635586deb431fb9ebf7c4a5a`

**Forbidden evidence IDs**

- `chunk-24feb9ae2816561bfb66d549dd480b574ec3cf2cc2ff6950630ff7a883b7ec56`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-heldout-create-user-repo-contract`

- cluster: `openapi-pair:repos/create-for-authenticated-user`
- family: `repositories_and_repository_webhooks`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current Create a repository for the authenticated user operation, what method and endpoint are used, which request field is required, what is the default privacy setting, and what classic token scopes are described for public versus private repositories?

**Gold facts**

- The operation uses POST /user/repos.
- The request body requires name.
- The private field defaults to false.
- OAuth app tokens and classic personal access tokens need public_repo or repo scope to create a public repository.
- The repo scope is required to create a private repository.

**Required evidence IDs**

- `chunk-0a98ac5e1a4daa0e51e91dc08bb8787b274704ce635586deb431fb9ebf7c4a5a`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-heldout-attestations-bundle-freshness`

- cluster: `openapi-pair:repos/list-attestations`
- family: `repositories_and_repository_webhooks`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy List attestations response schema embeds a bundle object inside each attestation. Under the frozen current 2026-03-10 operation contract, is that embedded bundle still defined, and which fields does the current attestation item schema define?

**Gold facts**

- The current attestation item schema does not define the historical embedded bundle property.
- The current attestation item schema defines bundle_url.
- The current attestation item schema defines initiator.
- The current attestation item schema defines repository_id.

**Required evidence IDs**

- `chunk-86c17157604102e82f7090de928de56d4222dae94608aed1a989cfab92eac54b`

**Forbidden evidence IDs**

- `chunk-c85c8bef9f92d7e2fe88eef66094a668f65db06cd9086f31f562d3dcb2cce665`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-heldout-attestations-authority`

- cluster: `openapi-pair:repos/list-attestations`
- family: `repositories_and_repository_webhooks`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

Under the current List attestations operation, what repository access and fine-grained token permission are required, and what verification requirements does the operation identify as necessary for meaningful security benefits?

**Gold facts**

- The authenticated user must have read access to the repository.
- A fine-grained access token requires the attestations:read permission.
- The attestation signature and timestamps must be cryptographically verified.
- The identity of the attestation signer must be validated.

**Required evidence IDs**

- `chunk-86c17157604102e82f7090de928de56d4222dae94608aed1a989cfab92eac54b`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.
