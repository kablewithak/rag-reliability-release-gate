# Phase 4C TUNING Canonical Case Candidate V1

**State:** authored candidate; not yet frozen and not baseline-authorized.

## Quotas

- cases: `24`
- clusters: `12`
- current single-source: `7`
- current multi-evidence: `5`
- version freshness: `5`
- authority/scope: `3`
- must-refuse: `4`

## `phase4-tuning-auth-username-password-current`

- cluster: `guidance:docs-authentication`
- family: `cross_cutting_rest_guidance`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy runbook tells users to authenticate to the GitHub REST API with their GitHub username and password. Under the frozen current authentication guidance, is username-and-password authentication supported, and what response class should be expected if it is attempted?

**Gold facts**

- Authentication with a GitHub username and password is not supported.
- Attempting username-and-password authentication returns a 4xx error.

**Required evidence IDs**

- `chunk-9acc16505e9259b57c6bbb30df45d6a4cbcf321495bf593087e573552ce437d0`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-auth-saml-actions`

- cluster: `guidance:docs-authentication`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

A team accesses an organization that enforces SAML SSO and is also moving API work into a GitHub Actions workflow. How does SAML authorization differ for a classic personal access token versus a fine-grained personal access token, and for the workflow itself what credential does GitHub recommend and how are its permissions granted?

**Gold facts**

- A classic personal access token must be authorized after creation for an organization that enforces SAML SSO.
- A fine-grained personal access token is authorized during token creation before organization access is granted.
- Inside a GitHub Actions workflow, GitHub recommends using the built-in GITHUB_TOKEN instead of creating another token.
- Permissions for GITHUB_TOKEN can be granted with the workflow permissions key.

**Required evidence IDs**

- `chunk-5d04e2ccdfe8bd57d67d12bda6baf3a623435b28c003f2661238c6998b696dda`
- `chunk-9acc16505e9259b57c6bbb30df45d6a4cbcf321495bf593087e573552ce437d0`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-credential-method-scope`

- cluster: `guidance:docs-credential-security`
- family: `cross_cutting_rest_guidance`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

Choose the credential type that the current GitHub guidance recommends for three different principals: personal API use, API use on behalf of an organization or another user, and API use inside GitHub Actions. What least-privilege rule should be applied to the credential's scopes or permissions?

**Gold facts**

- For personal API use, the guidance recommends a personal access token.
- For API use on behalf of an organization or another user, the guidance recommends a GitHub App.
- For API use in a GitHub Actions workflow, the guidance recommends the built-in GITHUB_TOKEN.
- Credentials should receive only the minimum scopes or permissions required for the task.

**Required evidence IDs**

- `chunk-e2c15dc4625f251c70f2cdb31eec44532a56c5300292d61dddc6f3010184a0fb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-credential-remediation`

- cluster: `guidance:docs-credential-security`
- family: `cross_cutting_rest_guidance`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

The team discovers that an API credential has leaked. According to the current credential-security guidance, what three remediation actions should the team take?

**Gold facts**

- Generate a new credential.
- Replace the old credential with the new credential everywhere it is stored or accessed.
- Delete the old compromised credential.

**Required evidence IDs**

- `chunk-e2c15dc4625f251c70f2cdb31eec44532a56c5300292d61dddc6f3010184a0fb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-rate-primary-status`

- cluster: `guidance:docs-rate-limits`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For unauthenticated requests that fetch public data, what is the primary REST API rate limit and what identity is it associated with? Explain how primary-rate-limit status can be inspected through response headers and GET /rate_limit, including how that endpoint affects the primary and secondary limits, and whether secondary-rate-limit status can be queried directly.

**Gold facts**

- The primary rate limit for unauthenticated requests is 60 requests per hour.
- Unauthenticated requests are associated with the originating IP address.
- Primary rate-limit status can be inspected using rate-limit response headers.
- GET /rate_limit can also check rate-limit status and does not count against the primary rate limit, although it can count against the secondary rate limit.
- There is no way to directly check the status of the secondary rate limit.

**Required evidence IDs**

- `chunk-90aa40f5585c27ad415f5b18364968bc333a802224510c4f5a464ae4eb591f3e`
- `chunk-98db24aebd4add7d628a9b2f602393c6db25f6ab0d6ed8a467964b0bb2dcdcf5`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-rate-actions-secondary-retry`

- cluster: `guidance:docs-rate-limits`
- family: `cross_cutting_rest_guidance`
- scenario: `current_multi_evidence_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

A GitHub Actions workflow uses GITHUB_TOKEN and later receives a secondary-rate-limit failure. What primary hourly budget applies to GITHUB_TOKEN, including the Enterprise Cloud case, and what retry sequence should the client follow for the secondary-limit response?

**Gold facts**

- GITHUB_TOKEN has a primary rate limit of 1,000 requests per hour per repository.
- For resources belonging to a GitHub Enterprise Cloud account, the GITHUB_TOKEN limit is 15,000 requests per hour per repository.
- A secondary-rate-limit failure may return HTTP 403 or 429.
- If retry-after is present, the client should wait that many seconds before retrying.
- If x-ratelimit-remaining is zero, the client should wait until x-ratelimit-reset.
- Otherwise the client should wait at least one minute, use exponentially increasing waits if failures continue, and stop after a bounded number of retries.

**Required evidence IDs**

- `chunk-90aa40f5585c27ad415f5b18364968bc333a802224510c4f5a464ae4eb591f3e`
- `chunk-98db24aebd4add7d628a9b2f602393c6db25f6ab0d6ed8a467964b0bb2dcdcf5`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-actions-repo-registration-scope`

- cluster: `openapi-pair:actions/create-registration-token-for-repo`
- family: `actions`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

Under the current repository self-hosted-runner registration-token operation, what repository authority must the authenticated user have, and what scope is required for OAuth tokens or classic personal access tokens?

**Gold facts**

- The authenticated user must have admin access to the repository.
- OAuth tokens and classic personal access tokens need the repo scope.

**Required evidence IDs**

- `chunk-c17c181dc4ea53ab06b9afd42b1371e4c84991ee1e799c7cd8fd0a8f071f3fa6`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-actions-repo-registration-token`

- cluster: `openapi-pair:actions/create-registration-token-for-repo`
- family: `actions`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current GitHub REST contract, which method and endpoint create a self-hosted runner registration token for a repository, how long does that token remain valid, and what successful status is documented?

**Gold facts**

- The operation uses POST /repos/{owner}/{repo}/actions/runners/registration-token.
- The registration token expires after one hour.
- The successful response status is HTTP 201.

**Required evidence IDs**

- `chunk-c17c181dc4ea53ab06b9afd42b1371e4c84991ee1e799c7cd8fd0a8f071f3fa6`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-workflow-dispatch-current-contract`

- cluster: `openapi-pair:actions/create-workflow-dispatch`
- family: `actions`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy client sends return_run_details=false when creating a workflow dispatch and expects HTTP 204. Under the frozen current 2026-03-10 operation contract, is return_run_details part of the request schema, and what successful response is documented instead?

**Gold facts**

- The current request schema does not contain the return_run_details property.
- The current operation documents HTTP 200 as the successful response.
- The HTTP 200 response includes the workflow run ID and URLs.
- The current operation does not document the historical HTTP 204 response.

**Required evidence IDs**

- `chunk-2662bbb46cac69cfc201f58fa703962df5571ff6ac684e765137368268f351f5`

**Forbidden evidence IDs**

- `chunk-c2692e000e203199b6dd7a3e5eb7bbc5bbadf87ebb479fa451652f20c83ebc52`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.

## `phase4-tuning-workflow-dispatch-requirements`

- cluster: `openapi-pair:actions/create-workflow-dispatch`
- family: `actions`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

What must be configured before the workflow-dispatch REST endpoint can manually trigger a workflow, what required request field identifies the git reference, what forms may that reference take, how many input properties may be supplied, and what happens to configured default input properties when inputs are omitted?

**Gold facts**

- The workflow must be configured to run when the workflow_dispatch event occurs.
- The request body requires the ref field.
- The ref may be a branch or tag name.
- The inputs object may contain at most 25 properties.
- Defaults configured in the workflow file are used when corresponding inputs are omitted.

**Required evidence IDs**

- `chunk-2662bbb46cac69cfc201f58fa703962df5571ff6ac684e765137368268f351f5`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-sub-issue-request-contract`

- cluster: `openapi-pair:issues/add-sub-issue`
- family: `issues`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For the current Add sub-issue operation, what HTTP method and endpoint are used, which request-body field is required, what ownership constraint applies to the sub-issue, and what does replace_parent=true mean?

**Gold facts**

- The operation uses POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues.
- The request body requires sub_issue_id.
- The sub-issue must belong to the same repository owner as the parent issue.
- replace_parent=true instructs the operation to replace the sub-issue's current parent issue.

**Required evidence IDs**

- `chunk-dce9a384052fb0b5e660fcf172f8457b8e00d415535f2f845a4cda06dbca9afb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-sub-issue-media-response`

- cluster: `openapi-pair:issues/add-sub-issue`
- family: `issues`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

For Add sub-issue, what status indicates success, what body representation is returned by the default raw media type, and what body representations are included by the full media type?

**Gold facts**

- The successful response status is HTTP 201.
- application/vnd.github.raw+json is the default and returns the raw Markdown body in body.
- application/vnd.github.full+json includes body, body_text, and body_html.

**Required evidence IDs**

- `chunk-dce9a384052fb0b5e660fcf172f8457b8e00d415535f2f845a4cda06dbca9afb`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-pull-mergeable-null-refusal`

- cluster: `openapi-pair:pulls/get`
- family: `pull_requests`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

A Get pull request response contains mergeable=null. Using only that observed value, tell me definitively whether this pull request is mergeable or unmergeable.

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: mergeable=null does not establish whether the pull request is mergeable because computation may still be pending.

## `phase4-tuning-pull-merge-commit-semantics`

- cluster: `openapi-pair:pulls/get`
- family: `pull_requests`
- scenario: `current_single_source_answerable`
- criticality: `noncritical`
- response mode: `answer`

**Query**

Explain how merge_commit_sha should be interpreted for Get pull request before the pull request is merged and after merge-commit, squash, or rebase merging.

**Gold facts**

- Before merging, merge_commit_sha holds the SHA of the test merge commit.
- If the pull request is merged with a merge commit, merge_commit_sha becomes the SHA of that merge commit.
- If squash merged, merge_commit_sha represents the squashed commit on the base branch.
- If rebased, merge_commit_sha represents the commit that the base branch was updated to.

**Required evidence IDs**

- `chunk-f195cc3e0ba24c3ae8273d49e92e001fac39dcfd9fa3a7eafad7a7f95ff85781`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-update-pull-422-refusal`

- cluster: `openapi-pair:pulls/update`
- family: `pull_requests`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

An Update pull request request returns HTTP 422, but I have no response body or request-field details. Which exact field or validation condition caused this particular failure?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: A 422 response from updating a pull request does not by itself establish the exact validation cause.

## `phase4-tuning-update-pull-scope`

- cluster: `openapi-pair:pulls/update`
- family: `pull_requests`
- scenario: `authority_scope_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

For the current Update pull request operation, what access is required to update a pull request in a public repository, what additional membership condition applies to an organization-owned repository, and what restrictions apply when changing the base branch?

**Gold facts**

- Updating a pull request in a public repository requires write access to the head or source branch.
- For an organization-owned repository, the user must be a member of the organization that owns the repository.
- A new base value must name an existing branch in the current repository.
- The base branch cannot be changed to point to another repository.

**Required evidence IDs**

- `chunk-3b49054d748e4cfbf79ad140015fe2c6d73db66c9185f434fbced3a37c84d285`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice.

## `phase4-tuning-create-in-org-451-refusal`

- cluster: `openapi-pair:repos/create-in-org`
- family: `repositories_and_repository_webhooks`
- scenario: `must_refuse_insufficient_or_conflicting_evidence`
- criticality: `critical`
- response mode: `refuse`

**Query**

A Create an organization repository request returns HTTP 451. With only that status and no response details, what exact condition triggered this particular 451?

**Refusal reason:** `insufficient_evidence`

**Required evidence IDs**

- `none`

**Forbidden evidence IDs**

- `none`

**Scoring notes**

Expected runtime behaviour is insufficient-evidence refusal. The evaluator must not reward an unsupported answer that exceeds the reviewed evidence boundary. Reviewed refusal boundary: A 451 response from creating an organization repository does not by itself establish the exact triggering cause.

## `phase4-tuning-create-in-org-current-451`

- cluster: `openapi-pair:repos/create-in-org`
- family: `repositories_and_repository_webhooks`
- scenario: `version_freshness_disambiguation`
- criticality: `critical`
- response mode: `qualified_answer`

**Query**

A legacy contract for Create an organization repository does not list HTTP 451. Under the frozen current 2026-03-10 operation contract, is HTTP 451 now a documented response, and how is that response represented?

**Gold facts**

- The current Create an organization repository contract documents HTTP 451.
- The HTTP 451 response references the shared validation_failed response contract.

**Required evidence IDs**

- `chunk-0866e576fcc08a7d8b93d77a2710ca186b1b7ab008a0c3332a53230283b04136`

**Forbidden evidence IDs**

- `chunk-9415dcdaefed1c781040a1a24f82567f5cd9976d4b6936bfe2b187819aebba7d`

**Scoring notes**

Full credit requires every gold fact and support from the required evidence IDs. Partial-credit denominators and failure precedence are not frozen in this authoring slice. Historical comparison evidence is explicitly forbidden as final support because the query asks for the current 2026-03-10 contract.
