# Phase 4C Refusal Full-Corpus Audit V1

**Purpose:** deterministically surface runtime evidence that could invalidate the ten provisional refusal intents.

> This artifact is candidate discovery, not a semantic verdict. A lexical match cannot prove either answerability or absence of support.

> The scan covers the frozen 1,333-chunk runtime corpus, including background and shared component evidence.

**Phase 3D chunk manifest SHA256:** `1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd`

**Phase 4 constitution SHA256:** `e2f1ca0985157ea43e7e648fa431e30c2b139cf9b3ea364d7356e8e11311816d`

## `dev-api-version-after-2026-03-10`

- cluster: `guidance:docs-api-versions`
- role: `evaluation_development_case`
- pattern: `future_version_unknown`
- provisional claim: The frozen corpus does not establish the identity or release date of an API version after 2026-03-10.
- total discovered candidates: 1209
- candidates outside Phase 4 gold evidence: 1172
- automated verdict: `review_required`

### Search terms

- topic: `X-GitHub-Api-Version`, `API version`, `2026-03-10`
- diagnostic: `2022-11-28`, `closing down`, `supported`

### Highest-ranked candidates (max 25)

#### `chunk-983a0027263f77cae71fe270dd205876fd7df230c10e5b64d2d069352dc1e97d`

- score: `57`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-api-versions`
- topic matches: `X-GitHub-Api-Version`, `API version`, `2026-03-10`
- diagnostic matches: `2022-11-28`, `closing down`, `supported`

<pre>
--- title: API Versions shortTitle: API Versions intro: Learn how to specify which REST API version to use whenever you make a request to the REST API. versions: fpt: '*' ghes: '*' ghec: '*' redirect_from: - /rest/overview/api-versions category: - Learn about the REST API --- ## About API versioning The GitHub REST API is versioned. The API version name is based on the date when the API version was released. For example, the API version `2026-03-10` was released on Tue, 10 Mar 2026. Breaking changes are changes that can potentially break an integration. Breaking changes will be released in a new API version. We will provide advance notice before releasing breaking changes. Breaking changes include: * Removing an entire operation * Removing or renaming a parameter * Removing or renaming a response field * Adding a new required parameter * Making a previously optional parameter required * Changing the type of a parameter or response field * Removing enum values * Adding a new validation rule to an existing parameter * Changing authentication or authorization requirements Any additive (non-breaking) changes will be available in all supported API versions. Additive changes are changes
</pre>

#### `chunk-8dd06f9776710075a0304ff05e06d9c104a0eea6e99e20b7be4e1ac5187d4f27`

- score: `49`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-troubleshooting`
- topic matches: `X-GitHub-Api-Version`, `API version`, `2026-03-10`
- diagnostic matches: `supported`

<pre>
## Missing results Most endpoints that return a list of resources support pagination. For most of these endpoints, only the first 30 resources are returned by default. In order to see all of the resources, you need to paginate through the results. For more information, see [/rest/using-the-rest-api/using-pagination-in-the-rest-api](/rest/using-the-rest-api/using-pagination-in-the-rest-api). If you are using pagination correctly and still do not see all of the results that you expect, you should confirm that the authentication credentials that you used have access to all of the expected resources. For example, if you are using a GitHub App installation access token, if the installation was only granted access to a subset of repositories in an organization, any request for all repositories in that organization will return only the repositories that the app installation can access. ## Requires authentication when using basic authentication Basic authentication with your username and password is not supported. Instead, you should use a personal access token or an access token for a GitHub App or OAuth app. For more information, see [/rest/authentication/authenticating-to-the-rest-api](
</pre>

#### `chunk-a981d6e38d9441e15e23523d1c41a137f0222d21b4a47e67fc322b3edd4489be`

- score: `49`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `X-GitHub-Api-Version`, `API version`, `2026-03-10`
- diagnostic matches: `supported`

<pre>
--- title: Breaking changes shortTitle: Breaking changes intro: Learn about breaking changes that were introduced in each REST API version. versions: fpt: '*' ghes: '*' ghec: '*' redirect_from: - /rest/overview/breaking-changes category: - Learn about the REST API --- ## About breaking changes in the REST API The GitHub REST API is versioned. The API version name is based on the date when the API version was released. For example, the API version `2026-03-10` was released on Tue, 10 Mar 2026. Breaking changes are changes that can potentially break an integration. Breaking changes will be released in a new API version. We will provide advance notice before releasing breaking changes. Breaking changes include: * Removing an entire operation * Removing or renaming a parameter * Removing or renaming a response field * Adding a new required parameter * Making a previously optional parameter required * Changing the type of a parameter or response field * Removing enum values * Adding a new validation rule to an existing parameter * Changing authentication or authorization requirements Any additive (non-breaking) changes will be available in all supported API versions. Additive changes ar
</pre>

#### `chunk-26b602928020bab70748654dd84106df4188f1d8bd4ce038b8dab607c8201215`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-getting-started`
- topic matches: `X-GitHub-Api-Version`, `API version`
- diagnostic matches: `2022-11-28`

<pre>
### 4. Make a request with GitHub CLI Use the GitHub CLI `api` subcommand to make your API request. For more information, see the [GitHub CLI `api` documentation](https://cli.github.com/manual/gh_api). In your request, specify the following options and values: * **--method** followed by the HTTP method and the path of the endpoint. For more information, see [HTTP method](#http-method) and [Path](#path). * **--header:** * **`Accept`:** Pass the media type in an `Accept` header. To pass multiple media types in an `Accept` header, separate the media types with a comma: `Accept: application/vnd.github+json,application/vnd.github.diff`. For more information, see [`Accept`](#accept) and [Media types](#media-types). * **`X-GitHub-Api-Version`:** Pass the API version in a `X-GitHub-Api-Version` header. For more information, see [`X-GitHub-Api-Version`](#x-github-api-version). * **`-f`** or **`-F`** followed by any body parameters or query parameters in `key=value` format. Use the `-F` option to pass a parameter that is a number, Boolean, or null. Use the `-f` option to pass string parameters. Some endpoints use query parameters that are arrays. To send an array in the query string, use the
</pre>

#### `chunk-5d04e2ccdfe8bd57d67d12bda6baf3a623435b28c003f2661238c6998b696dda`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-authentication`
- topic matches: `X-GitHub-Api-Version`, `2026-03-10`
- diagnostic matches: `2022-11-28`

<pre>
--- title: Authenticating to the REST API intro: You can authenticate to the REST API to access more endpoints and have a higher rate limit. redirect_from: - /v3/auth - /rest/overview/other-authentication-methods - /rest/overview/authenticating-to-the-rest-api versions: fpt: '*' ghes: '*' ghec: '*' shortTitle: Authenticating category: - Authenticate API requests --- ## About authentication Many REST API endpoints require authentication or return additional information if you are authenticated. Additionally, you can make more requests per hour when you are authenticated. To authenticate your request, you will need to provide an authentication token with the required scopes or permissions. There a few different ways to get a token: You can create a personal access token, generate a token with a GitHub App, or use the built-in `GITHUB_TOKEN` in a GitHub Actions workflow. After creating a token, you can authenticate your request by sending the token in the `Authorization` header of your request. For example, in the following request, replace `YOUR-TOKEN` with a reference to your token: ```shell curl --request GET \ --url "https://api.github.com/octocat" \ --header "Authorization: Beare
</pre>

#### `chunk-9acc16505e9259b57c6bbb30df45d6a4cbcf321495bf593087e573552ce437d0`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-authentication`
- topic matches: `X-GitHub-Api-Version`, `2026-03-10`
- diagnostic matches: `supported`

<pre>
### Using basic authentication Some REST API endpoints for GitHub Apps and OAuth apps require you to use basic authentication to access the endpoint. You will use the app's client ID as the username and the app's client secret as the password. For example: ```shell curl --request POST \ --url "https://api.github.com/applications/YOUR_CLIENT_ID/token" \ --user "YOUR_CLIENT_ID:YOUR_CLIENT_SECRET" \ --header "Accept: application/vnd.github+json" \ --header "X-GitHub-Api-Version: 2026-03-10" \ --data '{ "access_token": "ACCESS_TOKEN_TO_CHECK" }' ``` The client ID and client secret are associated with the app, not with the owner of the app or a user who authorized the app. They are used to perform operations on behalf of the app, such as creating access tokens. If you are the owner of a GitHub App or OAuth app, or if you are an app manager for a GitHub App, you can find the client ID and generate a client secret on the settings page for your app. To navigate to your app's settings page: 1. In the upper-right corner of any page on GitHub, click your profile picture. 1. Navigate to your account settings. * For an app owned by a personal account, click **Settings**. * For an app owned by a
</pre>

#### `chunk-a18a4454d3420e3b5e0048ccde681face338278d04f270a1882bb6d483f289fb`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-getting-started`
- topic matches: `X-GitHub-Api-Version`, `2026-03-10`
- diagnostic matches: `2022-11-28`

<pre>
#### Example request using query parameters The ["List public events" endpoint](/rest/activity/events#list-public-events) returns thirty issues by default. The following example uses the `per_page` query parameter to return two issues instead of 30, and the `page` query parameter to fetch only the first page of results. ```shell copy curl --request GET \ --url "https://api.github.com/events?per_page=2&amp;page=1" \ --header "Accept: application/vnd.github+json" \ --header "X-GitHub-Api-Version: 2022-11-28" \ https://api.github.com/events ``` #### Example request using body parameters The following example uses the [Create an issue](/rest/issues/issues#create-an-issue) endpoint to create a new issue in the octocat/Spoon-Knife repository. Replace `YOUR-TOKEN` with the authentication token you created in a previous step. &gt; [!NOTE] &gt; If you are using a fine-grained personal access token, you must replace `octocat/Spoon-Knife` with a repository that you own or that is owned by an organization that you are a member of. Your token must have access to that repository and have read and write permissions for repository issues. For more information, see [/authentication/keeping-your-account-and-d
</pre>

#### `chunk-0c39718da981e6f97bb7c5cf94eb651c8d1ef9532bbfc7e38a9b46d25641f9af`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/update`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`, `supported`

<pre>
{"fragments":[{"path":["operation","requestBody","content","application/json","schema","properties","security_and_analysis"],"value":{"description":"Specify which security and analysis features to enable or disable for the repository.\n\nTo use this parameter, you must have admin permissions for the repository or be an owner or security manager for the organization that owns the repository. For more information, see \"[Managing security managers in your organization](https://docs.github.com/organizations/managing-peoples-access-to-your-organization-with-roles/managing-security-managers-in-your-organization).\"\n\nFor example, to enable GitHub Advanced Security, use this data in the body of the `PATCH` request:\n`{ \"security_and_analysis\": {\"advanced_security\": { \"status\": \"enabled\" } } }`.\n\nYou can check which security and analysis features are currently enabled by using a `GET /repos/{owner}/{repo}` request.","nullable":true,"properties":{"advanced_security":{"description":"Use the `status` property to enable or disable GitHub Advanced Security for this repository.\nFor more information, see \"[About GitHub Advanced\nSecurity](/github/getting-started-with-github/learning
</pre>

#### `chunk-04e27893cade7a2cb64b06cc387db4cefb1c887db971ddfdc6082b8c136a206b`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/get-content`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Gets the contents of a file or directory in a repository. Specify the file path or directory with the `path` parameter. If you omit the `path` parameter, you will receive the contents of the repository's root directory.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw file contents for files and symlinks.\n- **`application/vnd.github.html+json`**: Returns the file contents in HTML. Markup languages are rendered to HTML using GitHub's open-source [Markup library](https://github.com/github/markup).\n- **`application/vnd.github.object+json`**: Returns the contents in a consistent object format regardless of the content type. For example, instead of an array of objects for a directory, the response will be an object with an `entries` attribute containing the array of objects.\n\nIf the content is a directory: The response will be an array of objects, one object for each item in the directory.\n\nIf the
</pre>

#### `chunk-0866e576fcc08a7d8b93d77a2710ca186b1b7ab008a0c3332a53230283b04136`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository in the specified organization. The authenticated user must be a member of the organization.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-an-organization-repository"},"operationId":"repos/create-in-org","parameters":[{"$ref":"#/components/parameters/org"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repository","has_issues":true,"has_projects":true,"has_wiki":true,"homepage":"https://github.com","name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Either `true` to allow auto-merge on pull requests, or `false` to disallow auto-merge.","type":"boolean"},"allow_merge_commit":{"default":true,"description":"Either `true` to allow merging pull requests with a merge commit, or `false` to prevent merging pull requests with
</pre>

#### `chunk-0b351263c3e84b013e6023b583d860d8ddec76363e7adb26df1bbd9b5f73ef76`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-webhook`, `openapi-current-2026-03-10:repos/get-webhook`, `openapi-current-2026-03-10:repos/get-webhook-config-for-repo`, `openapi-current-2026-03-10:repos/list-webhooks`, `openapi-current-2026-03-10:repos/update-webhook`, `openapi-current-2026-03-10:repos/update-webhook-config-for-repo`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/webhook-config-content-type","value":{"description":"The media type used to serialize the payloads. Supported values include `json` and `form`. The default is `form`.","example":"\"json\"","type":"string"}}}]}
</pre>

#### `chunk-10c4429504de54597968c4f4e6ad3cd193495b142512d84fd924790d86eb6bb3`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:repos/list-issue-types`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue-type","value":{"description":"The type assigned to the issue. This is only present for issues in repositories where issue types are supported.","nullable":true,"properties":{"color":{"description":"The color of the issue type.","enum":["gray","blue","green","yellow","orange","red","pink","purple"],"nullable":true,"type":"string"},"created_at":{"description":"The time the issue type created.","format":"date-time","type":"string"},"description":{"description":"The description of the issue type.","nullable":true,"type":"string"},"id":{"description":"The unique identifier of the issue type.","type":"integer"},"is_enabled":{"description":"The enabled state of the issue type.","type":"boolean"},"name":{"description":"The name of the issue type.","type":"string"},"node_id":{"description":"The node identifier of the issue type.","type":"string"},"updated_at":{"description":"The time the issue type last updated.","format":"date-time","type":"string"}},"required":["id","node_id","name","description"],"title":"Issue Type","type":"object"}}}]}
</pre>

#### `chunk-1d8e71443dfb4843186d33f63e58515e725944385529fdaa2feefb572a10408d`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/get-workflow-usage`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"&gt; [!WARNING] \n&gt; This endpoint is in the process of closing down. Refer to \"[Actions Get workflow usage and Get workflow run usage endpoints closing down](https://github.blog/changelog/2025-02-02-actions-get-workflow-usage-and-get-workflow-run-usage-endpoints-closing-down/)\" for more information.\n\nGets the number of billable minutes used by a specific workflow during the current billing cycle. Billable minutes only apply to workflows in private repositories that use GitHub-hosted runners. Usage is listed for each GitHub-hosted runner operating system in milliseconds. Any job re-runs are also included in the usage. The usage does not include the multiplier for macOS and Windows runners and is not rounded up to the nearest whole minute. For more information, see \"[Managing billing for GitHub Actions](https://docs.github.com/github/setting-up-and-managing-billing-and-payments-on-github/managing-billing-for-github-actions)\".\n\nYou can replace `workflow_id` with the workflow file name. For example, you could use `main.yaml`.\n\nAnyone with read access to the repository can use this endpoint.\n\nOAuth app
</pre>

#### `chunk-3ac77b13bea67347653851ee01090d4f29f36b87ea04d1a4398e818a988a8504`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-webhook`, `openapi-current-2026-03-10:repos/get-webhook`, `openapi-current-2026-03-10:repos/get-webhook-config-for-repo`, `openapi-current-2026-03-10:repos/list-webhooks`, `openapi-current-2026-03-10:repos/update-webhook`, `openapi-current-2026-03-10:repos/update-webhook-config-for-repo`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/webhook-config-insecure-ssl","value":{"oneOf":[{"description":"Determines whether the SSL certificate of the host for `url` will be verified when delivering payloads. Supported values include `0` (verification is performed) and `1` (verification is not performed). The default is `0`. **We strongly recommend not setting this to `1` as you are subject to man-in-the-middle and other attacks.**","example":"\"0\"","type":"string"},{"type":"number"}]}}}]}
</pre>

#### `chunk-3c499f1990ac0c066d520f07851659dcd0fdb7821fde7a966223a22b8038e1fd`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-getting-started`
- topic matches: `X-GitHub-Api-Version`
- diagnostic matches: `supported`

<pre>
--- title: Getting started with the REST API shortTitle: Getting started intro: 'Learn how to use the GitHub REST API.' versions: fpt: '*' ghes: '*' ghec: '*' redirect_from: - /rest/guides/getting-started-with-the-rest-api - /rest/initialize-the-repo - /rest/overview/resources-in-the-rest-api - /rest/using-the-rest-api/resources-in-the-rest-api - /v3/media - /rest/overview/media-types - /rest/using-the-rest-api/media-types category: - Learn about the REST API --- ## Introduction This article describes how to use the GitHub REST API with GitHub CLI, `curl`, or JavaScript. For a quickstart guide, see [/rest/quickstart](/rest/quickstart). ## About requests to the REST API This section describes the elements that make up an API request: * [HTTP method](#http-method) * [Path](#path) * [Headers](#headers) * [Media types](#media-types) * [Authentication](#authentication) * [Parameters](#parameters) Every request to the REST API includes an HTTP method and a path. Depending on the REST API endpoint, you might also need to specify request headers, authentication information, query parameters, or body parameters. The REST API reference documentation describes the HTTP method, path, and param
</pre>

#### `chunk-4ad7d584f3fcb025e837a6994ffe8681278b13f070cf0fe485b7b5fb19a6821d`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/update-branch-protection`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":["operation","requestBody"],"value":{"content":{"application/json":{"examples":{"default":{"value":{"allow_deletions":true,"allow_force_pushes":true,"allow_fork_syncing":true,"block_creations":true,"enforce_admins":true,"lock_branch":true,"required_conversation_resolution":true,"required_linear_history":true,"required_pull_request_reviews":{"bypass_pull_request_allowances":{"teams":["justice-league"],"users":["octocat"]},"dismiss_stale_reviews":true,"dismissal_restrictions":{"teams":["justice-league"],"users":["octocat"]},"require_code_owner_reviews":true,"require_last_push_approval":true,"required_approving_review_count":2},"required_status_checks":{"contexts":["continuous-integration/travis-ci"],"strict":true},"restrictions":{"apps":["super-ci"],"teams":["justice-league"],"users":["octocat"]}}}},"schema":{"properties":{"allow_deletions":{"description":"Allows deletion of the protected branch by anyone with write access to the repository. Set to `false` to prevent deletion of the protected branch. Default: `false`. For more information, see \"[Enabling force pushes to a protected branch](https://docs.github.com/github/administering-a-repository/enabling-force
</pre>

#### `chunk-5ecdf08a05759270e435b3cbcb04c2202e20a1307ec9ad740845b3510702b440`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/get-workflow-run-usage`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"&gt; [!WARNING] \n&gt; This endpoint is in the process of closing down. Refer to \"[Actions Get workflow usage and Get workflow run usage endpoints closing down](https://github.blog/changelog/2025-02-02-actions-get-workflow-usage-and-get-workflow-run-usage-endpoints-closing-down/)\" for more information.\n\nGets the number of billable minutes and total run time for a specific workflow run. Billable minutes only apply to workflows in private repositories that use GitHub-hosted runners. Usage is listed for each GitHub-hosted runner operating system in milliseconds. Any job re-runs are also included in the usage. The usage does not include the multiplier for macOS and Windows runners and is not rounded up to the nearest whole minute. For more information, see \"[Managing billing for GitHub Actions](https://docs.github.com/github/setting-up-and-managing-billing-and-payments-on-github/managing-billing-for-github-actions)\".\n\nAnyone with read access to the repository can use this endpoint.\n\nOAuth app tokens and personal access tokens (classic) need the `repo` scope to use this endpoint with a private repository.",
</pre>

#### `chunk-62d5a201c8c8a626beb73974d72b14772321642072b146953d161ce4c5078e39`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/update-status-check-protection`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Protected branches are available in public repositories with GitHub Free and GitHub Free for organizations, and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nUpdating required status checks requires admin or owner permissions to the repository and branch protection to be enabled.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/branches/branch-protection#update-status-check-protection"},"operationId":"repos/update-status-check-protection","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/branch"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"contexts":["continuous-integration/travis-ci"],"strict":true}}},"schema":{"properties":{"checks":{"description":"The list of status checks to require in order to merge into this bran
</pre>

#### `chunk-658e7aa6c12ee1a76e2f198722cba975e64c276a1f26fcac7e9ac725de2c23ec`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create-reply-for-review-comment`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a reply to a review comment for a pull request. For the `comment_id`, provide the ID of the review comment you are replying to. This must be the ID of a _top-level review comment_, not a reply to that comment. Replies to replies are not supported.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you
</pre>

#### `chunk-937f6695df9910d351b879dfd90bc46786341a98593e317acf58bcfe00203894`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create-review-comment`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a review comment on the diff of a specified pull request. To add a regular comment to a pull request timeline, see \"[Create an issue comment](https://docs.github.com/rest/issues/comments#create-an-issue-comment).\"\n\nIf your comment applies to more than one line in the pull request diff, you should use the parameters `line`, `side`, and optionally `start_line` and `start_side` in your request.\n\nThe `position` parameter is closing down. If you use `position`, the `line`, `side`, `start_line`, and `start_side` parameters are not required.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom
</pre>

#### `chunk-aa78d7e63594d522aa1c8dbc61b763296c399c8869ed807a91452dc690b62868`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue-type","value":{"description":"The type assigned to the issue. This is only present for issues in repositories where issue types are supported.","nullable":true,"properties":{"color":{"description":"The color of the issue type.","enum":["gray","blue","green","yellow","orange","red","pink","purple"],"nullable":true,"type":"string"},"created_at":{"description":"The time the issue type created.","format":"date-time","type":"string"},"description":{"description":"The description of the issue type.","nullable":true,"type":"string"},"id":{"description":"The unique identifier of the issue type.","type":"integer"},"is_enabled":{"description":"The enabled state of the issue type.","type":"boolean"},"name":{"description":"The name of the issue type.","type":"string"},"node_id":{"description":"The node identifier of the issue type.","type":"string"},"updated_at":{"description":"The time the issue type last updated.","format":"date-time","type":"string"}},"required":["id","node_id","name","description"],"title":"Issue Type","type":"object"}}}]}
</pre>

#### `chunk-c40a61fe0163c9ca20b18305e37dd16f184be4556c4d0ff2a75da6076b7951f0`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/get-commit`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Returns the contents of a single commit reference. You must have `read` access for the repository to use this endpoint.\n\n&gt; [!NOTE]\n&gt; If there are more than 300 files in the commit diff and the default JSON media type is requested, the response will include pagination link headers for the remaining files, up to a limit of 3000 files. Each page contains the static commit information, and the only changes are to the file listing.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\" Pagination query parameters are not supported for these media types.\n\n- **`application/vnd.github.diff`**: Returns the diff of the commit. Larger diffs may time out and return a 5xx status code.\n- **`application/vnd.github.patch`**: Returns the patch of the commit. Diffs with binary data will have no `patch` property. Larger diffs may time out and return a 5xx status code.\n- **`application/vnd.github.sha`**: Returns the commit's SHA-1 hash. You can use this endpoint to check if a
</pre>

#### `chunk-da04294be42e1dd93e90fa4da64500642d095abd22102bf076a89f26043090d0`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/list-events`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-timeline`
- topic matches: `2026-03-10`
- diagnostic matches: `supported`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-issue-event-intent","value":{"description":"The intent behind an agent's action on an issue, including the rationale and confidence. Present (and `null` when the event carried no agent intent) on supported event types while the issue suggestions feature is enabled for the repository; the property is omitted entirely when the feature is disabled or the event type does not support intent.","nullable":true,"properties":{"confidence":{"description":"The confidence level the agent had when performing this action.","enum":["LOW","MEDIUM","HIGH"],"nullable":true,"type":"string"},"rationale":{"description":"The reasoning the agent provided for the change.","nullable":true,"type":"string"}},"title":"Issue Event Intent","type":"object"}}}]}
</pre>

#### `chunk-ddc3a415d9ebe1d117e09fefdd816cde9d71b26204c6a5e2aab0d21c9213e2ab`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-deployment-status`, `openapi-current-2026-03-10:repos/get-deployment-status`, `openapi-current-2026-03-10:repos/list-deployment-statuses`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/deployment-status","value":{"description":"The status of a deployment.","properties":{"created_at":{"example":"2012-07-20T01:19:13Z","format":"date-time","type":"string"},"creator":{"$ref":"#/components/schemas/nullable-simple-user"},"deployment_url":{"example":"https://api.github.com/repos/octocat/example/deployments/42","format":"uri","type":"string"},"description":{"default":"","description":"A short description of the status.","example":"Deployment finished successfully.","maxLength":140,"type":"string"},"environment":{"default":"","description":"The environment of the deployment that the status is for.","example":"production","type":"string"},"environment_url":{"default":"","description":"The URL for accessing your environment.","example":"https://staging.example.com/","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"log_url":{"default":"","description":"The URL to associate with this status.","example":"https://example.com/deployment/42/output","format":"uri","type":"string"},"node_id":{"example":"MDE2OkRlcGxveW1lbnRTdGF0dXMx","type":"string"},"performed_via_github_app":{"
</pre>

#### `chunk-e45f2383d85aa9d8b3145a8dbe636ae52757b5cd7b8903706a7856ecef7bc624`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:pulls/create-reply-for-review-comment`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/get-review-comment`, `openapi-current-2026-03-10:pulls/list-review-comments`, `openapi-current-2026-03-10:pulls/list-review-comments-for-repo`, `openapi-current-2026-03-10:pulls/update-review-comment`
- topic matches: `2026-03-10`
- diagnostic matches: `closing down`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-review-comment","value":{"description":"Pull Request Review Comments are comments on a portion of the Pull Request's diff.","properties":{"_links":{"properties":{"html":{"properties":{"href":{"example":"https://github.com/octocat/Hello-World/pull/1#discussion-diff-1","format":"uri","type":"string"}},"required":["href"],"type":"object"},"pull_request":{"properties":{"href":{"example":"https://api.github.com/repos/octocat/Hello-World/pulls/1","format":"uri","type":"string"}},"required":["href"],"type":"object"},"self":{"properties":{"href":{"example":"https://api.github.com/repos/octocat/Hello-World/pulls/comments/1","format":"uri","type":"string"}},"required":["href"],"type":"object"}},"required":["self","html","pull_request"],"type":"object"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"The text of the comment.","example":"We should probably include a check for null values here.","type":"string"},"body_html":{"example":"\"&lt;p&gt;comment body&lt;/p&gt;\"","type":"string"},"body_text":{"example":"\"comment body\"","type":"string"},"commit_id":{"description":"The SH
</pre>

## `dev-add-assignees-silent-ignore-cause`

- cluster: `openapi-pair:issues/add-assignees`
- role: `evaluation_development_case`
- pattern: `silent_mutation_cause`
- provisional claim: A generic successful add-assignees outcome does not establish exactly which requested assignee was ignored or the concrete reason.
- total discovered candidates: 175
- candidates outside Phase 4 gold evidence: 163
- automated verdict: `review_required`

### Search terms

- topic: `issues/add-assignees`, `add assignees`, `assignees`
- diagnostic: `silently ignored`, `silently dropped`, `push access`, `ignored_reason`

### Highest-ranked candidates (max 25)

#### `chunk-4ef0bdd3ba1424f602eb63cd7cda604ca17a79a151816fddca4e7aa117ee58ff`

- score: `53`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`
- topic matches: `issues/add-assignees`, `add assignees`, `assignees`
- diagnostic matches: `silently ignored`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Adds up to 10 assignees to an issue. Users already assigned to an issue are not replaced.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/assignees#add-assignees-to-an-issue"},"operationId":"issues/add-assignees","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["hubot","other_user"]}}},"schema":{"properties":{"assignees":{"description":"Usernames of people to assign this issue to. _NOTE: Only users with push access can add assignees to an issue. Assignees are silently ignored otherwise._","items":{"oneOf":[{"type":"string"},{"properties":{"confidence":{"description":"The confidence level for this assignee choice.","enum":["low","medium","high"],"type":"string"},"login":{"description":"The login of the user to assign.","type":"string"},"rationale":{"description":"Optional reasoning for adding this assignee.","type":"string"},"suggest":{"description":"If `true`, the assign
</pre>

#### `chunk-db26bf1f3b7de296c0851a148250427f380b5c18b32e5662922d579b158be8bb`

- score: `53`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`
- topic matches: `issues/add-assignees`, `add assignees`, `assignees`
- diagnostic matches: `silently ignored`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Adds up to 10 assignees to an issue. Users already assigned to an issue are not replaced.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/assignees#add-assignees-to-an-issue"},"operationId":"issues/add-assignees","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["hubot","other_user"]}}},"schema":{"properties":{"assignees":{"description":"Usernames of people to assign this issue to. _NOTE: Only users with push access can add assignees to an issue. Assignees are silently ignored otherwise._","items":{"oneOf":[{"type":"string"},{"properties":{"confidence":{"description":"The confidence level for this assignee choice.","enum":["low","medium","high"],"type":"string"},"login":{"description":"The login of the user to assign.","type":"string"},"rationale":{"description":"Optional reasoning for adding this assignee.","type":"string"},"suggest":{"description":"If `true`, the assign
</pre>

#### `chunk-9f6d396d1ea063055154a1c2a2afaccb1765997b4a064996834dcdd09eb56146`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignee":{"$ref":"#/components/schemas/nullable-simple-user"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","t
</pre>

#### `chunk-f278490de8dd1b2e881f4047023fc16f627898e6e966176283a86ef9325c775a`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","type":"integer"},"issue_dependencies_summary":{"$ref":"#/componen
</pre>

#### `chunk-2210894abf46695e0ed3b04922c99f77aff95c630cce76e3183c71ab96e2420c`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/list-events-for-repo`
- topic matches: `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","nullable":true,"properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","type":"integer"},"issue_dependencies_sum
</pre>

#### `chunk-26388d13c264f9446b0d6f5ddc6c93fe95743a333c7583b9fb435b344ef34b34`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/remove-assignees`
- topic matches: `assignees`
- diagnostic matches: `silently ignored`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"Removes one or more assignees from an issue.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/assignees#remove-assignees-from-an-issue"},"operationId":"issues/remove-assignees","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["hubot","other_user"]}}},"schema":{"properties":{"assignees":{"description":"Usernames of assignees to remove from an issue. _NOTE: Only users with push access can remove assignees from an issue. Assignees are silently ignored otherwise._","items":{"type":"string"},"type":"array"}},"type":"object"}}}},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response"}},"summary":"Remove assignees from an issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"assi
</pre>

#### `chunk-7d23320f73fb390fdd09ff2a55515db617f24d5d9dfb610dd7745a4026fb4cf4`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`
- topic matches: `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","type":"integer"},"issue_dependencies_summary":{"$ref":"#/componen
</pre>

#### `chunk-818a2d7af95a38d5ffd8d96869fbd8198cb399d3e2e8c55900c85770cf07a1d9`

- score: `33`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create`
- topic matches: `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+js
</pre>

#### `chunk-a6f2c249acaf3aadd70ac7964297edb46071d6ab5d2fed98384b39ba0e34862f`

- score: `33`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/create`
- topic matches: `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+js
</pre>

#### `chunk-cd375411d841104feb9b2825d17e637b92b9d817f6f22d1c52d0fbce134f328d`

- score: `33`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/update`
- topic matches: `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":["method"],"value":"patch"},{"path":["operation","description"],"value":"Issue owners and users with push access or Triage role can edit an issue.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`."},{"path":["operation","externalDocs"],"value":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#update-an-issue"}},{"path":["operation","operationId"],"value":"issues/update"},{"path":["operation","parameters"]
</pre>

#### `chunk-db4f7149fb4f7e84d0de4a79830ed8a35e793d967bbf7c60f5d4f35fad88f118`

- score: `33`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/update`
- topic matches: `assignees`
- diagnostic matches: `silently dropped`, `push access`

<pre>
{"fragments":[{"path":["method"],"value":"patch"},{"path":["operation","description"],"value":"Issue owners and users with push access or Triage role can edit an issue.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`."},{"path":["operation","externalDocs"],"value":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#update-an-issue"}},{"path":["operation","operationId"],"value":"issues/update"},{"path":["operation","parameters"]
</pre>

#### `chunk-2a1b7e2dd72157f835c63422ef3416992ea7a3c25b55460ada39cd66ca0d6f3f`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/update`
- topic matches: `assignees`
- diagnostic matches: `ignored_reason`

<pre>
{"fragments":[{"path":["operation","responses"],"value":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"allOf":[{"$ref":"#/components/schemas/issue"},{"properties":{"suggestions":{"description":"Pending suggestions for each suggestible field (`type`,\n`issue_field_values`, `labels`, `assignees`, `state`) the\nrequest touched. Omitted for fields not in the request or\nwith no pending or ignored suggestions. Items tagged\n`ignored` are echoes of the current request's inputs that\nwere not persisted as pending suggestions.\n","properties":{"assignees":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"login":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"issue_field_values":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"field_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale"
</pre>

#### `chunk-a1a6a71a7bf60ff978907f1339ae3ce7cc900759a29c6114fdff63e37a492421`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/update`
- topic matches: `assignees`
- diagnostic matches: `ignored_reason`

<pre>
{"fragments":[{"path":["operation","responses"],"value":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"allOf":[{"$ref":"#/components/schemas/issue"},{"properties":{"suggestions":{"description":"Pending suggestions for each suggestible field (`type`,\n`issue_field_values`, `labels`, `assignees`, `state`) the\nrequest touched. Omitted for fields not in the request or\nwith no pending or ignored suggestions. Items tagged\n`ignored` are echoes of the current request's inputs that\nwere not persisted as pending suggestions.\n","properties":{"assignees":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"login":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"issue_field_values":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"field_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale"
</pre>

#### `chunk-02b485cc4541fe819035acc2eed397529f2d4591bb286a303128cb0ece36d2ca`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/examples/issue","value":{"value":{"active_lock_reason":"too heated","assignee":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"assignees":[{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github
</pre>

#### `chunk-0fb8f7cec6b12687d9ca57a3028edfc64d2e9527be0ea74b8314c5f49553eb44`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-license-simple","value":{"description":"License Simple","nullable":true,"properties":{"html_url":{"format":"uri","type":"string"},"key":{"example":"mit","type":"string"},"name":{"example":"MIT License","type":"string"},"node_id":{"example":"MDc6TGljZW5zZW1pdA==","type":"string"},"spdx_id":{"example":"MIT","nullable":true,"type":"string"},"url":{"example":"https://api.github.com/licenses/mit","format":"uri","nullable":true,"type":"string"}},"required":["key","name","url","spdx_id","node_id"],"title":"License Simple","type":"object"}}}]}
</pre>

#### `chunk-11b5175be59882555f143170b8b25fce2a8662dc9e99cc5d4a4ae2f49d46c79a`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-pinned-issue-comment","value":{"description":"Context around who pinned an issue comment and when it was pinned.","nullable":true,"properties":{"pinned_at":{"example":"2011-04-14T16:00:49Z","format":"date-time","type":"string"},"pinned_by":{"$ref":"#/components/schemas/nullable-simple-user"}},"required":["pinned_at","pinned_by"],"title":"Pinned Issue Comment","type":"object"}}}]}
</pre>

#### `chunk-17edde83c545913ec5e5e340594689c4f03d9457e9df3404c718aa2e3b01ab3f`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-204acb984c21136818ef3812eda236d4a282a72bad856a6833effa0a1e07d976`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue-type","value":{"description":"The type assigned to the issue. This is only present for issues in repositories where issue types are supported.","nullable":true,"properties":{"color":{"description":"The color of the issue type.","enum":["gray","blue","green","yellow","orange","red","pink","purple"],"nullable":true,"type":"string"},"created_at":{"description":"The time the issue type created.","format":"date-time","type":"string"},"description":{"description":"The description of the issue type.","nullable":true,"type":"string"},"id":{"description":"The unique identifier of the issue type.","type":"integer"},"is_enabled":{"description":"The enabled state of the issue type.","type":"boolean"},"name":{"description":"The name of the issue type.","type":"string"},"node_id":{"description":"The node identifier of the issue type.","type":"string"},"updated_at":{"description":"The time the issue type last updated.","format":"date-time","type":"string"}},"required":["id","node_id","name","description"],"title":"Issue Type","type":"object"}}}]}
</pre>

#### `chunk-20e6d65f58412d5ff8d152ca4cdecd24734513599159d11a178371d59f8c96f0`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-2b16d069835e47a207140fb0c82c7ae5e2c45338ed52316db8d22323fe089e9f`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/sub-issues-summary","value":{"properties":{"completed":{"type":"integer"},"percent_completed":{"type":"integer"},"total":{"type":"integer"}},"required":["total","completed","percent_completed"],"title":"Sub-issues Summary","type":"object"}}}]}
</pre>

#### `chunk-2def5cb713729f41143b8fd1ad8790eef2b416595be1165bcde4c58579f643bc`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-milestone","value":{"description":"A collection of related issues and pull requests.","nullable":true,"properties":{"closed_at":{"example":"2013-02-12T13:22:01Z","format":"date-time","nullable":true,"type":"string"},"closed_issues":{"example":8,"type":"integer"},"created_at":{"example":"2011-04-10T20:09:31Z","format":"date-time","type":"string"},"creator":{"$ref":"#/components/schemas/nullable-simple-user"},"description":{"example":"Tracking milestone for version 1.0","nullable":true,"type":"string"},"due_on":{"example":"2012-10-09T23:39:01Z","format":"date-time","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat/Hello-World/milestones/v1.0","format":"uri","type":"string"},"id":{"example":1002604,"type":"integer"},"labels_url":{"example":"https://api.github.com/repos/octocat/Hello-World/milestones/1/labels","format":"uri","type":"string"},"node_id":{"example":"MDk6TWlsZXN0b25lMTAwMjYwNA==","type":"string"},"number":{"description":"The number of the milestone.","example":42,"type":"integer"},"open_issues":{"example":4,"type":"integer"},"state":{"default":"open","description":
</pre>

#### `chunk-38411a79ddfe1706ac4d09200cbb85e69ebd4ec73501282a92c6a9a73e7301a2`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue-field-value","value":{"description":"A value assigned to an issue field","properties":{"data_type":{"description":"The data type of the issue field","enum":["text","single_select","multi_select","number","date"],"example":"text","type":"string"},"issue_field_id":{"description":"Unique identifier for the issue field.","example":1,"format":"int64","type":"integer"},"issue_field_name":{"description":"The human-readable name of the issue field.","example":"Priority","type":"string"},"multi_select_options":{"description":"Details about the selected options","items":{"properties":{"color":{"description":"The color of the option","example":"red","type":"string"},"id":{"description":"Unique identifier for the option.","example":1,"format":"int64","type":"integer"},"name":{"description":"The name of the option","example":"High","type":"string"}},"required":["id","name","color"],"type":"object"},"nullable":true,"type":"array"},"node_id":{"example":"IFT_GDKND","type":"string"},"single_select_option":{"description":"Details about the selected option (only present for single_select fields)","nullable":true,"properties":{"
</pre>

#### `chunk-393263c6350daa1c0052f9d88c7b5e666502f089386dfe50ee16091e4e65348e`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-issue-comment-minimized","value":{"description":"Details about why an issue comment was minimized.","nullable":true,"properties":{"reason":{"description":"The reason the comment was minimized.","example":"low-quality","nullable":true,"type":"string"}},"required":["reason"],"title":"Minimized Issue Comment","type":"object"}}}]}
</pre>

#### `chunk-46e55579c254198f0c8ee06435e5fe62e11b1e9792931165fbb24bf847cc5d08`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/enterprise","value":{"description":"An enterprise on GitHub.","properties":{"avatar_url":{"format":"uri","type":"string"},"created_at":{"example":"2019-01-26T19:01:12Z","format":"date-time","nullable":true,"type":"string"},"description":{"description":"A short description of the enterprise.","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/enterprises/octo-business","format":"uri","type":"string"},"id":{"description":"Unique identifier of the enterprise","example":42,"type":"integer"},"name":{"description":"The name of the enterprise.","example":"Octo Business","type":"string"},"node_id":{"example":"MDEwOlJlcG9zaXRvcnkxMjk2MjY5","type":"string"},"slug":{"description":"The slug url identifier for the enterprise.","example":"octo-business","type":"string"},"updated_at":{"example":"2019-01-26T19:14:43Z","format":"date-time","nullable":true,"type":"string"},"website_url":{"description":"The enterprise's website URL.","format":"uri","nullable":true,"type":"string"}},"required":["id","node_id","name","slug","html_url","created_at","updated_at","avatar_url"],"title":"Enterprise","type":"object"}}
</pre>

#### `chunk-49519478c38225329e86c9ce6516c1d569e666049bd05417cd94a80c8f89fdef`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/add-assignees`, `assignees`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/parameters/issue-number","value":{"description":"The number that identifies the issue.","in":"path","name":"issue_number","required":true,"schema":{"type":"integer"}}}}]}
</pre>

## `dev-create-issue-silent-drop-cause`

- cluster: `openapi-pair:issues/create`
- role: `evaluation_development_case`
- pattern: `silent_mutation_cause`
- provisional claim: Generic success when creating an issue does not establish the exact actor or permission deficiency responsible for silently dropped optional fields.
- total discovered candidates: 278
- candidates outside Phase 4 gold evidence: 253
- automated verdict: `review_required`

### Search terms

- topic: `issues/create`, `create an issue`, `/issues`
- diagnostic: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

### Highest-ranked candidates (max 25)

#### `chunk-818a2d7af95a38d5ffd8d96869fbd8198cb399d3e2e8c55900c85770cf07a1d9`

- score: `65`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create`
- topic matches: `issues/create`, `create an issue`, `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+js
</pre>

#### `chunk-a6f2c249acaf3aadd70ac7964297edb46071d6ab5d2fed98384b39ba0e34862f`

- score: `65`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/create`
- topic matches: `issues/create`, `create an issue`, `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+js
</pre>

#### `chunk-9f6d396d1ea063055154a1c2a2afaccb1765997b4a064996834dcdd09eb56146`

- score: `55`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignee":{"$ref":"#/components/schemas/nullable-simple-user"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","t
</pre>

#### `chunk-f278490de8dd1b2e881f4047023fc16f627898e6e966176283a86ef9325c775a`

- score: `55`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","type":"integer"},"issue_dependencies_summary":{"$ref":"#/componen
</pre>

#### `chunk-02b485cc4541fe819035acc2eed397529f2d4591bb286a303128cb0ece36d2ca`

- score: `47`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/examples/issue","value":{"value":{"active_lock_reason":"too heated","assignee":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"assignees":[{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github
</pre>

#### `chunk-a4c281e9a5097786168a2c4134908920f7b2c0c5f77ec899e2dd3803f18a04f0`

- score: `47`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/examples/issue","value":{"value":{"active_lock_reason":"too heated","assignees":[{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"}],"author_association":"COLLABORATOR","body":"I'm having a problem with this.","closed_at":null,"closed_by":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_
</pre>

#### `chunk-2210894abf46695e0ed3b04922c99f77aff95c630cce76e3183c71ab96e2420c`

- score: `45`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/list-events-for-repo`
- topic matches: `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","nullable":true,"properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","type":"integer"},"issue_dependencies_sum
</pre>

#### `chunk-7d23320f73fb390fdd09ff2a55515db617f24d5d9dfb610dd7745a4026fb4cf4`

- score: `45`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`
- topic matches: `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/issue","value":{"description":"Issues are a great way to keep track of tasks, enhancements, and bugs for your projects.","properties":{"active_lock_reason":{"nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue","example":"It looks like the new widget form is broken on Safari. When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser bug?","nullable":true,"type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"closed_at":{"format":"date-time","nullable":true,"type":"string"},"closed_by":{"$ref":"#/components/schemas/nullable-simple-user"},"comments":{"type":"integer"},"comments_url":{"format":"uri","type":"string"},"created_at":{"format":"date-time","type":"string"},"draft":{"type":"boolean"},"events_url":{"format":"uri","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"format":"int64","type":"integer"},"issue_dependencies_summary":{"$ref":"#/componen
</pre>

#### `chunk-cd375411d841104feb9b2825d17e637b92b9d817f6f22d1c52d0fbce134f328d`

- score: `45`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/update`
- topic matches: `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["method"],"value":"patch"},{"path":["operation","description"],"value":"Issue owners and users with push access or Triage role can edit an issue.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`."},{"path":["operation","externalDocs"],"value":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#update-an-issue"}},{"path":["operation","operationId"],"value":"issues/update"},{"path":["operation","parameters"]
</pre>

#### `chunk-db4f7149fb4f7e84d0de4a79830ed8a35e793d967bbf7c60f5d4f35fad88f118`

- score: `45`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/update`
- topic matches: `/issues`
- diagnostic matches: `silently dropped`, `push access`, `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["method"],"value":"patch"},{"path":["operation","description"],"value":"Issue owners and users with push access or Triage role can edit an issue.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`."},{"path":["operation","externalDocs"],"value":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#update-an-issue"}},{"path":["operation","operationId"],"value":"issues/update"},{"path":["operation","parameters"]
</pre>

#### `chunk-17edde83c545913ec5e5e340594689c4f03d9457e9df3404c718aa2e3b01ab3f`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `assignees`, `labels`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-016bb9166542c2ba4bbd33a1aeb8d10d0cc889e5a0c2276d00dc5a5e88f4cb07`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-getting-started`
- topic matches: `create an issue`, `/issues`
- diagnostic matches: `labels`

<pre>
### Authentication Many endpoints require authentication or return additional information if you are authenticated. Additionally, you can make more requests per hour when you are authenticated. To authenticate your request, you will need to provide an authentication token with the required scopes or permissions. There a few different ways to get a token: You can create a personal access token, generate a token with a GitHub App, or use the built-in `GITHUB_TOKEN` in a GitHub Actions workflow. For more information, see [/rest/authentication/authenticating-to-the-rest-api](/rest/authentication/authenticating-to-the-rest-api). For an example of a request that uses an authentication token, see [Making a request](#making-a-request). &gt; [!NOTE] &gt; If you don't want to create a token, you can use GitHub CLI. GitHub CLI will take care of authentication for you, and help keep your account secure. For more information, see the [GitHub CLI version of this page](/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=cli). &gt; [!WARNING] &gt; Treat your access token the same way you would treat your passwords or other sensitive credentials. For more information, see [/rest/authentication/keep
</pre>

#### `chunk-20e6d65f58412d5ff8d152ca4cdecd24734513599159d11a178371d59f8c96f0`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `assignees`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-7adac06a2caab9a9b07ecec0547dbb8d8c2a1fa86f3471ffa2f1d5a12552f7fe`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create-label`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `labels`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a label for the specified repository with the given name and color. The name and color parameters are required. The color must be a valid [hexadecimal color code](http://www.color-hex.com/).","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/labels#create-a-label"},"operationId":"issues/create-label","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"color":"f29513","description":"Something isn't working","name":"bug"}}},"schema":{"properties":{"color":{"description":"The [hexadecimal color code](http://www.color-hex.com/) for the label, without the leading `#`.","type":"string"},"description":{"description":"A short description of the label. Must be 100 characters or fewer.","type":"string"},"name":{"description":"The name of the label. Emoji can be added to label names, using either native emoji or colon-style markup. For example, typing `:strawberry:` will render the emoji ![:strawberry:](https://github.githubassets.com/ima
</pre>

#### `chunk-9f7ca80f0e064800eff1f8a1a6d53e3d21312e715e980fc43571b48bda322ae9`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `assignees`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-issue-comment","value":{"description":"Comments provide a way for people to collaborate on an issue.","nullable":true,"properties":{"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue comment","example":"What version of Safari were you using when you observed this bug?","type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"created_at":{"example":"2011-04-14T16:00:49Z","format":"date-time","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"description":"Unique identifier of the issue comment","example":42,"format":"int64","type":"integer"},"issue_url":{"format":"uri","type":"string"},"minimized":{"$ref":"#/components/schemas/nullable-issue-comment-minimized"},"node_id":{"type":"string"},"performed_via_github_app":{"$ref":"#/components/schemas/nullable-integration"},"pin":{"$ref":"#/components/schemas/nullable-pinned-issue-comment"},"reactions":{"$ref":"#/components/schemas/reaction-rollup"},"updated_at":{"example":"2011-04-14T16:00:49Z","format":"date-time","type":"string"},"url":{"description":"URL for
</pre>

#### `chunk-ba4bd38e729c1ceaecf1593bcedd06c9ef769ecad0a2728e6d14beaf0366f552`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create-milestone`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `milestone`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a milestone.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/milestones#create-a-milestone"},"operationId":"issues/create-milestone","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"Tracking milestone for version 1.0","due_on":"2012-10-09T23:39:01Z","state":"open","title":"v1.0"}}},"schema":{"properties":{"description":{"description":"A description of the milestone.","type":"string"},"due_on":{"description":"The milestone due date. This is a timestamp in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format: `YYYY-MM-DDTHH:MM:SSZ`.","format":"date-time","type":"string"},"state":{"default":"open","description":"The state of the milestone. Either `open` or `closed`.","enum":["open","closed"],"type":"string"},"title":{"description":"The title of the milestone.","type":"string"}},"required":["title"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":
</pre>

#### `chunk-cef3fa3b35babe4f360b341d02e1e163c6426e94fe97d16814d5a4db326db888`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`
- topic matches: `issues/create`, `/issues`
- diagnostic matches: `assignees`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-issue-comment","value":{"description":"Comments provide a way for people to collaborate on an issue.","nullable":true,"properties":{"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"Contents of the issue comment","example":"What version of Safari were you using when you observed this bug?","type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"created_at":{"example":"2011-04-14T16:00:49Z","format":"date-time","type":"string"},"html_url":{"format":"uri","type":"string"},"id":{"description":"Unique identifier of the issue comment","example":42,"format":"int64","type":"integer"},"issue_url":{"format":"uri","type":"string"},"minimized":{"$ref":"#/components/schemas/nullable-issue-comment-minimized"},"node_id":{"type":"string"},"performed_via_github_app":{"$ref":"#/components/schemas/nullable-integration"},"pin":{"$ref":"#/components/schemas/nullable-pinned-issue-comment"},"reactions":{"$ref":"#/components/schemas/reaction-rollup"},"updated_at":{"example":"2011-04-14T16:00:49Z","format":"date-time","type":"string"},"url":{"description":"URL for
</pre>

#### `chunk-01e1a4c8b445326635d01eb4a8e1d4a4f409cec9e75cc6d6648d3b7de8dc4203`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/get`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/full-repository-default-response"},{"path":["value","summary"],"value":"Default response"},{"path":["value","value","allow_auto_merge"],"value":false},{"path":["value","value","allow_forking"],"value":true},{"path":["value","value","allow_merge_commit"],"value":true},{"path":["value","value","allow_rebase_merge"],"value":true},{"path":["value","value","allow_squash_merge"],"value":true},{"path":["value","value","archive_url"],"value":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}"},{"path":["value","value","archived"],"value":false},{"path":["value","value","assignees_url"],"value":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}"},{"path":["value","value","blobs_url"],"value":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}"},{"path":["value","value","branches_url"],"value":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}"},{"path":["value","value","clone_url"],"value":"https://github.com/octocat/Hello-World.git"},{"path":["value","value","collaborators_url"],"value":"https://api.github.com/repos/octocat/Hello-World/collaborators{/colla
</pre>

#### `chunk-03ae34fdd7b0679afa9488de9046d697815f4370129a24d8e59ea7a0d5662b99`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["value","value","parent"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","delete_branch_on_merge":true,"deployments_url":"h
</pre>

#### `chunk-09ac95f73522a07fd46753b2c201e1f6df802c154178ec7f483ca48058d7b99e`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/full-repository"},{"path":["value","value","allow_auto_merge"],"value":false},{"path":["value","value","allow_forking"],"value":true},{"path":["value","value","allow_merge_commit"],"value":true},{"path":["value","value","allow_rebase_merge"],"value":true},{"path":["value","value","allow_squash_merge"],"value":true},{"path":["value","value","archive_url"],"value":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}"},{"path":["value","value","archived"],"value":false},{"path":["value","value","assignees_url"],"value":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}"},{"path":["value","value","blobs_url"],"value":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}"},{"path":["value","value","branches_url"],"value":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}"},{"path":["value","value","clone_url"],"value":"https://github.com/octocat/Hello-World.git"},{"path":["value","value","collaborators_url"],"value":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}"},{"path":["value","value","comments_url"],"value":"https://api.
</pre>

#### `chunk-09ba432523c47ce24c5f7dbf9511a86af57fa918a28656609f80dec02de58f0d`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-simple","value":{"description":"Pull Request Simple","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"assignee":{"$ref":"#/components/schemas/nullable-simple-user"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"auto_merge":{"$ref":"#/components/schemas/auto-merge"},"base":{"properties":{"label":{"type":"string"},"ref":{"type":"string"},"repo":{"$ref":"#/components/schemas/repository"},"sha":{"type":"string"},"user":{"$ref":"#/componen
</pre>

#### `chunk-0abbd7a854918234366253dd1d3ed720e1b0e6694424a28ea7ea69b2af0a73df`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/get-event`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/examples/issue-event","value":{"value":{"actor":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"commit_id":"6dcb09b5b57875f334f61aebed695e2e4193db5e","commit_url":"https://api.github.com/repos/octocat/Hello-World/commits/6dcb09b5b57875f334f61aebed695e2e4193db5e","created_at":"2011-04-14T16:00:49Z","event":"c
</pre>

#### `chunk-0b4362b5c74738930daf7f17fe2a0a80be8221d6a3f5dcb4d91d0fbce778d156`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/get`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["value","value","source"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","delete_branch_on_merge":true,"deployments_url":"h
</pre>

#### `chunk-0b5384c3f2739db2f813d61c28c3617a3827b9f8ace418ea5f90d78da2c26005`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/issue-with-repo-items"},{"path":["value","value",0,"active_lock_reason"],"value":"too heated"},{"path":["value","value",0,"assignee"],"value":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"}},{"path":["value","value",0,"assignees"],"value":[{"avatar_url":"https://github.com/images/error/octocat_happy.gi
</pre>

#### `chunk-0c78f95dae69f0a545240c9a60a47ebe04298e13c4728e4b9319de9a5632a884`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-events-for-repo`
- topic matches: `/issues`
- diagnostic matches: `assignees`, `labels`, `milestone`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/examples/issue-event-items","value":{"value":[{"actor":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"commit_id":"6dcb09b5b57875f334f61aebed695e2e4193db5e","commit_url":"https://api.github.com/repos/octocat/Hello-World/commits/6dcb09b5b57875f334f61aebed695e2e4193db5e","created_at":"2011-04-14T16:00:49Z","ev
</pre>

## `dev-remove-reviewers-422-cause`

- cluster: `openapi-pair:pulls/remove-requested-reviewers`
- role: `evaluation_development_case`
- pattern: `status_cause`
- provisional claim: A 422 response from removing requested reviewers does not by itself establish the exact validation cause.
- total discovered candidates: 64
- candidates outside Phase 4 gold evidence: 57
- automated verdict: `review_required`

### Search terms

- topic: `pulls/remove-requested-reviewers`, `remove requested reviewers`, `requested_reviewers`
- diagnostic: `422`, `validation failed`, `invalid request`

### Highest-ranked candidates (max 25)

#### `chunk-dfd55afaa0a00a80b6074c48a0605b597cb4aabe4060b7d06eb3020d245a0dcb`

- score: `49`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`, `remove requested reviewers`, `requested_reviewers`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"Removes review requests from a pull request for a given set of users and/or teams.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/review-requests#remove-requested-reviewers-from-a-pull-request"},"operationId":"pulls/remove-requested-reviewers","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"reviewers":["octocat","hubot","other_user"],"team_reviewers":["justice-league"]}}},"schema":{"properties":{"reviewers":{"description":"An array of user `login`s that will be removed.","items":{"type":"string"},"type":"array"},"team_reviewers":{"description":"An array of team `slug`s that will be removed.","items":{"type":"string"},"type":"array"}},"required":["reviewers"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request-simple"}},"schema":{"$ref":"#/components/schemas/pull-request-simple"}}},
</pre>

#### `chunk-f9d283e08561bb7d1da3ce9d16ea579e71b25546ce4f648653fee458bf70314a`

- score: `49`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`, `remove requested reviewers`, `requested_reviewers`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"Removes review requests from a pull request for a given set of users and/or teams.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/review-requests#remove-requested-reviewers-from-a-pull-request"},"operationId":"pulls/remove-requested-reviewers","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"reviewers":["octocat","hubot","other_user"],"team_reviewers":["justice-league"]}}},"schema":{"properties":{"reviewers":{"description":"An array of user `login`s that will be removed.","items":{"type":"string"},"type":"array"},"team_reviewers":{"description":"An array of team `slug`s that will be removed.","items":{"type":"string"},"type":"array"}},"required":["reviewers"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request-simple"}},"schema":{"$ref":"#/components/schemas/pull-request-simple"}}},
</pre>

#### `chunk-74f1f93d8305d71a7383663446c672b2e0c01cbd5cecf28318ce9e24433b3bc2`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-aab4129e4bb838cd0c62c3f8927832a3e6b4f6b3004791373d71661b624e5b45`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `requested_reviewers`
- diagnostic matches: `422`

<pre>
- `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue` - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` - `GET /events` - `GET /installation/repositories` - `GET /issues` - `GET /networks/{owner}/{repo}/events` - `GET /notifications` - `GET /notifications/threads/{thread_id}` - `GET /orgs/{org}/actions/permissions/repositories` - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories` - `GET /orgs/{org}/actions/runner-groups/{runner_group_id}/repositories` - `GET /orgs/{org}/actions/secrets/{secret_name}/repositories` - `GET /orgs/{org}/actions/variables/{name}/repositories` - `GET /orgs/{org}/codespaces` - `GET /orgs/{org}/codespaces/secrets/{secret_name}/repositories` - `GET /orgs/{org}/dependabot/secrets/{secret_name}/repositories` - `GET /orgs/{org}/docker/conflicts` - `GET /orgs/{org}/events` - `GET /orgs/{org}/issues` - `GET /orgs/{org}/members/{username}/codespaces` - `GET /orgs/{org}/migrations` - `GET /orgs/{org}/migrations/{migration_id}` - `GET /orgs/{org}/migrations/{mi
</pre>

#### `chunk-b2bc4ff09e8a4d33ded81556b6e442081bb05dfb99780a4f904024be5a0e77ff`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-d878c26fa45d4c05350e5a5fd3f08deeb3c6251129889118dac3eac6215f9ef0`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/request-reviewers`
- topic matches: `requested_reviewers`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Requests reviews for a pull request from a given set of users and/or teams.\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\" and \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/review-requests#request-reviewers-for-a-pull-request"},"operationId":"pulls/request-reviewers","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"reviewers":["octocat","hubot","other_user"],"team_reviewers":["justice-league"]}}},"schema":{"anyOf":[{"require
</pre>

#### `chunk-09ba432523c47ce24c5f7dbf9511a86af57fa918a28656609f80dec02de58f0d`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`, `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-simple","value":{"description":"Pull Request Simple","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"assignee":{"$ref":"#/components/schemas/nullable-simple-user"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"auto_merge":{"$ref":"#/components/schemas/auto-merge"},"base":{"properties":{"label":{"type":"string"},"ref":{"type":"string"},"repo":{"$ref":"#/components/schemas/repository"},"sha":{"type":"string"},"user":{"$ref":"#/componen
</pre>

#### `chunk-0f9af6624192933c7ec027ab9d676761ad7ba4dd2395cf7040c52cc48ea16461`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`, `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["value","value","milestone"],"value":{"closed_at":"2013-02-12T13:22:01Z","closed_issues":8,"created_at":"2011-04-10T20:09:31Z","creator":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"description":"Tracking milestone for version 1.0","due_on":"2012-10-09T23:39:01Z","html_url":"https://github.com/octocat/Hello-World/milestones/v1.0","id":100260
</pre>

#### `chunk-ceb95ec3cfc0fa19fdbb9536aef32a7c807e73c150ba6e2209a8c4db079bd6d6`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`, `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-simple","value":{"description":"Pull Request Simple","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"auto_merge":{"$ref":"#/components/schemas/auto-merge"},"base":{"properties":{"label":{"type":"string"},"ref":{"type":"string"},"repo":{"$ref":"#/components/schemas/repository"},"sha":{"type":"string"},"user":{"$ref":"#/components/schemas/nullable-simple-user"}},"required":["label","ref","re
</pre>

#### `chunk-d838799eccf2375270cb36034353cafdf1f34d3efca726c5e90fe51ef4f48bd8`

- score: `20`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`, `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["value","value","milestone"],"value":{"closed_at":"2013-02-12T13:22:01Z","closed_issues":8,"created_at":"2011-04-10T20:09:31Z","creator":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"description":"Tracking milestone for version 1.0","due_on":"2012-10-09T23:39:01Z","html_url":"https://github.com/octocat/Hello-World/milestones/v1.0","id":100260
</pre>

#### `chunk-8dd06f9776710075a0304ff05e06d9c104a0eea6e99e20b7be4e1ac5187d4f27`

- score: `12`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-troubleshooting`
- topic matches: `none`
- diagnostic matches: `422`, `validation failed`, `invalid request`

<pre>
## Missing results Most endpoints that return a list of resources support pagination. For most of these endpoints, only the first 30 resources are returned by default. In order to see all of the resources, you need to paginate through the results. For more information, see [/rest/using-the-rest-api/using-pagination-in-the-rest-api](/rest/using-the-rest-api/using-pagination-in-the-rest-api). If you are using pagination correctly and still do not see all of the results that you expect, you should confirm that the authentication credentials that you used have access to all of the expected resources. For example, if you are using a GitHub App installation access token, if the installation was only granted access to a subset of repositories in an organization, any request for all repositories in that organization will return only the repositories that the app installation can access. ## Requires authentication when using basic authentication Basic authentication with your username and password is not supported. Instead, you should use a personal access token or an access token for a GitHub App or OAuth app. For more information, see [/rest/authentication/authenticating-to-the-rest-api](
</pre>

#### `chunk-012e2b07475393a6a87427d13bf80f0b111cfb4e5108009302da1fd2fa3363b0`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-team-simple","value":{"description":"Groups of organization members that gives permissions on specified repositories.","nullable":true,"properties":{"description":{"description":"Description of the team","example":"A great team.","nullable":true,"type":"string"},"enterprise_id":{"description":"Unique identifier of the enterprise to which this team belongs","example":42,"type":"integer"},"html_url":{"example":"https://github.com/orgs/rails/teams/core","format":"uri","type":"string"},"id":{"description":"Unique identifier of the team","example":1,"type":"integer"},"ldap_dn":{"description":"Distinguished Name (DN) that team maps to within LDAP environment","example":"uid=example,ou=users,dc=github,dc=com","type":"string"},"members_url":{"example":"https://api.github.com/organizations/1/team/1/members{/member}","type":"string"},"name":{"description":"Name of the team","example":"Justice League","type":"string"},"node_id":{"example":"MDQ6VGVhbTE=","type":"string"},"notification_setting":{"description":"The notification setting the team has set","example":"notifications_enabled","type":"string"},"organization_id
</pre>

#### `chunk-07888ee72666d7f189d02f1a04e67f358ad0b8bb9abd0ea2ea6da06f12002805`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/pull-request-simple"},{"path":["value","value","_links"],"value":{"comments":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"},"commits":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits"},"html":{"href":"https://github.com/octocat/Hello-World/pull/1347"},"issue":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347"},"review_comment":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}"},"review_comments":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments"},"self":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347"},"statuses":{"href":"https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e"}}},{"path":["value","value","active_lock_reason"],"value":"too heated"},{"path":["value","value","assignee"],"value":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://
</pre>

#### `chunk-099035e853588f6d8e3d3e13466602b62f7366fe77f3f99d48f8a53c0fd435ce`

- score: `10`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `requested_reviewers`
- diagnostic matches: `none`

<pre>
## Version 2026-03-10 - **Remove deprecated `rate` property from rate limit endpoint** The `rate` property has been deprecated since 2021 and duplicates information available in the `resources.core` property. To migrate, update your integration to read rate limit information from `resources.core` instead of `rate`. See https://docs.github.com/rest/rate-limit for updated documentation. &lt;details&gt; &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt; - `GET /rate_limit` &lt;/details&gt; - **Remove deprecated `permission` property from request when a team is created** &lt;details&gt; &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt; - `POST /orgs/{org}/teams` &lt;/details&gt; - **Updates the "Get repository content" API, so that, when listing the contents of a directory, submodules have the `type` "submodule" instead of the `type` "file"** &lt;details&gt; &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt; - `GET /repos/{owner}/{repo}/contents/{path}` &lt;/details&gt; - **Change Content-Type of SARIF response** When trying to receive the SARIF upload by setting the `Accept` header to `application/sarif+json` the response `Content-Type` would incorrectly be set to `application/json+sarif`. This change corre
</pre>

#### `chunk-0fb8f7cec6b12687d9ca57a3028edfc64d2e9527be0ea74b8314c5f49553eb44`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-license-simple","value":{"description":"License Simple","nullable":true,"properties":{"html_url":{"format":"uri","type":"string"},"key":{"example":"mit","type":"string"},"name":{"example":"MIT License","type":"string"},"node_id":{"example":"MDc6TGljZW5zZW1pdA==","type":"string"},"spdx_id":{"example":"MIT","nullable":true,"type":"string"},"url":{"example":"https://api.github.com/licenses/mit","format":"uri","nullable":true,"type":"string"}},"required":["key","name","url","spdx_id","node_id"],"title":"License Simple","type":"object"}}}]}
</pre>

#### `chunk-17edde83c545913ec5e5e340594689c4f03d9457e9df3404c718aa2e3b01ab3f`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-187b39a35571e4bb69c19fcddbed5557b102f09ae87bb9bd08139ccb91c50675`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["value","value","milestone"],"value":{"closed_at":"2013-02-12T13:22:01Z","closed_issues":8,"created_at":"2011-04-10T20:09:31Z","creator":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"description":"Tracking milestone for version 1.0","due_on":"2012-10-09T23:39:01Z","html_url":"https://github.com/octocat/Hello-World/milestones/v1.0","id":100260
</pre>

#### `chunk-1ab9c465d5c4852a0d12f1a61a125ef0851163c86736210ba87188fe8442d643`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/request-reviewers`, `openapi-current-2026-03-10:repos/list-pull-requests-associated-with-commit`
- topic matches: `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-simple","value":{"description":"Pull Request Simple","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"auto_merge":{"$ref":"#/components/schemas/auto-merge"},"base":{"properties":{"label":{"type":"string"},"ref":{"type":"string"},"repo":{"$ref":"#/components/schemas/repository"},"sha":{"type":"string"},"user":{"$ref":"#/components/schemas/nullable-simple-user"}},"required":["label","ref","re
</pre>

#### `chunk-1c3c998887b2de813f5993089d5dd4b43f2627f93632626fccb793611803d873`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/validation-error","value":{"description":"Validation Error","properties":{"documentation_url":{"type":"string"},"errors":{"items":{"properties":{"code":{"type":"string"},"field":{"type":"string"},"index":{"type":"integer"},"message":{"type":"string"},"resource":{"type":"string"},"value":{"oneOf":[{"nullable":true,"type":"string"},{"nullable":true,"type":"integer"},{"items":{"type":"string"},"nullable":true,"type":"array"}]}},"required":["code"],"type":"object"},"type":"array"},"message":{"type":"string"}},"required":["message","documentation_url"],"title":"Validation Error","type":"object"}}}]}
</pre>

#### `chunk-20e6d65f58412d5ff8d152ca4cdecd24734513599159d11a178371d59f8c96f0`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-21459555b5559a85fb8dd65e99e0c85210139a88e7b13c63d5157f32965d28e0`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/pull-request-simple"},{"path":["value","value","_links"],"value":{"comments":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"},"commits":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits"},"html":{"href":"https://github.com/octocat/Hello-World/pull/1347"},"issue":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347"},"review_comment":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}"},"review_comments":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments"},"self":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347"},"statuses":{"href":"https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e"}}},{"path":["value","value","active_lock_reason"],"value":"too heated"},{"path":["value","value","assignees"],"value":[{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https:
</pre>

#### `chunk-2def5cb713729f41143b8fd1ad8790eef2b416595be1165bcde4c58579f643bc`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-milestone","value":{"description":"A collection of related issues and pull requests.","nullable":true,"properties":{"closed_at":{"example":"2013-02-12T13:22:01Z","format":"date-time","nullable":true,"type":"string"},"closed_issues":{"example":8,"type":"integer"},"created_at":{"example":"2011-04-10T20:09:31Z","format":"date-time","type":"string"},"creator":{"$ref":"#/components/schemas/nullable-simple-user"},"description":{"example":"Tracking milestone for version 1.0","nullable":true,"type":"string"},"due_on":{"example":"2012-10-09T23:39:01Z","format":"date-time","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat/Hello-World/milestones/v1.0","format":"uri","type":"string"},"id":{"example":1002604,"type":"integer"},"labels_url":{"example":"https://api.github.com/repos/octocat/Hello-World/milestones/1/labels","format":"uri","type":"string"},"node_id":{"example":"MDk6TWlsZXN0b25lMTAwMjYwNA==","type":"string"},"number":{"description":"The number of the milestone.","example":42,"type":"integer"},"open_issues":{"example":4,"type":"integer"},"state":{"default":"open","description":
</pre>

#### `chunk-2e834b5e16aad77c21e3ed6f71700063bde8caf8323258751f8433423ca35ed2`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/link","value":{"description":"Hypermedia Link","properties":{"href":{"type":"string"}},"required":["href"],"title":"Link","type":"object"}}}]}
</pre>

#### `chunk-40ee8ff29e25fced7475002e643809ad9d032e2a674444f33e005ddb5751dc42`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `requested_reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request","value":{"description":"Pull requests let you tell others about changes you've pushed to a repository on GitHub. Once a pull request is sent, interested parties can review the set of changes, discuss potential modifications, and even push follow-up commits if necessary.","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"additions":{"example":100,"type":"integer"},"assignee":{"$ref":"#/components/schemas/nullable-simple-user"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/com
</pre>

#### `chunk-44541bac2a96ccc6a4f22f9b9818271fe4c7a3e51ffb45aa0a8f40afea67f868`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- topic matches: `pulls/remove-requested-reviewers`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["value","value","head"],"value":{"label":"octocat:new-topic","ref":"new-topic","repo":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master
</pre>

## `tuning-get-pull-mergeable-null`

- cluster: `openapi-pair:pulls/get`
- role: `intervention_tuning_case`
- pattern: `pending_state_unknown`
- provisional claim: mergeable=null does not establish whether the pull request is mergeable because computation may still be pending.
- total discovered candidates: 74
- candidates outside Phase 4 gold evidence: 72
- automated verdict: `review_required`

### Search terms

- topic: `pulls/get`, `get a pull request`, `mergeable`
- diagnostic: `background job`, `mergeability`, `resubmit`, `null`

### Highest-ranked candidates (max 25)

#### `chunk-ded348a713590dacd422877d3fd903bf33666202b0b1128840cad1d1971792cd`

- score: `61`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/get`
- topic matches: `pulls/get`, `get a pull request`, `mergeable`
- diagnostic matches: `background job`, `mergeability`, `resubmit`, `null`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nLists details of a pull request by providing its number.\n\nWhen you get, [create](https://docs.github.com/rest/pulls/pulls/#create-a-pull-request), or [edit](https://docs.github.com/rest/pulls/pulls#update-a-pull-request) a pull request, GitHub creates a merge commit to test whether the pull request can be automatically merged into the base branch. This test commit is not added to the base branch or the head branch. You can review the status of the test commit using the `mergeable` key. For more information, see \"[Checking mergeability of pull requests](https://docs.github.com/rest/guides/getting-started-with-the-git-database-api#checking-mergeability-of-pull-requests)\".\n\nThe value of the `mergeable` a
</pre>

#### `chunk-f195cc3e0ba24c3ae8273d49e92e001fac39dcfd9fa3a7eafad7a7f95ff85781`

- score: `61`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/get`
- topic matches: `pulls/get`, `get a pull request`, `mergeable`
- diagnostic matches: `background job`, `mergeability`, `resubmit`, `null`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nLists details of a pull request by providing its number.\n\nWhen you get, [create](https://docs.github.com/rest/pulls/pulls/#create-a-pull-request), or [edit](https://docs.github.com/rest/pulls/pulls#update-a-pull-request) a pull request, GitHub creates a merge commit to test whether the pull request can be automatically merged into the base branch. This test commit is not added to the base branch or the head branch. You can review the status of the test commit using the `mergeable` key. For more information, see \"[Checking mergeability of pull requests](https://docs.github.com/rest/guides/getting-started-with-the-git-database-api#checking-mergeability-of-pull-requests)\".\n\nThe value of the `mergeable` a
</pre>

#### `chunk-40ee8ff29e25fced7475002e643809ad9d032e2a674444f33e005ddb5751dc42`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/get`, `mergeable`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request","value":{"description":"Pull requests let you tell others about changes you've pushed to a repository on GitHub. Once a pull request is sent, interested parties can review the set of changes, discuss potential modifications, and even push follow-up commits if necessary.","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"additions":{"example":100,"type":"integer"},"assignee":{"$ref":"#/components/schemas/nullable-simple-user"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/com
</pre>

#### `chunk-870b771f0c7cb0063e41a23191f090a018056eb5f4f6572007f8c2a49d39c6b1`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`, `mergeable`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["value","value","head"],"value":{"label":"octocat:new-topic","ref":"new-topic","repo":{"allow_forking":true,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","d
</pre>

#### `chunk-88cda7173ad99d3ea7a77113101d8757a82dfb41b7f018b2ae6abb3dfb930077`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/get`, `mergeable`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["value","value","head"],"value":{"label":"octocat:new-topic","ref":"new-topic","repo":{"allow_forking":true,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","d
</pre>

#### `chunk-8cf83808551b3de25053ffb111ca1c1f15648f5c1615877403a089259c70ea1a`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`, `mergeable`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request","value":{"description":"Pull requests let you tell others about changes you've pushed to a repository on GitHub. Once a pull request is sent, interested parties can review the set of changes, discuss potential modifications, and even push follow-up commits if necessary.","properties":{"_links":{"properties":{"comments":{"$ref":"#/components/schemas/link"},"commits":{"$ref":"#/components/schemas/link"},"html":{"$ref":"#/components/schemas/link"},"issue":{"$ref":"#/components/schemas/link"},"review_comment":{"$ref":"#/components/schemas/link"},"review_comments":{"$ref":"#/components/schemas/link"},"self":{"$ref":"#/components/schemas/link"},"statuses":{"$ref":"#/components/schemas/link"}},"required":["comments","commits","statuses","html","issue","review_comments","review_comment","self"],"type":"object"},"active_lock_reason":{"example":"too heated","nullable":true,"type":"string"},"additions":{"example":100,"type":"integer"},"assignees":{"items":{"$ref":"#/components/schemas/simple-user"},"type":"array"},"author_association":{"$ref":"#/components/schemas/author-association"},"auto_merge":{"$ref":"#/com
</pre>

#### `chunk-0fb8f7cec6b12687d9ca57a3028edfc64d2e9527be0ea74b8314c5f49553eb44`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-license-simple","value":{"description":"License Simple","nullable":true,"properties":{"html_url":{"format":"uri","type":"string"},"key":{"example":"mit","type":"string"},"name":{"example":"MIT License","type":"string"},"node_id":{"example":"MDc6TGljZW5zZW1pdA==","type":"string"},"spdx_id":{"example":"MIT","nullable":true,"type":"string"},"url":{"example":"https://api.github.com/licenses/mit","format":"uri","nullable":true,"type":"string"}},"required":["key","name","url","spdx_id","node_id"],"title":"License Simple","type":"object"}}}]}
</pre>

#### `chunk-17edde83c545913ec5e5e340594689c4f03d9457e9df3404c718aa2e3b01ab3f`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-20e6d65f58412d5ff8d152ca4cdecd24734513599159d11a178371d59f8c96f0`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-2def5cb713729f41143b8fd1ad8790eef2b416595be1165bcde4c58579f643bc`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-milestone","value":{"description":"A collection of related issues and pull requests.","nullable":true,"properties":{"closed_at":{"example":"2013-02-12T13:22:01Z","format":"date-time","nullable":true,"type":"string"},"closed_issues":{"example":8,"type":"integer"},"created_at":{"example":"2011-04-10T20:09:31Z","format":"date-time","type":"string"},"creator":{"$ref":"#/components/schemas/nullable-simple-user"},"description":{"example":"Tracking milestone for version 1.0","nullable":true,"type":"string"},"due_on":{"example":"2012-10-09T23:39:01Z","format":"date-time","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat/Hello-World/milestones/v1.0","format":"uri","type":"string"},"id":{"example":1002604,"type":"integer"},"labels_url":{"example":"https://api.github.com/repos/octocat/Hello-World/milestones/1/labels","format":"uri","type":"string"},"node_id":{"example":"MDk6TWlsZXN0b25lMTAwMjYwNA==","type":"string"},"number":{"description":"The number of the milestone.","example":42,"type":"integer"},"open_issues":{"example":4,"type":"integer"},"state":{"default":"open","description":
</pre>

#### `chunk-344e5831dc73d11d077a437c51bfa1b5e8fd80324fb320a719078e865076524b`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["value","value","base"],"value":{"label":"octocat:master","ref":"master","repo":{"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","deployments_url":"https://ap
</pre>

#### `chunk-3601b6755598b081f3fac60e651e2e01ea112cf94f326c5c3c9713c4e71a2003`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/review-pending-deployments-for-run`, `openapi-current-2026-03-10:issues/create-comment`, `openapi-current-2026-03-10:issues/create-milestone`, `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-comment`, `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/get-milestone`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-comments`, `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-milestones`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/pin-comment`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:issues/update-comment`, `openapi-current-2026-03-10:issues/update-milestone`, `openapi-current-2026-03-10:pulls/create-reply-for-review-comment`, `openapi-current-2026-03-10:pulls/create-review`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/delete-pending-review`, `openapi-current-2026-03-10:pulls/dismiss-review`, `openapi-current-2026-03-10:pulls/get-review`, `openapi-current-2026-03-10:pulls/get-review-comment`, `openapi-current-2026-03-10:pulls/list-comments-for-review`, `openapi-current-2026-03-10:pulls/list-review-comments`, `openapi-current-2026-03-10:pulls/list-review-comments-for-repo`, `openapi-current-2026-03-10:pulls/list-reviews`, `openapi-current-2026-03-10:pulls/request-reviewers`, `openapi-current-2026-03-10:pulls/submit-review`, `openapi-current-2026-03-10:pulls/update-review`, `openapi-current-2026-03-10:pulls/update-review-comment`, `openapi-current-2026-03-10:repos/add-collaborator`, `openapi-current-2026-03-10:repos/create-commit-comment`, `openapi-current-2026-03-10:repos/create-commit-status`, `openapi-current-2026-03-10:repos/create-deployment`, `openapi-current-2026-03-10:repos/create-deployment-status`, `openapi-current-2026-03-10:repos/create-fork`, `openapi-current-2026-03-10:repos/create-release`, `openapi-current-2026-03-10:repos/create-using-template`, `openapi-current-2026-03-10:repos/get`, `openapi-current-2026-03-10:repos/get-commit-comment`, `openapi-current-2026-03-10:repos/get-contributors-stats`, `openapi-current-2026-03-10:repos/get-deployment`, `openapi-current-2026-03-10:repos/get-deployment-status`, `openapi-current-2026-03-10:repos/get-latest-pages-build`, `openapi-current-2026-03-10:repos/get-latest-release`, `openapi-current-2026-03-10:repos/get-pages-build`, `openapi-current-2026-03-10:repos/get-release`, `openapi-current-2026-03-10:repos/get-release-asset`, `openapi-current-2026-03-10:repos/get-release-by-tag`, `openapi-current-2026-03-10:repos/list-activities`, `openapi-current-2026-03-10:repos/list-comments-for-commit`, `openapi-current-2026-03-10:repos/list-commit-comments-for-repo`, `openapi-current-2026-03-10:repos/list-commit-statuses-for-ref`, `openapi-current-2026-03-10:repos/list-deployment-statuses`, `openapi-current-2026-03-10:repos/list-deployments`, `openapi-current-2026-03-10:repos/list-invitations`, `openapi-current-2026-03-10:repos/list-invitations-for-authenticated-user`, `openapi-current-2026-03-10:repos/list-pages-builds`, `openapi-current-2026-03-10:repos/list-pull-requests-associated-with-commit`, `openapi-current-2026-03-10:repos/list-release-assets`, `openapi-current-2026-03-10:repos/list-releases`, `openapi-current-2026-03-10:repos/update`, `openapi-current-2026-03-10:repos/update-commit-comment`, `openapi-current-2026-03-10:repos/update-invitation`, `openapi-current-2026-03-10:repos/update-release`, `openapi-current-2026-03-10:repos/update-release-asset`, `openapi-current-2026-03-10:repos/upload-release-asset`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-simple-user","value":{"description":"A GitHub user.","nullable":true,"properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"receive
</pre>

#### `chunk-460b3544c092ec69fbca59e2948c7cbadfface19fc655b242977d15f0836be89`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/auto-merge","value":{"description":"The status of auto merging a pull request.","nullable":true,"properties":{"commit_message":{"description":"Commit message for the merge commit.","type":"string"},"commit_title":{"description":"Title for the merge commit message.","type":"string"},"enabled_by":{"$ref":"#/components/schemas/simple-user"},"merge_method":{"description":"The merge method to use.","enum":["merge","squash","rebase"],"type":"string"}},"required":["enabled_by","merge_method","commit_title","commit_message"],"title":"Auto merge","type":"object"}}}]}
</pre>

#### `chunk-4de76ccd2002dc08909896184f182ca4367d5e82a763a569b7eaea6d7d319b5d`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-simple-user","value":{"description":"A GitHub user.","nullable":true,"properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"receive
</pre>

#### `chunk-5135c4f505924cb4ab197421ca531e90441791d5f06fab915f21f366deea2f8a`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/team-simple","value":{"description":"Groups of organization members that gives permissions on specified repositories.","properties":{"description":{"description":"Description of the team","example":"A great team.","nullable":true,"type":"string"},"enterprise_id":{"description":"Unique identifier of the enterprise to which this team belongs","example":42,"type":"integer"},"html_url":{"example":"https://github.com/orgs/rails/teams/core","format":"uri","type":"string"},"id":{"description":"Unique identifier of the team","example":1,"type":"integer"},"ldap_dn":{"description":"Distinguished Name (DN) that team maps to within LDAP environment","example":"uid=example,ou=users,dc=github,dc=com","type":"string"},"members_url":{"example":"https://api.github.com/organizations/1/team/1/members{/member}","type":"string"},"name":{"description":"Name of the team","example":"Justice League","type":"string"},"node_id":{"example":"MDQ6VGVhbTE=","type":"string"},"notification_setting":{"description":"The notification setting the team has set","example":"notifications_enabled","type":"string"},"organization_id":{"description":"Unique
</pre>

#### `chunk-67f3339e54c53b9465795a373b7e7822bf47e11cf6ff344cd1e75d267a7b40ee`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-simple-user","value":{"description":"A GitHub user.","nullable":true,"properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"receive
</pre>

#### `chunk-71b86a248a18bb29c59034208e5d3961ccc145584374695672a0857e460d478b`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/pull-request"},{"path":["value","value","_links"],"value":{"comments":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"},"commits":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits"},"html":{"href":"https://github.com/octocat/Hello-World/pull/1347"},"issue":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347"},"review_comment":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}"},"review_comments":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments"},"self":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347"},"statuses":{"href":"https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e"}}},{"path":["value","value","active_lock_reason"],"value":"too heated"},{"path":["value","value","additions"],"value":100},{"path":["value","value","assignees"],"value":[{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/user
</pre>

#### `chunk-7b45e6e1fc59a711453321dc17482be8547958854e63b9e4a25911bddc5313cc`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-milestone","value":{"description":"A collection of related issues and pull requests.","nullable":true,"properties":{"closed_at":{"example":"2013-02-12T13:22:01Z","format":"date-time","nullable":true,"type":"string"},"closed_issues":{"example":8,"type":"integer"},"created_at":{"example":"2011-04-10T20:09:31Z","format":"date-time","type":"string"},"creator":{"$ref":"#/components/schemas/nullable-simple-user"},"description":{"example":"Tracking milestone for version 1.0","nullable":true,"type":"string"},"due_on":{"example":"2012-10-09T23:39:01Z","format":"date-time","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat/Hello-World/milestones/v1.0","format":"uri","type":"string"},"id":{"example":1002604,"type":"integer"},"labels_url":{"example":"https://api.github.com/repos/octocat/Hello-World/milestones/1/labels","format":"uri","type":"string"},"node_id":{"example":"MDk6TWlsZXN0b25lMTAwMjYwNA==","type":"string"},"number":{"description":"The number of the milestone.","example":42,"type":"integer"},"open_issues":{"example":4,"type":"integer"},"state":{"default":"open","description":
</pre>

#### `chunk-7d6ce3823f46bf727106324b04990ca782c48ec3e489734807f2269f82e6f000`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["value","properties","labels_url"],"value":{"example":"http://api.github.com/repos/octocat/Hello-World/labels{/name}","type":"string"}},{"path":["value","properties","language"],"value":{"nullable":true,"type":"string"}},{"path":["value","properties","languages_url"],"value":{"example":"http://api.github.com/repos/octocat/Hello-World/languages","format":"uri","type":"string"}},{"path":["value","properties","license"],"value":{"$ref":"#/components/schemas/nullable-license-simple"}},{"path":["value","properties","master_branch"],"value":{"type":"string"}},{"path":["value","properties","merge_commit_message"],"value":{"description":"The default value for a merge commit message.\n\n- `PR_TITLE` - default to the pull request's title.\n- `PR_BODY` - default to the pull request's body.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","PR_TITLE","BLANK"],"type":"string"}},{"path":["value","properties","merge_commit_title"],"value":{"description":"The default value for a merge commit title.\n\n- `PR_TITLE` - default to the pull request's title.\n- `MERGE_MESSAGE` - default to the classic title for a merge message (e.g., Merge pull request #123 from b
</pre>

#### `chunk-826929a7a8f6a94de734a888120cdc25cde062d3c244ec33f6cbfd17031dd86f`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["value","value","base"],"value":{"label":"octocat:master","ref":"master","repo":{"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","deployments_url":"https://ap
</pre>

#### `chunk-a28e9f64481e7ccb8541a6ab67f2c6119f53da5365a01c4574a624346b4fc746`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/team-simple","value":{"description":"Groups of organization members that gives permissions on specified repositories.","properties":{"description":{"description":"Description of the team","example":"A great team.","nullable":true,"type":"string"},"enterprise_id":{"description":"Unique identifier of the enterprise to which this team belongs","example":42,"type":"integer"},"html_url":{"example":"https://github.com/orgs/rails/teams/core","format":"uri","type":"string"},"id":{"description":"Unique identifier of the team","example":1,"type":"integer"},"ldap_dn":{"description":"Distinguished Name (DN) that team maps to within LDAP environment","example":"uid=example,ou=users,dc=github,dc=com","type":"string"},"members_url":{"example":"https://api.github.com/organizations/1/team/1/members{/member}","type":"string"},"name":{"description":"Name of the team","example":"Justice League","type":"string"},"node_id":{"example":"MDQ6VGVhbTE=","type":"string"},"notification_setting":{"description":"The notification setting the team has set","example":"notifications_enabled","type":"string"},"organization_id":{"description":"Unique
</pre>

#### `chunk-a9321afb0f2f76d21ae52438f938896b2a18d9a74cd44da644ae24b8540cd237`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/pull-request"},{"path":["value","value","_links"],"value":{"comments":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"},"commits":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits"},"html":{"href":"https://github.com/octocat/Hello-World/pull/1347"},"issue":{"href":"https://api.github.com/repos/octocat/Hello-World/issues/1347"},"review_comment":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/comments{/number}"},"review_comments":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347/comments"},"self":{"href":"https://api.github.com/repos/octocat/Hello-World/pulls/1347"},"statuses":{"href":"https://api.github.com/repos/octocat/Hello-World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e"}}},{"path":["value","value","active_lock_reason"],"value":"too heated"},{"path":["value","value","additions"],"value":100},{"path":["value","value","assignee"],"value":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/
</pre>

#### `chunk-b1cce45b75c2dda126bc489e266406517a20285f65da1c9ef6ca4cea2b292562`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create-review`, `openapi-current-2026-03-10:pulls/delete-pending-review`, `openapi-current-2026-03-10:pulls/dismiss-review`, `openapi-current-2026-03-10:pulls/get-review`, `openapi-current-2026-03-10:pulls/list-reviews`, `openapi-current-2026-03-10:pulls/submit-review`, `openapi-current-2026-03-10:pulls/update-review`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-review","value":{"description":"Pull Request Reviews are reviews on pull requests.","properties":{"_links":{"properties":{"html":{"properties":{"href":{"type":"string"}},"required":["href"],"type":"object"},"pull_request":{"properties":{"href":{"type":"string"}},"required":["href"],"type":"object"}},"required":["html","pull_request"],"type":"object"},"author_association":{"$ref":"#/components/schemas/author-association"},"body":{"description":"The text of the review.","example":"This looks great.","type":"string"},"body_html":{"type":"string"},"body_text":{"type":"string"},"commit_id":{"description":"A commit SHA for the review. If the commit object was garbage collected or forcibly deleted, then it no longer exists in Git and this value will be `null`.","example":"54bb654c9e6025347f57900a4a5c2313a96b8035","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat/Hello-World/pull/12#pullrequestreview-80","format":"uri","type":"string"},"id":{"description":"Unique identifier of the review","example":42,"format":"int64","type":"integer"},"node_id":{"example":"MDE3OlB1bGxSZXF1ZXN0
</pre>

#### `chunk-b58f00f5e16b6bdab9f9547aeab1ae39c6399a044ae9f6efc25250caccd43f23`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/pull-request-stack","value":{"description":"The stack information associated with a pull request.","nullable":true,"properties":{"base":{"properties":{"ref":{"description":"The base ref of the stack this pull request belongs to.","type":"string"},"sha":{"description":"The base SHA of the stack this pull request belongs to.","type":"string"}},"required":["ref","sha"],"type":"object"},"id":{"description":"The ID of the stack that this pull request belongs to.","type":"integer"},"number":{"description":"The number of the stack that this pull request belongs to.","type":"integer"},"position":{"description":"The one-based position of this pull request within the stack, where 1 is the bottom of the stack.","type":"integer"},"size":{"description":"The total number of pull requests in the stack.","type":"integer"}},"required":["base"],"title":"Pull Request Stack","type":"object"}}}]}
</pre>

#### `chunk-b6ab5f19af6bce05f8dd21f0c39090ea00a5098315eb6018f81776be705ee8c9`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/get`
- diagnostic matches: `null`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-license-simple","value":{"description":"License Simple","nullable":true,"properties":{"html_url":{"format":"uri","type":"string"},"key":{"example":"mit","type":"string"},"name":{"example":"MIT License","type":"string"},"node_id":{"example":"MDc6TGljZW5zZW1pdA==","type":"string"},"spdx_id":{"example":"MIT","nullable":true,"type":"string"},"url":{"example":"https://api.github.com/licenses/mit","format":"uri","nullable":true,"type":"string"}},"required":["key","name","url","spdx_id","node_id"],"title":"License Simple","type":"object"}}}]}
</pre>

## `tuning-update-pull-422-cause`

- cluster: `openapi-pair:pulls/update`
- role: `intervention_tuning_case`
- pattern: `status_cause`
- provisional claim: A 422 response from updating a pull request does not by itself establish the exact validation cause.
- total discovered candidates: 74
- candidates outside Phase 4 gold evidence: 69
- automated verdict: `review_required`

### Search terms

- topic: `pulls/update`, `update a pull request`
- diagnostic: `422`, `validation failed`, `invalid request`

### Highest-ranked candidates (max 25)

#### `chunk-39b03b894e1f89fc54ff1bcdd8fa4d9173d2c040436a2ae1f2daa1ecf7449406`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/update`, `update a pull request`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markd
</pre>

#### `chunk-3b49054d748e4cfbf79ad140015fe2c6d73db66c9185f434fbced3a37c84d285`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/update`, `update a pull request`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markd
</pre>

#### `chunk-9ded1e1dc9da4f59e8800fe3565472c3e8dd55ce0c56869ee91cf49c32ebbc5a`

- score: `39`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/update-branch`
- topic matches: `pulls/update`, `update a pull request`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Updates the pull request branch with the latest upstream changes by merging HEAD from the base branch into the pull request branch.\nNote: If making a request on behalf of a GitHub App you must also have permissions to write the contents of the head repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#update-a-pull-request-branch"},"operationId":"pulls/update-branch","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"expected_head_sha":"6dcb09b5b57875f334f61aebed695e2e4193db5e"}}},"schema":{"nullable":true,"properties":{"expected_head_sha":{"description":"The expected SHA of the pull request's HEAD ref. This is the most recent commit on the pull request's branch. If the expected SHA does not match the pull request's HEAD, you will receive a `422 Unprocessable Entity` status. You can use the \"[List commits](https://docs.github.com/rest/commits/commits#list-commits)\" endpoin
</pre>

#### `chunk-2601e2eee7b80d49c71037f08955a31b13928438ccccc8ab133b7bd729d05f8e`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/add-custom-labels-to-self-hosted-runner-for-org`, `openapi-current-2026-03-10:actions/add-custom-labels-to-self-hosted-runner-for-repo`, `openapi-current-2026-03-10:actions/delete-self-hosted-runner-from-org`, `openapi-current-2026-03-10:actions/delete-self-hosted-runner-from-repo`, `openapi-current-2026-03-10:actions/generate-runner-jitconfig-for-org`, `openapi-current-2026-03-10:actions/generate-runner-jitconfig-for-repo`, `openapi-current-2026-03-10:actions/remove-custom-label-from-self-hosted-runner-for-org`, `openapi-current-2026-03-10:actions/remove-custom-label-from-self-hosted-runner-for-repo`, `openapi-current-2026-03-10:actions/set-custom-labels-for-self-hosted-runner-for-org`, `openapi-current-2026-03-10:actions/set-custom-labels-for-self-hosted-runner-for-repo`, `openapi-current-2026-03-10:actions/set-custom-oidc-sub-claim-for-repo`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:pulls/create-review`, `openapi-current-2026-03-10:pulls/delete-pending-review`, `openapi-current-2026-03-10:pulls/dismiss-review`, `openapi-current-2026-03-10:pulls/submit-review`, `openapi-current-2026-03-10:pulls/update-review`, `openapi-current-2026-03-10:repos/delete-deployment`, `openapi-current-2026-03-10:repos/list-activities`, `openapi-current-2026-03-10:repos/replace-all-topics`, `openapi-current-2026-03-10:repos/update-branch-protection`
- topic matches: `pulls/update`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed_simple","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error-simple"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-369285132391ff80887ae5f629cdc3f8e51353126ac8a4fd8df22b4d1a86bb24`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/update-review`
- topic matches: `pulls/update`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Updates the contents of a specified review summary comment.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github-commitcomment.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github-commitcomment.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github-commitcomment.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/reviews#update-a-review-for-a-pull-request"},"operationId":"pulls/update-review","parameters":[{"$ref":"#/components/parameters/o
</pre>

#### `chunk-42d7b7bbff67f5e75d5363b820cd6182d79785cad570a499b58e253942474944`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`
- topic matches: `update a pull request`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\" and \"[Best practices for using the REST API](https://docs.githu
</pre>

#### `chunk-74f1f93d8305d71a7383663446c672b2e0c01cbd5cecf28318ce9e24433b3bc2`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/update`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-779dd47fb0b30ba0e7b4fbdfbdccc3516c88e19aad9f170f4d26f37079997105`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/disable-selected-repository-self-hosted-runners-organization`, `openapi-current-2026-03-10:actions/enable-selected-repository-self-hosted-runners-organization`, `openapi-current-2026-03-10:actions/get-concurrency-group-for-repository`, `openapi-current-2026-03-10:actions/list-concurrency-groups-for-repository`, `openapi-current-2026-03-10:actions/list-concurrency-groups-for-workflow-run`, `openapi-current-2026-03-10:actions/set-artifact-and-log-retention-settings-organization`, `openapi-current-2026-03-10:actions/set-artifact-and-log-retention-settings-repository`, `openapi-current-2026-03-10:actions/set-fork-pr-contributor-approval-permissions-organization`, `openapi-current-2026-03-10:actions/set-fork-pr-contributor-approval-permissions-repository`, `openapi-current-2026-03-10:actions/set-private-repo-fork-pr-workflows-settings-organization`, `openapi-current-2026-03-10:actions/set-private-repo-fork-pr-workflows-settings-repository`, `openapi-current-2026-03-10:actions/set-selected-repositories-self-hosted-runners-organization`, `openapi-current-2026-03-10:actions/set-self-hosted-runners-permissions-organization`, `openapi-current-2026-03-10:issues/add-issue-field-values`, `openapi-current-2026-03-10:issues/add-labels`, `openapi-current-2026-03-10:issues/approve-suggestion`, `openapi-current-2026-03-10:issues/create-comment`, `openapi-current-2026-03-10:issues/create-label`, `openapi-current-2026-03-10:issues/create-milestone`, `openapi-current-2026-03-10:issues/delete-issue-field-value`, `openapi-current-2026-03-10:issues/dismiss-suggestion`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-suggestions`, `openapi-current-2026-03-10:issues/lock`, `openapi-current-2026-03-10:issues/pin-comment`, `openapi-current-2026-03-10:issues/set-issue-field-values`, `openapi-current-2026-03-10:issues/set-labels`, `openapi-current-2026-03-10:issues/update-comment`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/list-files`, `openapi-current-2026-03-10:pulls/merge`, `openapi-current-2026-03-10:pulls/merge-async`, `openapi-current-2026-03-10:pulls/update-branch`, `openapi-current-2026-03-10:repos/add-app-access-restrictions`, `openapi-current-2026-03-10:repos/add-status-check-contexts`, `openapi-current-2026-03-10:repos/add-team-access-restrictions`, `openapi-current-2026-03-10:repos/add-user-access-restrictions`, `openapi-current-2026-03-10:repos/create-attestation`, `openapi-current-2026-03-10:repos/create-autolink`, `openapi-current-2026-03-10:repos/create-commit-comment`, `openapi-current-2026-03-10:repos/create-deploy-key`, `openapi-current-2026-03-10:repos/create-deployment`, `openapi-current-2026-03-10:repos/create-deployment-status`, `openapi-current-2026-03-10:repos/create-dispatch-event`, `openapi-current-2026-03-10:repos/create-fork`, `openapi-current-2026-03-10:repos/create-or-update-file-contents`, `openapi-current-2026-03-10:repos/create-org-ruleset`, `openapi-current-2026-03-10:repos/create-pages-deployment`, `openapi-current-2026-03-10:repos/create-pages-site`, `openapi-current-2026-03-10:repos/create-release`, `openapi-current-2026-03-10:repos/create-repo-ruleset`, `openapi-current-2026-03-10:repos/create-webhook`, `openapi-current-2026-03-10:repos/custom-properties-for-repos-create-or-update-repository-values`, `openapi-current-2026-03-10:repos/delete-file`, `openapi-current-2026-03-10:repos/delete-pages-site`, `openapi-current-2026-03-10:repos/get-commit`, `openapi-current-2026-03-10:repos/get-readme`, `openapi-current-2026-03-10:repos/get-readme-in-directory`, `openapi-current-2026-03-10:repos/get-webhook-delivery`, `openapi-current-2026-03-10:repos/list-branches-for-head-commit`, `openapi-current-2026-03-10:repos/list-for-authenticated-user`, `openapi-current-2026-03-10:repos/list-public`, `openapi-current-2026-03-10:repos/list-webhook-deliveries`, `openapi-current-2026-03-10:repos/merge`, `openapi-current-2026-03-10:repos/redeliver-webhook-delivery`, `openapi-current-2026-03-10:repos/remove-app-access-restrictions`, `openapi-current-2026-03-10:repos/remove-collaborator`, `openapi-current-2026-03-10:repos/remove-status-check-contexts`, `openapi-current-2026-03-10:repos/remove-team-access-restrictions`, `openapi-current-2026-03-10:repos/remove-user-access-restrictions`, `openapi-current-2026-03-10:repos/rename-branch`, `openapi-current-2026-03-10:repos/set-app-access-restrictions`, `openapi-current-2026-03-10:repos/set-status-check-contexts`, `openapi-current-2026-03-10:repos/set-team-access-restrictions`, `openapi-current-2026-03-10:repos/set-user-access-restrictions`, `openapi-current-2026-03-10:repos/update`, `openapi-current-2026-03-10:repos/update-information-about-pages-site`, `openapi-current-2026-03-10:repos/update-org-ruleset`, `openapi-current-2026-03-10:repos/update-pull-request-review-protection`, `openapi-current-2026-03-10:repos/update-repo-ruleset`, `openapi-current-2026-03-10:repos/update-status-check-protection`, `openapi-current-2026-03-10:repos/update-webhook`
- topic matches: `pulls/update`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-b2bc4ff09e8a4d33ded81556b6e442081bb05dfb99780a4f904024be5a0e77ff`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/update`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-e8fc96fbaa45f2c119f5c6ebb463aa1f2185ef34a62d159f349d65c167f4caca`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`
- topic matches: `update a pull request`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\" and \"[Best practices for using the REST API](https://docs.githu
</pre>

#### `chunk-8dd06f9776710075a0304ff05e06d9c104a0eea6e99e20b7be4e1ac5187d4f27`

- score: `12`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-troubleshooting`
- topic matches: `none`
- diagnostic matches: `422`, `validation failed`, `invalid request`

<pre>
## Missing results Most endpoints that return a list of resources support pagination. For most of these endpoints, only the first 30 resources are returned by default. In order to see all of the resources, you need to paginate through the results. For more information, see [/rest/using-the-rest-api/using-pagination-in-the-rest-api](/rest/using-the-rest-api/using-pagination-in-the-rest-api). If you are using pagination correctly and still do not see all of the results that you expect, you should confirm that the authentication credentials that you used have access to all of the expected resources. For example, if you are using a GitHub App installation access token, if the installation was only granted access to a subset of repositories in an organization, any request for all repositories in that organization will return only the repositories that the app installation can access. ## Requires authentication when using basic authentication Basic authentication with your username and password is not supported. Instead, you should use a personal access token or an access token for a GitHub App or OAuth app. For more information, see [/rest/authentication/authenticating-to-the-rest-api](
</pre>

#### `chunk-0fb8f7cec6b12687d9ca57a3028edfc64d2e9527be0ea74b8314c5f49553eb44`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-license-simple","value":{"description":"License Simple","nullable":true,"properties":{"html_url":{"format":"uri","type":"string"},"key":{"example":"mit","type":"string"},"name":{"example":"MIT License","type":"string"},"node_id":{"example":"MDc6TGljZW5zZW1pdA==","type":"string"},"spdx_id":{"example":"MIT","nullable":true,"type":"string"},"url":{"example":"https://api.github.com/licenses/mit","format":"uri","nullable":true,"type":"string"}},"required":["key","name","url","spdx_id","node_id"],"title":"License Simple","type":"object"}}}]}
</pre>

#### `chunk-17edde83c545913ec5e5e340594689c4f03d9457e9df3404c718aa2e3b01ab3f`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-18453b4a4521922329160b2f3e0e1f5fea00002968114fba83ed2cef21e2e7fd`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`, `openapi-current-2026-03-10:repos/get-content`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/forbidden","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/basic-error"}}},"description":"Forbidden"}}}]}
</pre>

#### `chunk-187b39a35571e4bb69c19fcddbed5557b102f09ae87bb9bd08139ccb91c50675`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["value","value","milestone"],"value":{"closed_at":"2013-02-12T13:22:01Z","closed_issues":8,"created_at":"2011-04-10T20:09:31Z","creator":{"avatar_url":"https://github.com/images/error/octocat_happy.gif","events_url":"https://api.github.com/users/octocat/events{/privacy}","followers_url":"https://api.github.com/users/octocat/followers","following_url":"https://api.github.com/users/octocat/following{/other_user}","gists_url":"https://api.github.com/users/octocat/gists{/gist_id}","gravatar_id":"","html_url":"https://github.com/octocat","id":1,"login":"octocat","node_id":"MDQ6VXNlcjE=","organizations_url":"https://api.github.com/users/octocat/orgs","received_events_url":"https://api.github.com/users/octocat/received_events","repos_url":"https://api.github.com/users/octocat/repos","site_admin":false,"starred_url":"https://api.github.com/users/octocat/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/octocat/subscriptions","type":"User","url":"https://api.github.com/users/octocat"},"description":"Tracking milestone for version 1.0","due_on":"2012-10-09T23:39:01Z","html_url":"https://github.com/octocat/Hello-World/milestones/v1.0","id":100260
</pre>

#### `chunk-1c3c998887b2de813f5993089d5dd4b43f2627f93632626fccb793611803d873`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/validation-error","value":{"description":"Validation Error","properties":{"documentation_url":{"type":"string"},"errors":{"items":{"properties":{"code":{"type":"string"},"field":{"type":"string"},"index":{"type":"integer"},"message":{"type":"string"},"resource":{"type":"string"},"value":{"oneOf":[{"nullable":true,"type":"string"},{"nullable":true,"type":"integer"},{"items":{"type":"string"},"nullable":true,"type":"array"}]}},"required":["code"],"type":"object"},"type":"array"},"message":{"type":"string"}},"required":["message","documentation_url"],"title":"Validation Error","type":"object"}}}]}
</pre>

#### `chunk-20e6d65f58412d5ff8d152ca4cdecd24734513599159d11a178371d59f8c96f0`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/schemas/repository"},{"path":["value","description"],"value":"A repository on GitHub."},{"path":["value","properties","allow_auto_merge"],"value":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"}},{"path":["value","properties","allow_forking"],"value":{"description":"Whether to allow forking this repo","type":"boolean"}},{"path":["value","properties","allow_merge_commit"],"value":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_rebase_merge"],"value":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_squash_merge"],"value":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"}},{"path":["value","properties","allow_update_branch"],"value":{"default":false,"description":"Whether or not a pull request head branch that is behind its base branch can always be updated even if it is not required to
</pre>

#### `chunk-24199694faca2405b980691af07b2c30f4eb53bb46299020e585d749413f3754`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create-comment`, `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-comment`, `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-comments`, `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/pin-comment`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:issues/update-comment`, `openapi-current-2026-03-10:pulls/create-reply-for-review-comment`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/get-review-comment`, `openapi-current-2026-03-10:pulls/list-comments-for-review`, `openapi-current-2026-03-10:pulls/list-review-comments`, `openapi-current-2026-03-10:pulls/list-review-comments-for-repo`, `openapi-current-2026-03-10:pulls/update-review-comment`, `openapi-current-2026-03-10:repos/create-commit-comment`, `openapi-current-2026-03-10:repos/create-release`, `openapi-current-2026-03-10:repos/get-commit-comment`, `openapi-current-2026-03-10:repos/get-latest-release`, `openapi-current-2026-03-10:repos/get-release`, `openapi-current-2026-03-10:repos/get-release-by-tag`, `openapi-current-2026-03-10:repos/list-comments-for-commit`, `openapi-current-2026-03-10:repos/list-commit-comments-for-repo`, `openapi-current-2026-03-10:repos/list-releases`, `openapi-current-2026-03-10:repos/update-commit-comment`, `openapi-current-2026-03-10:repos/update-release`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/reaction-rollup","value":{"properties":{"+1":{"type":"integer"},"-1":{"type":"integer"},"confused":{"type":"integer"},"eyes":{"type":"integer"},"heart":{"type":"integer"},"hooray":{"type":"integer"},"laugh":{"type":"integer"},"rocket":{"type":"integer"},"total_count":{"type":"integer"},"url":{"format":"uri","type":"string"}},"required":["url","total_count","+1","-1","laugh","confused","heart","hooray","eyes","rocket"],"title":"Reaction Rollup","type":"object"}}}]}
</pre>

#### `chunk-24b3cb75de16c1bc945df0ed7ecfd86371de9c5066dfe08245f4823ed145b618`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/accept-invitation-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`, `openapi-historical-2022-11-28:repos/get-content`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/forbidden","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/basic-error"}}},"description":"Forbidden"}}}]}
</pre>

#### `chunk-272a43d8c372584c4758763706a3cf70ee4eba0170d634743b38aba5d5750295`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create-comment`, `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-comment`, `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-comments`, `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/pin-comment`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:issues/update-comment`, `openapi-current-2026-03-10:pulls/create-reply-for-review-comment`, `openapi-current-2026-03-10:pulls/create-review`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/delete-pending-review`, `openapi-current-2026-03-10:pulls/dismiss-review`, `openapi-current-2026-03-10:pulls/get-review`, `openapi-current-2026-03-10:pulls/get-review-comment`, `openapi-current-2026-03-10:pulls/list-comments-for-review`, `openapi-current-2026-03-10:pulls/list-review-comments`, `openapi-current-2026-03-10:pulls/list-review-comments-for-repo`, `openapi-current-2026-03-10:pulls/list-reviews`, `openapi-current-2026-03-10:pulls/request-reviewers`, `openapi-current-2026-03-10:pulls/submit-review`, `openapi-current-2026-03-10:pulls/update-review`, `openapi-current-2026-03-10:pulls/update-review-comment`, `openapi-current-2026-03-10:repos/create-commit-comment`, `openapi-current-2026-03-10:repos/get-commit-comment`, `openapi-current-2026-03-10:repos/list-comments-for-commit`, `openapi-current-2026-03-10:repos/list-commit-comments-for-repo`, `openapi-current-2026-03-10:repos/list-pull-requests-associated-with-commit`, `openapi-current-2026-03-10:repos/update-commit-comment`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/author-association","value":{"description":"How the author is associated with the repository.","enum":["COLLABORATOR","CONTRIBUTOR","FIRST_TIMER","FIRST_TIME_CONTRIBUTOR","MANNEQUIN","MEMBER","NONE","OWNER"],"example":"OWNER","title":"author_association","type":"string"}}}]}
</pre>

#### `chunk-2d37d693076f8b53f2ed9fad952a2813d0197965b4d21a8cf1e568398fa4d9e4`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/add-custom-labels-to-self-hosted-runner-for-org`, `openapi-current-2026-03-10:actions/add-custom-labels-to-self-hosted-runner-for-repo`, `openapi-current-2026-03-10:actions/delete-self-hosted-runner-from-org`, `openapi-current-2026-03-10:actions/delete-self-hosted-runner-from-repo`, `openapi-current-2026-03-10:actions/generate-runner-jitconfig-for-org`, `openapi-current-2026-03-10:actions/generate-runner-jitconfig-for-repo`, `openapi-current-2026-03-10:actions/remove-custom-label-from-self-hosted-runner-for-org`, `openapi-current-2026-03-10:actions/remove-custom-label-from-self-hosted-runner-for-repo`, `openapi-current-2026-03-10:actions/set-custom-labels-for-self-hosted-runner-for-org`, `openapi-current-2026-03-10:actions/set-custom-labels-for-self-hosted-runner-for-repo`, `openapi-current-2026-03-10:actions/set-custom-oidc-sub-claim-for-repo`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:pulls/create-review`, `openapi-current-2026-03-10:pulls/delete-pending-review`, `openapi-current-2026-03-10:pulls/dismiss-review`, `openapi-current-2026-03-10:pulls/submit-review`, `openapi-current-2026-03-10:pulls/update-review`, `openapi-current-2026-03-10:repos/delete-deployment`, `openapi-current-2026-03-10:repos/list-activities`, `openapi-current-2026-03-10:repos/replace-all-topics`, `openapi-current-2026-03-10:repos/update-branch-protection`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/validation-error-simple","value":{"description":"Validation Error Simple","properties":{"documentation_url":{"type":"string"},"errors":{"items":{"type":"string"},"type":"array"},"message":{"type":"string"}},"required":["message","documentation_url"],"title":"Validation Error Simple","type":"object"}}}]}
</pre>

#### `chunk-2def5cb713729f41143b8fd1ad8790eef2b416595be1165bcde4c58579f643bc`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-milestone","value":{"description":"A collection of related issues and pull requests.","nullable":true,"properties":{"closed_at":{"example":"2013-02-12T13:22:01Z","format":"date-time","nullable":true,"type":"string"},"closed_issues":{"example":8,"type":"integer"},"created_at":{"example":"2011-04-10T20:09:31Z","format":"date-time","type":"string"},"creator":{"$ref":"#/components/schemas/nullable-simple-user"},"description":{"example":"Tracking milestone for version 1.0","nullable":true,"type":"string"},"due_on":{"example":"2012-10-09T23:39:01Z","format":"date-time","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat/Hello-World/milestones/v1.0","format":"uri","type":"string"},"id":{"example":1002604,"type":"integer"},"labels_url":{"example":"https://api.github.com/repos/octocat/Hello-World/milestones/1/labels","format":"uri","type":"string"},"node_id":{"example":"MDk6TWlsZXN0b25lMTAwMjYwNA==","type":"string"},"number":{"description":"The number of the milestone.","example":42,"type":"integer"},"open_issues":{"example":4,"type":"integer"},"state":{"default":"open","description":
</pre>

#### `chunk-2e834b5e16aad77c21e3ed6f71700063bde8caf8323258751f8433423ca35ed2`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/link","value":{"description":"Hypermedia Link","properties":{"href":{"type":"string"}},"required":["href"],"title":"Link","type":"object"}}}]}
</pre>

#### `chunk-344e5831dc73d11d077a437c51bfa1b5e8fd80324fb320a719078e865076524b`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":["value","value","base"],"value":{"label":"octocat:master","ref":"master","repo":{"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","deployments_url":"https://ap
</pre>

#### `chunk-3601b6755598b081f3fac60e651e2e01ea112cf94f326c5c3c9713c4e71a2003`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/review-pending-deployments-for-run`, `openapi-current-2026-03-10:issues/create-comment`, `openapi-current-2026-03-10:issues/create-milestone`, `openapi-current-2026-03-10:issues/get`, `openapi-current-2026-03-10:issues/get-comment`, `openapi-current-2026-03-10:issues/get-event`, `openapi-current-2026-03-10:issues/get-milestone`, `openapi-current-2026-03-10:issues/get-parent`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-comments`, `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`, `openapi-current-2026-03-10:issues/list-dependencies-blocking`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-timeline`, `openapi-current-2026-03-10:issues/list-for-authenticated-user`, `openapi-current-2026-03-10:issues/list-for-org`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-milestones`, `openapi-current-2026-03-10:issues/list-sub-issues`, `openapi-current-2026-03-10:issues/pin-comment`, `openapi-current-2026-03-10:issues/remove-assignees`, `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`, `openapi-current-2026-03-10:issues/remove-sub-issue`, `openapi-current-2026-03-10:issues/reprioritize-sub-issue`, `openapi-current-2026-03-10:issues/update-comment`, `openapi-current-2026-03-10:issues/update-milestone`, `openapi-current-2026-03-10:pulls/create-reply-for-review-comment`, `openapi-current-2026-03-10:pulls/create-review`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/delete-pending-review`, `openapi-current-2026-03-10:pulls/dismiss-review`, `openapi-current-2026-03-10:pulls/get-review`, `openapi-current-2026-03-10:pulls/get-review-comment`, `openapi-current-2026-03-10:pulls/list-comments-for-review`, `openapi-current-2026-03-10:pulls/list-review-comments`, `openapi-current-2026-03-10:pulls/list-review-comments-for-repo`, `openapi-current-2026-03-10:pulls/list-reviews`, `openapi-current-2026-03-10:pulls/request-reviewers`, `openapi-current-2026-03-10:pulls/submit-review`, `openapi-current-2026-03-10:pulls/update-review`, `openapi-current-2026-03-10:pulls/update-review-comment`, `openapi-current-2026-03-10:repos/add-collaborator`, `openapi-current-2026-03-10:repos/create-commit-comment`, `openapi-current-2026-03-10:repos/create-commit-status`, `openapi-current-2026-03-10:repos/create-deployment`, `openapi-current-2026-03-10:repos/create-deployment-status`, `openapi-current-2026-03-10:repos/create-fork`, `openapi-current-2026-03-10:repos/create-release`, `openapi-current-2026-03-10:repos/create-using-template`, `openapi-current-2026-03-10:repos/get`, `openapi-current-2026-03-10:repos/get-commit-comment`, `openapi-current-2026-03-10:repos/get-contributors-stats`, `openapi-current-2026-03-10:repos/get-deployment`, `openapi-current-2026-03-10:repos/get-deployment-status`, `openapi-current-2026-03-10:repos/get-latest-pages-build`, `openapi-current-2026-03-10:repos/get-latest-release`, `openapi-current-2026-03-10:repos/get-pages-build`, `openapi-current-2026-03-10:repos/get-release`, `openapi-current-2026-03-10:repos/get-release-asset`, `openapi-current-2026-03-10:repos/get-release-by-tag`, `openapi-current-2026-03-10:repos/list-activities`, `openapi-current-2026-03-10:repos/list-comments-for-commit`, `openapi-current-2026-03-10:repos/list-commit-comments-for-repo`, `openapi-current-2026-03-10:repos/list-commit-statuses-for-ref`, `openapi-current-2026-03-10:repos/list-deployment-statuses`, `openapi-current-2026-03-10:repos/list-deployments`, `openapi-current-2026-03-10:repos/list-invitations`, `openapi-current-2026-03-10:repos/list-invitations-for-authenticated-user`, `openapi-current-2026-03-10:repos/list-pages-builds`, `openapi-current-2026-03-10:repos/list-pull-requests-associated-with-commit`, `openapi-current-2026-03-10:repos/list-release-assets`, `openapi-current-2026-03-10:repos/list-releases`, `openapi-current-2026-03-10:repos/update`, `openapi-current-2026-03-10:repos/update-commit-comment`, `openapi-current-2026-03-10:repos/update-invitation`, `openapi-current-2026-03-10:repos/update-release`, `openapi-current-2026-03-10:repos/update-release-asset`, `openapi-current-2026-03-10:repos/upload-release-asset`
- topic matches: `pulls/update`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-simple-user","value":{"description":"A GitHub user.","nullable":true,"properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"receive
</pre>

## `tuning-create-in-org-451-cause`

- cluster: `openapi-pair:repos/create-in-org`
- role: `intervention_tuning_case`
- pattern: `status_cause`
- provisional claim: A 451 response from creating an organization repository does not by itself establish the exact cause.
- total discovered candidates: 53
- candidates outside Phase 4 gold evidence: 47
- automated verdict: `review_required`

### Search terms

- topic: `repos/create-in-org`, `create an organization repository`, `/orgs/{org}/repos`
- diagnostic: `451`, `validation failed`, `error`

### Highest-ranked candidates (max 25)

#### `chunk-0866e576fcc08a7d8b93d77a2710ca186b1b7ab008a0c3332a53230283b04136`

- score: `53`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`, `create an organization repository`, `/orgs/{org}/repos`
- diagnostic matches: `451`, `error`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository in the specified organization. The authenticated user must be a member of the organization.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-an-organization-repository"},"operationId":"repos/create-in-org","parameters":[{"$ref":"#/components/parameters/org"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repository","has_issues":true,"has_projects":true,"has_wiki":true,"homepage":"https://github.com","name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Either `true` to allow auto-merge on pull requests, or `false` to disallow auto-merge.","type":"boolean"},"allow_merge_commit":{"default":true,"description":"Either `true` to allow merging pull requests with a merge commit, or `false` to prevent merging pull requests with
</pre>

#### `chunk-9415dcdaefed1c781040a1a24f82567f5cd9976d4b6936bfe2b187819aebba7d`

- score: `49`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`, `create an organization repository`, `/orgs/{org}/repos`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository in the specified organization. The authenticated user must be a member of the organization.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-an-organization-repository"},"operationId":"repos/create-in-org","parameters":[{"$ref":"#/components/parameters/org"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repository","has_issues":true,"has_projects":true,"has_wiki":true,"homepage":"https://github.com","name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Either `true` to allow auto-merge on pull requests, or `false` to disallow auto-merge.","type":"boolean"},"allow_merge_commit":{"default":true,"description":"Either `true` to allow merging pull requests with a merge commit, or `false` to prevent merging pull requests with
</pre>

#### `chunk-74f1f93d8305d71a7383663446c672b2e0c01cbd5cecf28318ce9e24433b3bc2`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `validation failed`, `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-b2bc4ff09e8a4d33ded81556b6e442081bb05dfb99780a4f904024be5a0e77ff`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `validation failed`, `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-03ae34fdd7b0679afa9488de9046d697815f4370129a24d8e59ea7a0d5662b99`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["value","value","parent"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","delete_branch_on_merge":true,"deployments_url":"h
</pre>

#### `chunk-09ac95f73522a07fd46753b2c201e1f6df802c154178ec7f483ca48058d7b99e`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/full-repository"},{"path":["value","value","allow_auto_merge"],"value":false},{"path":["value","value","allow_forking"],"value":true},{"path":["value","value","allow_merge_commit"],"value":true},{"path":["value","value","allow_rebase_merge"],"value":true},{"path":["value","value","allow_squash_merge"],"value":true},{"path":["value","value","archive_url"],"value":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}"},{"path":["value","value","archived"],"value":false},{"path":["value","value","assignees_url"],"value":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}"},{"path":["value","value","blobs_url"],"value":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}"},{"path":["value","value","branches_url"],"value":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}"},{"path":["value","value","clone_url"],"value":"https://github.com/octocat/Hello-World.git"},{"path":["value","value","collaborators_url"],"value":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}"},{"path":["value","value","comments_url"],"value":"https://api.
</pre>

#### `chunk-18453b4a4521922329160b2f3e0e1f5fea00002968114fba83ed2cef21e2e7fd`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`, `openapi-current-2026-03-10:repos/get-content`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/forbidden","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/basic-error"}}},"description":"Forbidden"}}}]}
</pre>

#### `chunk-1c3c998887b2de813f5993089d5dd4b43f2627f93632626fccb793611803d873`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/validation-error","value":{"description":"Validation Error","properties":{"documentation_url":{"type":"string"},"errors":{"items":{"properties":{"code":{"type":"string"},"field":{"type":"string"},"index":{"type":"integer"},"message":{"type":"string"},"resource":{"type":"string"},"value":{"oneOf":[{"nullable":true,"type":"string"},{"nullable":true,"type":"integer"},{"items":{"type":"string"},"nullable":true,"type":"array"}]}},"required":["code"],"type":"object"},"type":"array"},"message":{"type":"string"}},"required":["message","documentation_url"],"title":"Validation Error","type":"object"}}}]}
</pre>

#### `chunk-24b3cb75de16c1bc945df0ed7ecfd86371de9c5066dfe08245f4823ed145b618`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/accept-invitation-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`, `openapi-historical-2022-11-28:repos/get-content`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/forbidden","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/basic-error"}}},"description":"Forbidden"}}}]}
</pre>

#### `chunk-3798df4c0bb40f34bf2fdbfb52bd3dc9e126738525d0385e540741c3bacbf69b`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["value","value","template_repository"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World-Template/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World-Template/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World-Template/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World-Template/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World-Template.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World-Template/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World-Template/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World-Template/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World-Template/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World-Template/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World-Template/contributors",
</pre>

#### `chunk-37baf17ba7fd988bd13097a2822f6c9fb8602fbb9b0b7ffeefe47077b8be43ed`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/accept-invitation-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`, `openapi-historical-2022-11-28:repos/get-content`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/basic-error","value":{"description":"Basic Error","properties":{"documentation_url":{"type":"string"},"message":{"type":"string"},"status":{"type":"string"},"url":{"type":"string"}},"title":"Basic Error","type":"object"}}}]}
</pre>

#### `chunk-3d8fe3177d633f830beea9d8a68bbff64dcdbf86355688a00128277c947b3ffe`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["value","value","template_repository"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World-Template/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World-Template/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World-Template/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World-Template/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World-Template.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World-Template/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World-Template/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World-Template/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World-Template/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World-Template/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World-Template/contributors",
</pre>

#### `chunk-49beb1a062dc90a2cfeffb3164930bc05aca361bad0e89c9d369acaf25917592`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/validation-error","value":{"description":"Validation Error","properties":{"documentation_url":{"type":"string"},"errors":{"items":{"properties":{"code":{"type":"string"},"field":{"type":"string"},"index":{"type":"integer"},"message":{"type":"string"},"resource":{"type":"string"},"value":{"oneOf":[{"nullable":true,"type":"string"},{"nullable":true,"type":"integer"},{"items":{"type":"string"},"nullable":true,"type":"array"}]}},"required":["code"],"type":"object"},"type":"array"},"message":{"type":"string"}},"required":["message","documentation_url"],"title":"Validation Error","type":"object"}}}]}
</pre>

#### `chunk-4a6fdd602798478ba7660d823a99589e570e50ee2ca05c8f9d788fac6bb087ae`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["value","value","parent"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","delete_branch_on_merge":true,"deployments_url":"h
</pre>

#### `chunk-4de76ccd2002dc08909896184f182ca4367d5e82a763a569b7eaea6d7d319b5d`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-simple-user","value":{"description":"A GitHub user.","nullable":true,"properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"receive
</pre>

#### `chunk-67f3339e54c53b9465795a373b7e7822bf47e11cf6ff344cd1e75d267a7b40ee`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/nullable-simple-user","value":{"description":"A GitHub user.","nullable":true,"properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"receive
</pre>

#### `chunk-6a34dca66ca3afcf12c6d51aab19492b8760fb39411b4f93aa70828d7ad1b7d3`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`, `openapi-current-2026-03-10:repos/get-content`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/basic-error","value":{"description":"Basic Error","properties":{"documentation_url":{"type":"string"},"message":{"type":"string"},"status":{"type":"string"},"url":{"type":"string"}},"title":"Basic Error","type":"object"}}}]}
</pre>

#### `chunk-858231dbb533e53e8b6ea90013f7465481b23b8341812fd54b28d596d5c71fe0`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["value","value","source"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","delete_branch_on_merge":true,"deployments_url":"h
</pre>

#### `chunk-87b09a56691da35f56cbde727a3f934b15754679bc22e6527b261ffd852e36cd`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["reference"],"value":"#/components/examples/full-repository"},{"path":["value","value","allow_auto_merge"],"value":false},{"path":["value","value","allow_forking"],"value":true},{"path":["value","value","allow_merge_commit"],"value":true},{"path":["value","value","allow_rebase_merge"],"value":true},{"path":["value","value","allow_squash_merge"],"value":true},{"path":["value","value","archive_url"],"value":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}"},{"path":["value","value","archived"],"value":false},{"path":["value","value","assignees_url"],"value":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}"},{"path":["value","value","blobs_url"],"value":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}"},{"path":["value","value","branches_url"],"value":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}"},{"path":["value","value","clone_url"],"value":"https://github.com/octocat/Hello-World.git"},{"path":["value","value","collaborators_url"],"value":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}"},{"path":["value","value","comments_url"],"value":"https://api.
</pre>

#### `chunk-9ee4ee6ae32d9c3b131685a4ebf36f6b56da6c0fb21d6a581006d2f71f2dd6a3`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-org-ruleset`
- topic matches: `create an organization repository`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Create a repository ruleset for an organization.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/orgs/rules#create-an-organization-repository-ruleset"},"operationId":"repos/create-org-ruleset","parameters":[{"$ref":"#/components/parameters/org"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"bypass_actors":[{"actor_id":234,"actor_type":"Team","bypass_mode":"always"}],"conditions":{"ref_name":{"exclude":["refs/heads/dev*"],"include":["refs/heads/main","refs/heads/master"]},"repository_name":{"exclude":["unimportant_repository"],"include":["important_repository","another_important_repository"],"protected":true}},"enforcement":"active","name":"super cool ruleset","rules":[{"parameters":{"operator":"contains","pattern":"github"},"type":"commit_author_email_pattern"}],"target":"branch"}}},"schema":{"properties":{"bypass_actors":{"description":"The actors that can bypass the rules in this ruleset","items":{"$ref":"#/components/schemas/repository-ruleset-bypass-actor"},"type":"array"},"conditions":{"$ref":"#/components/schemas/org-rul
</pre>

#### `chunk-aab4129e4bb838cd0c62c3f8927832a3e6b4f6b3004791373d71661b624e5b45`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `/orgs/{org}/repos`
- diagnostic matches: `451`

<pre>
- `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue` - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` - `GET /events` - `GET /installation/repositories` - `GET /issues` - `GET /networks/{owner}/{repo}/events` - `GET /notifications` - `GET /notifications/threads/{thread_id}` - `GET /orgs/{org}/actions/permissions/repositories` - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories` - `GET /orgs/{org}/actions/runner-groups/{runner_group_id}/repositories` - `GET /orgs/{org}/actions/secrets/{secret_name}/repositories` - `GET /orgs/{org}/actions/variables/{name}/repositories` - `GET /orgs/{org}/codespaces` - `GET /orgs/{org}/codespaces/secrets/{secret_name}/repositories` - `GET /orgs/{org}/dependabot/secrets/{secret_name}/repositories` - `GET /orgs/{org}/docker/conflicts` - `GET /orgs/{org}/events` - `GET /orgs/{org}/issues` - `GET /orgs/{org}/members/{username}/codespaces` - `GET /orgs/{org}/migrations` - `GET /orgs/{org}/migrations/{migration_id}` - `GET /orgs/{org}/migrations/{mi
</pre>

#### `chunk-d180dce326c94f1d9ab39fdf3a80229a643924b32ec147f6cfbb6d67fee7684c`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":["value","value","source"],"value":{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,"archive_url":"https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}","archived":false,"assignees_url":"https://api.github.com/repos/octocat/Hello-World/assignees{/user}","blobs_url":"https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}","branches_url":"https://api.github.com/repos/octocat/Hello-World/branches{/branch}","clone_url":"https://github.com/octocat/Hello-World.git","collaborators_url":"https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/octocat/Hello-World/comments{/number}","commits_url":"https://api.github.com/repos/octocat/Hello-World/commits{/sha}","compare_url":"https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}","contents_url":"https://api.github.com/repos/octocat/Hello-World/contents/{+path}","contributors_url":"https://api.github.com/repos/octocat/Hello-World/contributors","created_at":"2011-01-26T19:01:12Z","default_branch":"master","delete_branch_on_merge":true,"deployments_url":"h
</pre>

#### `chunk-de780ec68b2c87a487ff7661b7dd4e1e42f8776ad10e8067ffe5fd54d90e8948`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/create-registration-token-for-org`, `openapi-current-2026-03-10:actions/create-registration-token-for-repo`, `openapi-current-2026-03-10:actions/create-remove-token-for-org`, `openapi-current-2026-03-10:actions/create-remove-token-for-repo`, `openapi-current-2026-03-10:issues/add-assignees`, `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/get`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/simple-user","value":{"description":"A GitHub user.","properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"received_events_url":{"example":
</pre>

#### `chunk-f652a8ffa16dcc2b62b2b0fda4b74f53a2e5723530d015b28189c0d2b9df0724`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`, `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`, `openapi-historical-2022-11-28:actions/create-remove-token-for-org`, `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`, `openapi-historical-2022-11-28:issues/add-assignees`, `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/get`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `error`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/simple-user","value":{"description":"A GitHub user.","properties":{"avatar_url":{"example":"https://github.com/images/error/octocat_happy.gif","format":"uri","type":"string"},"email":{"nullable":true,"type":"string"},"events_url":{"example":"https://api.github.com/users/octocat/events{/privacy}","type":"string"},"followers_url":{"example":"https://api.github.com/users/octocat/followers","format":"uri","type":"string"},"following_url":{"example":"https://api.github.com/users/octocat/following{/other_user}","type":"string"},"gists_url":{"example":"https://api.github.com/users/octocat/gists{/gist_id}","type":"string"},"gravatar_id":{"example":"41d064eb2195891e12d0413f63227ea7","nullable":true,"type":"string"},"html_url":{"example":"https://github.com/octocat","format":"uri","type":"string"},"id":{"example":1,"format":"int64","type":"integer"},"login":{"example":"octocat","type":"string"},"name":{"nullable":true,"type":"string"},"node_id":{"example":"MDQ6VXNlcjE=","type":"string"},"organizations_url":{"example":"https://api.github.com/users/octocat/orgs","format":"uri","type":"string"},"received_events_url":{"example":
</pre>

#### `chunk-0093b1f2881c7bb7cda1b9dfedeffe2ee576475cab4692a0147c36ca2dfae6a5`

- score: `10`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `repos/create-in-org`
- diagnostic matches: `none`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/schemas/code-of-conduct-simple","value":{"description":"Code of Conduct Simple","properties":{"html_url":{"example":"https://github.com/github/docs/blob/main/CODE_OF_CONDUCT.md","format":"uri","nullable":true,"type":"string"},"key":{"example":"citizen_code_of_conduct","type":"string"},"name":{"example":"Citizen Code of Conduct","type":"string"},"url":{"example":"https://api.github.com/repos/github/docs/community/code_of_conduct","format":"uri","type":"string"}},"required":["url","key","name","html_url"],"title":"Code Of Conduct Simple","type":"object"}}}]}
</pre>

## `heldout-last-known-timezone`

- cluster: `guidance:docs-timezones`
- role: `held_out_release_case`
- pattern: `user_state_unknown`
- provisional claim: Without observed user state, the authenticated user's last-known timezone cannot be inferred.
- total discovered candidates: 1
- candidates outside Phase 4 gold evidence: 0
- automated verdict: `review_required`

### Search terms

- topic: `Time-Zone`, `last known timezone`, `timezone`
- diagnostic: `authenticated user`, `defaulting to UTC`, `browse the GitHub website`

### Highest-ranked candidates (max 25)

#### `chunk-cd0e87ca852080c49fd723c0efd6e0225afeae8be7ed5ec25df339ed1e8807bb`

- score: `57`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-timezones`
- topic matches: `Time-Zone`, `last known timezone`, `timezone`
- diagnostic matches: `authenticated user`, `defaulting to UTC`, `browse the GitHub website`

<pre>
--- title: Timezones and the REST API shortTitle: Timezones intro: 'Some REST API endpoints allow you to specify timezone information with your request.' versions: fpt: '*' ghes: '*' ghec: '*' category: - Learn about the REST API --- Some requests that create new data, such as creating a new commit, allow you to provide timezone information when specifying or generating timestamps. Note that these rules apply only to data passed to the API, not to data returned by the API. Timestamps returned by the API are in UTC time, ISO 8601 format. ## Determining the timezone for a request To determine timezone information for applicable API calls, we apply these rules in order of priority: 1. [Explicitly providing an ISO 8601 timestamp with timezone information](#explicitly-providing-an-iso-8601-timestamp-with-timezone-information) 1. [Using the `Time-Zone` header](#using-the-time-zone-header) 1. [Using the last known timezone for the user](#using-the-last-known-timezone-for-the-user) 1. [Defaulting to UTC without other timezone information](#defaulting-to-utc-without-other-timezone-information) ### Explicitly providing an ISO 8601 timestamp with timezone information For API calls that allow
</pre>

## `heldout-blocked-by-failure-cause`

- cluster: `openapi-pair:issues/add-blocked-by-dependency`
- role: `held_out_release_case`
- pattern: `status_cause`
- provisional claim: A generic error response from adding an issue dependency does not by itself establish the exact failure cause.
- total discovered candidates: 215
- candidates outside Phase 4 gold evidence: 185
- automated verdict: `review_required`

### Search terms

- topic: `issues/add-blocked-by-dependency`, `blocked by`, `issue_id`
- diagnostic: `422`, `403`, `404`, `410`, `validation failed`

### Highest-ranked candidates (max 25)

#### `chunk-4b5aeb1527d8e5bf06d0b49a1ffe5ddb97b1f8c467cf4e2db9f2a9e1f4b89f00`

- score: `61`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`
- topic matches: `issues/add-blocked-by-dependency`, `blocked by`, `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add a 'blocked by' relationship to an issue.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see [Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\nand [Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\n\nThis endpoint supports the following custom media types. For more information, see [Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\n\n- **`application/vnd.github.raw+json`**: Returns the raw Markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the Markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's Markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns r
</pre>

#### `chunk-54218cead5dc4d96ffc452ff1dbd07d9b0f4dab0236c0d3ab315168d9f0d4124`

- score: `61`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`
- topic matches: `issues/add-blocked-by-dependency`, `blocked by`, `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add a 'blocked by' relationship to an issue.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see [Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\nand [Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\n\nThis endpoint supports the following custom media types. For more information, see [Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\n\n- **`application/vnd.github.raw+json`**: Returns the raw Markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the Markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's Markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns r
</pre>

#### `chunk-a41dc9aeec35bdbd194ee7d0cc2da1161d9e9c221840acae825f6cbaa13b156f`

- score: `47`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/remove-dependency-blocked-by`
- topic matches: `blocked by`, `issue_id`
- diagnostic matches: `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"You can use the REST API to remove a dependency that an issue is blocked by.\n\nRemoving content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see [Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\nand [Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\n\nThis endpoint supports the following custom media types. For more information, see [Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\n- **`application/vnd.github.raw+json`**: Returns the raw Markdown body. Response will include `body`. This is the default if you do not pass a specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the Markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's Markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns
</pre>

#### `chunk-aab4129e4bb838cd0c62c3f8927832a3e6b4f6b3004791373d71661b624e5b45`

- score: `43`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `blocked by`, `issue_id`
- diagnostic matches: `422`, `403`

<pre>
- `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue` - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` - `GET /events` - `GET /installation/repositories` - `GET /issues` - `GET /networks/{owner}/{repo}/events` - `GET /notifications` - `GET /notifications/threads/{thread_id}` - `GET /orgs/{org}/actions/permissions/repositories` - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories` - `GET /orgs/{org}/actions/runner-groups/{runner_group_id}/repositories` - `GET /orgs/{org}/actions/secrets/{secret_name}/repositories` - `GET /orgs/{org}/actions/variables/{name}/repositories` - `GET /orgs/{org}/codespaces` - `GET /orgs/{org}/codespaces/secrets/{secret_name}/repositories` - `GET /orgs/{org}/dependabot/secrets/{secret_name}/repositories` - `GET /orgs/{org}/docker/conflicts` - `GET /orgs/{org}/events` - `GET /orgs/{org}/issues` - `GET /orgs/{org}/members/{username}/codespaces` - `GET /orgs/{org}/migrations` - `GET /orgs/{org}/migrations/{migration_id}` - `GET /orgs/{org}/migrations/{mi
</pre>

#### `chunk-2a1b7e2dd72157f835c63422ef3416992ea7a3c25b55460ada39cd66ca0d6f3f`

- score: `41`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/update`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":["operation","responses"],"value":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"allOf":[{"$ref":"#/components/schemas/issue"},{"properties":{"suggestions":{"description":"Pending suggestions for each suggestible field (`type`,\n`issue_field_values`, `labels`, `assignees`, `state`) the\nrequest touched. Omitted for fields not in the request or\nwith no pending or ignored suggestions. Items tagged\n`ignored` are echoes of the current request's inputs that\nwere not persisted as pending suggestions.\n","properties":{"assignees":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"login":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"issue_field_values":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"field_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale"
</pre>

#### `chunk-818a2d7af95a38d5ffd8d96869fbd8198cb399d3e2e8c55900c85770cf07a1d9`

- score: `41`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+js
</pre>

#### `chunk-a1a6a71a7bf60ff978907f1339ae3ce7cc900759a29c6114fdff63e37a492421`

- score: `41`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/update`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":["operation","responses"],"value":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"allOf":[{"$ref":"#/components/schemas/issue"},{"properties":{"suggestions":{"description":"Pending suggestions for each suggestible field (`type`,\n`issue_field_values`, `labels`, `assignees`, `state`) the\nrequest touched. Omitted for fields not in the request or\nwith no pending or ignored suggestions. Items tagged\n`ignored` are echoes of the current request's inputs that\nwere not persisted as pending suggestions.\n","properties":{"assignees":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"login":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"issue_field_values":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"field_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale"
</pre>

#### `chunk-a6f2c249acaf3aadd70ac7964297edb46071d6ab5d2fed98384b39ba0e34862f`

- score: `41`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/create`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+js
</pre>

#### `chunk-b89980229e1c8d141c4d35d0701e5158e706010316939034baa54354b28e701e`

- score: `41`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-sub-issue`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add sub-issues to issues.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, tex
</pre>

#### `chunk-dce9a384052fb0b5e660fcf172f8457b8e00d415535f2f845a4cda06dbca9afb`

- score: `41`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-sub-issue`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add sub-issues to issues.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, tex
</pre>

#### `chunk-d72e0d593230f2080481b546c222dafe91eb8de566b8bfd58a3910770f0448b0`

- score: `39`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `blocked by`, `issue_id`
- diagnostic matches: `403`

<pre>
- **Change accept repository invitation response from `403` to `451` when blocked by trade controls** Repository invitation acceptance blocked by trade controls now returns `451 Unavailable For Legal Reasons` instead of `403 Forbidden`. &lt;details&gt; &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt; - `PATCH /user/repository_invitations/{invitation_id}` &lt;/details&gt; - **Remove deprecated `hub_url` property from API root response** &lt;details&gt; &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt; - `GET /` &lt;/details&gt; - **Deprecate `cvss` property in favor of `cvss_severities` for advisory APIs** The `cvss_severities` property will supplant the existing `cvss` property and contain `cvss_v3` and `cvss_v4` properties if they exist on the advisory. &lt;details&gt; &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt; - `GET /advisories` - `GET /advisories/{ghsa_id}` - `GET /enterprises/{enterprise}/dependabot/alerts` - `GET /orgs/{org}/dependabot/alerts` - `GET /orgs/{org}/security-advisories` - `GET /repos/{owner}/{repo}/dependabot/alerts` - `GET /repos/{owner}/{repo}/dependabot/alerts/{alert_number}` - `GET /repos/{owner}/{repo}/security-advisories` - `GET /repos/{owner}/{repo}/security-advi
</pre>

#### `chunk-e4c9b9fef7dd5218549430cedb6a3d118fc647e391648b57c9fe97c14d006640`

- score: `37`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/reprioritize-sub-issue`
- topic matches: `issue_id`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"You can use the REST API to reprioritize a sub-issue to a different position in the parent list.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/sub-issues#reprioritize-sub-issue"},"operationId":"issues/reprioritize-sub-issue","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"after_id":5,"sub_issue_id":6}}},"schema":{"properties":{"after_id":{"description":"The id of the sub-issue to be prioritized after (either positional argument after OR before should be specified).","type":"integer"},"before_id":{"description":"The id of the sub-issue to be prioritized before (either positional argument after OR before should be specified).","type":"integer"},"sub_issue_id":{"description":"The id of the sub-issue to reprioritize","type":"integer"}},"required":["sub_issue_id"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/c
</pre>

#### `chunk-c1cd7eb5721580f7b92305ddc4e494e603601b70da5a86f6bb32d0a6ab994a1d`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-dependencies-blocked-by`
- topic matches: `blocked by`
- diagnostic matches: `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"You can use the REST API to list the dependencies an issue is blocked by.\n\nThis endpoint supports the following custom media types. For more information, see [Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\n\n- **`application/vnd.github.raw+json`**: Returns the raw Markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the Markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's Markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issue-dependencies#list-dependencies-an-issue-is-blocked-by"},"operationId":"issues/list-dependencies-blocked-by","parameters":[{"$ref":"#/components/parameters/owner"},{"$re
</pre>

#### `chunk-eae2743d904189f15379fadc5d7b511ba4697e527cf53dbf55c6730878eaa920`

- score: `33`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/remove-sub-issue`
- topic matches: `issue_id`
- diagnostic matches: `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"You can use the REST API to remove a sub-issue from an issue.\nRemoving content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass a specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, t
</pre>

#### `chunk-74f1f93d8305d71a7383663446c672b2e0c01cbd5cecf28318ce9e24433b3bc2`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `issues/add-blocked-by-dependency`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-b2bc4ff09e8a4d33ded81556b6e442081bb05dfb99780a4f904024be5a0e77ff`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `issues/add-blocked-by-dependency`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-076bce2c6fa23c80e6fdbb9b5238f479855006ab828b09ba5f603a7d57dee47a`

- score: `16`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/pin-comment`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"You can use the REST API to pin comments on issues.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/comments#pin-an-issue-comment"},"operationId":"issues/pin-comment","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/paramete
</pre>

#### `chunk-6e38c405928360f86a05182432df5af831217e6d321ef675b4b86022dda9c92c`

- score: `16`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/lock`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Users with push access can lock an issue or pull request's conversation.\n\nNote that, if you choose not to pass any parameters, you'll need to set `Content-Length` to zero when calling out to this endpoint. For more information, see \"[HTTP method](https://docs.github.com/rest/guides/getting-started-with-the-rest-api#http-method).\"","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#lock-an-issue"},"operationId":"issues/lock","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"summary":"Example of locking an issue as off-topic","value":{"lock_reason":"off-topic"}}},"schema":{"nullable":true,"properties":{"lock_reason":{"description":"The reason for locking the issue or pull request conversation. Lock will fail if you don't use one of these reasons: \n * `off-topic` \n * `too heated` \n * `resolved` \n * `spam`","enum":["off-topic","too heated","resolved","spam"],"type":"string"}},"type":"ob
</pre>

#### `chunk-ce98be82d981091242abf065676ac0f09e8506b32206c7de65f1dc6fa79be909`

- score: `16`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/create-comment`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`, `410`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to create comments on issues and pull requests. Every pull request is an issue, but not every issue is a pull request.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications).\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the m
</pre>

#### `chunk-0a98ac5e1a4daa0e51e91dc08bb8787b274704ce635586deb431fb9ebf7c4a5a`

- score: `12`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/create-for-authenticated-user`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository for the authenticated user.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-a-repository-for-the-authenticated-user"},"operationId":"repos/create-for-authenticated-user","parameters":[],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repo!","homepage":"https://github.com","is_template":true,"name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"},"allow_merge_commit":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"},"allow_rebase_merge":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"},"allow_squash_merge":
</pre>

#### `chunk-0c39718da981e6f97bb7c5cf94eb651c8d1ef9532bbfc7e38a9b46d25641f9af`

- score: `12`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/update`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":["operation","requestBody","content","application/json","schema","properties","security_and_analysis"],"value":{"description":"Specify which security and analysis features to enable or disable for the repository.\n\nTo use this parameter, you must have admin permissions for the repository or be an owner or security manager for the organization that owns the repository. For more information, see \"[Managing security managers in your organization](https://docs.github.com/organizations/managing-peoples-access-to-your-organization-with-roles/managing-security-managers-in-your-organization).\"\n\nFor example, to enable GitHub Advanced Security, use this data in the body of the `PATCH` request:\n`{ \"security_and_analysis\": {\"advanced_security\": { \"status\": \"enabled\" } } }`.\n\nYou can check which security and analysis features are currently enabled by using a `GET /repos/{owner}/{repo}` request.","nullable":true,"properties":{"advanced_security":{"description":"Use the `status` property to enable or disable GitHub Advanced Security for this repository.\nFor more information, see \"[About GitHub Advanced\nSecurity](/github/getting-started-with-github/learning
</pre>

#### `chunk-0dc68ce2e247fd04bd519730c36240df3a2315a307d67db7e87a6ce06ddc6fe9`

- score: `12`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-issue-field-values`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Add custom field values to an issue. You can set values for organization-level issue fields that have been defined for the repository's organization.\nAdding an empty array will clear all existing field values for the issue.\n\nThis endpoint supports the following field data types:\n- **`text`**: String values for text fields\n- **`single_select`**: Option names for single-select fields (must match an existing option name)\n- **`number`**: Numeric values for number fields\n- **`date`**: ISO 8601 date strings for date fields\n\nOnly users with push access to the repository can add issue field values. If you don't have the proper permissions, you'll receive a `403 Forbidden` response.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using t
</pre>

#### `chunk-0e81b6794d91344df3f4727830735797fe8e3fac9599f8dd7a982e72a753ce23`

- score: `12`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/rename-branch`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Renames a branch in a repository.\n\n&gt; [!NOTE]\n&gt; Although the API responds immediately, the branch rename process might take some extra time to complete in the background. You won't be able to push to the old branch name while the rename process is in progress. For more information, see \"[Renaming a branch](https://docs.github.com/github/administering-a-repository/renaming-a-branch)\".\n\nThe authenticated user must have push access to the branch. If the branch is the default branch, the authenticated user must also have admin or owner permissions.\n\nIn order to rename the default branch, fine-grained access tokens also need the `administration:write` repository permission.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/branches/branches#rename-a-branch"},"operationId":"repos/rename-branch","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/branch"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"new_name":"my_renamed_branch"}}},"schema":{"propertie
</pre>

#### `chunk-0f4fd479b03e601d79cf5b1336643ac1336ae7740942a64e5f08e306dc3ee213`

- score: `12`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:repos/add-status-check-contexts`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Protected branches are available in public repositories with GitHub Free and GitHub Free for organizations, and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud, and GitHub Enterprise Server. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/branches/branch-protection#add-status-check-contexts"},"operationId":"repos/add-status-check-contexts","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/branch"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"summary":"Example adding status checks to a branch protection rule","value":{"contexts":["continuous-integration/travis-ci","continuous-integration/jenkins"]}}},"schema":{"oneOf":[{"example":{"contexts":["contexts"]},"properties":{"contexts":{"description":"The name of the status checks","items":{"type":"string"},"type":"array
</pre>

#### `chunk-0fd1551aeb004a56214b40ec6147f0693abeb5d08c3606ebdf6bea75629599ef`

- score: `12`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/approve-suggestion`
- topic matches: `none`
- diagnostic matches: `422`, `403`, `404`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Approves a pending suggestion on an issue. Applies the proposed change (creating the corresponding timeline event), transitions the suggestion to `approved`, and dismisses any competing pending suggestions for the same change.\n\nRequires triage access to the repository. Approving a suggestion also requires permission to perform the change it applies (for example, setting the issue type, adding a label or assignee, or closing the issue); this only affects fine-grained access tokens and GitHub Apps whose permissions are narrower than the triage role. This endpoint only supports issues, not pull requests.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#approve-an-issue-suggestion"},"operationId":"issues/approve-suggestion","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"},{"description":"The unique identifier of the suggestion.","in":"path","name":"suggestion_id","required":true,"schema":{"type":"integer"}}],"responses":{"200":{"content":{"application/json"
</pre>

## `heldout-list-pulls-422-cause`

- cluster: `openapi-pair:pulls/list`
- role: `held_out_release_case`
- pattern: `status_cause`
- provisional claim: A 422 response from listing pull requests does not by itself establish the exact validation cause.
- total discovered candidates: 230
- candidates outside Phase 4 gold evidence: 211
- automated verdict: `review_required`

### Search terms

- topic: `pulls/list`, `list pull requests`, `/pulls`
- diagnostic: `422`, `validation failed`, `sort`, `direction`

### Highest-ranked candidates (max 25)

#### `chunk-0d1569942ce3eb27dd225f5c465d8d55795c6773041393e19ff2e8ff40b9e5b3`

- score: `57`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/list`
- topic matches: `pulls/list`, `list pull requests`, `/pulls`
- diagnostic matches: `422`, `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists pull requests in a specified repository.\n\nDraft pull requests are available in public repositories with GitHub\nFree and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing\nplans, and in public and private repositories with GitHub Team and GitHub Enterprise\nCloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products)\nin the GitHub Help documentation.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+j
</pre>

#### `chunk-d6f84e700ca07621d49f9acf93a7b400c99920d86bb9400a2284f79570f46e41`

- score: `57`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/list`
- topic matches: `pulls/list`, `list pull requests`, `/pulls`
- diagnostic matches: `422`, `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists pull requests in a specified repository.\n\nDraft pull requests are available in public repositories with GitHub\nFree and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing\nplans, and in public and private repositories with GitHub Team and GitHub Enterprise\nCloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products)\nin the GitHub Help documentation.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+j
</pre>

#### `chunk-f28dbff9088f8b00d911d491812a9dcff925fcea6e2f2a2e261747265f567e66`

- score: `49`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/list-files`
- topic matches: `pulls/list`, `list pull requests`, `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists the files in a specified pull request.\n\n&gt; [!NOTE]\n&gt; Responses include a maximum of 3000 files. The paginated response returns 30 files per page by default.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#list-pull-requests-files"},"operationId":"pulls/list-files","parameters":[
</pre>

#### `chunk-41ffdefaedbaf086b1281a79b6b25d1ed73933c2b0802ebcb23ab082c14f62e5`

- score: `47`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-for-repo`
- topic matches: `list pull requests`, `/pulls`
- diagnostic matches: `422`, `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"List issues in a repository. Only open issues will be listed.\n\n&gt; [!NOTE]\n&gt; GitHub's REST API considers every pull request an issue, but not every issue is a pull request. For this reason, \"Issues\" endpoints may return both issues and pull requests in the response. You can identify pull requests by the `pull_request` key. Be aware that the `id` of a pull request returned from \"Issues\" endpoints will be an _issue id_. To find out the pull request id, use the \"[List pull requests](https://docs.github.com/rest/pulls/pulls#list-pull-requests)\" endpoint.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML
</pre>

#### `chunk-8c748840079e1fa0fd891c3fa24e094bc7d11d88b9a50d180e4c9e20b87d93f1`

- score: `47`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list`
- topic matches: `list pull requests`, `/pulls`
- diagnostic matches: `422`, `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"List issues assigned to the authenticated user across all visible repositories including owned repositories, member\nrepositories, and organization repositories. You can use the `filter` query parameter to fetch issues that are not\nnecessarily assigned to you.\n\n&gt; [!NOTE]\n&gt; GitHub's REST API considers every pull request an issue, but not every issue is a pull request. For this reason, \"Issues\" endpoints may return both issues and pull requests in the response. You can identify pull requests by the `pull_request` key. Be aware that the `id` of a pull request returned from \"Issues\" endpoints will be an _issue id_. To find out the pull request id, use the \"[List pull requests](https://docs.github.com/rest/pulls/pulls#list-pull-requests)\" endpoint.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific me
</pre>

#### `chunk-614e8962dcc21793e7277e291bb150572d4f6f518145ca3e09b939ef9f738a5e`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-for-authenticated-user`
- topic matches: `list pull requests`, `/pulls`
- diagnostic matches: `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"List issues across owned and member repositories assigned to the authenticated user.\n\n&gt; [!NOTE]\n&gt; GitHub's REST API considers every pull request an issue, but not every issue is a pull request. For this reason, \"Issues\" endpoints may return both issues and pull requests in the response. You can identify pull requests by the `pull_request` key. Be aware that the `id` of a pull request returned from \"Issues\" endpoints will be an _issue id_. To find out the pull request id, use the \"[List pull requests](https://docs.github.com/rest/pulls/pulls#list-pull-requests)\" endpoint.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.htm
</pre>

#### `chunk-969bc23402db0c1a3d4c99669275c7a0834fceb980745461d19536f2e40c8033`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/list-review-comments-for-repo`
- topic matches: `pulls/list`, `/pulls`
- diagnostic matches: `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists review comments for all pull requests in a repository. By default,\nreview comments are in ascending order by ID.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github-commitcomment.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github-commitcomment.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github-commitcomment.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/comments#list-review-comments-in-a-repository"},"operationId":"pulls/
</pre>

#### `chunk-c39e33e5f991eeaf94b7a91c5b6643aeb7d603a9e0ba91144ba817caf4f6b475`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-for-org`
- topic matches: `list pull requests`, `/pulls`
- diagnostic matches: `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"List issues in an organization assigned to the authenticated user.\n\n&gt; [!NOTE]\n&gt; GitHub's REST API considers every pull request an issue, but not every issue is a pull request. For this reason, \"Issues\" endpoints may return both issues and pull requests in the response. You can identify pull requests by the `pull_request` key. Be aware that the `id` of a pull request returned from \"Issues\" endpoints will be an _issue id_. To find out the pull request id, use the \"[List pull requests](https://docs.github.com/rest/pulls/pulls#list-pull-requests)\" endpoint.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns
</pre>

#### `chunk-c9699394fda102de7dd5605eeeae97a5ff9cff36a1de39261ad1d6d5a7cb7b35`

- score: `43`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/list-review-comments`
- topic matches: `pulls/list`, `/pulls`
- diagnostic matches: `sort`, `direction`

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists all review comments for a specified pull request. By default, review comments\nare in ascending order by ID.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github-commitcomment.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github-commitcomment.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github-commitcomment.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/comments#list-review-comments-on-a-pull-request"},"operationId":"pulls/lis
</pre>

#### `chunk-369285132391ff80887ae5f629cdc3f8e51353126ac8a4fd8df22b4d1a86bb24`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/update-review`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Updates the contents of a specified review summary comment.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github-commitcomment.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github-commitcomment.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github-commitcomment.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/reviews#update-a-review-for-a-pull-request"},"operationId":"pulls/update-review","parameters":[{"$ref":"#/components/parameters/o
</pre>

#### `chunk-39b03b894e1f89fc54ff1bcdd8fa4d9173d2c040436a2ae1f2daa1ecf7449406`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/update`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markd
</pre>

#### `chunk-3b49054d748e4cfbf79ad140015fe2c6d73db66c9185f434fbced3a37c84d285`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/update`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markd
</pre>

#### `chunk-42d7b7bbff67f5e75d5363b820cd6182d79785cad570a499b58e253942474944`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:pulls/create`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\" and \"[Best practices for using the REST API](https://docs.githu
</pre>

#### `chunk-4822abf057b571cf16b0e79561614b306b380042a4e8f09996404099bc026e31`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-best-practices`
- topic matches: `/pulls`
- diagnostic matches: `sort`

<pre>
## Make requests that can be cached A conditional request only saves you time and rate limit if the endpoint returns `304 Not Modified`. The endpoint returns `304` when the representation that you requested has not changed since you saved its `etag` or `last-modified` value; unrelated response headers, such as the date, can still differ. To make `304` responses more likely when you poll, keep your requests stable and specific. Request only the data that you need. A smaller, more specific response changes less often, so it returns `304 Not Modified` more often. For example, to check the pull requests for one branch, filter the list by that branch instead of listing every pull request and searching the results yourself. Replace `HEAD-OWNER` with the account that owns the head branch; for a pull request from a fork, this is the account that owns the fork. Replace `BRANCH-NAME` with the name of the branch, and URL-encode it if it contains special characters such as `#` or `&amp;`: ```shell curl --include --header "Authorization: Bearer YOUR-TOKEN" "https://api.github.com/repos/octocat/Spoon-Knife/pulls?head=HEAD-OWNER:BRANCH-NAME" ``` If you page through a list, use a stable sort order. So
</pre>

#### `chunk-5c0a6eb1c4043357fb8fd8bb267e1b21daa364e42624039e78a2d8b193faec18`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/dismiss-review`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Dismisses a specified review on a pull request.\n\n&gt; [!NOTE]\n&gt; To dismiss a pull request review on a [protected branch](https://docs.github.com/rest/branches/branch-protection), you must be a repository administrator or be included in the list of people or teams who can dismiss pull request reviews.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github-commitcomment.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github-commitcomment.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github-commitcomment.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and
</pre>

#### `chunk-5e98a1c019997e43d007269f287eb35d7febe2426e9b187bf151082ebb128d93`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/merge-async`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Merges a pull request into the base branch in the background. Merging in this way allows certain types of errors to be retried, and avoids the risk of timeouts for particularly complex merges.\n\nThis is the required method for merging stacked PRs, but also supports unstacked PRs. When using this endpoint to merge a stacked pull request, all pull requests in the stack up to and including the requested PR will be merged into the base branch.\n\nThe response includes a UUID that can be used to fetch the result of the merge. If another asynchronous merge request has already been made for this pull request, the UUID of that request will be returned instead with a 409 response status to indicate that the merge options may be different from those that were requested. If there isn't an existing asynchronous merge request, a 202 response status is used.\n\nIf the pull request is already merged, the merge commit OID will be returned immediately with a 200 status.\n\nIf the pull request cannot be merged (e.g. because it is closed, or still a draft) this result will be returned immediately with a 400 response status.
</pre>

#### `chunk-6cf6f509c32862dc45dc8b6ba4676ac75a76e2d040637650ca029817d983f5c5`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:pulls/list-review-comments`
- topic matches: `pulls/list`
- diagnostic matches: `sort`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/parameters/sort","value":{"description":"The property to sort the results by.","in":"query","name":"sort","required":false,"schema":{"default":"created","enum":["created","updated"],"type":"string"}}}}]}
</pre>

#### `chunk-74f1f93d8305d71a7383663446c672b2e0c01cbd5cecf28318ce9e24433b3bc2`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `historical_comparison`
- authority: `historical`
- API version/snapshot: `2022-11-28`
- source IDs: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`, `openapi-historical-2022-11-28:issues/add-sub-issue`, `openapi-historical-2022-11-28:issues/create`, `openapi-historical-2022-11-28:issues/update`, `openapi-historical-2022-11-28:pulls/create`, `openapi-historical-2022-11-28:pulls/list`, `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`, `openapi-historical-2022-11-28:pulls/update`, `openapi-historical-2022-11-28:repos/create-for-authenticated-user`, `openapi-historical-2022-11-28:repos/create-in-org`
- topic matches: `pulls/list`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-77535aaddea9aeca80ab13f907e5048af9e86c336794212b441bdc880ea0d23b`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/submit-review`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Submits a pending review for a pull request. For more information about creating a pending review for a pull request, see \"[Create a review for a pull request](https://docs.github.com/rest/pulls/reviews#create-a-review-for-a-pull-request).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github-commitcomment.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github-commitcomment.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github-commitcomment.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github-commitcomment.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method do
</pre>

#### `chunk-779dd47fb0b30ba0e7b4fbdfbdccc3516c88e19aad9f170f4d26f37079997105`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:actions/disable-selected-repository-self-hosted-runners-organization`, `openapi-current-2026-03-10:actions/enable-selected-repository-self-hosted-runners-organization`, `openapi-current-2026-03-10:actions/get-concurrency-group-for-repository`, `openapi-current-2026-03-10:actions/list-concurrency-groups-for-repository`, `openapi-current-2026-03-10:actions/list-concurrency-groups-for-workflow-run`, `openapi-current-2026-03-10:actions/set-artifact-and-log-retention-settings-organization`, `openapi-current-2026-03-10:actions/set-artifact-and-log-retention-settings-repository`, `openapi-current-2026-03-10:actions/set-fork-pr-contributor-approval-permissions-organization`, `openapi-current-2026-03-10:actions/set-fork-pr-contributor-approval-permissions-repository`, `openapi-current-2026-03-10:actions/set-private-repo-fork-pr-workflows-settings-organization`, `openapi-current-2026-03-10:actions/set-private-repo-fork-pr-workflows-settings-repository`, `openapi-current-2026-03-10:actions/set-selected-repositories-self-hosted-runners-organization`, `openapi-current-2026-03-10:actions/set-self-hosted-runners-permissions-organization`, `openapi-current-2026-03-10:issues/add-issue-field-values`, `openapi-current-2026-03-10:issues/add-labels`, `openapi-current-2026-03-10:issues/approve-suggestion`, `openapi-current-2026-03-10:issues/create-comment`, `openapi-current-2026-03-10:issues/create-label`, `openapi-current-2026-03-10:issues/create-milestone`, `openapi-current-2026-03-10:issues/delete-issue-field-value`, `openapi-current-2026-03-10:issues/dismiss-suggestion`, `openapi-current-2026-03-10:issues/list`, `openapi-current-2026-03-10:issues/list-comments-for-repo`, `openapi-current-2026-03-10:issues/list-events-for-repo`, `openapi-current-2026-03-10:issues/list-for-repo`, `openapi-current-2026-03-10:issues/list-suggestions`, `openapi-current-2026-03-10:issues/lock`, `openapi-current-2026-03-10:issues/pin-comment`, `openapi-current-2026-03-10:issues/set-issue-field-values`, `openapi-current-2026-03-10:issues/set-labels`, `openapi-current-2026-03-10:issues/update-comment`, `openapi-current-2026-03-10:pulls/create-review-comment`, `openapi-current-2026-03-10:pulls/list-files`, `openapi-current-2026-03-10:pulls/merge`, `openapi-current-2026-03-10:pulls/merge-async`, `openapi-current-2026-03-10:pulls/update-branch`, `openapi-current-2026-03-10:repos/add-app-access-restrictions`, `openapi-current-2026-03-10:repos/add-status-check-contexts`, `openapi-current-2026-03-10:repos/add-team-access-restrictions`, `openapi-current-2026-03-10:repos/add-user-access-restrictions`, `openapi-current-2026-03-10:repos/create-attestation`, `openapi-current-2026-03-10:repos/create-autolink`, `openapi-current-2026-03-10:repos/create-commit-comment`, `openapi-current-2026-03-10:repos/create-deploy-key`, `openapi-current-2026-03-10:repos/create-deployment`, `openapi-current-2026-03-10:repos/create-deployment-status`, `openapi-current-2026-03-10:repos/create-dispatch-event`, `openapi-current-2026-03-10:repos/create-fork`, `openapi-current-2026-03-10:repos/create-or-update-file-contents`, `openapi-current-2026-03-10:repos/create-org-ruleset`, `openapi-current-2026-03-10:repos/create-pages-deployment`, `openapi-current-2026-03-10:repos/create-pages-site`, `openapi-current-2026-03-10:repos/create-release`, `openapi-current-2026-03-10:repos/create-repo-ruleset`, `openapi-current-2026-03-10:repos/create-webhook`, `openapi-current-2026-03-10:repos/custom-properties-for-repos-create-or-update-repository-values`, `openapi-current-2026-03-10:repos/delete-file`, `openapi-current-2026-03-10:repos/delete-pages-site`, `openapi-current-2026-03-10:repos/get-commit`, `openapi-current-2026-03-10:repos/get-readme`, `openapi-current-2026-03-10:repos/get-readme-in-directory`, `openapi-current-2026-03-10:repos/get-webhook-delivery`, `openapi-current-2026-03-10:repos/list-branches-for-head-commit`, `openapi-current-2026-03-10:repos/list-for-authenticated-user`, `openapi-current-2026-03-10:repos/list-public`, `openapi-current-2026-03-10:repos/list-webhook-deliveries`, `openapi-current-2026-03-10:repos/merge`, `openapi-current-2026-03-10:repos/redeliver-webhook-delivery`, `openapi-current-2026-03-10:repos/remove-app-access-restrictions`, `openapi-current-2026-03-10:repos/remove-collaborator`, `openapi-current-2026-03-10:repos/remove-status-check-contexts`, `openapi-current-2026-03-10:repos/remove-team-access-restrictions`, `openapi-current-2026-03-10:repos/remove-user-access-restrictions`, `openapi-current-2026-03-10:repos/rename-branch`, `openapi-current-2026-03-10:repos/set-app-access-restrictions`, `openapi-current-2026-03-10:repos/set-status-check-contexts`, `openapi-current-2026-03-10:repos/set-team-access-restrictions`, `openapi-current-2026-03-10:repos/set-user-access-restrictions`, `openapi-current-2026-03-10:repos/update`, `openapi-current-2026-03-10:repos/update-information-about-pages-site`, `openapi-current-2026-03-10:repos/update-org-ruleset`, `openapi-current-2026-03-10:repos/update-pull-request-review-protection`, `openapi-current-2026-03-10:repos/update-repo-ruleset`, `openapi-current-2026-03-10:repos/update-status-check-protection`, `openapi-current-2026-03-10:repos/update-webhook`
- topic matches: `pulls/list`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>

#### `chunk-937f6695df9910d351b879dfd90bc46786341a98593e317acf58bcfe00203894`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/create-review-comment`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a review comment on the diff of a specified pull request. To add a regular comment to a pull request timeline, see \"[Create an issue comment](https://docs.github.com/rest/issues/comments#create-an-issue-comment).\"\n\nIf your comment applies to more than one line in the pull request diff, you should use the parameters `line`, `side`, and optionally `start_line` and `start_side` in your request.\n\nThe `position` parameter is closing down. If you use `position`, the `line`, `side`, `start_line`, and `start_side` parameters are not required.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom
</pre>

#### `chunk-9ded1e1dc9da4f59e8800fe3565472c3e8dd55ce0c56869ee91cf49c32ebbc5a`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:pulls/update-branch`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
{"fragments":[{"path":[],"value":{"method":"put","operation":{"description":"Updates the pull request branch with the latest upstream changes by merging HEAD from the base branch into the pull request branch.\nNote: If making a request on behalf of a GitHub App you must also have permissions to write the contents of the head repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#update-a-pull-request-branch"},"operationId":"pulls/update-branch","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"expected_head_sha":"6dcb09b5b57875f334f61aebed695e2e4193db5e"}}},"schema":{"nullable":true,"properties":{"expected_head_sha":{"description":"The expected SHA of the pull request's HEAD ref. This is the most recent commit on the pull request's branch. If the expected SHA does not match the pull request's HEAD, you will receive a `422 Unprocessable Entity` status. You can use the \"[List commits](https://docs.github.com/rest/commits/commits#list-commits)\" endpoin
</pre>

#### `chunk-aab4129e4bb838cd0c62c3f8927832a3e6b4f6b3004791373d71661b624e5b45`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-breaking-changes`
- topic matches: `/pulls`
- diagnostic matches: `422`

<pre>
- `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}` - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue` - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` - `GET /events` - `GET /installation/repositories` - `GET /issues` - `GET /networks/{owner}/{repo}/events` - `GET /notifications` - `GET /notifications/threads/{thread_id}` - `GET /orgs/{org}/actions/permissions/repositories` - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories` - `GET /orgs/{org}/actions/runner-groups/{runner_group_id}/repositories` - `GET /orgs/{org}/actions/secrets/{secret_name}/repositories` - `GET /orgs/{org}/actions/variables/{name}/repositories` - `GET /orgs/{org}/codespaces` - `GET /orgs/{org}/codespaces/secrets/{secret_name}/repositories` - `GET /orgs/{org}/dependabot/secrets/{secret_name}/repositories` - `GET /orgs/{org}/docker/conflicts` - `GET /orgs/{org}/events` - `GET /orgs/{org}/issues` - `GET /orgs/{org}/members/{username}/codespaces` - `GET /orgs/{org}/migrations` - `GET /orgs/{org}/migrations/{migration_id}` - `GET /orgs/{org}/migrations/{mi
</pre>

#### `chunk-ae6500530a333bc9c4e22391d66658e15a22d8b95500170cbc0ae422fb2cf66f`

- score: `29`
- Phase 4 gold evidence: `true`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `docs-best-practices`
- topic matches: `/pulls`
- diagnostic matches: `direction`

<pre>
--- title: Best practices for using the REST API intro: 'Follow these best practices when using GitHub''s API.' redirect_from: - /guides/best-practices-for-integrators - /v3/guides/best-practices-for-integrators - /rest/guides/best-practices-for-integrators - /rest/guides/best-practices-for-using-the-rest-api versions: fpt: '*' ghes: '*' ghec: '*' shortTitle: Best practices category: - Learn about the REST API --- ## Avoid polling You should subscribe to webhook events instead of polling the API for data. This will help your integration stay within the API rate limit. For more information, see [/webhooks](/webhooks). If you cannot use webhooks and you must poll the API, poll as efficiently as possible to avoid exceeding the rate limit: * Poll only as often as you need to, on a fixed schedule. If a response includes an `x-poll-interval` header, wait at least that many seconds before you poll the same endpoint again. * Make authenticated conditional requests, so that unchanged data does not count against your primary rate limit. For more information, see [Use conditional requests](#use-conditional-requests). * Request only the data that you need, and keep responses stable, so that mo
</pre>

#### `chunk-b2bc4ff09e8a4d33ded81556b6e442081bb05dfb99780a4f904024be5a0e77ff`

- score: `29`
- Phase 4 gold evidence: `false`
- source state: `current`
- authority: `authoritative`
- API version/snapshot: `2026-03-10`
- source IDs: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`, `openapi-current-2026-03-10:issues/add-sub-issue`, `openapi-current-2026-03-10:issues/create`, `openapi-current-2026-03-10:issues/update`, `openapi-current-2026-03-10:pulls/create`, `openapi-current-2026-03-10:pulls/list`, `openapi-current-2026-03-10:pulls/remove-requested-reviewers`, `openapi-current-2026-03-10:pulls/update`, `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-for-authenticated-user`, `openapi-current-2026-03-10:repos/create-in-org`
- topic matches: `pulls/list`
- diagnostic matches: `validation failed`

<pre>
{"fragments":[{"path":[],"value":{"reference":"#/components/responses/validation_failed","value":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/validation-error"}}},"description":"Validation failed, or the endpoint has been spammed."}}}]}
</pre>
