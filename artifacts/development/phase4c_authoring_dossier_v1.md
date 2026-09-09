# Phase 4C Authoring Dossier V1

**Purpose:** deterministic, read-only review of the frozen evidence available for canonical case authoring.

**Phase 4 constitution SHA256:** `e2f1ca0985157ea43e7e648fa431e30c2b139cf9b3ea364d7356e8e11311816d`

**Phase 3D chunk manifest SHA256:** `1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd`

> This is an authoring aid. It does not change cluster roles, expand gold evidence, authorize baseline execution, or enter the runtime RAG input.

> Evidence text below is HTML-escaped for review. The authoritative source identity is the recorded content path and SHA256.

## Cluster: `guidance:docs-api-versions`

- evaluation role: `evaluation_development_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-api-versions`

### Current evidence: `chunk-983a0027263f77cae71fe270dd205876fd7df230c10e5b64d2d069352dc1e97d`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-983a0027263f77cae71fe270dd205876fd7df230c10e5b64d2d069352dc1e97d.md`
- content SHA256: `c87d8451283cfadc0512d54cefac720c0a258c7e7f399006fa0a69f570891955`
- byte count: `5532`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About API versioning` ? `Specifying an API version` ? `Upgrading to a new API version` ? `API version closing down` ? `Exceptions to standard versioning` ? `Security, availability, and reliability issues` ? `Low-usage services` ? `Supported API versions`
- parent source ID: `docs-api-versions`
- parent document ID: `authored-docs-api-versions`
- parent normalized SHA256: `c87d8451283cfadc0512d54cefac720c0a258c7e7f399006fa0a69f570891955`

<details>
<summary>Evidence content</summary>

<pre>
---
title: API Versions
shortTitle: API Versions
intro: Learn how to specify which REST API version to use whenever you make a request to the REST API.
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
redirect_from:
  - /rest/overview/api-versions
category:
  - Learn about the REST API
---

## About API versioning

The GitHub REST API is versioned. The API version name is based on the date when the API version was released. For example, the API version `2026-03-10` was released on Tue, 10 Mar 2026.

Breaking changes are changes that can potentially break an integration. Breaking changes will be released in a new API version. We will provide advance notice before releasing breaking changes. Breaking changes include:

* Removing an entire operation
* Removing or renaming a parameter
* Removing or renaming a response field
* Adding a new required parameter
* Making a previously optional parameter required
* Changing the type of a parameter or response field
* Removing enum values
* Adding a new validation rule to an existing parameter
* Changing authentication or authorization requirements

Any additive (non-breaking) changes will be available in all supported API versions. Additive changes are changes that should not break an integration. Additive changes include:

* Adding an operation
* Adding an optional parameter
* Adding an optional request header
* Adding a response field
* Adding a response header
* Adding enum values

When a new REST API version is released, the previous API version will be supported for at least 24 more months following the release of the new API version.




## Specifying an API version

You should use the `X-GitHub-Api-Version` header to specify an API version. For example:

```shell
curl --header "X-GitHub-Api-Version:2026-03-10"
 https://api.github.com/zen
```

Requests without the `X-GitHub-Api-Version` header will default to use the `2022-11-28` version.

If you specify an API version that is no longer supported, you will receive a `410 Gone` response.

## Upgrading to a new API version

Before upgrading to a new REST API version, you should read the changelog of breaking changes for the new API version to understand what breaking changes are included and to learn more about how to upgrade to that specific API version. For more information, see [/rest/about-the-rest-api/breaking-changes](/rest/about-the-rest-api/breaking-changes).

When you update your integration to specify the new API version in the `X-GitHub-Api-Version` header, you'll also need to make any changes required for your integration to work with the new API version.

Once your integration is updated, test your integration to verify that it works with the new API version.

## API version closing down

API versions are supported for 24 months after a newer API version is released.

While a version is within its support window but approaching  closing down, GitHub includes the following headers in API responses to help you prepare for migration:

* `Deprecation` — The date when the API version will be closing down, formatted as an HTTP date per [RFC 7231](https://tools.ietf.org/html/rfc7231#section-7.1.1.1). For example: `Wed, 27 Nov 2019 14:34:29 GMT`. &lt;!-- markdownlint-disable-line GHD046 --&gt;
* `Sunset` — The date when the API version will be completely removed (retired), after which requests will return a `410 Gone` response. Follows [RFC 8594](https://tools.ietf.org/html/rfc8594). For example: `Fri, 27 Nov 2020 14:34:29 GMT`. &lt;!-- markdownlint-disable-line GHD046 --&gt;

After the support window ends:

* Requests that specify a closing down API version receive a `410 Gone` response.
* Requests that do not specify an API version default to the next oldest supported version, not the closing down version. If you rely on unversioned requests, you may observe behavioral changes as older versions are removed from support.

For more information on migrating to a newer API version, see [/rest/about-the-rest-api/breaking-changes](/rest/about-the-rest-api/breaking-changes).

## Exceptions to standard versioning

In rare cases, GitHub may make changes outside the normal API versioning cadence. These are exceptional interventions that do not alter the standard versioning guarantees for most integrators.

### Security, availability, and reliability issues

Critical security vulnerabilities, data exposure risks, or severe reliability issues may require changes outside the normal release schedule. GitHub may release an unscheduled API version, backport fixes to supported versions, or in rare cases, introduce a breaking change to an existing version to protect users and platform integrity.

GitHub will communicate such changes through release notes, changelogs, and direct communication explaining what changed and why. Where feasible, advance notice will be provided. Immediate action may be taken without advance notice when required.

### Low-usage services

For certain services with very low usage, GitHub may deprecate functionality outside the standard versioning process. In these cases, GitHub will communicate the intent and reach out to affected integrators directly.

## Supported API versions

The following REST API versions are currently supported.

| API version | End of support date |
| --- | --- |
| `2026-03-10` | Not yet scheduled |
| `2022-11-28` | March 10, 2028 |

You can also make an API request to get all of the supported API versions. For more information, see [/rest/meta/meta#get-all-api-versions](/rest/meta/meta#get-all-api-versions).

</pre>

</details>

## Cluster: `guidance:docs-authentication`

- evaluation role: `intervention_tuning_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-authentication`

### Current evidence: `chunk-5d04e2ccdfe8bd57d67d12bda6baf3a623435b28c003f2661238c6998b696dda`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-5d04e2ccdfe8bd57d67d12bda6baf3a623435b28c003f2661238c6998b696dda.md`
- content SHA256: `d91a6aa7b3d1b029cffa45819fdfda23f2ab4fc4b705e575ae2b6fc64b3076bf`
- byte count: `6847`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About authentication` ? `Failed login limit` ? `Authenticating with a personal access token` ? `Personal access tokens and SAML SSO` ? `Authenticating with a token generated by an app`
- parent source ID: `docs-authentication`
- parent document ID: `authored-docs-authentication`
- parent normalized SHA256: `81055b628f2d3ae348ccbb6eecc16df7b4fa5180daf3166afcc8e82bb6cafbcb`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Authenticating to the REST API
intro: You can authenticate to the REST API to access more endpoints and have a higher rate limit.
redirect_from:
  - /v3/auth
  - /rest/overview/other-authentication-methods
  - /rest/overview/authenticating-to-the-rest-api
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
shortTitle: Authenticating
category:
  - Authenticate API requests
---

## About authentication

Many REST API endpoints require authentication or return additional information if you are authenticated. Additionally, you can make more requests per hour when you are authenticated.

To authenticate your request, you will need to provide an authentication token with the required scopes or permissions. There a few different ways to get a token: You can create a personal access token, generate a token with a GitHub App, or use the built-in `GITHUB_TOKEN` in a GitHub Actions workflow.

After creating a token, you can authenticate your request by sending the token in the `Authorization` header of your request. For example, in the following request, replace `YOUR-TOKEN` with a reference to your token:

```shell
curl --request GET \
--url "https://api.github.com/octocat" \
--header "Authorization: Bearer YOUR-TOKEN" \
--header "X-GitHub-Api-Version: 2026-03-10"
```

&gt; [!NOTE]
&gt; In most cases, you can use `Authorization: Bearer` or `Authorization: token` to pass a token. However, if you are passing a JSON web token (JWT), you must use `Authorization: Bearer`.


### Failed login limit

If you try to use a REST API endpoint without a token or with a token that has insufficient permissions, you will receive a `404 Not Found` or `403 Forbidden` response. Authenticating with invalid credentials will initially return a `401 Unauthorized` response.

After detecting several requests with invalid credentials within a short period, the API will temporarily reject all authentication attempts for that user (including ones with valid credentials) with a `403 Forbidden` response. For more information, see [/rest/using-the-rest-api/rate-limits-for-the-rest-api](/rest/using-the-rest-api/rate-limits-for-the-rest-api).

## Authenticating with a personal access token

If you want to use the GitHub REST API for personal use, you can create a personal access token. If possible, GitHub recommends that you use a fine-grained personal access token instead of a personal access token (classic). For more information about creating a personal access token, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

If you are using a fine-grained personal access token, your fine-grained personal access token requires specific permissions in order to access each REST API endpoint. The REST API reference document for each endpoint states whether the endpoint works with fine-grained personal access tokens and states what permissions are required in order for the token to use the endpoint. Some endpoints may require multiple permissions, and some endpoints may require one of multiple permissions. For an overview of which REST API endpoints a fine-grained personal access token can access with each permission, see [/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens](/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens).

If you are using a personal access token (classic), it requires specific scopes in order to access each REST API endpoint. For general guidance about what scopes to choose, see [/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes](/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).

Personal access tokens act as your identity (limited by the scopes or permissions you selected) when you make requests to the REST API. As such, it is important to keep your personal access tokens secure. For more information about keeping your personal access tokens secure, see [/rest/authentication/keeping-your-api-credentials-secure?apiVersion=2022-11-28](/rest/authentication/keeping-your-api-credentials-secure?apiVersion=2022-11-28).

### Personal access tokens and SAML SSO

If you use a personal access token (classic) to access an organization that enforces SAML single sign-on (SSO) for authentication, you will need to authorize your token after creation. Fine-grained personal access tokens are authorized during token creation, before access to the organization is granted. For more information, see [/authentication/authenticating-with-single-sign-on/authorizing-a-personal-access-token-for-use-with-single-sign-on](/authentication/authenticating-with-single-sign-on/authorizing-a-personal-access-token-for-use-with-single-sign-on).

If you do not authorize your personal access token (classic) for SAML SSO before you try to use it to access a single organization that enforces SAML SSO, you may receive a `404 Not Found` or a `403 Forbidden` error. If you receive a `403 Forbidden` error, the `X-GitHub-SSO` header will include a URL that you can follow to authorize your token. The URL expires after one hour.

If you do not authorize your personal access token (classic) for SAML SSO before you try to use it to access multiple organizations, the API will not return results from the organizations that require SAML SSO and the `X-GitHub-SSO` header will indicate the ID of the organizations that require SAML SSO authorization of your personal access token (classic). For example: `X-GitHub-SSO: partial-results; organizations=21955855,20582480`.



## Authenticating with a token generated by an app

If you want to use the API for an organization or on behalf of another user, GitHub recommends that you use a GitHub App. For more information, see [/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app](/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app).

The REST API reference documentation for each endpoint states whether the endpoint works with GitHub Apps and states what permissions are required in order for the app to use the endpoint. Some endpoints may require multiple permissions, and some endpoints may require one of multiple permissions. For an overview of which REST API endpoints a GitHub App can access with each permission, see [/rest/authentication/permissions-required-for-github-apps](/rest/authentication/permissions-required-for-github-apps).

You can also create an OAuth token with an OAuth app to access the REST API. However, GitHub recommends that you use a GitHub App instead. GitHub Apps allow more control over the access and permission that the app has.

Access tokens created by apps are automatically authorized for SAML SSO.


</pre>

</details>

### Current evidence: `chunk-9acc16505e9259b57c6bbb30df45d6a4cbcf321495bf593087e573552ce437d0`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-9acc16505e9259b57c6bbb30df45d6a4cbcf321495bf593087e573552ce437d0.md`
- content SHA256: `4b369c788fc9df92d7bf7dd724e4c5b33d78626fb09d4f532c7f21095bd5fd46`
- byte count: `5454`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Using basic authentication` ? `Authenticating in a GitHub Actions workflow` ? `Authenticating in a GitHub Actions workflow using GitHub CLI` ? `Authenticating in a GitHub Actions workflow using `curl`` ? `Authenticating in a GitHub Actions workflow using JavaScript` ? `Authenticating with username and password` ? `Further reading`
- parent source ID: `docs-authentication`
- parent document ID: `authored-docs-authentication`
- parent normalized SHA256: `81055b628f2d3ae348ccbb6eecc16df7b4fa5180daf3166afcc8e82bb6cafbcb`

<details>
<summary>Evidence content</summary>

<pre>
### Using basic authentication

Some REST API endpoints for GitHub Apps and OAuth apps require you to use basic authentication to access the endpoint. You will use the app's client ID as the username and the app's client secret as the password.

For example:

```shell
curl --request POST \
--url "https://api.github.com/applications/YOUR_CLIENT_ID/token" \
--user "YOUR_CLIENT_ID:YOUR_CLIENT_SECRET" \
--header "Accept: application/vnd.github+json" \
--header "X-GitHub-Api-Version: 2026-03-10" \
--data '{
  "access_token": "ACCESS_TOKEN_TO_CHECK"
}'
```

The client ID and client secret are associated with the app, not with the owner of the app or a user who authorized the app. They are used to perform operations on behalf of the app, such as creating access tokens.

If you are the owner of a GitHub App or OAuth app, or if you are an app manager for a GitHub App, you can find the client ID and generate a client secret on the settings page for your app. To navigate to your app's settings page:

1. In the upper-right corner of any page on GitHub, click your profile picture.
1. Navigate to your account settings.
   * For an app owned by a personal account, click **Settings**.
   * For an app owned by an organization:
     1. Click **Your organizations**.
     1. To the right of the organization, click **Settings**.
1. In the left sidebar, click **code Developer settings**.

1. In the left sidebar, click **GitHub Apps** or **OAuth apps**.
1. For GitHub Apps, to the right of the GitHub App you want to access, click **Edit**. For OAuth apps, click the app that you want to access.
1. Next to **Client ID**, you will see the client ID for your app.
1. Next to **Client secrets**, click **Generate a new client secret** to generate a client secret for your app.

## Authenticating in a GitHub Actions workflow

If you want to use the API in a GitHub Actions workflow, GitHub recommends that you authenticate with the built-in `GITHUB_TOKEN` instead of creating a token. You can grant permissions to the `GITHUB_TOKEN` with the `permissions` key. For more information, see [/actions/tutorials/authenticate-with-github_token#modifying-the-permissions-for-the-github_token](/actions/tutorials/authenticate-with-github_token#modifying-the-permissions-for-the-github_token).

If this is not possible, you can store your token as a secret and use the name of your secret in your GitHub Actions workflow. For more information about secrets, see [/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets](/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

### Authenticating in a GitHub Actions workflow using GitHub CLI

To make an authenticated request to the API in a GitHub Actions workflow using GitHub CLI, you can store the value of `GITHUB_TOKEN` as an environment variable, and use the `run` keyword to execute the GitHub CLI `api` subcommand. For more information about the `run` keyword, see [/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsrun](/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsrun).

In the following example workflow, replace `PATH` with the path of the endpoint. For more information about the path, see [/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=cli#path](/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=cli#path).

```yaml
jobs:
  use_api:
    runs-on: ubuntu-latest
    permissions: {}
    steps:
      - env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh api /PATH
```

### Authenticating in a GitHub Actions workflow using `curl`

To make an authenticated request to the API in a GitHub Actions workflow using `curl`, you can store the value of `GITHUB_TOKEN` as an environment variable, and use the `run` keyword to execute a `curl` request to the API. For more information about the `run` keyword, see [/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsrun](/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsrun).

In the following example workflow, replace `PATH` with the path of the endpoint. For more information about the path, see [/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=cli#path](/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=cli#path).

```yaml copy
jobs:
  use_api:
    runs-on: ubuntu-latest
    permissions: {}
    steps:
      - env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          curl --request GET \
          --url "https://api.github.com/PATH" \
          --header "Authorization: Bearer $GH_TOKEN"
```

### Authenticating in a GitHub Actions workflow using JavaScript

For an example of how to authenticate in a GitHub Actions workflow using JavaScript, see [/rest/guides/scripting-with-the-rest-api-and-javascript#authenticating-in-github-actions](/rest/guides/scripting-with-the-rest-api-and-javascript#authenticating-in-github-actions).

## Authenticating with username and password



Authentication with username and password is not supported. If you try to authenticate with user name and password, you will receive a 4xx error.



## Further reading

* [/rest/authentication/keeping-your-api-credentials-secure](/rest/authentication/keeping-your-api-credentials-secure)
* [/rest/using-the-rest-api/getting-started-with-the-rest-api#authentication](/rest/using-the-rest-api/getting-started-with-the-rest-api#authentication)

</pre>

</details>

## Cluster: `guidance:docs-best-practices`

- evaluation role: `held_out_release_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-best-practices`

### Current evidence: `chunk-4822abf057b571cf16b0e79561614b306b380042a4e8f09996404099bc026e31`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-4822abf057b571cf16b0e79561614b306b380042a4e8f09996404099bc026e31.md`
- content SHA256: `b03c2ef785ce68a0a98510d44dd30bb1ea672fa2f890328fea79912c4a65a0b9`
- byte count: `3562`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Make requests that can be cached` ? `Do not ignore errors` ? `Further reading`
- parent source ID: `docs-best-practices`
- parent document ID: `authored-docs-best-practices`
- parent normalized SHA256: `6412524ae8f0048ca20eb52e9c2475dff5cdee3ae2930c8ce3fe361dac5b7ed9`

<details>
<summary>Evidence content</summary>

<pre>
## Make requests that can be cached

A conditional request only saves you time and rate limit if the endpoint returns `304 Not Modified`. The endpoint returns `304` when the representation that you requested has not changed since you saved its `etag` or `last-modified` value; unrelated response headers, such as the date, can still differ. To make `304` responses more likely when you poll, keep your requests stable and specific.

Request only the data that you need. A smaller, more specific response changes less often, so it returns `304 Not Modified` more often. For example, to check the pull requests for one branch, filter the list by that branch instead of listing every pull request and searching the results yourself. Replace `HEAD-OWNER` with the account that owns the head branch; for a pull request from a fork, this is the account that owns the fork. Replace `BRANCH-NAME` with the name of the branch, and URL-encode it if it contains special characters such as `#` or `&amp;`:

```shell
curl --include --header "Authorization: Bearer YOUR-TOKEN" "https://api.github.com/repos/octocat/Spoon-Knife/pulls?head=HEAD-OWNER:BRANCH-NAME"
```

If you page through a list, use a stable sort order. Some parameters, such as `sort=updated`, reorder the list whenever an item changes. When an item moves to a new position, the items between its old and new positions shift onto different pages, so pages that you already fetched can return new data instead of `304 Not Modified`. A stable order, such as the default, stops updates to existing items from reordering the list, although adding or removing items can still shift entries onto other pages.

Use the same parameters every time you poll the same data. A different page size, page number, or filter produces a different response with a different `etag`.

## Do not ignore errors

You should not ignore repeated `4xx` and `5xx` error codes. Instead, you should ensure that you are correctly interacting with the API. For example, if an endpoint requests a string and you are passing it a numeric value, you will receive a validation error. Similarly, attempting to access an unauthorized or nonexistent endpoint will result in a `4xx` error.

If you are polling and a resource repeatedly returns a `404 Not Found` response, do not keep requesting it on every poll. First, make sure that the `404` is not caused by authentication or authorization. GitHub returns a `404 Not Found` response instead of a `403 Forbidden` response for some private resources when your credentials do not grant access, so a `404` does not always mean that the resource is absent. For more information, see [/rest/using-the-rest-api/troubleshooting-the-rest-api#404-not-found-for-an-existing-resource](/rest/using-the-rest-api/troubleshooting-the-rest-api#404-not-found-for-an-existing-resource). Once you have confirmed that your credentials are correct, wait much longer before you check again, or check again only when you have a reason to believe that the resource now exists. Repeatedly requesting a missing resource wastes your rate limit and can trigger a secondary rate limit.

Intentionally ignoring repeated validation errors may result in the suspension of your app for abuse.

## Further reading

* [/webhooks/using-webhooks/best-practices-for-using-webhooks](/webhooks/using-webhooks/best-practices-for-using-webhooks)
* [/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app](/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app)

</pre>

</details>

### Current evidence: `chunk-ae6500530a333bc9c4e22391d66658e15a22d8b95500170cbc0ae422fb2cf66f`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-ae6500530a333bc9c4e22391d66658e15a22d8b95500170cbc0ae422fb2cf66f.md`
- content SHA256: `0f16ecad61faf29da253453c061751cbffce5df2a04b4a01a342c136ea8b8d6f`
- byte count: `6796`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Avoid polling` ? `Make authenticated requests` ? `Avoid concurrent requests` ? `Pause between mutative requests` ? `Handle rate limit errors appropriately` ? `Follow redirects` ? `Do not manually parse URLs` ? `Use conditional requests`
- parent source ID: `docs-best-practices`
- parent document ID: `authored-docs-best-practices`
- parent normalized SHA256: `6412524ae8f0048ca20eb52e9c2475dff5cdee3ae2930c8ce3fe361dac5b7ed9`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Best practices for using the REST API
intro: 'Follow these best practices when using GitHub''s API.'
redirect_from:
  - /guides/best-practices-for-integrators
  - /v3/guides/best-practices-for-integrators
  - /rest/guides/best-practices-for-integrators
  - /rest/guides/best-practices-for-using-the-rest-api
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
shortTitle: Best practices
category:
  - Learn about the REST API
---



## Avoid polling

You should subscribe to webhook events instead of polling the API for data. This will help your integration stay within the API rate limit. For more information, see [/webhooks](/webhooks).

If you cannot use webhooks and you must poll the API, poll as efficiently as possible to avoid exceeding the rate limit:

* Poll only as often as you need to, on a fixed schedule. If a response includes an `x-poll-interval` header, wait at least that many seconds before you poll the same endpoint again.
* Make authenticated conditional requests, so that unchanged data does not count against your primary rate limit. For more information, see [Use conditional requests](#use-conditional-requests).
* Request only the data that you need, and keep responses stable, so that more of your polls return `304 Not Modified`. For more information, see [Make requests that can be cached](#make-requests-that-can-be-cached).

## Make authenticated requests

Authenticated requests have a higher primary rate limit than unauthenticated requests. To avoid exceeding the rate limit, you should make authenticated requests. For more information, see [/rest/using-the-rest-api/rate-limits-for-the-rest-api](/rest/using-the-rest-api/rate-limits-for-the-rest-api).

## Avoid concurrent requests

To avoid exceeding secondary rate limits, you should make requests serially instead of concurrently. To achieve this, you can implement a queue system for requests.

## Pause between mutative requests

If you are making a large number of `POST`, `PATCH`, `PUT`, or `DELETE` requests, wait at least one second between each request. This will help you avoid secondary rate limits.

## Handle rate limit errors appropriately

If you receive a rate limit error, you should stop making requests temporarily according to these guidelines:

* If the `retry-after` response header is present, you should not retry your request until after that many seconds has elapsed.
* If the `x-ratelimit-remaining` header is `0`, you should not make another request until after the time specified by the `x-ratelimit-reset` header. The `x-ratelimit-reset` header is in UTC epoch seconds.
* Otherwise, wait for at least one minute before retrying. If your request continues to fail due to a secondary rate limit, wait for an exponentially increasing amount of time between retries, and throw an error after a specific number of retries.

Continuing to make requests while you are rate limited may result in the banning of your integration.




## Follow redirects

The GitHub REST API uses HTTP redirection where appropriate. You should assume that any
request may result in a redirection. Receiving an HTTP redirection is not an error, and you should follow the redirect.

A `301` status code indicates permanent redirection. You should repeat your request to the URL specified by the `location` header. Additionally, you should update your code to use this URL for future requests.

A `302` or `307` status code indicates temporary redirection. You should repeat your request to the URL specified by the `location` header. However, you should not update your code to use this URL for future requests.

Other redirection status codes may be used in accordance with HTTP specifications.

## Do not manually parse URLs

Many API endpoints return URL values for fields in the response body. You should not try to parse these URLs or to predict the structure of future URLs. This can cause your integration to break if GitHub changes the structure of the URL in the future. Instead, you should look for a field that contains the information that you need. For example, the endpoint to create an issue returns an `html_url` field with a value like `https://github.com/octocat/Hello-World/issues/1347` and a `number` field with a value like `1347`. If you need to know the number of the issue, use the `number` field instead of parsing the `html_url` field.

Similarly, you should not try to manually construct pagination queries. Instead, you should use the link headers to determine what pages of results you can request. For more information, see [/rest/using-the-rest-api/using-pagination-in-the-rest-api](/rest/using-the-rest-api/using-pagination-in-the-rest-api).

## Use conditional requests

Most endpoints return an `etag` header, and many endpoints return a `last-modified` header. You can use the values of these headers to make conditional `GET` requests. If the response has not changed, you will receive a `304 Not Modified` response. Making a conditional request does not count against your primary rate limit if a `304` response is returned and the request was made while correctly authorized with an `Authorization` header. This makes conditional requests especially useful when you poll an endpoint, because each `304 Not Modified` response is fast and does not use your rate limit.

In the following examples, replace `YOUR-TOKEN` with your access token.

To make a conditional request with an `etag`:

1. Make a request and save the value of the `etag` header from the response.

   ```shell
   curl --include --header "Authorization: Bearer YOUR-TOKEN" https://api.github.com/repos/octocat/Spoon-Knife/pulls
   ```

   The response includes an `etag` header:

   ```text
   HTTP/2 200
   etag: "644b5b0155e6404a9cc4bd9d8b1ae730"
   ```

1. On your next request to the same URL, send the saved value in the `if-none-match` header.

   ```shell
   curl --include --header "Authorization: Bearer YOUR-TOKEN" --header 'if-none-match: "644b5b0155e6404a9cc4bd9d8b1ae730"' https://api.github.com/repos/octocat/Spoon-Knife/pulls
   ```

   If the data has not changed, you will receive a `304 Not Modified` response, which does not count against your primary rate limit:

   ```text
   HTTP/2 304
   ```

You can also use the `last-modified` header. For example, if a previous request returned a `last-modified` header value of `Wed, 25 Oct 2023 19:17:59 GMT`, you can use the `if-modified-since` header in a future request:

```shell
curl --include --header "Authorization: Bearer YOUR-TOKEN" --header 'if-modified-since: Wed, 25 Oct 2023 19:17:59 GMT' https://api.github.com/repos/octocat/Spoon-Knife
```

Conditional requests for unsafe methods, such as `POST`, `PUT`, `PATCH`, and `DELETE` are not supported unless otherwise noted in the documentation for a specific endpoint.


</pre>

</details>

## Cluster: `guidance:docs-breaking-changes`

- evaluation role: `evaluation_development_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-breaking-changes`

### Current evidence: `chunk-099035e853588f6d8e3d3e13466602b62f7366fe77f3f99d48f8a53c0fd435ce`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-099035e853588f6d8e3d3e13466602b62f7366fe77f3f99d48f8a53c0fd435ce.md`
- content SHA256: `b50a148b56f96b1f7395fe756f22a71024dfb9d1e7dd8df20253e65e8ec857b6`
- byte count: `6244`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Version 2026-03-10`
- parent source ID: `docs-breaking-changes`
- parent document ID: `authored-docs-breaking-changes`
- parent normalized SHA256: `973bd3d7a310e43d39b904118a9a2c39d324bd01e47673aadd42c7f29fd7d6dd`

<details>
<summary>Evidence content</summary>

<pre>
## Version 2026-03-10

- **Remove deprecated `rate` property from rate limit endpoint**
  The `rate` property has been deprecated since 2021 and duplicates information
  available in the `resources.core` property. To migrate, update your integration
  to read rate limit information from `resources.core` instead of `rate`.

  See https://docs.github.com/rest/rate-limit for updated documentation.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /rate_limit`

  &lt;/details&gt;

- **Remove deprecated `permission` property from request when a team is created**

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `POST /orgs/{org}/teams`

  &lt;/details&gt;

- **Updates the "Get repository content" API, so that, when listing the contents of a directory, submodules have the `type` "submodule" instead of the `type` "file"**

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /repos/{owner}/{repo}/contents/{path}`

  &lt;/details&gt;

- **Change Content-Type of SARIF response**
  When trying to receive the SARIF upload by setting the `Accept` header to `application/sarif+json` the response `Content-Type` would incorrectly be set to `application/json+sarif`.
  This change corrects this so the response `Content-Type` in this case becomes `application/sarif+json`.

  For more information, see "[Get a code scanning analysis for a repository](https://docs.github.com/rest/code-scanning/code-scanning#get-a-code-scanning-analysis-for-a-repository)" in the REST API documentation.
- **Remove deprecated `use_squash_pr_title_as_default` property from repo settings endpoints**
  This property has been replaced by `squash_merge_commit_title`.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue`
  - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `GET /events`
  - `GET /installation/repositories`
  - `GET /issues`
  - `GET /networks/{owner}/{repo}/events`
  - `GET /orgs/{org}/actions/permissions/repositories`
  - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories`
  - `GET /orgs/{org}/events`
  - `GET /orgs/{org}/issues`
  - `GET /orgs/{org}/migrations`
  - `GET /orgs/{org}/migrations/{migration_id}`
  - `GET /repos/{owner}/{repo}`
  - `GET /repos/{owner}/{repo}/commits/{commit_sha}/pulls`
  - `GET /repos/{owner}/{repo}/events`
  - `GET /repos/{owner}/{repo}/issues`
  - `GET /repos/{owner}/{repo}/issues/events`
  - `GET /repos/{owner}/{repo}/issues/events/{event_id}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocking`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/parent`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/timeline`
  - `GET /repos/{owner}/{repo}/pulls`
  - `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - `GET /search/issues`
  - `GET /teams/{team_id}/repos/{owner}/{repo}`
  - `GET /user/installations/{installation_id}/repositories`
  - `GET /user/issues`
  - `GET /user/migrations`
  - `GET /user/migrations/{migration_id}`
  - `GET /user/repos`
  - `GET /user/starred`
  - `GET /users/{username}/events`
  - `GET /users/{username}/events/orgs/{org}`
  - `GET /users/{username}/events/public`
  - `GET /users/{username}/received_events`
  - `GET /users/{username}/received_events/public`
  - `GET /users/{username}/starred`
  - `PATCH /repos/{owner}/{repo}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}/sub_issues/priority`
  - `PATCH /repos/{owner}/{repo}/pulls/{pull_number}`
  - `POST /app/installations/{installation_id}/access_tokens`
  - `POST /enterprises/{enterprise}/actions/runners/registration-token`
  - `POST /enterprises/{enterprise}/actions/runners/remove-token`
  - `POST /orgs/{org}/actions/runners/registration-token`
  - `POST /orgs/{org}/actions/runners/remove-token`
  - `POST /orgs/{org}/migrations`
  - `POST /orgs/{org}/projectsV2/{project_number}/drafts`
  - `POST /orgs/{org}/projectsV2/{project_number}/items`
  - `POST /orgs/{org}/repos`
  - `POST /repos/{owner}/{repo}/actions/runners/registration-token`
  - `POST /repos/{owner}/{repo}/actions/runners/remove-token`
  - `POST /repos/{owner}/{repo}/forks`
  - `POST /repos/{owner}/{repo}/issues`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `POST /repos/{owner}/{repo}/pulls`
  - `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `POST /repos/{owner}/{repo}/security-advisories/{ghsa_id}/forks`
  - `POST /repos/{template_owner}/{template_repo}/generate`
  - `POST /user/codespaces/{codespace_name}/publish`
  - `POST /user/migrations`
  - `POST /user/repos`
  - `POST /user/{user_id}/projectsV2/{project_number}/drafts`
  - `POST /users/{username}/projectsV2/{project_number}/items`

  &lt;/details&gt;

- **Remove `authorizations_url` from the API root (`GET /`)**
  The OAuth Authorization API has been [deprecated since 2020](https://developer.github.com/changes/2020-02-14-deprecating-oauth-auth-endpoint/).

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /`

  &lt;/details&gt;

- **Deprecate support for the `beta` media type**
  This media type was officially deprecated in 2014. However, there are still remnants
  of its use that modify response payloads. The following response properties are
  deprecated as a result:

  - `emails` response as a flat array of strings instead of email objects
  - `pull_request` response property with `null` default values
  - `user` response property, replaced by `owner`
  - `master_branch` response property, replaced by `default_branch`

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;


</pre>

</details>

### Current evidence: `chunk-a981d6e38d9441e15e23523d1c41a137f0222d21b4a47e67fc322b3edd4489be`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-a981d6e38d9441e15e23523d1c41a137f0222d21b4a47e67fc322b3edd4489be.md`
- content SHA256: `959f160d37cd1ab2ddb2dbb6dbdc444da1dba40b8b8b9dbf438368ce18979821`
- byte count: `2405`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About breaking changes in the REST API` ? `Upgrading to a new API version`
- parent source ID: `docs-breaking-changes`
- parent document ID: `authored-docs-breaking-changes`
- parent normalized SHA256: `973bd3d7a310e43d39b904118a9a2c39d324bd01e47673aadd42c7f29fd7d6dd`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Breaking changes
shortTitle: Breaking changes
intro: Learn about breaking changes that were introduced in each REST API version.
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
redirect_from:
  - /rest/overview/breaking-changes
category:
  - Learn about the REST API
---

## About breaking changes in the REST API

The GitHub REST API is versioned. The API version name is based on the date when the API version was released. For example, the API version `2026-03-10` was released on Tue, 10 Mar 2026.

Breaking changes are changes that can potentially break an integration. Breaking changes will be released in a new API version. We will provide advance notice before releasing breaking changes. Breaking changes include:

* Removing an entire operation
* Removing or renaming a parameter
* Removing or renaming a response field
* Adding a new required parameter
* Making a previously optional parameter required
* Changing the type of a parameter or response field
* Removing enum values
* Adding a new validation rule to an existing parameter
* Changing authentication or authorization requirements

Any additive (non-breaking) changes will be available in all supported API versions. Additive changes are changes that should not break an integration. Additive changes include:

* Adding an operation
* Adding an optional parameter
* Adding an optional request header
* Adding a response field
* Adding a response header
* Adding enum values

When a new REST API version is released, the previous API version will be supported for at least 24 more months following the release of the new API version.


For more information about API versions, see [/rest/about-the-rest-api/api-versions](/rest/about-the-rest-api/api-versions).

## Upgrading to a new API version

Before upgrading to a new REST API version, you should read the section on this page that corresponds to the new API version to understand what breaking changes are included and to learn more about how to upgrade to that API version.

When you update your integration to specify the new API version in the `X-GitHub-Api-Version` header, you'll also need to make any changes required for your integration to work with the new API version.

Once your integration is updated, test your integration to verify that it works with the new API version.

&lt;!-- markdownlint-disable liquid-quoted-conditional-arg search-replace GHD046 --&gt;



</pre>

</details>

### Current evidence: `chunk-aab4129e4bb838cd0c62c3f8927832a3e6b4f6b3004791373d71661b624e5b45`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-aab4129e4bb838cd0c62c3f8927832a3e6b4f6b3004791373d71661b624e5b45.md`
- content SHA256: `36df5d030666bb3bf712ff77ad2bc24b75d69a578b89d776d9b3ed22e0f1a369`
- byte count: `8030`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Version 2026-03-10`
- parent source ID: `docs-breaking-changes`
- parent document ID: `authored-docs-breaking-changes`
- parent normalized SHA256: `973bd3d7a310e43d39b904118a9a2c39d324bd01e47673aadd42c7f29fd7d6dd`

<details>
<summary>Evidence content</summary>

<pre>
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue`
  - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `GET /events`
  - `GET /installation/repositories`
  - `GET /issues`
  - `GET /networks/{owner}/{repo}/events`
  - `GET /notifications`
  - `GET /notifications/threads/{thread_id}`
  - `GET /orgs/{org}/actions/permissions/repositories`
  - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories`
  - `GET /orgs/{org}/actions/runner-groups/{runner_group_id}/repositories`
  - `GET /orgs/{org}/actions/secrets/{secret_name}/repositories`
  - `GET /orgs/{org}/actions/variables/{name}/repositories`
  - `GET /orgs/{org}/codespaces`
  - `GET /orgs/{org}/codespaces/secrets/{secret_name}/repositories`
  - `GET /orgs/{org}/dependabot/secrets/{secret_name}/repositories`
  - `GET /orgs/{org}/docker/conflicts`
  - `GET /orgs/{org}/events`
  - `GET /orgs/{org}/issues`
  - `GET /orgs/{org}/members/{username}/codespaces`
  - `GET /orgs/{org}/migrations`
  - `GET /orgs/{org}/migrations/{migration_id}`
  - `GET /orgs/{org}/migrations/{migration_id}/repositories`
  - `GET /orgs/{org}/packages`
  - `GET /orgs/{org}/packages/{package_type}/{package_name}`
  - `GET /orgs/{org}/personal-access-token-requests/{pat_request_id}/repositories`
  - `GET /orgs/{org}/personal-access-tokens/{pat_id}/repositories`
  - `GET /orgs/{org}/repos`
  - `GET /orgs/{org}/settings/immutable-releases/repositories`
  - `GET /orgs/{org}/teams/{team_slug}/repos`
  - `GET /orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}`
  - `GET /repos/{owner}/{repo}`
  - `GET /repos/{owner}/{repo}/actions/runs`
  - `GET /repos/{owner}/{repo}/actions/runs/{run_id}`
  - `GET /repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt_number}`
  - `GET /repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs`
  - `GET /repos/{owner}/{repo}/check-suites/{check_suite_id}`
  - `GET /repos/{owner}/{repo}/codespaces`
  - `GET /repos/{owner}/{repo}/commits/{commit_sha}/pulls`
  - `GET /repos/{owner}/{repo}/commits/{ref}/check-suites`
  - `GET /repos/{owner}/{repo}/commits/{ref}/status`
  - `GET /repos/{owner}/{repo}/events`
  - `GET /repos/{owner}/{repo}/forks`
  - `GET /repos/{owner}/{repo}/invitations`
  - `GET /repos/{owner}/{repo}/issues`
  - `GET /repos/{owner}/{repo}/issues/events`
  - `GET /repos/{owner}/{repo}/issues/events/{event_id}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocking`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/parent`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/timeline`
  - `GET /repos/{owner}/{repo}/notifications`
  - `GET /repos/{owner}/{repo}/pulls`
  - `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - `GET /repositories`
  - `GET /search/code`
  - `GET /search/commits`
  - `GET /search/issues`
  - `GET /teams/{team_id}/repos`
  - `GET /teams/{team_id}/repos/{owner}/{repo}`
  - `GET /user/codespaces`
  - `GET /user/codespaces/secrets/{secret_name}/repositories`
  - `GET /user/codespaces/{codespace_name}`
  - `GET /user/docker/conflicts`
  - `GET /user/installations/{installation_id}/repositories`
  - `GET /user/issues`
  - `GET /user/migrations`
  - `GET /user/migrations/{migration_id}`
  - `GET /user/migrations/{migration_id}/repositories`
  - `GET /user/packages`
  - `GET /user/packages/{package_type}/{package_name}`
  - `GET /user/repos`
  - `GET /user/repository_invitations`
  - `GET /user/starred`
  - `GET /user/subscriptions`
  - `GET /users/{username}/docker/conflicts`
  - `GET /users/{username}/events`
  - `GET /users/{username}/events/orgs/{org}`
  - `GET /users/{username}/events/public`
  - `GET /users/{username}/packages`
  - `GET /users/{username}/packages/{package_type}/{package_name}`
  - `GET /users/{username}/received_events`
  - `GET /users/{username}/received_events/public`
  - `GET /users/{username}/repos`
  - `GET /users/{username}/starred`
  - `GET /users/{username}/subscriptions`
  - `PATCH /repos/{owner}/{repo}`
  - `PATCH /repos/{owner}/{repo}/check-suites/preferences`
  - `PATCH /repos/{owner}/{repo}/invitations/{invitation_id}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}/sub_issues/priority`
  - `PATCH /repos/{owner}/{repo}/pulls/{pull_number}`
  - `PATCH /user/codespaces/{codespace_name}`
  - `POST /app/installations/{installation_id}/access_tokens`
  - `POST /enterprises/{enterprise}/actions/runners/registration-token`
  - `POST /enterprises/{enterprise}/actions/runners/remove-token`
  - `POST /orgs/{org}/actions/runners/registration-token`
  - `POST /orgs/{org}/actions/runners/remove-token`
  - `POST /orgs/{org}/members/{username}/codespaces/{codespace_name}/stop`
  - `POST /orgs/{org}/migrations`
  - `POST /orgs/{org}/projectsV2/{project_number}/drafts`
  - `POST /orgs/{org}/projectsV2/{project_number}/items`
  - `POST /orgs/{org}/repos`
  - `POST /repos/{owner}/{repo}/actions/runners/registration-token`
  - `POST /repos/{owner}/{repo}/actions/runners/remove-token`
  - `POST /repos/{owner}/{repo}/check-suites`
  - `POST /repos/{owner}/{repo}/codespaces`
  - `POST /repos/{owner}/{repo}/forks`
  - `POST /repos/{owner}/{repo}/issues`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `POST /repos/{owner}/{repo}/pulls`
  - `POST /repos/{owner}/{repo}/pulls/{pull_number}/codespaces`
  - `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `POST /repos/{owner}/{repo}/security-advisories/{ghsa_id}/forks`
  - `POST /repos/{owner}/{repo}/transfer`
  - `POST /repos/{template_owner}/{template_repo}/generate`
  - `POST /user/codespaces`
  - `POST /user/codespaces/{codespace_name}/publish`
  - `POST /user/codespaces/{codespace_name}/start`
  - `POST /user/codespaces/{codespace_name}/stop`
  - `POST /user/migrations`
  - `POST /user/repos`
  - `POST /user/{user_id}/projectsV2/{project_number}/drafts`
  - `POST /users/{username}/projectsV2/{project_number}/items`
  - `PUT /repos/{owner}/{repo}/collaborators/{username}`

  &lt;/details&gt;

- **Change create repository response from `422` to `451` when blocked by trade controls**
  Repository creation requests where the creator or owner is subject to trade control regulations
  now return `451 Unavailable For Legal Reasons` instead of `422 Unprocessable Entity`.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `POST /orgs/{org}/repos`
  - `POST /user/repos`

  &lt;/details&gt;

- **Change delete organization response from `403` to `451` when blocked by trade controls**
  Organization deletion requests blocked by trade controls now return `451 Unavailable For Legal Reasons` instead of `403 Forbidden`.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `DELETE /orgs/{org}`

  &lt;/details&gt;

- **Change remove organization member response from `403` to `451` when blocked by trade controls**
  Requests to remove a member from a trade-controlled organization now return `451 Unavailable For Legal Reasons` instead of `403 Forbidden`.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `DELETE /orgs/{org}/members/{username}`

  &lt;/details&gt;

- **Change update organization membership response from `403` to `451` when blocked by trade controls**
  Membership update requests for trade-controlled organizations now return `451 Unavailable For Legal Reasons` instead of `403 Forbidden`.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `PUT /orgs/{org}/memberships/{username}`

  &lt;/details&gt;


</pre>

</details>

### Current evidence: `chunk-cf790cc8a7edd6efb9809f062aa0c37c593a47c61d41148a5ff769aecdc1d919`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-cf790cc8a7edd6efb9809f062aa0c37c593a47c61d41148a5ff769aecdc1d919.md`
- content SHA256: `993145fc44cf3027ac58803b8905ea20c56c4ac7c15b3be6e51b512b4ee4840f`
- byte count: `201`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Version 2022-11-28`
- parent source ID: `docs-breaking-changes`
- parent document ID: `authored-docs-breaking-changes`
- parent normalized SHA256: `973bd3d7a310e43d39b904118a9a2c39d324bd01e47673aadd42c7f29fd7d6dd`

<details>
<summary>Evidence content</summary>

<pre>
## Version 2022-11-28

Version `2022-11-28` is the first version of the GitHub Free, Pro &amp; Team REST API after date-based versioning was introduced. This version does not include any breaking changes.

</pre>

</details>

### Current evidence: `chunk-d72e0d593230f2080481b546c222dafe91eb8de566b8bfd58a3910770f0448b0`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-d72e0d593230f2080481b546c222dafe91eb8de566b8bfd58a3910770f0448b0.md`
- content SHA256: `1a5d4fbb79b3d8440214d1d8132646a2d062520bd27fa8eafafce621eb0837b4`
- byte count: `7431`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Version 2026-03-10`
- parent source ID: `docs-breaking-changes`
- parent document ID: `authored-docs-breaking-changes`
- parent normalized SHA256: `973bd3d7a310e43d39b904118a9a2c39d324bd01e47673aadd42c7f29fd7d6dd`

<details>
<summary>Evidence content</summary>

<pre>
- **Change accept repository invitation response from `403` to `451` when blocked by trade controls**
  Repository invitation acceptance blocked by trade controls now returns `451 Unavailable For Legal Reasons` instead of `403 Forbidden`.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `PATCH /user/repository_invitations/{invitation_id}`

  &lt;/details&gt;

- **Remove deprecated `hub_url` property from API root response**

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /`

  &lt;/details&gt;

- **Deprecate `cvss` property in favor of `cvss_severities` for advisory APIs**
  The `cvss_severities` property will supplant the existing `cvss` property and contain `cvss_v3` and `cvss_v4` properties if they exist on the advisory.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /advisories`
  - `GET /advisories/{ghsa_id}`
  - `GET /enterprises/{enterprise}/dependabot/alerts`
  - `GET /orgs/{org}/dependabot/alerts`
  - `GET /orgs/{org}/security-advisories`
  - `GET /repos/{owner}/{repo}/dependabot/alerts`
  - `GET /repos/{owner}/{repo}/dependabot/alerts/{alert_number}`
  - `GET /repos/{owner}/{repo}/security-advisories`
  - `GET /repos/{owner}/{repo}/security-advisories/{ghsa_id}`
  - `PATCH /repos/{owner}/{repo}/dependabot/alerts/{alert_number}`
  - `PATCH /repos/{owner}/{repo}/security-advisories/{ghsa_id}`
  - `POST /repos/{owner}/{repo}/security-advisories`
  - `POST /repos/{owner}/{repo}/security-advisories/reports`

  &lt;/details&gt;

- **Remove repository detail fields from migration resource responses**

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /orgs/{org}/migrations`
  - `GET /orgs/{org}/migrations/{migration_id}`
  - `GET /orgs/{org}/migrations/{migration_id}/repositories`
  - `GET /user/migrations`
  - `GET /user/migrations/{migration_id}`
  - `GET /user/migrations/{migration_id}/repositories`
  - `POST /orgs/{org}/migrations`
  - `POST /user/migrations`

  &lt;/details&gt;

- **Remove deprecated `/hub` endpoint**
- **Remove `merge_commit_sha` field from pull request responses**
  The `merge_commit_sha` property is removed from pull request payloads across all endpoints that return pull request objects.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `GET /events`
  - `GET /networks/{owner}/{repo}/events`
  - `GET /orgs/{org}/events`
  - `GET /repos/{owner}/{repo}/commits/{commit_sha}/pulls`
  - `GET /repos/{owner}/{repo}/events`
  - `GET /repos/{owner}/{repo}/pulls`
  - `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - `GET /users/{username}/events`
  - `GET /users/{username}/events/orgs/{org}`
  - `GET /users/{username}/events/public`
  - `GET /users/{username}/received_events`
  - `GET /users/{username}/received_events/public`
  - `PATCH /repos/{owner}/{repo}/pulls/{pull_number}`
  - `POST /orgs/{org}/projectsV2/{project_number}/drafts`
  - `POST /orgs/{org}/projectsV2/{project_number}/items`
  - `POST /repos/{owner}/{repo}/pulls`
  - `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `POST /user/{user_id}/projectsV2/{project_number}/drafts`
  - `POST /users/{username}/projectsV2/{project_number}/items`

  &lt;/details&gt;

- **Change workflow dispatch response from `204` to `200` with workflow run details**
  Removes the `return_run_details` parameter. The endpoint now always returns `200` with the workflow run details in the response body.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`

  &lt;/details&gt;

- **Remove deprecated singular "assignee" field from Issue and Pull Request endpoints**
  The singular `assignee` field has been marked as "closing down" for years and
  duplicates information available in the `assignees` array. To migrate, update
  your integration to:

  - Use the `assignees` array parameter instead of the singular `assignee`
    parameter when creating or updating Issues.
  - Read assignee information from the `assignees` array instead of the singular
    `assignee` property in Issue and Pull Request responses.

  See https://docs.github.com/rest/issues/issues for updated documentation.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue`
  - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `GET /events`
  - `GET /issues`
  - `GET /networks/{owner}/{repo}/events`
  - `GET /orgs/{org}/events`
  - `GET /orgs/{org}/issues`
  - `GET /repos/{owner}/{repo}/commits/{commit_sha}/pulls`
  - `GET /repos/{owner}/{repo}/events`
  - `GET /repos/{owner}/{repo}/issues`
  - `GET /repos/{owner}/{repo}/issues/events`
  - `GET /repos/{owner}/{repo}/issues/events/{event_id}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocking`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/parent`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/timeline`
  - `GET /repos/{owner}/{repo}/pulls`
  - `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - `GET /search/issues`
  - `GET /user/issues`
  - `GET /users/{username}/events`
  - `GET /users/{username}/events/orgs/{org}`
  - `GET /users/{username}/events/public`
  - `GET /users/{username}/received_events`
  - `GET /users/{username}/received_events/public`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}/sub_issues/priority`
  - `PATCH /repos/{owner}/{repo}/pulls/{pull_number}`
  - `POST /orgs/{org}/projectsV2/{project_number}/drafts`
  - `POST /orgs/{org}/projectsV2/{project_number}/items`
  - `POST /repos/{owner}/{repo}/issues`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `POST /repos/{owner}/{repo}/pulls`
  - `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `POST /user/{user_id}/projectsV2/{project_number}/drafts`
  - `POST /users/{username}/projectsV2/{project_number}/items`

  &lt;/details&gt;

- **Change `selected_repository_ids` parameter to only accept integers for Dependabot org secrets**

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `PUT /orgs/{org}/dependabot/secrets/{secret_name}`

  &lt;/details&gt;

- **Remove the `bundle` property from attestation list responses**
  The `bundle` field is removed from repo, org, and user attestation list and bulk-list responses. Use `bundle_url` to retrieve the attestation bundle.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /orgs/{org}/attestations/{subject_digest}`
  - `GET /repos/{owner}/{repo}/attestations/{subject_digest}`
  - `GET /users/{username}/attestations/{subject_digest}`
  - `POST /orgs/{org}/attestations/bulk-list`
  - `POST /users/{username}/attestations/bulk-list`

  &lt;/details&gt;




</pre>

</details>

### Current evidence: `chunk-fa7753569817ab1d9b643bf1dc484ec3fe35cff7e1ca50252fbe32c38b815fc9`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-fa7753569817ab1d9b643bf1dc484ec3fe35cff7e1ca50252fbe32c38b815fc9.md`
- content SHA256: `57a12be7a581125a8f6dfabc742cbe0c664d38bcf59a39182bc5ebea345c1f71`
- byte count: `6115`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Version 2026-03-10`
- parent source ID: `docs-breaking-changes`
- parent document ID: `authored-docs-breaking-changes`
- parent normalized SHA256: `973bd3d7a310e43d39b904118a9a2c39d324bd01e47673aadd42c7f29fd7d6dd`

<details>
<summary>Evidence content</summary>

<pre>
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id}`
  - `DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issue`
  - `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `GET /events`
  - `GET /gists`
  - `GET /gists/public`
  - `GET /gists/starred`
  - `GET /installation/repositories`
  - `GET /issues`
  - `GET /networks/{owner}/{repo}/events`
  - `GET /orgs/{org}/actions/permissions/repositories`
  - `GET /orgs/{org}/actions/permissions/self-hosted-runners/repositories`
  - `GET /orgs/{org}/events`
  - `GET /orgs/{org}/issues`
  - `GET /orgs/{org}/migrations`
  - `GET /orgs/{org}/migrations/{migration_id}`
  - `GET /repos/{owner}/{repo}`
  - `GET /repos/{owner}/{repo}/commits/{commit_sha}/pulls`
  - `GET /repos/{owner}/{repo}/events`
  - `GET /repos/{owner}/{repo}/issues`
  - `GET /repos/{owner}/{repo}/issues/events`
  - `GET /repos/{owner}/{repo}/issues/events/{event_id}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocking`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/parent`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `GET /repos/{owner}/{repo}/issues/{issue_number}/timeline`
  - `GET /repos/{owner}/{repo}/pulls`
  - `GET /repos/{owner}/{repo}/pulls/{pull_number}`
  - `GET /search/issues`
  - `GET /teams/{team_id}/repos/{owner}/{repo}`
  - `GET /user/installations/{installation_id}/repositories`
  - `GET /user/issues`
  - `GET /user/migrations`
  - `GET /user/migrations/{migration_id}`
  - `GET /user/repos`
  - `GET /user/starred`
  - `GET /users/{username}/events`
  - `GET /users/{username}/events/orgs/{org}`
  - `GET /users/{username}/events/public`
  - `GET /users/{username}/gists`
  - `GET /users/{username}/received_events`
  - `GET /users/{username}/received_events/public`
  - `GET /users/{username}/starred`
  - `PATCH /repos/{owner}/{repo}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}`
  - `PATCH /repos/{owner}/{repo}/issues/{issue_number}/sub_issues/priority`
  - `PATCH /repos/{owner}/{repo}/pulls/{pull_number}`
  - `POST /app/installations/{installation_id}/access_tokens`
  - `POST /enterprises/{enterprise}/actions/runners/registration-token`
  - `POST /enterprises/{enterprise}/actions/runners/remove-token`
  - `POST /gists/{gist_id}/forks`
  - `POST /orgs/{org}/actions/runners/registration-token`
  - `POST /orgs/{org}/actions/runners/remove-token`
  - `POST /orgs/{org}/migrations`
  - `POST /orgs/{org}/projectsV2/{project_number}/drafts`
  - `POST /orgs/{org}/projectsV2/{project_number}/items`
  - `POST /orgs/{org}/repos`
  - `POST /repos/{owner}/{repo}/actions/runners/registration-token`
  - `POST /repos/{owner}/{repo}/actions/runners/remove-token`
  - `POST /repos/{owner}/{repo}/forks`
  - `POST /repos/{owner}/{repo}/issues`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/assignees`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by`
  - `POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`
  - `POST /repos/{owner}/{repo}/pulls`
  - `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
  - `POST /repos/{owner}/{repo}/security-advisories/{ghsa_id}/forks`
  - `POST /repos/{template_owner}/{template_repo}/generate`
  - `POST /user/codespaces/{codespace_name}/publish`
  - `POST /user/migrations`
  - `POST /user/repos`
  - `POST /user/{user_id}/projectsV2/{project_number}/drafts`
  - `POST /users/{username}/projectsV2/{project_number}/items`

  &lt;/details&gt;

- **This changeset removes the underspecified fields `history` and `forks` from the base-gist object**
  These properties were unintentionally added when we converted JSON schemas to OpenAPI. The
  properties appear in resources such as "gist revisions" and "update gist" but should not
  be implemented in the base gist object.

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /gists`
  - `GET /gists/public`
  - `GET /gists/starred`
  - `GET /gists/{gist_id}`
  - `GET /gists/{gist_id}/forks`
  - `GET /gists/{gist_id}/{sha}`
  - `GET /users/{username}/gists`
  - `PATCH /gists/{gist_id}`
  - `POST /gists`
  - `POST /gists/{gist_id}/forks`

  &lt;/details&gt;

- **Change success status code from `204` to `202` for deleting an installation**
  The installation deletion is being moved to the background

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `DELETE /app/installations/{installation_id}`

  &lt;/details&gt;

- **Remove `secret_scanning_push_protection_custom_link_enabled` from the organization request and response**

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /orgs/{org}`
  - `PATCH /orgs/{org}`

  &lt;/details&gt;

- **Remove `javascript` and `typescript` values from the `languages` enum in code scanning default setup responses, in favor of `javascript-typescript`**
  JavaScript and TypeScript are analyzed together by CodeQL, so having separate enum values was misleading and inconsistent with how the analysis actually works. This breaking change removes the individual "javascript" and "typescript" values in favor of the combined "javascript-typescript" value that accurately represents the unified analysis.

  For more information, see "[Get a code scanning default setup configuration](https://docs.github.com/rest/code-scanning/code-scanning#get-a-code-scanning-default-setup-configuration)" in the REST API documentation and the related [`codeql-action` CHANGELOG](https://github.com/github/codeql-action/blob/main/CHANGELOG.md#2218---19-sep-2023).

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;

  - `GET /repos/{owner}/{repo}/code-scanning/default-setup`

  &lt;/details&gt;

- **Remove deprecated `has_downloads` property from Repository response**
  `has_downloads` has been deprecated for 10+ years

  &lt;details&gt;
  &lt;summary&gt;&lt;strong&gt;Affected endpoints&lt;/strong&gt;&lt;/summary&gt;


</pre>

</details>

## Cluster: `guidance:docs-credential-security`

- evaluation role: `intervention_tuning_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-credential-security`

### Current evidence: `chunk-e2c15dc4625f251c70f2cdb31eec44532a56c5300292d61dddc6f3010184a0fb`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-e2c15dc4625f251c70f2cdb31eec44532a56c5300292d61dddc6f3010184a0fb.md`
- content SHA256: `e2094fccc7253ceceb9e6c430d14566e3870c1f5e6b447bf89c3a055e95d9c05`
- byte count: `7979`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Choose an appropriate authentication method` ? `Limit the permissions of your credentials` ? `Store your authentication credentials securely` ? `Limit who can access your authentication credentials` ? `Use authentication credentials securely in your code` ? `Prepare a remediation plan`
- parent source ID: `docs-credential-security`
- parent document ID: `authored-docs-credential-security`
- parent normalized SHA256: `e2094fccc7253ceceb9e6c430d14566e3870c1f5e6b447bf89c3a055e95d9c05`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Keeping your API credentials secure
shortTitle: Keeping API credentials secure
intro: Follow these best practices to keep your API credentials and tokens secure.
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
redirect_from:
  - /rest/overview/keeping-your-api-credentials-secure
category:
  - Authenticate API requests
---

## Choose an appropriate authentication method

You should choose an authentication method that is appropriate for the task you want to accomplish.

* To use the API for personal use, you can create a personal access token.
* To use the API on behalf of an organization or another user, you should create a GitHub App.
* To use the API in a GitHub Actions workflow, you should authenticate with the built-in `GITHUB_TOKEN`.

For more information, see [/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#authenticating-with-the-api](/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#authenticating-with-the-api).

## Limit the permissions of your credentials

When creating a personal access token, only select the minimum permissions or scopes needed, and set an expiration date for the minimum amount of time you'll need to use the token. GitHub recommends that you use fine-grained personal access tokens instead of personal access tokens (classic). For more information, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#types-of-personal-access-tokens](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#types-of-personal-access-tokens).

A token has the same capabilities to access resources and perform actions on those resources that the owner of the token has, and is further limited by any scopes or permissions granted to the token. A token cannot grant additional access capabilities to a user.


When creating a GitHub App, select the minimum permissions that your GitHub App will need. For more information, see [/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app](/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app).

When authenticating with `GITHUB_TOKEN` in a GitHub Actions workflow, only give the minimum amount of permissions needed. For more information, see [/actions/tutorials/authenticate-with-github_token#modifying-the-permissions-for-the-github_token](/actions/tutorials/authenticate-with-github_token#modifying-the-permissions-for-the-github_token).

## Store your authentication credentials securely

Treat authentication credentials the same way you would treat your passwords or other sensitive credentials.

* Don't share authentication credentials using an unencrypted messaging or email system.
* Don't pass your personal access token as plain text in the command line. For more information, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#keeping-your-personal-access-tokens-secure](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#keeping-your-personal-access-tokens-secure).
* Don't push unencrypted authentication credentials like tokens or keys to any repository, even if the repository is private. Instead consider using a GitHub Actions secret or Codespaces secret. For more information, see [/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets](/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) and [/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces](/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces).
* You can use secret scanning to discover tokens, private keys, and other secrets that were pushed to a repository, or to block future pushes that contain secrets. For more information, see [/code-security/concepts/secret-security/secret-scanning](/code-security/concepts/secret-security/secret-scanning).

## Limit who can access your authentication credentials

Don't share your personal access token with others. Instead of sharing a personal access token, consider creating a GitHub App. For more information, see [/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps](/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps).

If you need to share credentials with a team, store the credentials in a secure shared system. For example, you could store and share passwords securely using [1Password](https://1password.com/), or you could store keys in [Azure KeyVault](https://azure.microsoft.com/en-gb/products/key-vault) and manage access with your IAM (Identity and access management).

If you're creating a GitHub Actions workflow that needs to access the API, you can store your credentials in an encrypted secret, and access the encrypted secret from the workflow. For more information, see [/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets](/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) and [/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow](/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow).

## Use authentication credentials securely in your code

Never hardcode authentication credentials like tokens, keys, or app-related secrets into your code. Instead, consider using a secret manager such as [Azure Key Vault](https://azure.microsoft.com/products/key-vault) or [HashiCorp Vault](https://www.hashicorp.com/products/vault). For more information about securing GitHub App credentials, see [/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app](/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app).



If you find another user's personal access token exposed on GitHub or elsewhere, you can submit a revocation request through the REST API. See [/rest/credentials/revoke#revoke-a-list-of-credentials](/rest/credentials/revoke#revoke-a-list-of-credentials).




When using a personal access token in a script, consider storing your token as a GitHub Actions secret and running your script through GitHub Actions. You can also store your token as a Codespaces secret and run your script in Codespaces. For more information, see [/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets](/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) and [/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces](/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces).

If none of these options are possible, you can store authentication credentials in a `.env` file. Make sure to encrypt your `.env` file, and never push it to any repository.

## Prepare a remediation plan

You should create a plan to handle any security breaches in a timely manner. In the event that your token or other authentication credential is leaked, you will need to:

* Generate a new credential.
* Replace the old credential with the new one everywhere that you are storing or accessing the credential.
* Delete the old compromised credential.

For information about rotating compromised credentials for a GitHub App, see [/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app](/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app).

For information about creating and deleting personal access tokens, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

</pre>

</details>

## Cluster: `guidance:docs-getting-started`

- evaluation role: `held_out_release_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-getting-started`

### Current evidence: `chunk-016bb9166542c2ba4bbd33a1aeb8d10d0cc889e5a0c2276d00dc5a5e88f4cb07`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-016bb9166542c2ba4bbd33a1aeb8d10d0cc889e5a0c2276d00dc5a5e88f4cb07.md`
- content SHA256: `a8836c7b2f278d78a015b5e9bb942664955e20d7ecf203de4446dca6f4e399ad`
- byte count: `7037`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Authentication` ? `Parameters` ? `Path parameters` ? `Body parameters` ? `Query parameters` ? `Making a request` ? `1. Setup` ? `2. Authenticate` ? `3. Choose an endpoint for your request`
- parent source ID: `docs-getting-started`
- parent document ID: `authored-docs-getting-started`
- parent normalized SHA256: `c8fc1dfea1c46150a8e153cdbde4832a4566d90f7d79cd0e00bacc523f91da96`

<details>
<summary>Evidence content</summary>

<pre>
### Authentication

Many endpoints require authentication or return additional information if you are authenticated. Additionally, you can make more requests per hour when you are authenticated.



To authenticate your request, you will need to provide an authentication token with the required scopes or permissions. There a few different ways to get a token: You can create a personal access token, generate a token with a GitHub App, or use the built-in `GITHUB_TOKEN` in a GitHub Actions workflow. For more information, see [/rest/authentication/authenticating-to-the-rest-api](/rest/authentication/authenticating-to-the-rest-api).

For an example of a request that uses an authentication token, see [Making a request](#making-a-request).

&gt; [!NOTE]
&gt; If you don't want to create a token, you can use GitHub CLI. GitHub CLI will take care of authentication for you, and help keep your account secure. For more information, see the [GitHub CLI version of this page](/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=cli).

&gt; [!WARNING]
&gt; Treat your access token the same way you would treat your passwords or other sensitive credentials. For more information, see [/rest/authentication/keeping-your-api-credentials-secure](/rest/authentication/keeping-your-api-credentials-secure).





Although some REST API endpoints are accessible without authentication, GitHub CLI requires you to authenticate before you can use the `api` subcommand to make an API request. Use the `auth login` subcommand to authenticate to GitHub. For more information, see [Making a request](#making-a-request).





To authenticate your request, you will need to provide an authentication token with the required scopes or permissions. There a few different ways to get a token: You can create a personal access token, generate a token with a GitHub App, or use the built-in `GITHUB_TOKEN` in a GitHub Actions workflow. For more information, see [/rest/authentication/authenticating-to-the-rest-api](/rest/authentication/authenticating-to-the-rest-api).

For an example of a request that uses an authentication token, see [Making a request](#making-a-request).

&gt; [!WARNING]
&gt; Treat your access token the same way you would treat your passwords or other sensitive credentials. For more information, see [/rest/authentication/keeping-your-api-credentials-secure](/rest/authentication/keeping-your-api-credentials-secure).



### Parameters

Many API methods require or allow you to send additional information in parameters in your request. There are a few different types of parameters: Path parameters, body parameters, and query parameters.

#### Path parameters

Path parameters modify the endpoint path. These parameters are required in your request. For more information, see [Path](#path).

#### Body parameters

Body parameters allow you to pass additional data to the API. These parameters can be optional or required, depending on the endpoint. For example, a body parameter may allow you to specify an issue title when creating a new issue, or specify certain settings when enabling or disabling a feature. The documentation for each GitHub REST API endpoint will describe the body parameters that it supports. For more information, see the [/rest](/rest).

For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) requires that you specify a title for the new issue in your request. It also allows you to optionally specify other information, such as text to put in the issue body, users to assign to the new issue, or labels to apply to the new issue. For an example of a request that uses body parameters, see [Making a request](#making-a-request).

You must authenticate your request to pass body parameters. For more information, see [Authentication](#authentication).

#### Query parameters

Query parameters allow you to control what data is returned for a request. These parameters are usually optional. The documentation for each GitHub REST API endpoint will describe any query parameters that it supports. For more information, see the [/rest](/rest).

For example, the ["List public events" endpoint](/rest/activity/events#list-public-events) returns thirty issues by default. You can use the `per_page` query parameter to return two issues instead of 30. You can use the `page` query parameter to fetch only the first page of results. For an example of a request that uses query parameters, see [Making a request](#making-a-request).

## Making a request



This section demonstrates how to make an authenticated request to the GitHub REST API using GitHub CLI.

### 1. Setup

Install GitHub CLI on macOS, Windows, or Linux. For more information, see [Installation](https://github.com/cli/cli#installation) in the GitHub CLI repository.

### 2. Authenticate

1. To authenticate to GitHub, run the following command from your terminal.

   ```shell
   gh auth login
   ```

   You can use the `--scopes` option to specify what scopes you want. If you want to authenticate with a token that you created, you can use the `--with-token` option. For more information, see the [GitHub CLI `auth login` documentation](https://cli.github.com/manual/gh_auth_login).

1. Select where you want to authenticate to:

   * If you access GitHub at GitHub.com, select **GitHub.com**.
   * If you access GitHub at a different domain, select **Other**, then enter your hostname (for example: `octocorp.ghe.com`).

1. Follow the rest of the on-screen prompts.

   GitHub CLI automatically stores your Git credentials for you when you choose HTTPS as your preferred protocol for Git operations and answer "yes" to the prompt asking if you would like to authenticate to Git with your GitHub credentials. This can be useful as it allows you to use Git commands like `git push` and `git pull` without needing to set up a separate credential manager or use SSH.

### 3. Choose an endpoint for your request

1. Choose an endpoint to make a request to. You can explore GitHub's [REST API documentation](/rest) to discover endpoints that you can use to interact with GitHub.
1. Identify the HTTP method and path of the endpoint. You will send these with your request. For more information, see [HTTP method](#http-method) and [Path](#path).

   For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) uses the HTTP method `POST` and the path `/repos/{owner}/{repo}/issues`.

1. Identify any required path parameters. Required path parameters appear in curly brackets `{}` in the path of the endpoint. Replace each parameter placeholder with the desired value. For more information, see [Path](#path).

   For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) uses the path `/repos/{owner}/{repo}/issues`, and the path parameters are `{owner}` and `{repo}`. To use this path in your API request, replace `{repo}` with the name of the repository where you would like to create a new issue, and replace `{owner}` with the name of the account that owns the repository.


</pre>

</details>

### Current evidence: `chunk-26153d3a142bbfb1e096af76f089d6e3d16a83f63644c3f0cc7134f9fd6487ac`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-26153d3a142bbfb1e096af76f089d6e3d16a83f63644c3f0cc7134f9fd6487ac.md`
- content SHA256: `d68aea1bd65d42850337ef47a62fe7ad6e6611cad88c5bfaf0412ca42d01b234`
- byte count: `5489`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About the response body` ? `Detailed versus summary representations` ? `Hypermedia` ? `Rate limiting` ? `Next steps`
- parent source ID: `docs-getting-started`
- parent document ID: `authored-docs-getting-started`
- parent normalized SHA256: `c8fc1dfea1c46150a8e153cdbde4832a4566d90f7d79cd0e00bacc523f91da96`

<details>
<summary>Evidence content</summary>

<pre>
### About the response body

Many endpoints will return a response body. Unless otherwise specified, the response body is in JSON format. Blank fields are included as `null` instead of being omitted. All timestamps return in UTC time, ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`.

Unlike the GraphQL API where you specify what information you want, the REST API typically returns more information than you need. If desired, you can parse the response to pull out specific pieces of information.



For example, you can use `&gt;` to redirect the response to a file. In the following example, replace `REPO-OWNER` with the name of the account that owns the repository, and `REPO-NAME` with the name of the repository.

```shell copy
gh api \
--header 'Accept: application/vnd.github+json' \
--method GET /repos/REPO-OWNER/REPO-NAME/issues \
-F per_page=2 &gt; data.json
```

Then you can use jq to get the title and author ID of each issue:

```shell copy
jq '.[] | {title: .title, authorID: .user.id}' data.json
```

The previous two commands return something like:

```json
{
  "title": "Update index.html",
  "authorID": 10701255
}
{
  "title": "Edit index file",
  "authorID": 53709285
}
```

For more information about jq, see [the jq documentation](https://stedolan.github.io/jq/).





For example, you can get the title and author ID of each issue. In the following example, replace `REPO-OWNER` with the name of the account that owns the repository, and `REPO-NAME` with the name of the repository.

```javascript copy
try {
  const result = await octokit.request("GET /repos/{owner}/{repo}/issues", {
    owner: "REPO-OWNER",
    repo: "REPO-NAME",
    per_page: 2,
  });

  const titleAndAuthor = result.data.map(issue =&gt; {title: issue.title, authorID: issue.user.id})

  console.log(titleAndAuthor)

} catch (error) {
  console.log(`Error! Status: ${error.status}. Message: ${error.response.data.message}`)
}
```





For example, you can use `&gt;` to redirect the response to a file. In the following example, replace `REPO-OWNER` with the name of the account that owns the repository, and `REPO-NAME` with the name of the repository.

```shell copy
curl --request GET \
--url "https://api.github.com/repos/REPO-OWNER/REPO-NAME/issues?per_page=2" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer YOUR-TOKEN" &gt; data.json
```

Then you can use jq to get the title and author ID of each issue:

```shell copy
jq '.[] | {title: .title, authorID: .user.id}' data.json
```

The previous two commands return something like:

```json
{
  "title": "Update index.html",
  "authorID": 10701255
}
{
  "title": "Edit index file",
  "authorID": 53709285
}
```

For more information about jq, see [the jq documentation](https://stedolan.github.io/jq/).



#### Detailed versus summary representations

A response can include all attributes for a resource or only a subset of attributes, depending on whether you fetch an individual resource or a list of resources.

* When you fetch an _individual resource_, like a specific repository, the response will typically include all attributes for that resource. This is the "detailed" representation of the resource.
* When you fetch a _list of resources_, like a list of multiple repositories, the response will only include a subset of the attributes for each resource. This is the "summary" representation of the resource.

Note that authorization sometimes influences the amount of detail included in a representation.

The reason for this is because some attributes are computationally expensive for the API to provide, so GitHub excludes those attributes from the summary representation. To obtain those attributes, you can fetch the detailed representation.

The documentation provides an example response for each API method. The example response illustrates all attributes that are returned by that method.

#### Hypermedia

All resources may have one or more `*_url` properties linking to other resources. These are meant to provide explicit URLs so that proper API clients don't need to construct URLs on their own. It is highly recommended that API clients use these. Doing so will make future upgrades of the API easier for developers. All URLs are expected to be proper [RFC 6570](https://datatracker.ietf.org/doc/html/rfc6570) URI templates.

You can then expand these templates using something like the [uri_template](https://github.com/hannesg/uri_template) gem:

```ruby
&gt;&gt; tmpl = URITemplate.new('/notifications{?since,all,participating}')
&gt;&gt; tmpl.expand
=&gt; "/notifications"

&gt;&gt; tmpl.expand all: 1
=&gt; "/notifications?all=1"

&gt;&gt; tmpl.expand all: 1, participating: 1
=&gt; "/notifications?all=1&amp;participating=1"
```

## Rate limiting

The GitHub REST API limits the number of requests you can make within a given time period. For more information about rate limits and how to check your current rate limit status, see [/rest/using-the-rest-api/rate-limits-for-the-rest-api](/rest/using-the-rest-api/rate-limits-for-the-rest-api).

## Next steps

This article demonstrated how to list and create issues in a repository. For more practice, try to comment on an issue, edit the title of an issue, or close an issue. For more information, see the ["Create an issue comment" endpoint](/rest/issues/comments#create-an-issue-comment) and the ["Update an issue" endpoint](/rest/issues/issues#update-an-issue).

For more information about other endpoints that you can use, see the [REST reference documentation](/rest).

</pre>

</details>

### Current evidence: `chunk-26b602928020bab70748654dd84106df4188f1d8bd4ce038b8dab607c8201215`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-26b602928020bab70748654dd84106df4188f1d8bd4ce038b8dab607c8201215.md`
- content SHA256: `d53a2b9b15bca0926ec554e6436a4f4947c18bb9eca109bb1c3d322315c32a64`
- byte count: `8160`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `4. Make a request with GitHub CLI` ? `Example request` ? `Example request using query parameters` ? `Example request using body parameters` ? `1. Setup` ? `2. Choose an endpoint for your request` ? `3. Create authentication credentials` ? `4. Make a `curl` request` ? `Example request`
- parent source ID: `docs-getting-started`
- parent document ID: `authored-docs-getting-started`
- parent normalized SHA256: `c8fc1dfea1c46150a8e153cdbde4832a4566d90f7d79cd0e00bacc523f91da96`

<details>
<summary>Evidence content</summary>

<pre>
### 4. Make a request with GitHub CLI

Use the GitHub CLI `api` subcommand to make your API request. For more information, see the [GitHub CLI `api` documentation](https://cli.github.com/manual/gh_api).

In your request, specify the following options and values:
* **--method** followed by the HTTP method and the path of the endpoint. For more information, see [HTTP method](#http-method) and [Path](#path).
* **--header:**
  * **`Accept`:** Pass the media type in an `Accept` header. To pass multiple media types in an `Accept` header, separate the media types with a comma: `Accept: application/vnd.github+json,application/vnd.github.diff`. For more information, see [`Accept`](#accept) and [Media types](#media-types).
  * **`X-GitHub-Api-Version`:** Pass the API version in a `X-GitHub-Api-Version` header. For more information, see [`X-GitHub-Api-Version`](#x-github-api-version).
* **`-f`** or **`-F`** followed by any body parameters or query parameters in `key=value` format. Use the `-F` option to pass a parameter that is a number, Boolean, or null. Use the `-f` option to pass string parameters.

  Some endpoints use query parameters that are arrays. To send an array in the query string, use the query parameter once per array item, and append `[]` after the query parameter name. For example, to provide an array of two repository IDs, use `-f repository_ids[]=REPOSITORY_A_ID -f repository_ids[]=REPOSITORY_B_ID`.

  If you do not need to specify any body parameters or query parameters in your request, omit this option. For more information, see [Body parameters](#body-parameters) and [Query parameters](#query-parameters). For examples, see [Example request using body parameters](#example-request-using-body-parameters) and [Example request using query parameters](#example-request-using-query-parameters).

#### Example request

The following example request uses the ["Get Octocat" endpoint](/rest/meta/meta#get-octocat) to return the octocat as ASCII art.

```shell copy
gh api --method GET /octocat \
--header 'Accept: application/vnd.github+json' \
--header "X-GitHub-Api-Version: 2022-11-28"
```

#### Example request using query parameters

The ["List public events" endpoint](/rest/activity/events#list-public-events) returns thirty issues by default. The following example uses the `per_page` query parameter to return two issues instead of 30, and the `page` query parameter to fetch only the first page of results.

```shell copy
gh api --method GET /events -F per_page=2 -F page=1
--header 'Accept: application/vnd.github+json' \
```

#### Example request using body parameters

The following example uses the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) to create a new issue in the octocat/Spoon-Knife repository. In the response, find the `html_url` of your issue, and navigate to your issue in the browser.

```shell copy
gh api --method POST /repos/octocat/Spoon-Knife/issues \
--header "Accept: application/vnd.github+json" \
--header "X-GitHub-Api-Version: 2022-11-28" \
-f title='Created with the REST API' \
-f body='This is a test issue created by the REST API' \
```





This section demonstrates how to make an authenticated request to the GitHub REST API using `curl`.

### 1. Setup

You must have `curl` installed on your machine. To check if `curl` is already installed, run `curl --version` on the command line.

* If the output provides information about the version of `curl`, that means `curl` is installed.
* If you get a message similar to `command not found: curl`, that means `curl` is not installed. Download and install `curl`. For more information, see [the curl download page](https://curl.se/download.html).

### 2. Choose an endpoint for your request

1. Choose an endpoint to make a request to. You can explore GitHub's [REST API documentation](/rest) to discover endpoints that you can use to interact with GitHub.
1. Identify the HTTP method and path of the endpoint. You will send these with your request. For more information, see [HTTP method](#http-method) and [Path](#path).

   For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) uses the HTTP method `POST` and the path `/repos/{owner}/{repo}/issues`.

1. Identify any required path parameters. Required path parameters appear in curly brackets `{}` in the path of the endpoint. Replace each parameter placeholder with the desired value. For more information, see [Path](#path).

   For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) uses the path `/repos/{owner}/{repo}/issues`, and the path parameters are `{owner}` and `{repo}`. To use this path in your API request, replace `{repo}` with the name of the repository where you would like to create a new issue, and replace `{owner}` with the name of the account that owns the repository.

### 3. Create authentication credentials

Create an access token to authenticate your request. You can save your token and use it for multiple requests. Give the token any scopes or permissions that are required to access the endpoint. You will send this token in an `Authorization` header with your request. For more information, see [Authentication](#authentication).

### 4. Make a `curl` request

Use the `curl` command to make your request. For more information, see [the curl documentation](https://curl.se/docs/manpage.html).

Specify the following options and values in your request:

* **`--request` or `-X`** followed by the HTTP method as the value. For more information, see [HTTP method](#http-method).
* **`--url`** followed by the full path as the value. The full path is a URL that includes the base URL for the GitHub REST API (`https://api.github.com`) and the path of the endpoint, like this: `https://api.github.com/PATH`. Replace `PATH` with the path of the endpoint. For more information, see [Path](#path).

  To use query parameters, add a `?` to the end of the path, then append your query parameter name and value in the form `parameter_name=value`. Separate multiple query parameters with `&amp;`. If you need to send an array in the query string, use the query parameter once per array item, and append `[]` after the query parameter name. For example, to provide an array of two repository IDs, use `?repository_ids[]=REPOSITORY_A_ID&amp;repository_ids[]=REPOSITORY_B_ID`. For more information, see [Query parameters](#query-parameters). For an example, see [Example request using query parameters](#example-request-using-query-parameters-1).
* **`--header` or `-H`:**
  * **`Accept`:** Pass the media type in an `Accept` header. To pass multiple media types in an `Accept` header, separate the media types with a comma, for example: `Accept: application/vnd.github+json,application/vnd.github.diff`. For more information, see [`Accept`](#accept) and [Media types](#media-types).
  * **`X-GitHub-Api-Version`:** Pass the API version in a `X-GitHub-Api-Version` header. For more information, see [`X-GitHub-Api-Version`](#x-github-api-version).
  * **`Authorization`:** Pass your authentication token in an `Authorization` header. Note that in most cases you can use `Authorization: Bearer` or `Authorization: token` to pass a token. However, if you are passing a JSON web token (JWT), you must use `Authorization: Bearer`. For more information, see [Authentication](#authentication). For an example of a request that uses an `Authorization` header, see [Example request using body parameters](#example-request-using-body-parameters-1).
* **`--data` or `-d`** followed by any body parameters within a JSON object. If you do not need to specify any body parameters in your request, omit this option. For more information, see [Body parameters](#body-parameters). For an example, see [Example request using body parameters](#example-request-using-body-parameters-1).

#### Example request

The following example request uses the ["Get Octocat" endpoint](/rest/meta/meta#get-octocat) to return the octocat as ASCII art.

```shell copy
curl --request GET \
--url "https://api.github.com/octocat" \
--header "Accept: application/vnd.github+json" \
--header "X-GitHub-Api-Version: 2022-11-28"
```


</pre>

</details>

### Current evidence: `chunk-3c499f1990ac0c066d520f07851659dcd0fdb7821fde7a966223a22b8038e1fd`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-3c499f1990ac0c066d520f07851659dcd0fdb7821fde7a966223a22b8038e1fd.md`
- content SHA256: `4b5fc21ea7abfc8bcb907759f604149268e4aa47f82f22346d5f2e48d87f9702`
- byte count: `6246`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Introduction` ? `About requests to the REST API` ? `HTTP method` ? `Path` ? `Headers` ? ``Accept`` ? ``X-GitHub-Api-Version`` ? ``User-Agent`` ? `Media types`
- parent source ID: `docs-getting-started`
- parent document ID: `authored-docs-getting-started`
- parent normalized SHA256: `c8fc1dfea1c46150a8e153cdbde4832a4566d90f7d79cd0e00bacc523f91da96`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Getting started with the REST API
shortTitle: Getting started
intro: 'Learn how to use the GitHub REST API.'
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
redirect_from:
  - /rest/guides/getting-started-with-the-rest-api
  - /rest/initialize-the-repo
  - /rest/overview/resources-in-the-rest-api
  - /rest/using-the-rest-api/resources-in-the-rest-api
  - /v3/media
  - /rest/overview/media-types
  - /rest/using-the-rest-api/media-types
category:
  - Learn about the REST API
---

## Introduction

This article describes how to use the GitHub REST API with GitHub CLI, `curl`, or JavaScript. For a quickstart guide, see [/rest/quickstart](/rest/quickstart).







## About requests to the REST API

This section describes the elements that make up an API request:

* [HTTP method](#http-method)
* [Path](#path)
* [Headers](#headers)
* [Media types](#media-types)
* [Authentication](#authentication)
* [Parameters](#parameters)

Every request to the REST API includes an HTTP method and a path. Depending on the REST API endpoint, you might also need to specify request headers, authentication information, query parameters, or body parameters.

The REST API reference documentation describes the HTTP method, path, and parameters for every endpoint. It also displays example requests and responses for each endpoint. For more information, see the [REST reference documentation](/rest).

### HTTP method

The HTTP method of an endpoint defines the type of action it performs on a given resource. Some common HTTP methods are `GET`, `POST`, `DELETE`, and `PATCH`. The REST API reference documentation provides the HTTP method for every endpoint.

For example, the HTTP method for the ["List repository issues" endpoint](/rest/issues/issues#list-repository-issues) is `GET`."

Where possible, the GitHub REST API strives to use an appropriate HTTP method for each action.

* `GET`: Used for retrieving resources.
* `POST`: Used for creating resources.
* `PATCH`: Used for updating properties of resources.
* `PUT`: Used for replacing resources or collections of resources.
* `DELETE`: Used for deleting resources.

### Path

Each endpoint has a path. The REST API reference documentation gives the path for every endpoint. For example, the path for the ["List repository issues" endpoint](/rest/issues/issues#list-repository-issues) is `/repos/{owner}/{repo}/issues`.

The curly brackets `{}` in a path denote path parameters that you need to specify. Path parameters modify the endpoint path and are required in your request. For example, the path parameters for the ["List repository issues" endpoint](/rest/issues/issues#list-repository-issues) are `{owner}` and `{repo}`. To use this path in your API request, replace `{repo}` with the name of the repository where you would like to request a list of issues, and replace `{owner}` with the name of the account that owns the repository.

### Headers

Headers provide extra information about the request and the desired response. Following are some examples of headers that you can use in your requests to the GitHub REST API. For an example of a request that uses headers, see [Making a request](#making-a-request).

#### `Accept`

Most GitHub REST API endpoints specify that you should pass an `Accept` header with a value of `application/vnd.github+json`. The value of the `Accept` header is a media type. For more information about media types, see [Media types](#media-types).

#### `X-GitHub-Api-Version`

You should use this header to specify a version of the REST API to use for your request. For more information, see [/rest/about-the-rest-api/api-versions](/rest/about-the-rest-api/api-versions).



#### `User-Agent`

All API requests must include a valid `User-Agent` header. The `User-Agent` header identifies the user or application that is making the request.



By default, GitHub CLI sends a valid `User-Agent` header. However, GitHub recommends using your GitHub username, or the name of your application, for the `User-Agent` header value. This allows GitHub to contact you if there are problems.





By default, `curl` sends a valid `User-Agent` header. However GitHub recommends using your GitHub username, or the name of your application, for the `User-Agent` header value. This allows GitHub to contact you if there are problems.





If you use the Octokit.js SDK, the SDK will send a valid `User-Agent` header for you. However, GitHub recommends using your GitHub username, or the name of your application, for the `User-Agent` header value. This allows GitHub to contact you if there are problems.



The following is an example `User-Agent` for an app named `Awesome-Octocat-App`:

```shell
User-Agent: Awesome-Octocat-App
```

Requests with no `User-Agent` header will be rejected. If you provide an invalid `User-Agent` header, you will receive a `403 Forbidden` response.



&lt;!-- Anchor to maintain links to this heading --&gt;
&lt;a name="media-types"&gt;&lt;/a&gt;

### Media types

You can specify one or more media types by adding them to the `Accept` header of your request. For more information about the `Accept` header, see [`Accept`](#accept).

Media types specify the format of the data you want to consume from the API. Media types are specific to resources, allowing them to change independently and support formats that other resources don't. The documentation for each GitHub REST API endpoint will describe the media types that it supports. For more information, see the [/rest](/rest).

The most common media types supported by the GitHub REST API are `application/vnd.github+json` and `application/json`.

There are custom media types that you can use with some endpoints. For example, the REST API to manage [commits](/rest/commits/commits#get-a-commit) and [pull requests](/rest/pulls/pulls) support the media types `diff`, `patch`, and `sha`. The media types `full`, `raw`, `text`, or `html` are used by some other endpoints.

All custom media types for GitHub look like this: `application/vnd.github.PARAM+json`, where `PARAM` is the name of the media type. For example, to specify the `raw` media type, you would use `application/vnd.github.raw+json`.

For an example of a request that uses media types, see [Making a request](#making-a-request).


</pre>

</details>

### Current evidence: `chunk-a18a4454d3420e3b5e0048ccde681face338278d04f270a1882bb6d483f289fb`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-a18a4454d3420e3b5e0048ccde681face338278d04f270a1882bb6d483f289fb.md`
- content SHA256: `4a65e485ed5a598be350d11f41908272acaf3aaa43ac6dc3ad3e71ae923936bb`
- byte count: `6515`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Example request using query parameters` ? `Example request using body parameters` ? `1. Setup` ? `2. Choose an endpoint for your request` ? `3. Create an access token` ? `4. Make a request with Octokit.js` ? `Using the response`
- parent source ID: `docs-getting-started`
- parent document ID: `authored-docs-getting-started`
- parent normalized SHA256: `c8fc1dfea1c46150a8e153cdbde4832a4566d90f7d79cd0e00bacc523f91da96`

<details>
<summary>Evidence content</summary>

<pre>
#### Example request using query parameters

The ["List public events" endpoint](/rest/activity/events#list-public-events) returns thirty issues by default. The following example uses the `per_page` query parameter to return two issues instead of 30, and the `page` query parameter to fetch only the first page of results.

```shell copy
curl --request GET \
--url "https://api.github.com/events?per_page=2&amp;page=1" \
--header "Accept: application/vnd.github+json" \
--header "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/events
```

#### Example request using body parameters

The following example uses the [Create an issue](/rest/issues/issues#create-an-issue) endpoint to create a new issue in the octocat/Spoon-Knife repository. Replace `YOUR-TOKEN` with the authentication token you created in a previous step.

&gt; [!NOTE]
&gt; If you are using a fine-grained personal access token, you must replace `octocat/Spoon-Knife` with a repository that you own or that is owned by an organization that you are a member of. Your token must have access to that repository and have read and write permissions for repository issues. For more information, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

```shell copy
curl \
--request POST \
--url "https://api.github.com/repos/octocat/Spoon-Knife/issues" \
--header "Accept: application/vnd.github+json" \
--header "X-GitHub-Api-Version: 2022-11-28" \
--header "Authorization: Bearer YOUR-TOKEN" \
--data '{
  "title": "Created with the REST API",
  "body": "This is a test issue created by the REST API"
}'
```





This section demonstrates how to make a request to the GitHub REST API using JavaScript and [Octokit.js](https://github.com/octokit/octokit.js). For a more detailed guide, see [/rest/guides/scripting-with-the-rest-api-and-javascript](/rest/guides/scripting-with-the-rest-api-and-javascript).

### 1. Setup

You must install `octokit` to use the Octokit.js library shown in the following examples.

* Install `octokit`. For example, `npm install octokit`. For other ways to install or load `octokit`, see [the Octokit.js README](https://github.com/octokit/octokit.js/#readme).

### 2. Choose an endpoint for your request

1. Choose an endpoint to make a request to. You can explore GitHub's [REST API documentation](/rest) to discover endpoints that you can use to interact with GitHub.
1. Identify the HTTP method and path of the endpoint. You will send these with your request. For more information, see [HTTP method](#http-method) and [Path](#path).

   For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) uses the HTTP method `POST` and the path `/repos/{owner}/{repo}/issues`.

1. Identify any required path parameters. Required path parameters appear in curly brackets `{}` in the path of the endpoint. Replace each parameter placeholder with the desired value. For more information, see [Path](#path).

   For example, the ["Create an issue" endpoint](/rest/issues/issues#create-an-issue) uses the path `/repos/{owner}/{repo}/issues`, and the path parameters are `{owner}` and `{repo}`. To use this path in your API request, replace `{repo}` with the name of the repository where you would like to create a new issue, and replace `{owner}` with the name of the account that owns the repository.

### 3. Create an access token

Create an access token to authenticate your request. You can save your token and use it for multiple requests. Give the token any scopes or permissions that are required to access the endpoint. You will send this token in an `Authorization` header with your request. For more information, see [Authentication](#authentication).

### 4. Make a request with Octokit.js

1. Import `octokit` in your script. For example, `import { Octokit } from "octokit";`. For other ways to import `octokit`, see [the Octokit.js README](https://github.com/octokit/octokit.js/#readme).
1. Create an instance of `Octokit` with your token. Replace `YOUR-TOKEN` with your token.

   ```javascript copy
   const octokit = new Octokit({
     auth: 'YOUR-TOKEN'
   });
   ```

1. Use `octokit.request` to execute your request.

   * Send the HTTP method and path as the first argument to the `request` method. For more information, see [HTTP method](#http-method) and [Path](#path).
   * Specify all path, query, and body parameters in an object as the second argument to the `request` method. For more information, see [Parameters](#parameters).

   In the following example request, the HTTP method is `POST`, the path is `/repos/{owner}/{repo}/issues`, the path parameters are `owner: "octocat"` and `repo: "Spoon-Knife"`, and the body parameters are `title: "Created with the REST API"` and `body: "This is a test issue created by the REST API"`.

   &gt; [!NOTE]
   &gt; If you are using a fine-grained personal access token, you must replace `octocat/Spoon-Knife` with a repository that you own or that is owned by an organization that you are a member of. Your token must have access to that repository and have read and write permissions for repository issues. For more information, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

   ```javascript copy
   await octokit.request("POST /repos/{owner}/{repo}/issues", {
     owner: "octocat",
     repo: "Spoon-Knife",
     title: "Created with the REST API",
     body: "This is a test issue created by the REST API",
   });
   ```

   The `request` method automatically passes the `Accept: application/vnd.github+json` header. To pass additional headers or a different `Accept` header, add a `headers` property to the object that is passed as a second argument. The value of the `headers` property is an object with the header names as keys and header values as values.

   For example, the following code will send a `content-type` header with a value of `text/plain` and a `X-GitHub-Api-Version` header with a value of `2026-03-10`.

   ```javascript copy
   await octokit.request("GET /octocat", {
     headers: {
       "content-type": "text/plain",
       "X-GitHub-Api-Version": "2026-03-10",
     },
   });
   ```



## Using the response

After you make a request, the API will return the response status code, response headers, and potentially a response body.


</pre>

</details>

### Current evidence: `chunk-f62c569b11e1f8f3e5f767abb6c1aee7161d6090ea5eb37948ea2c59cee855e9`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-f62c569b11e1f8f3e5f767abb6c1aee7161d6090ea5eb37948ea2c59cee855e9.md`
- content SHA256: `bd0b6eb0818694cd7f3ee2e58abe6644d48840de8bf4dbd8d1e7ade9861556b4`
- byte count: `5939`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About the response code and headers`
- parent source ID: `docs-getting-started`
- parent document ID: `authored-docs-getting-started`
- parent normalized SHA256: `c8fc1dfea1c46150a8e153cdbde4832a4566d90f7d79cd0e00bacc523f91da96`

<details>
<summary>Evidence content</summary>

<pre>
### About the response code and headers

Every request will return an HTTP status code that indicates the success of the response. For more information about response codes, see [the MDN HTTP response status code documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).

Additionally, the response will include headers that give more details about the response. Headers that start with `X-` or `x-` are custom to GitHub. For example, the `x-ratelimit-remaining` and `x-ratelimit-reset` headers tell you how many requests you can make in a time period.



To view the status code and headers, use the `--include` or `--i` option when you send your request.

For example, this request gets a list of issues in the octocat/Spoon-Knife repository:

```shell
gh api \
--header 'Accept: application/vnd.github+json' \
--method GET /repos/octocat/Spoon-Knife/issues \
-F per_page=2 --include
```

And it returns a response code and headers that look something like this:

```shell
HTTP/2.0 200 OK
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: ETag, Link, Location, Retry-After, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Resource, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type, X-GitHub-SSO, X-GitHub-Request-Id, Deprecation, Sunset
Cache-Control: private, max-age=60, s-maxage=60
Content-Security-Policy: default-src 'none'
Content-Type: application/json; charset=utf-8
Date: Thu, 04 Aug 2022 19:56:41 GMT
Etag: W/"a63dfbcfdb73621e9d2e89551edcf9856731ced534bd7f1e114a5da1f5f73418"
Link: &lt;https://api.github.com/repositories/1300192/issues?per_page=1&amp;page=2&gt;; rel="next", &lt;https://api.github.com/repositories/1300192/issues?per_page=1&amp;page=14817&gt;; rel="last"
Referrer-Policy: origin-when-cross-origin, strict-origin-when-cross-origin
Server: GitHub.com
Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
Vary: Accept, Authorization, Cookie, Accept-Encoding, Accept, X-Requested-With
X-Accepted-Oauth-Scopes: repo
X-Content-Type-Options: nosniff
X-Frame-Options: deny
X-Github-Api-Version-Selected: 2022-08-09
X-Github-Media-Type: github.v3; format=json
X-Github-Request-Id: 1C73:26D4:E2E500:1EF78F4:62EC2479
X-Oauth-Client-Id: 178c6fc778ccc68e1d6a
X-Oauth-Scopes: gist, read:org, repo, workflow
X-Ratelimit-Limit: 15000
X-Ratelimit-Remaining: 14996
X-Ratelimit-Reset: 1659645499
X-Ratelimit-Resource: core
X-Ratelimit-Used: 4
X-Xss-Protection: 0
```

In this example, the response code is `200`, which indicates a successful request.





When you make a request with Octokit.js, the `request` method returns a promise. If the request was successful, the promise resolves to an object that includes the HTTP status code of the response (`status`) and the response headers (`headers`). If an error occurs, the promise resolves to an object that includes the HTTP status code of the response (`status`) and the response headers (`response.headers`).

You can use a `try/catch` block to catch an error if it occurs. For example, if the request in the following script is successful, the script will log the status code and the value of the `x-ratelimit-remaining` header. If the request was not successful, the script will log the status code, the value of the `x-ratelimit-remaining` header, and the error message.

In the following example, replace `REPO-OWNER` with the name of the account that owns the repository, and `REPO-NAME` with the name of the repository.

```javascript copy
try {
  const result = await octokit.request("GET /repos/{owner}/{repo}/issues", {
    owner: "REPO-OWNER",
    repo: "REPO-NAME",
    per_page: 2,
  });

  console.log(`Success! Status: ${result.status}. Rate limit remaining: ${result.headers["x-ratelimit-remaining"]}`)

} catch (error) {
  console.log(`Error! Status: ${error.status}. Rate limit remaining: ${error.headers["x-ratelimit-remaining"]}. Message: ${error.response.data.message}`)
}
```





To view the status code and headers, use the `--include` or `--i` option when you send your request.

For example, this request gets a list of issues in the octocat/Spoon-Knife repository:

```shell
curl --request GET \
--url "https://api.github.com/repos/octocat/Spoon-Knife/issues?per_page=2" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer YOUR-TOKEN" \
--include
```

And it returns a response code and headers that look something like this:

```shell
HTTP/2 200
server: GitHub.com
date: Thu, 04 Aug 2022 20:07:51 GMT
content-type: application/json; charset=utf-8
cache-control: public, max-age=60, s-maxage=60
vary: Accept, Accept-Encoding, Accept, X-Requested-With
etag: W/"7fceb7e8c958d3ec4d02524b042578dcc7b282192e6c939070f4a70390962e18"
x-github-media-type: github.v3; format=json
link: &lt;https://api.github.com/repositories/1300192/issues?per_page=2&amp;sort=updated&amp;direction=asc&amp;page=2&gt;; rel="next", &lt;https://api.github.com/repositories/1300192/issues?per_page=2&amp;sort=updated&amp;direction=asc&amp;page=7409&gt;; rel="last"
access-control-expose-headers: ETag, Link, Location, Retry-After, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Resource, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type, X-GitHub-SSO, X-GitHub-Request-Id, Deprecation, Sunset
access-control-allow-origin: *
strict-transport-security: max-age=31536000; includeSubdomains; preload
x-frame-options: deny
x-content-type-options: nosniff
x-xss-protection: 0
referrer-policy: origin-when-cross-origin, strict-origin-when-cross-origin
content-security-policy: default-src 'none'
x-ratelimit-limit: 15000
x-ratelimit-remaining: 14996
x-ratelimit-reset: 1659645535
x-ratelimit-resource: core
x-ratelimit-used: 4
accept-ranges: bytes
content-length: 4936
x-github-request-id: 14E0:4BC6:F1B8BA:208E317:62EC2715
```

In this example, the response code is `200`, which indicates a successful request.




</pre>

</details>

## Cluster: `guidance:docs-pagination`

- evaluation role: `evaluation_development_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-pagination`

### Current evidence: `chunk-181c3fb39ae34ec7ece304c0896c9e1c80ebe919cb47ee0beb7d43a1795e9e12`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-181c3fb39ae34ec7ece304c0896c9e1c80ebe919cb47ee0beb7d43a1795e9e12.md`
- content SHA256: `3ad72fac3df56139966b83b0021a76157589622fd0b8dc9b4aac243550059e79`
- byte count: `2483`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Example creating a pagination method`
- parent source ID: `docs-pagination`
- parent document ID: `authored-docs-pagination`
- parent normalized SHA256: `73397c17264b0d32785fe0d17586c9f710cdfc7183aa7ac8698e168740c437b1`

<details>
<summary>Evidence content</summary>

<pre>
### Example creating a pagination method

If you are using another language or library that doesn't have a pagination method, you can build your own pagination method. This example still uses the Octokit.js library to make requests, but does not rely on `octokit.paginate()`.

The `getPaginatedData` function makes a request to an endpoint with `octokit.request()`. The data from the response is processed by `parseData`, which handles cases where no data is returned or cases where the data that is returned is an object instead of an array. The processed data is then appended to a list that contains all of the paginated data collected so far. If the response includes a `link` header and if the `link` header includes a link for the next page, then the function uses a RegEx pattern (`nextPattern`) to get the URL for the next page. The function then repeats the previous steps, now using this new URL. Once the `link` header no longer includes a link to the next page, all of the results are returned.

```javascript copy
import { Octokit } from "octokit";

const octokit = new Octokit({ });

async function getPaginatedData(url) {
  const nextPattern = /(?&lt;=&lt;)([\S]*)(?=&gt;; rel="next")/i;
  let pagesRemaining = true;
  let data = [];

  while (pagesRemaining) {
    const response = await octokit.request(`GET ${url}`, {
      per_page: 100,
      headers: {
        "X-GitHub-Api-Version":
          "2026-03-10",
      },
    });

    const parsedData = parseData(response.data)
    data = [...data, ...parsedData];

    const linkHeader = response.headers.link;

    pagesRemaining = linkHeader &amp;&amp; linkHeader.includes(`rel=\"next\"`);

    if (pagesRemaining) {
      url = linkHeader.match(nextPattern)[0];
    }
  }

  return data;
}

function parseData(data) {
  // If the data is an array, return that
    if (Array.isArray(data)) {
      return data
    }

  // Some endpoints respond with 204 No Content instead of empty array
  //   when there is no data. In that case, return an empty array.
  if (!data) {
    return []
  }

  // Otherwise, the array of items that we want is in an object
  // Delete keys that don't include the array of items
  delete data.incomplete_results;
  delete data.repository_selection;
  delete data.total_count;
  // Pull out the array of items
  const namespaceKey = Object.keys(data)[0];
  data = data[namespaceKey];

  return data;
}

const data = await getPaginatedData("/repos/octocat/Spoon-Knife/issues");

console.log(data);
```

</pre>

</details>

### Current evidence: `chunk-b549d8c7ee35b3cadf0a2abfd4e82db27c7d4de5876a2a6f401ac5fc469da40b`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-b549d8c7ee35b3cadf0a2abfd4e82db27c7d4de5876a2a6f401ac5fc469da40b.md`
- content SHA256: `bd3aef13e00db0226a31cc4351dfb741d37e8c93ea231791247a7bcd60f61144`
- byte count: `7446`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About pagination` ? `Using `link` headers` ? `Changing the number of items per page` ? `Scripting with pagination` ? `Example using the Octokit.js pagination method`
- parent source ID: `docs-pagination`
- parent document ID: `authored-docs-pagination`
- parent normalized SHA256: `73397c17264b0d32785fe0d17586c9f710cdfc7183aa7ac8698e168740c437b1`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Using pagination in the REST API
intro: Learn how to navigate through paginated responses from the REST API.
redirect_from:
  - /guides/traversing-with-pagination
  - /v3/guides/traversing-with-pagination
  - /rest/guides/traversing-with-pagination
  - /rest/guides/using-pagination-in-the-rest-api
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
shortTitle: Pagination
category:
  - Learn about the REST API
---

## About pagination

When a response from the REST API would include many results, GitHub will paginate the results and return a subset of the results. For example, `GET /repos/octocat/Spoon-Knife/issues` will only return 30 issues from the `octocat/Spoon-Knife` repository even though the repository includes over 1600 open issues. This makes the response easier to handle for servers and for people.

You can use the `link` header from the response to request additional pages of data. If an endpoint supports the `per_page` query parameter, you can control how many results are returned on a page.

This article demonstrates how to request additional pages of results for paginated responses, how to change the number of results returned on each page, and how to write a script to fetch multiple pages of results.

## Using `link` headers

When a response is paginated, the response headers will include a `link` header. If the endpoint does not support pagination, or if all results fit on a single page, the `link` header will be omitted.

The `link` header contains URLs that you can use to fetch additional pages of results. For example, the previous, next, first, and last page of results.

To see the response headers for a particular endpoint, you can use curl, GitHub CLI, or a library you're using to make requests. To see the response headers if you are using a library to make requests, follow the documentation for that library. To see the response headers if you are using curl or GitHub CLI, pass the `--include` flag with your request. For example:

  ```shell
  curl --include --request GET \
  --url "https://api.github.com/repos/octocat/Spoon-Knife/issues" \
  --header "Accept: application/vnd.github+json"
  ```

If the response is paginated, the `link` header will look something like this:

```http
link: &lt;https://api.github.com/repositories/1300192/issues?page=2&gt;; rel="prev", &lt;https://api.github.com/repositories/1300192/issues?page=4&gt;; rel="next", &lt;https://api.github.com/repositories/1300192/issues?page=515&gt;; rel="last", &lt;https://api.github.com/repositories/1300192/issues?page=1&gt;; rel="first"
```

The `link` header provides the URL for the previous, next, first, and last page of results:

* The URL for the previous page is followed by `rel="prev"`.
* The URL for the next page is followed by `rel="next"`.
* The URL for the last page is followed by `rel="last"`.
* The URL for the first page is followed by `rel="first"`.

In some cases, only a subset of these links are available. For example, the link to the previous page won't be included if you are on the first page of results, and the link to the last page won't be included if it can't be calculated.

You can use the URLs from the `link` header to request another page of results. For example, to request the last page of results based on the previous example:

```shell
curl --include --request GET \
--url "https://api.github.com/repositories/1300192/issues?page=515" \
--header "Accept: application/vnd.github+json"
```

The URLs in the `link` header use query parameters to indicate which page of results to return. The query parameters in the `link` URLs may differ between endpoints, however each paginated endpoint will use the `page`, `before`/`after`, or `since` query parameters. (Some endpoints use the `since` parameter for something other than pagination.) In all cases, you can use the URLs in the `link` header to fetch additional pages of results. For more information about query parameters see [/rest/using-the-rest-api/getting-started-with-the-rest-api#query-parameters](/rest/using-the-rest-api/getting-started-with-the-rest-api#query-parameters).

## Changing the number of items per page

If an endpoint supports the `per_page` query parameter, then you can control how many results are returned on a page. For more information about query parameters see [/rest/using-the-rest-api/getting-started-with-the-rest-api#query-parameters](/rest/using-the-rest-api/getting-started-with-the-rest-api#query-parameters).

For most endpoints, the maximum value of `per_page` is `100`. If you specify a value greater than the maximum, GitHub does not return an error. Instead, the value is automatically reduced to the maximum, and the response includes no more than the maximum number of results per page. Because the request still succeeds, you may receive fewer results than you expect without any indication that the `per_page` value was reduced. To confirm the default and maximum `per_page` values for an endpoint, see the reference documentation for that endpoint.

For example, this request uses the `per_page` query parameter to return two items per page:

```shell
curl --include --request GET \
--url "https://api.github.com/repos/octocat/Spoon-Knife/issues?per_page=2" \
--header "Accept: application/vnd.github+json"
```

The `per_page` parameter will automatically be included in the `link` header. For example:

```http
link: &lt;https://api.github.com/repositories/1300192/issues?per_page=2&amp;page=2&gt;; rel="next", &lt;https://api.github.com/repositories/1300192/issues?per_page=2&amp;page=7715&gt;; rel="last"
```

## Scripting with pagination

Instead of manually copying URLs from the `link` header, you can write a script to fetch multiple pages of results.

The following examples use JavaScript and GitHub's Octokit.js library. For more information about Octokit.js, see [/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=javascript](/rest/using-the-rest-api/getting-started-with-the-rest-api?tool=javascript) and [the Octokit.js README](https://github.com/octokit/octokit.js/#readme).

### Example using the Octokit.js pagination method

To fetch paginated results with Octokit.js, you can use `octokit.paginate()`. `octokit.paginate()` will fetch the next page of results until it reaches the last page and then return all of the results as a single array. A few endpoints return paginated results as array in an object, as opposed to returning the paginated results as an array. `octokit.paginate()` always returns an array of items even if the raw result was an object.

For example, this script gets all of the issues from the `octocat/Spoon-Knife` repository. Although it requests 100 issues at a time, the function won't return until the last page of data is reached.

```javascript copy
import { Octokit } from "octokit";

const octokit = new Octokit({ });

const data = await octokit.paginate("GET /repos/{owner}/{repo}/issues", {
  owner: "octocat",
  repo: "Spoon-Knife",
  per_page: 100,
  headers: {
    "X-GitHub-Api-Version": "2026-03-10",
  },
});

console.log(data)
```

You can pass an optional map function to `octokit.paginate()` to end pagination before the last page is reached or to reduce memory usage by keeping only a subset of the response. You can also use `octokit.paginate.iterator()` to iterate through a single page at a time instead of requesting every page. For more information, see [the Octokit.js documentation](https://github.com/octokit/octokit.js#pagination).


</pre>

</details>

## Cluster: `guidance:docs-rate-limits`

- evaluation role: `intervention_tuning_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-rate-limits`

### Current evidence: `chunk-90aa40f5585c27ad415f5b18364968bc333a802224510c4f5a464ae4eb591f3e`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-90aa40f5585c27ad415f5b18364968bc333a802224510c4f5a464ae4eb591f3e.md`
- content SHA256: `e16a68244c0fc4c7832b2e84d4fe649061086b8fdfd342b8be632db13dc7da0e`
- byte count: `7710`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `About primary rate limits` ? `Primary rate limit for unauthenticated users` ? `Primary rate limit for authenticated users` ? `Primary rate limit for Git LFS access` ? `Primary rate limit for GitHub App installations` ? `Primary rate limit for OAuth apps` ? `Primary rate limit for `GITHUB_TOKEN` in GitHub Actions` ? `About secondary rate limits`
- parent source ID: `docs-rate-limits`
- parent document ID: `authored-docs-rate-limits`
- parent normalized SHA256: `0572db1782e9c772493e40c03162d37c92e7e0bb1222cd1484fd55193a969ec5`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Rate limits for the REST API
shortTitle: Rate limits
intro: 'Learn about REST API rate limits, how to avoid exceeding them, and what to do if you do exceed them.'
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
redirect_from:
  - /rest/overview/rate-limits-for-the-rest-api
category:
  - Learn about the REST API
---



## About primary rate limits

GitHub limits the number of REST API requests that you can make within a specific amount of time. This limit helps prevent abuse and denial-of-service attacks, and ensures that the API remains available for all users.

Some endpoints, like the search endpoints, have more restrictive limits. For more information about these endpoints, see [/rest/rate-limit/rate-limit](/rest/rate-limit/rate-limit). The GraphQL API also has a separate primary rate limit. See [/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api](/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api).




In general, you can calculate your primary rate limit for the REST API based on your method of authentication, as described below.

### Primary rate limit for unauthenticated users

You can make unauthenticated requests if you are only fetching public data. Unauthenticated requests are associated with the originating IP address, not with the user or application that made the request.

  The primary rate limit for unauthenticated requests is 60 requests per hour.


### Primary rate limit for authenticated users

You can use a personal access token to make API requests. Additionally, you can authorize a GitHub App or OAuth app, which can then make API requests on your behalf.

  All of these requests count towards your personal rate limit of 5,000 requests per hour. Requests made on your behalf by a GitHub App that is owned by a GitHub Enterprise Cloud organization have a higher rate limit of 15,000 requests per hour. Similarly, requests made on your behalf by a OAuth app that is owned or approved by a GitHub Enterprise Cloud organization have a higher rate limit of 15,000 requests per hour if you are a member of the GitHub Enterprise Cloud organization. However, requests made by a higher-limit app reduce the remaining budget available for lower-limit authentication methods. For example, if an app with a 15,000 request limit makes 10,000 requests on your behalf, you will have exhausted the 5,000 request budget for your personal access tokens, even though the app has 5,000 requests remaining.




### Primary rate limit for Git LFS access

API requests are required when you upload or download Git LFS content. These count towards a separate rate limiting bucket with a limit of 300 requests per minute for unauthenticated requests and 3,000 requests per minute for authenticated requests.

Git LFS uses a batch API which processes 100 Git LFS objects per API request by default. That means unauthenticated users can download 30,000 Git LFS objects per minute and authenticated users can upload/download 300,000 Git LFS objects per minute.

### Primary rate limit for GitHub App installations

GitHub Apps authenticating with an installation access token use the installation's minimum rate limit of 5,000 requests per hour. If the installation is on a GitHub Enterprise Cloud organization, the installation has a rate limit of 15,000 requests per hour.

  For installations that are not on a GitHub Enterprise Cloud organization, the rate limit for the installation will scale with the number of users and repositories. Installations that have more than 20 repositories receive another 50 requests per hour for each repository. Installations that are on an organization that have more than 20 users receive another 50 requests per hour for each user. The rate limit cannot increase beyond 12,500 requests per hour.

  Primary rate limits for GitHub App user access tokens (as opposed to installation access tokens) are dictated by the primary rate limits for the authenticated user. This rate limit is combined with any requests that another GitHub App or OAuth app makes on that user's behalf and any requests that the user makes with a personal access token. For more information, see [/rest/using-the-rest-api/rate-limits-for-the-rest-api#primary-rate-limit-for-authenticated-users](/rest/using-the-rest-api/rate-limits-for-the-rest-api#primary-rate-limit-for-authenticated-users).


### Primary rate limit for OAuth apps

Primary rate limits for OAuth access tokens generated by a OAuth app are dictated by the primary rate limits for authenticated users. This rate limit is combined with any requests that another GitHub App or OAuth app makes on that user's behalf and any requests that the user makes with a personal access token. See [Primary rate limit for authenticated users](#primary-rate-limit-for-authenticated-users).

OAuth apps can also use their client ID and client secret to fetch public data. For example:

```shell
curl -u YOUR_CLIENT_ID:YOUR_CLIENT_SECRET -I https://api.github.com/meta
```

For these requests, the rate limit is 5,000 requests per hour per OAuth app. If the app is owned by a GitHub Enterprise Cloud organization, the rate limit is 15,000 requests per hour.


&gt; [!NOTE]
&gt; Never include your app's client secret in client-side code or in code that runs on a user device. The client secret can be used to generate OAuth access tokens for users who have authorized your app, so you should always keep the client secret secure.

### Primary rate limit for `GITHUB_TOKEN` in GitHub Actions

You can use the built-in `GITHUB_TOKEN` to authenticate requests in GitHub Actions workflows. See [/actions/tutorials/authenticate-with-github_token](/actions/tutorials/authenticate-with-github_token).

The rate limit for `GITHUB_TOKEN` is 1,000 requests per hour per repository. For requests to resources that belong to a GitHub Enterprise Cloud account, the limit is 15,000 requests per hour per repository.


## About secondary rate limits

In addition to primary rate limits, GitHub enforces secondary rate limits in order to prevent abuse and keep the API available for all users.

You may encounter a secondary rate limit if you:

* _Make too many concurrent requests._ No more than 100 concurrent requests are allowed. This limit is shared across the REST API and GraphQL API.
* _Make too many requests to a single endpoint per minute._ No more than 900 points per minute are allowed for REST API endpoints, and no more than 2,000 points per minute are allowed for the GraphQL API endpoint. For more information about points, see [Calculating points for the secondary rate limit](#calculating-points-for-the-secondary-rate-limit).
* _Make too many requests per minute._ No more than 90 seconds of CPU time per 60 seconds of real time is allowed. No more than 60 seconds of this CPU time may be for the GraphQL API. You can roughly estimate the CPU time by measuring the total response time for your API requests.
* _Make too many requests that consume excessive compute resources in a short period of time._
* _Create too much content on GitHub in a short amount of time._ In general, no more than 80 content-generating requests per minute and no more than 500 content-generating requests per hour are allowed. Some endpoints have lower content creation limits. Content creation limits include actions taken on the GitHub web interface as well as via the REST API and GraphQL API.
* _Make too many OAuth access token requests in a short period of time._ No more than 2,000 OAuth access token requests per hour are allowed for GitHub Apps and OAuth apps.

These secondary rate limits are subject to change without notice. You may also encounter a secondary rate limit for undisclosed reasons.


</pre>

</details>

### Current evidence: `chunk-98db24aebd4add7d628a9b2f602393c6db25f6ab0d6ed8a467964b0bb2dcdcf5`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-98db24aebd4add7d628a9b2f602393c6db25f6ab0d6ed8a467964b0bb2dcdcf5.md`
- content SHA256: `959d482d2db57d2dcf5442afe617f774b583f5721ed9ee13c267257f340c1369`
- byte count: `4086`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Calculating points for the secondary rate limit` ? `Checking the status of your rate limit` ? `Exceeding the rate limit` ? `Staying under the rate limit` ? `Getting a higher rate limit`
- parent source ID: `docs-rate-limits`
- parent document ID: `authored-docs-rate-limits`
- parent normalized SHA256: `0572db1782e9c772493e40c03162d37c92e7e0bb1222cd1484fd55193a969ec5`

<details>
<summary>Evidence content</summary>

<pre>
### Calculating points for the secondary rate limit

Some secondary rate limits are determined by the point values of requests. For GraphQL requests, these point values are separate from the point value calculations for the primary rate limit.

| Request | Points |
|--------|--------|
| GraphQL requests without mutations | 1 |
| GraphQL requests with mutations | 5 |
| Most REST API `GET`, `HEAD`, and `OPTIONS` requests | 1 |
| Most REST API `POST`, `PATCH`, `PUT`, or `DELETE` requests | 5 |

Some REST API endpoints have a different point cost that is not shared publicly.


## Checking the status of your rate limit

You can use the headers that are sent with each response to determine the current status of your primary rate limit.

Header name | Description
-----------|-----------|
`x-ratelimit-limit` | The maximum number of requests that you can make per hour
`x-ratelimit-remaining` | The number of requests remaining in the current rate limit window
`x-ratelimit-used` | The number of requests you have made in the current rate limit window
`x-ratelimit-reset` | The time at which the current rate limit window resets, in UTC epoch seconds
`x-ratelimit-resource` | The rate limit resource that the request counted against. For more information about the different resources, see [/rest/rate-limit/rate-limit#get-rate-limit-status-for-the-authenticated-user](/rest/rate-limit/rate-limit#get-rate-limit-status-for-the-authenticated-user).

You can also call the `GET /rate_limit` endpoint to check your rate limit. Calling this endpoint does not count against your primary rate limit, but it can count against your secondary rate limit. See [/rest/rate-limit/rate-limit](/rest/rate-limit/rate-limit). When possible, you should use the rate limit response headers instead of calling the API to check your rate limit.

There is not a way to check the status of your secondary rate limit.

## Exceeding the rate limit

If you exceed your primary rate limit, you will receive a `403` or `429` response, and the `x-ratelimit-remaining` header will be `0`. You should not retry your request until after the time specified by the `x-ratelimit-reset` header.

If you exceed a secondary rate limit, you will receive a `403` or `429` response and an error message that indicates that you exceeded a secondary rate limit. If the `retry-after` response header is present, you should not retry your request until after that many seconds has elapsed. If the `x-ratelimit-remaining` header is `0`, you should not retry your request until after the time, in UTC epoch seconds, specified by the `x-ratelimit-reset` header. Otherwise, wait for at least one minute before retrying. If your request continues to fail due to a secondary rate limit, wait for an exponentially increasing amount of time between retries, and throw an error after a specific number of retries.

Continuing to make requests while you are rate limited may result in the banning of your integration.

## Staying under the rate limit

You should follow best practices to help you stay under the rate limits. See [/rest/using-the-rest-api/best-practices-for-using-the-rest-api](/rest/using-the-rest-api/best-practices-for-using-the-rest-api).



## Getting a higher rate limit

If you want a higher primary rate limit, consider making authenticated requests instead of unauthenticated requests. Authenticated requests have a significantly higher rate limit than unauthenticated requests.

If you are using a personal access token for automation in your organization, consider whether a GitHub App will work instead. The rate limit for GitHub Apps using an installation access token scales with the number of repositories and number of organization users. See [/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps](/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps).



If you are using GitHub Apps or OAuth apps, consider upgrading to GitHub Enterprise Cloud. GitHub Apps or OAuth apps have higher rate limits for organizations that use GitHub Enterprise Cloud.

</pre>

</details>

## Cluster: `guidance:docs-timezones`

- evaluation role: `held_out_release_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-timezones`

### Current evidence: `chunk-cd0e87ca852080c49fd723c0efd6e0225afeae8be7ed5ec25df339ed1e8807bb`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-cd0e87ca852080c49fd723c0efd6e0225afeae8be7ed5ec25df339ed1e8807bb.md`
- content SHA256: `1098fec781d02a7612836ebdc790b59ed31e2f5a1c09ed47cd93cac203ec3ed6`
- byte count: `2683`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Determining the timezone for a request` ? `Explicitly providing an ISO 8601 timestamp with timezone information` ? `Using the `Time-Zone` header` ? `Using the last known timezone for the user` ? `Defaulting to UTC without other timezone information`
- parent source ID: `docs-timezones`
- parent document ID: `authored-docs-timezones`
- parent normalized SHA256: `1098fec781d02a7612836ebdc790b59ed31e2f5a1c09ed47cd93cac203ec3ed6`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Timezones and the REST API
shortTitle: Timezones
intro: 'Some REST API endpoints allow you to specify timezone information with your request.'
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
category:
  - Learn about the REST API
---

Some requests that create new data, such as creating a new commit, allow you to provide timezone information when specifying or generating timestamps.

Note that these rules apply only to data passed to the API, not to data returned by the API. Timestamps returned by the API are in UTC time, ISO 8601 format.

## Determining the timezone for a request

To determine timezone information for applicable API calls, we apply these rules in order of priority:

1. [Explicitly providing an ISO 8601 timestamp with timezone information](#explicitly-providing-an-iso-8601-timestamp-with-timezone-information)
1. [Using the `Time-Zone` header](#using-the-time-zone-header)
1. [Using the last known timezone for the user](#using-the-last-known-timezone-for-the-user)
1. [Defaulting to UTC without other timezone information](#defaulting-to-utc-without-other-timezone-information)

### Explicitly providing an ISO 8601 timestamp with timezone information

For API calls that allow for a timestamp to be specified, we use that exact timestamp. These timestamps look something like `2014-02-27T15:05:06+01:00`.

An example of this is the API to manage commits. For more information, see [/rest/git/commits#create-a-commit](/rest/git/commits#create-a-commit).

### Using the `Time-Zone` header

It is possible to supply a `Time-Zone` header, which defines a timezone according to the [list of names from the Olson database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

```shell
curl -H "Time-Zone: Europe/Amsterdam" -X POST https://api.github.com/repos/github-linguist/linguist/contents/new_file.md
```

This means that we generate a timestamp for the moment your API call is made, in the timezone this header defines.

For example, the API to manage contents generates a git commit for each addition or change, and it uses the current time as the timestamp. For more information, see [/rest/repos/contents](/rest/repos/contents). The `Time-Zone` header will determine the timezone used for generating that current timestamp.

### Using the last known timezone for the user

If no `Time-Zone` header is specified and you make an authenticated call to the API, we use the last known timezone for the authenticated user. The last known timezone is updated whenever you browse the GitHub website.

### Defaulting to UTC without other timezone information

If the steps above don't result in any information, we use UTC as the timezone.

</pre>

</details>

## Cluster: `guidance:docs-troubleshooting`

- evaluation role: `evaluation_development_case`
- cluster kind: `authored_guidance`
- source family: `cross_cutting_rest_guidance`
- authored source ID: `docs-troubleshooting`

### Current evidence: `chunk-6fc744dee58c1b47dfa67cf1f3c95bc4e791320346e08158a29f8be891afc752`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-6fc744dee58c1b47dfa67cf1f3c95bc4e791320346e08158a29f8be891afc752.md`
- content SHA256: `29430a0c1a7ab7e56975ed89d18006fc1d23fa79d25744f7d65f279b2e75acf1`
- byte count: `7475`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: ``404 Not Found` for an existing resource`
- parent source ID: `docs-troubleshooting`
- parent document ID: `authored-docs-troubleshooting`
- parent normalized SHA256: `69db71f26abf11f1ba9928fa6788de4e78e856b1fb953ff88097642bddcd076a`

<details>
<summary>Evidence content</summary>

<pre>
## `404 Not Found` for an existing resource

If you make a request to access a private resource and your request isn't properly authenticated, you will receive a `404 Not Found` response. GitHub uses a `404 Not Found` response instead of a `403 Forbidden` response to avoid confirming the existence of private repositories.

If you get a `404 Not Found` response when you know that the resource that you are requesting exists, you should check your authentication. For example:

* If you are using a personal access token (classic), you should ensure that:
  * The token has the scopes that are required to use the endpoint. For more information, see [/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes](/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes) and [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).
  * The owner of the token has any permissions that are required to use the endpoint. For example, if an endpoint can only be used by organization owners, only users that are owners of the affected organization can use the endpoint.
  * The token has not been expired or revoked. For more information, see [/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation](/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation).
* If you are using a fine-grained personal access token, you should ensure that:
  * The token has the permissions that are required to use the endpoint. For more information about the required permissions, see the documentation for the endpoint.
  * The resource owner that was specified for the token matches the owner of the resource that the endpoint will affect. For more information, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).
  * The token has access to any private repositories that the endpoint will affect. For more information, see [/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token](/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).
  * The owner of the token has any permissions that are required to use the endpoint. For example, if an endpoint can only be used by organization owners, only users that are owners of the affected organization can use the endpoint.
  * The token has not been expired or revoked. For more information, see [/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation](/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation).
* If you are using a GitHub App installation access token, you should ensure that:
  * The GitHub App has the permissions that are required to use the endpoint. For more information about the required permissions, see the documentation for the endpoint.
  * The endpoint is only affecting resources owned by the account where the GitHub App is installed.
  * The GitHub App has access to any repositories that the endpoint will affect.
  * The token has not been expired or revoked. For more information, see [/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation](/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation).
* If you are using a GitHub App user access token, you should ensure that:
  * The GitHub App has the permissions that are required to use the endpoint. For more information about the required permissions, see the documentation for the endpoint.
  * The user that authorized the token has any permissions that are required to use the endpoint. For example, if an endpoint can only be used by organization owners, only users that are owners of the affected organization can use the endpoint.
  * The GitHub App has access to any repositories that the endpoint will affect.
  * The user has access to any repositories that the endpoint will affect.
  * The user has approved any updated permissions for your GitHub App. For more information, see [/apps/using-github-apps/approving-updated-permissions-for-a-github-app](/apps/using-github-apps/approving-updated-permissions-for-a-github-app).
* If you are using an OAuth app user access token, you should ensure that:
  * The token has the scopes that are required to use the endpoint. For more information, see [/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes](/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).
  * The user that authorized the token has any permissions that are required to use the endpoint. For example, if an endpoint can only be used by organization owners, only users that are owners of the affected organization can use the endpoint.
  * The organization has not blocked OAuth app access, if you are using an endpoint that will affect resources owned by an organization. App owners cannot see whether their app is blocked, but they can instruct users of the app to check this. For more information, see [/organizations/managing-oauth-access-to-your-organizations-data/about-oauth-app-access-restrictions](/organizations/managing-oauth-access-to-your-organizations-data/about-oauth-app-access-restrictions).
  * The token has not been expired or revoked. For more information, see [/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation](/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation).
* If you are using `GITHUB_TOKEN` in a GitHub Actions workflow, you should ensure that:
  * The endpoint is only affecting resources owned by the repository where the workflow is running. If you need to access resources outside of that repository, such as resources owned by an organization or resources owned by another repository, you should use a personal access token or an access token for a GitHub App.

For more information about authentication, see [/rest/authentication/authenticating-to-the-rest-api](/rest/authentication/authenticating-to-the-rest-api).

You should also check for typos in your URL. For example, adding a trailing slash to the endpoint will result in a `404 Not Found`. You can refer to the reference documentation for the endpoint to confirm that you have the correct URL.

Additionally, any path parameters must be URL encoded. For example, any slashes in the parameter value must be replaced with `%2F`. If you don't properly encode any slashes in the parameter name, the endpoint URL will be misinterpreted.

You should also confirm that you are using an HTTP method that the endpoint supports. If you send a request with an HTTP method that the endpoint does not support, you will receive a `404 Not Found` response instead of `405 Method Not Allowed`. For example, sending a `DELETE` request to an endpoint that only supports `GET` will result in a `404 Not Found` response. You can refer to the reference documentation for the endpoint to confirm the supported HTTP method.


</pre>

</details>

### Current evidence: `chunk-8dd06f9776710075a0304ff05e06d9c104a0eea6e99e20b7be4e1ac5187d4f27`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-8dd06f9776710075a0304ff05e06d9c104a0eea6e99e20b7be4e1ac5187d4f27.md`
- content SHA256: `21d58f7978cefccb2d1bc2736bfc891cef7f67df7099dcd9ceea06bbceb19c1f`
- byte count: `6892`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Missing results` ? `Requires authentication when using basic authentication` ? `Timeouts` ? `Resource not accessible` ? `Problems parsing JSON` ? `Body should be a JSON object` ? `Invalid request` ? `Validation Failed` ? `Not a supported version` ? `User agent required` ? `Other errors` ? `Further reading`
- parent source ID: `docs-troubleshooting`
- parent document ID: `authored-docs-troubleshooting`
- parent normalized SHA256: `69db71f26abf11f1ba9928fa6788de4e78e856b1fb953ff88097642bddcd076a`

<details>
<summary>Evidence content</summary>

<pre>
## Missing results

Most endpoints that return a list of resources support pagination. For most of these endpoints, only the first 30 resources are returned by default. In order to see all of the resources, you need to paginate through the results. For more information, see [/rest/using-the-rest-api/using-pagination-in-the-rest-api](/rest/using-the-rest-api/using-pagination-in-the-rest-api).

If you are using pagination correctly and still do not see all of the results that you expect, you should confirm that the authentication credentials that you used have access to all of the expected resources. For example, if you are using a GitHub App installation access token, if the installation was only granted access to a subset of repositories in an organization, any request for all repositories in that organization will return only the repositories that the app installation can access.



## Requires authentication when using basic authentication

Basic authentication with your username and password is not supported. Instead, you should use a personal access token or an access token for a GitHub App or OAuth app. For more information, see [/rest/authentication/authenticating-to-the-rest-api](/rest/authentication/authenticating-to-the-rest-api).



## Timeouts

If GitHub takes more than 10 seconds to process an API request, GitHub will terminate the request and you will receive a timeout response and a "Server Error" message.

GitHub reserves the right to change the timeout window to protect the speed and reliability of the API.

You can check the status of the REST API at [githubstatus.com](https://www.githubstatus.com/) to determine whether the timeout is due to a problem with the API. You can also try to simplify your request or try your request later. For example, if you are requesting 100 items on a page, you can try requesting fewer items.

## Resource not accessible

If you are using a GitHub App or fine-grained personal access token and you receive a "Resource not accessible by integration" or "Resource not accessible by personal access token" error, then your token has insufficient permissions. For more information about the required permissions, see the documentation for the endpoint.

You can use the `X-Accepted-GitHub-Permissions` header to identify the permissions that are required to access the REST API endpoint.

The value of the `X-Accepted-GitHub-Permissions` header is a comma separated list of the permissions that are required to use the endpoint. Occasionally, you can choose from multiple permission sets. In these cases, multiple comma-separated lists will be separated by a semicolon.

For example:

* `X-Accepted-GitHub-Permissions: contents=read` means that your GitHub App or fine-grained personal access token needs read access to the contents permission.
* `X-Accepted-GitHub-Permissions: pull_requests=write,contents=read` means that your GitHub App or fine-grained personal access token needs write access to the pull request permission and read access to the contents permission.
* `X-Accepted-GitHub-Permissions: pull_requests=read,contents=read; issues=read,contents=read` means that your GitHub App or fine-grained personal access token needs either read access to the pull request permission and read access to the contents permission, or read access to the issues permission and read access to the contents permission.

## Problems parsing JSON

If you send invalid JSON in the request body, you may receive a `400 Bad Request` response and a "Problems parsing JSON" error message. You can use a linter or JSON validator to help you identify errors in your JSON.

## Body should be a JSON object

If the endpoint expects a JSON object and you do not format your request body as a JSON object, you may receive a `400 Bad Request` response and a "Body should be a JSON object" error message.

## Invalid request

If you omit required parameters or you use the wrong type for a parameter, you may receive a `422 Unprocessable Entity` response and an "Invalid request" error message. For example, you will get this error if you specify a parameter value as an array but the endpoint is expecting a string. You can refer to the reference documentation for the endpoint to verify that you are using the correct parameter types and that you are including all of the required parameters.

## Validation Failed

If your request could not be processed, you may receive a `422 Unprocessable Entity` response and a "Validation Failed" error message. The response body will include an `errors` property, which includes a `code` property to help you diagnose the problem.

Code | Description
-----------|-----------|
`missing` | A resource does not exist.
`missing_field` | A parameter that was required was not specified. Review the documentation for the endpoint to see what parameters are required.
`invalid` | The formatting of a parameter is invalid. Review the endpoint documentation for more specific information.
`already_exists` | Another resource has the same value as one of your parameters. This can happen in resources that must have some unique key (such as label names).
`unprocessable` | The parameters that were provided were invalid.
`custom` | Refer to the `message` property to diagnose the error.

## Not a supported version

You should use the `X-GitHub-Api-Version` header to specify an API version. For example:

```shell
curl --header "X-GitHub-Api-Version:2026-03-10"
 https://api.github.com/zen
```

If you specify a version that does not exist, you will receive a `400 Bad Request` error and a message about the version not being supported.

For more information, see [/rest/about-the-rest-api/api-versions](/rest/about-the-rest-api/api-versions).

## User agent required

Requests without a valid `User-Agent` header will be rejected. You should use your username or the name of your application for the `User-Agent` value.

curl sends a valid `User-Agent` header by default.

## Other errors

If you observe an error that is not addressed here, you should refer to the error message that the API gives you. Most error messages will provide a clue about what is wrong and a link to relevant documentation.

If you observe unexpected failures, you can use [githubstatus.com](https://www.githubstatus.com/) or the [GitHub status API](https://www.githubstatus.com/api) to check for incidents affecting the API.

## Further reading

* [/rest/using-the-rest-api/best-practices-for-using-the-rest-api](/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
* [/webhooks/testing-and-troubleshooting-webhooks/troubleshooting-webhooks](/webhooks/testing-and-troubleshooting-webhooks/troubleshooting-webhooks)
* [/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app](/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app)

</pre>

</details>

### Current evidence: `chunk-c302e7937061f7efe865d21345a74967955cdd60c1d86e84e99966fca1bd9440`

- chunk kind: `authored_section`
- content path: `datasets/chunks/phase3d_v1/authored/chunk-c302e7937061f7efe865d21345a74967955cdd60c1d86e84e99966fca1bd9440.md`
- content SHA256: `1450f5675770ff2c1b7c78a84a6f3ccd91e3d99bba7e2fd5dbfafb70e35642a6`
- byte count: `1952`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- section headings: `Rate limit errors`
- parent source ID: `docs-troubleshooting`
- parent document ID: `authored-docs-troubleshooting`
- parent normalized SHA256: `69db71f26abf11f1ba9928fa6788de4e78e856b1fb953ff88097642bddcd076a`

<details>
<summary>Evidence content</summary>

<pre>
---
title: Troubleshooting the REST API
shortTitle: Troubleshooting
intro: Learn how to diagnose and resolve common problems for the REST API.
redirect_from:
  - /v3/troubleshooting
  - /rest/overview/troubleshooting
  - /rest/overview/troubleshooting-the-rest-api
versions:
  fpt: '*'
  ghes: '*'
  ghec: '*'
category:
  - Learn about the REST API
---

## Rate limit errors

GitHub enforces rate limits to ensure that the API stays available for all users. For more information, see [/rest/using-the-rest-api/rate-limits-for-the-rest-api](/rest/using-the-rest-api/rate-limits-for-the-rest-api).

If you exceed your primary rate limit, you will receive a `403 Forbidden` or `429 Too Many Requests ` response, and the `x-ratelimit-remaining` header will be `0`. If you exceed a secondary rate limit, you will receive a `403 Forbidden` or `429 Too Many Requests ` response and an error message that indicates that you exceeded a secondary rate limit.

If you receive a rate limit error, you should stop making requests temporarily according to these guidelines:

* If the `retry-after` response header is present, you should not retry your request until after that many seconds has elapsed.
* If the `x-ratelimit-remaining` header is `0`, you should not make another request until after the time specified by the `x-ratelimit-reset` header. The `x-ratelimit-reset` header is in UTC epoch seconds.
* Otherwise, wait for at least one minute before retrying. If your request continues to fail due to a secondary rate limit, wait for an exponentially increasing amount of time between retries, and throw an error after a specific number of retries.

Continuing to make requests while you are rate limited may result in the banning of your integration.




For more information about how to avoid exceeding the rate limits, see [/rest/using-the-rest-api/best-practices-for-using-the-rest-api](/rest/using-the-rest-api/best-practices-for-using-the-rest-api).


</pre>

</details>

## Cluster: `openapi-pair:actions/create-registration-token-for-org`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `actions`
- operation ID: `actions/create-registration-token-for-org`

### Current evidence: `chunk-d694c138d0b2408b36c58947d94949887320b133b604f83157627a3d458410c7`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-d694c138d0b2408b36c58947d94949887320b133b604f83157627a3d458410c7.json`
- content SHA256: `0c665edf93b5f11ab76b8991a20bb62594683d5fe8dd287b051b849833dae9ca`
- byte count: `1498`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-registration-token-for-org`
- parent source ID: `openapi-current-2026-03-10:actions/create-registration-token-for-org`
- parent document ID: `openapi-current-actions-create-registration-token-for-org`
- parent normalized SHA256: `ff88ef1505d80c6728de7bc02c19ae4768b3e10fe77b4ff0c75a9ba4182b12a1`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to configure your self-hosted runner:\n\n```\n./config.sh --url https://github.com/octo-org --token TOKEN\n```\n\nAuthenticated users must have admin access to the organization to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the`admin:org` scope to use this endpoint. If the repository is private, OAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-registration-token-for-an-organization"},"operationId":"actions/create-registration-token-for-org","parameters":[{"$ref":"#/components/parameters/org"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a registration token for an organization","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/orgs/{org}/actions/runners/registration-token","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-d023e9ae7d491e5b7d6643b7308af67438502818868d5528c5ab73f3f1dd8035`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-d023e9ae7d491e5b7d6643b7308af67438502818868d5528c5ab73f3f1dd8035.json`
- content SHA256: `0c665edf93b5f11ab76b8991a20bb62594683d5fe8dd287b051b849833dae9ca`
- byte count: `1498`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-registration-token-for-org`
- parent source ID: `openapi-historical-2022-11-28:actions/create-registration-token-for-org`
- parent document ID: `openapi-historical-actions-create-registration-token-for-org`
- parent normalized SHA256: `a75e33be696266cc30b81538310b7783de85ad6c2af4e80a1d28e9eb9ee5ffad`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to configure your self-hosted runner:\n\n```\n./config.sh --url https://github.com/octo-org --token TOKEN\n```\n\nAuthenticated users must have admin access to the organization to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the`admin:org` scope to use this endpoint. If the repository is private, OAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-registration-token-for-an-organization"},"operationId":"actions/create-registration-token-for-org","parameters":[{"$ref":"#/components/parameters/org"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a registration token for an organization","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/orgs/{org}/actions/runners/registration-token","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:actions/create-registration-token-for-repo`

- evaluation role: `intervention_tuning_case`
- cluster kind: `openapi_version_pair`
- source family: `actions`
- operation ID: `actions/create-registration-token-for-repo`

### Current evidence: `chunk-c17c181dc4ea53ab06b9afd42b1371e4c84991ee1e799c7cd8fd0a8f071f3fa6`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-c17c181dc4ea53ab06b9afd42b1371e4c84991ee1e799c7cd8fd0a8f071f3fa6.json`
- content SHA256: `c03c111df5df66a9ff1f8cc3c54fd22190b6336129b29687af3936d02676986a`
- byte count: `1415`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-registration-token-for-repo`
- parent source ID: `openapi-current-2026-03-10:actions/create-registration-token-for-repo`
- parent document ID: `openapi-current-actions-create-registration-token-for-repo`
- parent normalized SHA256: `21b3014745aecc77656e99942efc10c22a95ddf102555c1f0b5ba2592a571d20`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to configure your self-hosted runner:\n\n```\n./config.sh --url https://github.com/octo-org --token TOKEN\n```\n\nAuthenticated users must have admin access to the repository to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository"},"operationId":"actions/create-registration-token-for-repo","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a registration token for a repository","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/repos/{owner}/{repo}/actions/runners/registration-token","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-dbf49b9a0cd3eb7fd414d8701ab14b0e6a56839678579efed80e04af3f61f4d5`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-dbf49b9a0cd3eb7fd414d8701ab14b0e6a56839678579efed80e04af3f61f4d5.json`
- content SHA256: `c03c111df5df66a9ff1f8cc3c54fd22190b6336129b29687af3936d02676986a`
- byte count: `1415`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-registration-token-for-repo`
- parent source ID: `openapi-historical-2022-11-28:actions/create-registration-token-for-repo`
- parent document ID: `openapi-historical-actions-create-registration-token-for-repo`
- parent normalized SHA256: `edcfe0a468f33669cc88ca28beb016e12ada0e67a22697b396b9379ac2f8f420`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to configure your self-hosted runner:\n\n```\n./config.sh --url https://github.com/octo-org --token TOKEN\n```\n\nAuthenticated users must have admin access to the repository to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository"},"operationId":"actions/create-registration-token-for-repo","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a registration token for a repository","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/repos/{owner}/{repo}/actions/runners/registration-token","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:actions/create-remove-token-for-org`

- evaluation role: `held_out_release_case`
- cluster kind: `openapi_version_pair`
- source family: `actions`
- operation ID: `actions/create-remove-token-for-org`

### Current evidence: `chunk-8cf27b1c1eb50de277026c4b7e29b3c23eb562dd3a0659630cea4fe56bf9ed70`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-8cf27b1c1eb50de277026c4b7e29b3c23eb562dd3a0659630cea4fe56bf9ed70.json`
- content SHA256: `de25e26aec042b477c99874f97a4ffd06015163201441dde8d17ba941b33b9f5`
- byte count: `1519`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-remove-token-for-org`
- parent source ID: `openapi-current-2026-03-10:actions/create-remove-token-for-org`
- parent document ID: `openapi-current-actions-create-remove-token-for-org`
- parent normalized SHA256: `de85de2fa019cb321562d1ecd5b9b97740da8ff13425ada6fde0843507a4d555`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script to remove a self-hosted runner from an organization. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to remove your self-hosted runner from an organization:\n\n```\n./config.sh remove --token TOKEN\n```\n\nAuthenticated users must have admin access to the organization to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the`admin:org` scope to use this endpoint. If the repository is private, OAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-remove-token-for-an-organization"},"operationId":"actions/create-remove-token-for-org","parameters":[{"$ref":"#/components/parameters/org"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token-2"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a remove token for an organization","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/orgs/{org}/actions/runners/remove-token","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-09395c668574eee2a6ff7ffdcd2707bca8b112970827d4273cdebd817a308b6f`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-09395c668574eee2a6ff7ffdcd2707bca8b112970827d4273cdebd817a308b6f.json`
- content SHA256: `de25e26aec042b477c99874f97a4ffd06015163201441dde8d17ba941b33b9f5`
- byte count: `1519`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-remove-token-for-org`
- parent source ID: `openapi-historical-2022-11-28:actions/create-remove-token-for-org`
- parent document ID: `openapi-historical-actions-create-remove-token-for-org`
- parent normalized SHA256: `39b909b8c0c48786bf632cc49ab7afda8118021f4269ed9ad36b83ce0db3cd80`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script to remove a self-hosted runner from an organization. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to remove your self-hosted runner from an organization:\n\n```\n./config.sh remove --token TOKEN\n```\n\nAuthenticated users must have admin access to the organization to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the`admin:org` scope to use this endpoint. If the repository is private, OAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-remove-token-for-an-organization"},"operationId":"actions/create-remove-token-for-org","parameters":[{"$ref":"#/components/parameters/org"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token-2"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a remove token for an organization","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/orgs/{org}/actions/runners/remove-token","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:actions/create-remove-token-for-repo`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `actions`
- operation ID: `actions/create-remove-token-for-repo`

### Current evidence: `chunk-9367992c420cc80d42b78e7129457783f233c67f35787f35c04d1096f8f5f99b`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-9367992c420cc80d42b78e7129457783f233c67f35787f35c04d1096f8f5f99b.json`
- content SHA256: `a08f316bcda2bb5a77b9b36d37439195a0825226673dae7092385ed1f2b60e26`
- byte count: `1434`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-remove-token-for-repo`
- parent source ID: `openapi-current-2026-03-10:actions/create-remove-token-for-repo`
- parent document ID: `openapi-current-actions-create-remove-token-for-repo`
- parent normalized SHA256: `5d9f45c50f2ae4986260a423e1a2cd5c7b152b00c445191ecd6ff57b28f8d104`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script to remove a self-hosted runner from an repository. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to remove your self-hosted runner from an organization:\n\n```\n./config.sh remove --token TOKEN\n```\n\nAuthenticated users must have admin access to the repository to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-remove-token-for-a-repository"},"operationId":"actions/create-remove-token-for-repo","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token-2"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a remove token for a repository","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/repos/{owner}/{repo}/actions/runners/remove-token","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-f8a409e7ecbbb688024449facc6c87f47a9eff2c4963f05edbf58e5e4eae7d31`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-f8a409e7ecbbb688024449facc6c87f47a9eff2c4963f05edbf58e5e4eae7d31.json`
- content SHA256: `a08f316bcda2bb5a77b9b36d37439195a0825226673dae7092385ed1f2b60e26`
- byte count: `1434`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-remove-token-for-repo`
- parent source ID: `openapi-historical-2022-11-28:actions/create-remove-token-for-repo`
- parent document ID: `openapi-historical-actions-create-remove-token-for-repo`
- parent normalized SHA256: `6d19f6796f11ffa885b6dc53f62ac9148195f3e1ebd368a46239ec93387a0822`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Returns a token that you can pass to the `config` script to remove a self-hosted runner from an repository. The token expires after one hour.\n\nFor example, you can replace `TOKEN` in the following example with the registration token provided by this endpoint to remove your self-hosted runner from an organization:\n\n```\n./config.sh remove --token TOKEN\n```\n\nAuthenticated users must have admin access to the repository to use this endpoint.\n\nOAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/self-hosted-runners#create-a-remove-token-for-a-repository"},"operationId":"actions/create-remove-token-for-repo","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/authentication-token-2"}},"schema":{"$ref":"#/components/schemas/authentication-token"}}},"description":"Response"}},"summary":"Create a remove token for a repository","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"self-hosted-runners"}},"path":"/repos/{owner}/{repo}/actions/runners/remove-token","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:actions/create-workflow-dispatch`

- evaluation role: `intervention_tuning_case`
- cluster kind: `openapi_version_pair`
- source family: `actions`
- operation ID: `actions/create-workflow-dispatch`

### Current evidence: `chunk-2662bbb46cac69cfc201f58fa703962df5571ff6ac684e765137368268f351f5`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-2662bbb46cac69cfc201f58fa703962df5571ff6ac684e765137368268f351f5.json`
- content SHA256: `214b09984e960349d9df5ebd7f9fd54ea75eb11842a3b0051b7356fca17e6cf4`
- byte count: `2326`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-workflow-dispatch`
- parent source ID: `openapi-current-2026-03-10:actions/create-workflow-dispatch`
- parent document ID: `openapi-current-actions-create-workflow-dispatch`
- parent normalized SHA256: `340ec55424a872c20d9da2a98c8a76251cf956c1ca74561ac3079309d8622270`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use this endpoint to manually trigger a GitHub Actions workflow run. You can replace `workflow_id` with the workflow file name. For example, you could use `main.yaml`.\n\nYou must configure your GitHub Actions workflow to run when the [`workflow_dispatch` webhook](/developers/webhooks-and-events/webhook-events-and-payloads#workflow_dispatch) event occurs. The `inputs` are configured in the workflow file. For more information about how to configure the `workflow_dispatch` event in the workflow file, see \"[Events that trigger workflows](/actions/reference/events-that-trigger-workflows#workflow_dispatch).\"\n\nOAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/workflows#create-a-workflow-dispatch-event"},"operationId":"actions/create-workflow-dispatch","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/workflow-id"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"inputs":{"home":"San Francisco, CA","name":"Mona the Octocat"},"ref":"topic-branch"}}},"schema":{"properties":{"inputs":{"additionalProperties":true,"description":"Input keys and values configured in the workflow file. The maximum number of properties is 25. Any default properties configured in the workflow file will be used when `inputs` are omitted.","maxProperties":25,"type":"object"},"ref":{"description":"The git reference for the workflow. The reference can be a branch or tag name.","type":"string"}},"required":["ref"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/workflow-dispatch-response"}},"schema":{"$ref":"#/components/schemas/workflow-dispatch-response"}}},"description":"Response including the workflow run ID and URLs."}},"summary":"Create a workflow dispatch event","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"workflows"}},"path":"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-c2692e000e203199b6dd7a3e5eb7bbc5bbadf87ebb479fa451652f20c83ebc52`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-c2692e000e203199b6dd7a3e5eb7bbc5bbadf87ebb479fa451652f20c83ebc52.json`
- content SHA256: `94c4a609acf884e076a2caf99bfa1e6c8ffa0c9b2f7e3447095538ed10424a58`
- byte count: `2581`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `actions`
- linked operations: `actions/create-workflow-dispatch`
- parent source ID: `openapi-historical-2022-11-28:actions/create-workflow-dispatch`
- parent document ID: `openapi-historical-actions-create-workflow-dispatch`
- parent normalized SHA256: `1afca3cfd5780d5d39701d8191b9865c0aff44ba5fa1242ff65411fd30ec0e1e`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use this endpoint to manually trigger a GitHub Actions workflow run. You can replace `workflow_id` with the workflow file name. For example, you could use `main.yaml`.\n\nYou must configure your GitHub Actions workflow to run when the [`workflow_dispatch` webhook](/developers/webhooks-and-events/webhook-events-and-payloads#workflow_dispatch) event occurs. The `inputs` are configured in the workflow file. For more information about how to configure the `workflow_dispatch` event in the workflow file, see \"[Events that trigger workflows](/actions/reference/events-that-trigger-workflows#workflow_dispatch).\"\n\nOAuth tokens and personal access tokens (classic) need the `repo` scope to use this endpoint.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/actions/workflows#create-a-workflow-dispatch-event"},"operationId":"actions/create-workflow-dispatch","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/workflow-id"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"inputs":{"home":"San Francisco, CA","name":"Mona the Octocat"},"ref":"topic-branch"}}},"schema":{"properties":{"inputs":{"additionalProperties":true,"description":"Input keys and values configured in the workflow file. The maximum number of properties is 25. Any default properties configured in the workflow file will be used when `inputs` are omitted.","maxProperties":25,"type":"object"},"ref":{"description":"The git reference for the workflow. The reference can be a branch or tag name.","type":"string"},"return_run_details":{"description":"Whether the response should include the workflow run ID and URLs.","type":"boolean"}},"required":["ref"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/workflow-dispatch-response"}},"schema":{"$ref":"#/components/schemas/workflow-dispatch-response"}}},"description":"Response including the workflow run ID and URLs when `return_run_details` parameter is `true`."},"204":{"description":"Empty response when `return_run_details` parameter is `false`."}},"summary":"Create a workflow dispatch event","tags":["actions"],"x-github":{"category":"actions","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"workflows"}},"path":"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:issues/add-assignees`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `issues`
- operation ID: `issues/add-assignees`

### Current evidence: `chunk-db26bf1f3b7de296c0851a148250427f380b5c18b32e5662922d579b158be8bb`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-db26bf1f3b7de296c0851a148250427f380b5c18b32e5662922d579b158be8bb.json`
- content SHA256: `db19be209b80c9a0b73361ec3f0a887c98ca1e2f9dbb61575faedf0395f2f7cc`
- byte count: `1842`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/add-assignees`
- parent source ID: `openapi-current-2026-03-10:issues/add-assignees`
- parent document ID: `openapi-current-issues-add-assignees`
- parent normalized SHA256: `0943e9429010eee5ce1db5380130c5bb9bba4aa94ed2a8d10363c35a0930e6bb`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Adds up to 10 assignees to an issue. Users already assigned to an issue are not replaced.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/assignees#add-assignees-to-an-issue"},"operationId":"issues/add-assignees","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["hubot","other_user"]}}},"schema":{"properties":{"assignees":{"description":"Usernames of people to assign this issue to. _NOTE: Only users with push access can add assignees to an issue. Assignees are silently ignored otherwise._","items":{"oneOf":[{"type":"string"},{"properties":{"confidence":{"description":"The confidence level for this assignee choice.","enum":["low","medium","high"],"type":"string"},"login":{"description":"The login of the user to assign.","type":"string"},"rationale":{"description":"Optional reasoning for adding this assignee.","type":"string"},"suggest":{"description":"If `true`, the assignee is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"}},"required":["login"],"type":"object"}]},"type":"array"}},"type":"object"}}},"required":false},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response"}},"summary":"Add assignees to an issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"assignees"}},"path":"/repos/{owner}/{repo}/issues/{issue_number}/assignees","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-4ef0bdd3ba1424f602eb63cd7cda604ca17a79a151816fddca4e7aa117ee58ff`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-4ef0bdd3ba1424f602eb63cd7cda604ca17a79a151816fddca4e7aa117ee58ff.json`
- content SHA256: `db19be209b80c9a0b73361ec3f0a887c98ca1e2f9dbb61575faedf0395f2f7cc`
- byte count: `1842`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/add-assignees`
- parent source ID: `openapi-historical-2022-11-28:issues/add-assignees`
- parent document ID: `openapi-historical-issues-add-assignees`
- parent normalized SHA256: `6c96357435b85230b77f1042598f5650f29917d8fe1d5ff4b6cacff0d3e00780`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Adds up to 10 assignees to an issue. Users already assigned to an issue are not replaced.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/assignees#add-assignees-to-an-issue"},"operationId":"issues/add-assignees","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["hubot","other_user"]}}},"schema":{"properties":{"assignees":{"description":"Usernames of people to assign this issue to. _NOTE: Only users with push access can add assignees to an issue. Assignees are silently ignored otherwise._","items":{"oneOf":[{"type":"string"},{"properties":{"confidence":{"description":"The confidence level for this assignee choice.","enum":["low","medium","high"],"type":"string"},"login":{"description":"The login of the user to assign.","type":"string"},"rationale":{"description":"Optional reasoning for adding this assignee.","type":"string"},"suggest":{"description":"If `true`, the assignee is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"}},"required":["login"],"type":"object"}]},"type":"array"}},"type":"object"}}},"required":false},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response"}},"summary":"Add assignees to an issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"assignees"}},"path":"/repos/{owner}/{repo}/issues/{issue_number}/assignees","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:issues/add-blocked-by-dependency`

- evaluation role: `held_out_release_case`
- cluster kind: `openapi_version_pair`
- source family: `issues`
- operation ID: `issues/add-blocked-by-dependency`

### Current evidence: `chunk-54218cead5dc4d96ffc452ff1dbd07d9b0f4dab0236c0d3ab315168d9f0d4124`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-54218cead5dc4d96ffc452ff1dbd07d9b0f4dab0236c0d3ab315168d9f0d4124.json`
- content SHA256: `3dcdca5ff84c8d4928de432a456176606d075aaf301fe1247bb52cb69bcc4898`
- byte count: `2842`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/add-blocked-by-dependency`
- parent source ID: `openapi-current-2026-03-10:issues/add-blocked-by-dependency`
- parent document ID: `openapi-current-issues-add-blocked-by-dependency`
- parent normalized SHA256: `b202376c4962c24f3f1ee9250c20729b0e9fdf10e54aaa5cd1556239e632633c`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add a 'blocked by' relationship to an issue.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see [Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\nand [Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\n\nThis endpoint supports the following custom media types. For more information, see [Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\n\n- **`application/vnd.github.raw+json`**: Returns the raw Markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the Markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's Markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issue-dependencies#add-a-dependency-an-issue-is-blocked-by"},"operationId":"issues/add-blocked-by-dependency","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"issue_id":1}}},"schema":{"properties":{"issue_id":{"description":"The id of the issue that blocks the current issue","type":"integer"}},"required":["issue_id"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/issues/1/dependencies/blocked_by","schema":{"type":"string"}}}},"301":{"$ref":"#/components/responses/moved_permanently"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Add a dependency an issue is blocked by","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"issue-dependencies","triggersNotification":true}},"path":"/repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-4b5aeb1527d8e5bf06d0b49a1ffe5ddb97b1f8c467cf4e2db9f2a9e1f4b89f00`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-4b5aeb1527d8e5bf06d0b49a1ffe5ddb97b1f8c467cf4e2db9f2a9e1f4b89f00.json`
- content SHA256: `3dcdca5ff84c8d4928de432a456176606d075aaf301fe1247bb52cb69bcc4898`
- byte count: `2842`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/add-blocked-by-dependency`
- parent source ID: `openapi-historical-2022-11-28:issues/add-blocked-by-dependency`
- parent document ID: `openapi-historical-issues-add-blocked-by-dependency`
- parent normalized SHA256: `fec6b67cf99fdb099e2c55721bcb571728a7bdfa13d4bf533fda3f13ae653dd6`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add a 'blocked by' relationship to an issue.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see [Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\nand [Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\n\nThis endpoint supports the following custom media types. For more information, see [Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\n\n- **`application/vnd.github.raw+json`**: Returns the raw Markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the Markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's Markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issue-dependencies#add-a-dependency-an-issue-is-blocked-by"},"operationId":"issues/add-blocked-by-dependency","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"issue_id":1}}},"schema":{"properties":{"issue_id":{"description":"The id of the issue that blocks the current issue","type":"integer"}},"required":["issue_id"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/issues/1/dependencies/blocked_by","schema":{"type":"string"}}}},"301":{"$ref":"#/components/responses/moved_permanently"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Add a dependency an issue is blocked by","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"issue-dependencies","triggersNotification":true}},"path":"/repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:issues/add-sub-issue`

- evaluation role: `intervention_tuning_case`
- cluster kind: `openapi_version_pair`
- source family: `issues`
- operation ID: `issues/add-sub-issue`

### Current evidence: `chunk-dce9a384052fb0b5e660fcf172f8457b8e00d415535f2f845a4cda06dbca9afb`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-dce9a384052fb0b5e660fcf172f8457b8e00d415535f2f845a4cda06dbca9afb.json`
- content SHA256: `3cc3ce2669fd1b848c23ca1ad7fc2cbb659a0f3c5f88295e49710191e5484ede`
- byte count: `2859`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/add-sub-issue`
- parent source ID: `openapi-current-2026-03-10:issues/add-sub-issue`
- parent document ID: `openapi-current-issues-add-sub-issue`
- parent normalized SHA256: `18821d47dc9c31acaa65d22c23df135371182aa15acef98ca28508cb9a93e140`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add sub-issues to issues.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/sub-issues#add-sub-issue"},"operationId":"issues/add-sub-issue","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"sub_issue_id":1}}},"schema":{"properties":{"replace_parent":{"description":"Option that, when true, instructs the operation to replace the sub-issues current parent issue","type":"boolean"},"sub_issue_id":{"description":"The id of the sub-issue to add. The sub-issue must belong to the same repository owner as the parent issue","type":"integer"}},"required":["sub_issue_id"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/issues/sub-issues/1","schema":{"type":"string"}}}},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Add sub-issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"sub-issues"}},"path":"/repos/{owner}/{repo}/issues/{issue_number}/sub_issues","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-b89980229e1c8d141c4d35d0701e5158e706010316939034baa54354b28e701e`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-b89980229e1c8d141c4d35d0701e5158e706010316939034baa54354b28e701e.json`
- content SHA256: `3cc3ce2669fd1b848c23ca1ad7fc2cbb659a0f3c5f88295e49710191e5484ede`
- byte count: `2859`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/add-sub-issue`
- parent source ID: `openapi-historical-2022-11-28:issues/add-sub-issue`
- parent document ID: `openapi-historical-issues-add-sub-issue`
- parent normalized SHA256: `9800f5b9bb2fb665d592c7ffe0457e9eb99b472b73e84c5fe2150d5cf00db9c9`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"You can use the REST API to add sub-issues to issues.\n\nCreating content too quickly using this endpoint may result in secondary rate limiting.\nFor more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/sub-issues#add-sub-issue"},"operationId":"issues/add-sub-issue","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"sub_issue_id":1}}},"schema":{"properties":{"replace_parent":{"description":"Option that, when true, instructs the operation to replace the sub-issues current parent issue","type":"boolean"},"sub_issue_id":{"description":"The id of the sub-issue to add. The sub-issue must belong to the same repository owner as the parent issue","type":"integer"}},"required":["sub_issue_id"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/issues/sub-issues/1","schema":{"type":"string"}}}},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Add sub-issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"sub-issues"}},"path":"/repos/{owner}/{repo}/issues/{issue_number}/sub_issues","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:issues/create`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `issues`
- operation ID: `issues/create`

### Current evidence: `chunk-818a2d7af95a38d5ffd8d96869fbd8198cb399d3e2e8c55900c85770cf07a1d9`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-818a2d7af95a38d5ffd8d96869fbd8198cb399d3e2e8c55900c85770cf07a1d9.json`
- content SHA256: `6b1fb56ba531275ff4c015652c1392fd6a2747175ed68c16105c656ac7a81937`
- byte count: `5214`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/create`
- parent source ID: `openapi-current-2026-03-10:issues/create`
- parent document ID: `openapi-current-issues-create`
- parent normalized SHA256: `932b59448ebb5c15f7a0a83d407228e48333ea1100d75cb0afc1c7d727c33951`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#create-an-issue"},"operationId":"issues/create","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["octocat"],"body":"I'm having a problem with this.","labels":["bug"],"milestone":1,"title":"Found a bug"}}},"schema":{"properties":{"assignees":{"description":"Logins for Users to assign to this issue. _NOTE: Only users with push access can set assignees for new issues. Assignees are silently dropped otherwise._","items":{"type":"string"},"type":"array"},"body":{"description":"The contents of the issue.","type":"string"},"issue_field_values":{"description":"An array of issue field values to set on this issue. Each field value must include the field ID and the value to set. Issue fields are only available for organization-owned repositories with the feature enabled. Field values are silently dropped otherwise.","items":{"additionalProperties":false,"properties":{"field_id":{"description":"The ID of the issue field to set","type":"integer"},"value":{"description":"The value to set for the field. For multi-select fields, provide an array of option names.","oneOf":[{"type":"string"},{"type":"number"},{"items":{"type":"string"},"type":"array"}]}},"required":["field_id","value"],"type":"object"},"type":"array"},"labels":{"description":"Labels to associate with this issue. _NOTE: Only users with push access can set labels for new issues. Labels are silently dropped otherwise._","items":{"oneOf":[{"type":"string"},{"properties":{"color":{"nullable":true,"type":"string"},"description":{"nullable":true,"type":"string"},"id":{"type":"integer"},"name":{"type":"string"}},"type":"object"}]},"type":"array"},"milestone":{"nullable":true,"oneOf":[{"type":"string"},{"description":"The `number` of the milestone to associate this issue with. _NOTE: Only users with push access can set the milestone for new issues. The milestone is silently dropped otherwise._","type":"integer"}]},"parent_issue_id":{"description":"The id of the parent issue to add this issue to as a sub-issue. _NOTE: Only users with triage access to both the parent issue's repository and this repository can set the parent issue._","type":"integer"},"title":{"description":"The title of the issue.","oneOf":[{"type":"string"},{"type":"integer"}]},"type":{"description":"The name of the issue type to associate with this issue. _NOTE: Only users with push access can set the type for new issues. The type is silently dropped otherwise._","example":"Epic","nullable":true,"type":"string"}},"required":["title"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/issues/1347","schema":{"type":"string"}}}},"400":{"$ref":"#/components/responses/bad_request"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"},"503":{"$ref":"#/components/responses/service_unavailable"}},"summary":"Create an issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"issues","triggersNotification":true}},"path":"/repos/{owner}/{repo}/issues","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-a6f2c249acaf3aadd70ac7964297edb46071d6ab5d2fed98384b39ba0e34862f`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-a6f2c249acaf3aadd70ac7964297edb46071d6ab5d2fed98384b39ba0e34862f.json`
- content SHA256: `e63b1c4ad74de58397daf638d798e71ab8e286207a028290ef2c5460ea399991`
- byte count: `5482`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/create`
- parent source ID: `openapi-historical-2022-11-28:issues/create`
- parent document ID: `openapi-historical-issues-create`
- parent normalized SHA256: `58a66638c41ce39fdf1a3f9d0753ecf0158764f0cd10d21508d227116a2aa7dd`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\"\nand \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#create-an-issue"},"operationId":"issues/create","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["octocat"],"body":"I'm having a problem with this.","labels":["bug"],"milestone":1,"title":"Found a bug"}}},"schema":{"properties":{"assignee":{"description":"Login for the user that this issue should be assigned to. _NOTE: Only users with push access can set the assignee for new issues. The assignee is silently dropped otherwise. **This field is closing down.**_","nullable":true,"type":"string"},"assignees":{"description":"Logins for Users to assign to this issue. _NOTE: Only users with push access can set assignees for new issues. Assignees are silently dropped otherwise._","items":{"type":"string"},"type":"array"},"body":{"description":"The contents of the issue.","type":"string"},"issue_field_values":{"description":"An array of issue field values to set on this issue. Each field value must include the field ID and the value to set. Issue fields are only available for organization-owned repositories with the feature enabled. Field values are silently dropped otherwise.","items":{"additionalProperties":false,"properties":{"field_id":{"description":"The ID of the issue field to set","type":"integer"},"value":{"description":"The value to set for the field. For multi-select fields, provide an array of option names.","oneOf":[{"type":"string"},{"type":"number"},{"items":{"type":"string"},"type":"array"}]}},"required":["field_id","value"],"type":"object"},"type":"array"},"labels":{"description":"Labels to associate with this issue. _NOTE: Only users with push access can set labels for new issues. Labels are silently dropped otherwise._","items":{"oneOf":[{"type":"string"},{"properties":{"color":{"nullable":true,"type":"string"},"description":{"nullable":true,"type":"string"},"id":{"type":"integer"},"name":{"type":"string"}},"type":"object"}]},"type":"array"},"milestone":{"nullable":true,"oneOf":[{"type":"string"},{"description":"The `number` of the milestone to associate this issue with. _NOTE: Only users with push access can set the milestone for new issues. The milestone is silently dropped otherwise._","type":"integer"}]},"parent_issue_id":{"description":"The id of the parent issue to add this issue to as a sub-issue. _NOTE: Only users with triage access to both the parent issue's repository and this repository can set the parent issue._","type":"integer"},"title":{"description":"The title of the issue.","oneOf":[{"type":"string"},{"type":"integer"}]},"type":{"description":"The name of the issue type to associate with this issue. _NOTE: Only users with push access can set the type for new issues. The type is silently dropped otherwise._","example":"Epic","nullable":true,"type":"string"}},"required":["title"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"$ref":"#/components/schemas/issue"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/issues/1347","schema":{"type":"string"}}}},"400":{"$ref":"#/components/responses/bad_request"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"},"503":{"$ref":"#/components/responses/service_unavailable"}},"summary":"Create an issue","tags":["issues"],"x-github":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"issues","triggersNotification":true}},"path":"/repos/{owner}/{repo}/issues","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:issues/update`

- evaluation role: `held_out_release_case`
- cluster kind: `openapi_version_pair`
- source family: `issues`
- operation ID: `issues/update`

### Current evidence: `chunk-2a1b7e2dd72157f835c63422ef3416992ea7a3c25b55460ada39cd66ca0d6f3f`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-2a1b7e2dd72157f835c63422ef3416992ea7a3c25b55460ada39cd66ca0d6f3f.json`
- content SHA256: `e3a690a17206eb8c46e286d5926e793588039b44fbf20f5de2574b283b7f01a8`
- byte count: `3183`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/update`
- parent source ID: `openapi-current-2026-03-10:issues/update`
- parent document ID: `openapi-current-issues-update`
- parent normalized SHA256: `cb235811e7a9fe417ad0d72b9ffc7041de502c4f891000ce2a02083a11346be5`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":["operation","responses"],"value":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"allOf":[{"$ref":"#/components/schemas/issue"},{"properties":{"suggestions":{"description":"Pending suggestions for each suggestible field (`type`,\n`issue_field_values`, `labels`, `assignees`, `state`) the\nrequest touched. Omitted for fields not in the request or\nwith no pending or ignored suggestions. Items tagged\n`ignored` are echoes of the current request's inputs that\nwere not persisted as pending suggestions.\n","properties":{"assignees":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"login":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"issue_field_values":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"field_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"},"value":{"oneOf":[{"type":"string"},{"type":"number"},{"items":{"type":"string"},"type":"array"}]}},"type":"object"},"type":"array"},"labels":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"name":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"state":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"duplicate_issue_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale":{"type":"string"},"state_reason":{"type":"string"},"suggest":{"type":"boolean"},"value":{"type":"string"}},"type":"object"},"type":"array"},"type":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"},"value":{"type":"string"}},"type":"object"},"type":"array"}},"type":"object"}},"type":"object"}]}}},"description":"Response"},"301":{"$ref":"#/components/responses/moved_permanently"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"},"503":{"$ref":"#/components/responses/service_unavailable"}}},{"path":["operation","summary"],"value":"Update an issue"},{"path":["operation","tags"],"value":["issues"]},{"path":["operation","x-github"],"value":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"issues"}},{"path":["path"],"value":"/repos/{owner}/{repo}/issues/{issue_number}"},{"path":["path_parameters"],"value":[]}]}
</pre>

</details>

### Current evidence: `chunk-cd375411d841104feb9b2825d17e637b92b9d817f6f22d1c52d0fbce134f328d`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-cd375411d841104feb9b2825d17e637b92b9d817f6f22d1c52d0fbce134f328d.json`
- content SHA256: `21540e252532b3c011d3bd3b1900583d143da379fc88091e0db38a2f6c46e121`
- byte count: `6428`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/update`
- parent source ID: `openapi-current-2026-03-10:issues/update`
- parent document ID: `openapi-current-issues-update`
- parent normalized SHA256: `cb235811e7a9fe417ad0d72b9ffc7041de502c4f891000ce2a02083a11346be5`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":["method"],"value":"patch"},{"path":["operation","description"],"value":"Issue owners and users with push access or Triage role can edit an issue.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`."},{"path":["operation","externalDocs"],"value":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#update-an-issue"}},{"path":["operation","operationId"],"value":"issues/update"},{"path":["operation","parameters"],"value":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}]},{"path":["operation","requestBody"],"value":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["octocat"],"body":"I'm having a problem with this.","labels":["bug"],"milestone":1,"state":"open","title":"Found a bug"}}},"schema":{"properties":{"assignees":{"description":"Usernames to assign to this issue. Pass one or more user logins to _replace_ the set of assignees on this issue. Send an empty array (`[]`) to clear all assignees from the issue. Only users with push access can set assignees for new issues. Without push access to the repository, assignee changes are silently dropped.","items":{"oneOf":[{"type":"string"},{"properties":{"confidence":{"description":"The confidence level for this assignee choice.","enum":["low","medium","high"],"type":"string"},"login":{"type":"string"},"rationale":{"description":"Optional reasoning for selecting this assignee.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"}},"type":"object"}]},"type":"array"},"body":{"description":"The contents of the issue.","nullable":true,"type":"string"},"duplicate_issue_id":{"description":"The ID of the issue to mark as the canonical duplicate when `state_reason` is `duplicate`. The issue must exist and be accessible to the authenticated user. Ignored when `state_reason` is not `duplicate`.","type":"integer"},"issue_field_values":{"description":"An array of issue field values to set on this issue. Each field value must include the field ID and the value to set. Only users with push access can set field values for issues","items":{"additionalProperties":false,"properties":{"confidence":{"description":"The confidence level for this field value choice.","enum":["low","medium","high"],"type":"string"},"field_id":{"description":"The ID of the issue field to set","type":"integer"},"rationale":{"description":"Optional reasoning for setting this field value.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"},"value":{"description":"The value to set for the field. For multi-select fields, provide an array of option names.","oneOf":[{"type":"string"},{"type":"number"},{"items":{"type":"string"},"type":"array"}]}},"required":["field_id","value"],"type":"object"},"type":"array"},"labels":{"description":"Labels to associate with this issue. Pass one or more labels to _replace_ the set of labels on this issue. Send an empty array (`[]`) to clear all labels from the issue. Only users with push access can set labels for issues. Without push access to the repository, label changes are silently dropped.","items":{"oneOf":[{"type":"string"},{"properties":{"color":{"nullable":true,"type":"string"},"confidence":{"description":"The confidence level for this label choice.","enum":["low","medium","high"],"type":"string"},"description":{"nullable":true,"type":"string"},"id":{"type":"integer"},"name":{"type":"string"},"rationale":{"description":"Optional reasoning for selecting this label.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"}},"type":"object"}]},"type":"array"},"milestone":{"nullable":true,"oneOf":[{"type":"string"},{"description":"The `number` of the milestone to associate this issue with or use `null` to remove the current milestone. Only users with push access can set the milestone for issues. Without push access to the repository, milestone changes are silently dropped.","type":"integer"}]},"state":{"description":"The open or closed state of the issue.","enum":["open","closed"],"type":"string"},"state_reason":{"description":"The reason for the state change. Ignored unless `state` is changed.","enum":["completed","not_planned","duplicate","reopened"],"example":"not_planned","nullable":true,"type":"string"},"title":{"description":"The title of the issue.","nullable":true,"oneOf":[{"type":"string"},{"type":"integer"}]},"type":{"description":"The issue type to associate with this issue. Only users with push access can set the type for issues. Without push access to the repository, type changes are silently dropped.","nullable":true,"oneOf":[{"description":"The name of the issue type.","example":"Epic","type":"string"},{"description":"The issue type with optional metadata.","properties":{"confidence":{"description":"The confidence level for this type choice.","enum":["low","medium","high"],"type":"string"},"rationale":{"description":"Optional reasoning for selecting this type.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"},"value":{"description":"The name of the issue type to associate with this issue, or `null` to remove the current issue type.","example":"Epic","nullable":true,"type":"string"}},"type":"object"}]}},"type":"object"}}},"required":false}}]}
</pre>

</details>

### Historical evidence: `chunk-a1a6a71a7bf60ff978907f1339ae3ce7cc900759a29c6114fdff63e37a492421`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-a1a6a71a7bf60ff978907f1339ae3ce7cc900759a29c6114fdff63e37a492421.json`
- content SHA256: `e3a690a17206eb8c46e286d5926e793588039b44fbf20f5de2574b283b7f01a8`
- byte count: `3183`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/update`
- parent source ID: `openapi-historical-2022-11-28:issues/update`
- parent document ID: `openapi-historical-issues-update`
- parent normalized SHA256: `51218db5e0c8bf50db736cced0c044bd5412137aa5629b3aaf26c7877a0c7416`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":["operation","responses"],"value":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/issue"}},"schema":{"allOf":[{"$ref":"#/components/schemas/issue"},{"properties":{"suggestions":{"description":"Pending suggestions for each suggestible field (`type`,\n`issue_field_values`, `labels`, `assignees`, `state`) the\nrequest touched. Omitted for fields not in the request or\nwith no pending or ignored suggestions. Items tagged\n`ignored` are echoes of the current request's inputs that\nwere not persisted as pending suggestions.\n","properties":{"assignees":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"login":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"issue_field_values":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"field_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"},"value":{"oneOf":[{"type":"string"},{"type":"number"},{"items":{"type":"string"},"type":"array"}]}},"type":"object"},"type":"array"},"labels":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"name":{"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"}},"type":"object"},"type":"array"},"state":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"duplicate_issue_id":{"type":"integer"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale":{"type":"string"},"state_reason":{"type":"string"},"suggest":{"type":"boolean"},"value":{"type":"string"}},"type":"object"},"type":"array"},"type":{"items":{"properties":{"confidence":{"enum":["low","medium","high"],"type":"string"},"ignored":{"type":"boolean"},"ignored_reason":{"enum":["already_applied","issue_already_closed"],"type":"string"},"rationale":{"type":"string"},"suggest":{"type":"boolean"},"value":{"type":"string"}},"type":"object"},"type":"array"}},"type":"object"}},"type":"object"}]}}},"description":"Response"},"301":{"$ref":"#/components/responses/moved_permanently"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"410":{"$ref":"#/components/responses/gone"},"422":{"$ref":"#/components/responses/validation_failed"},"503":{"$ref":"#/components/responses/service_unavailable"}}},{"path":["operation","summary"],"value":"Update an issue"},{"path":["operation","tags"],"value":["issues"]},{"path":["operation","x-github"],"value":{"category":"issues","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"issues"}},{"path":["path"],"value":"/repos/{owner}/{repo}/issues/{issue_number}"},{"path":["path_parameters"],"value":[]}]}
</pre>

</details>

### Historical evidence: `chunk-db4f7149fb4f7e84d0de4a79830ed8a35e793d967bbf7c60f5d4f35fad88f118`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-db4f7149fb4f7e84d0de4a79830ed8a35e793d967bbf7c60f5d4f35fad88f118.json`
- content SHA256: `95cd3d042612fcf8bf704dfebfda20386bf0f9c7a02049856b66d3e0266e999c`
- byte count: `6555`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `issues`
- linked operations: `issues/update`
- parent source ID: `openapi-historical-2022-11-28:issues/update`
- parent document ID: `openapi-historical-issues-update`
- parent normalized SHA256: `51218db5e0c8bf50db736cced0c044bd5412137aa5629b3aaf26c7877a0c7416`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":["method"],"value":"patch"},{"path":["operation","description"],"value":"Issue owners and users with push access or Triage role can edit an issue.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`."},{"path":["operation","externalDocs"],"value":{"description":"API method documentation","url":"https://docs.github.com/rest/issues/issues#update-an-issue"}},{"path":["operation","operationId"],"value":"issues/update"},{"path":["operation","parameters"],"value":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/issue-number"}]},{"path":["operation","requestBody"],"value":{"content":{"application/json":{"examples":{"default":{"value":{"assignees":["octocat"],"body":"I'm having a problem with this.","labels":["bug"],"milestone":1,"state":"open","title":"Found a bug"}}},"schema":{"properties":{"assignee":{"description":"Username to assign to this issue. **This field is closing down.**","nullable":true,"type":"string"},"assignees":{"description":"Usernames to assign to this issue. Pass one or more user logins to _replace_ the set of assignees on this issue. Send an empty array (`[]`) to clear all assignees from the issue. Only users with push access can set assignees for new issues. Without push access to the repository, assignee changes are silently dropped.","items":{"oneOf":[{"type":"string"},{"properties":{"confidence":{"description":"The confidence level for this assignee choice.","enum":["low","medium","high"],"type":"string"},"login":{"type":"string"},"rationale":{"description":"Optional reasoning for selecting this assignee.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"}},"type":"object"}]},"type":"array"},"body":{"description":"The contents of the issue.","nullable":true,"type":"string"},"duplicate_issue_id":{"description":"The ID of the issue to mark as the canonical duplicate when `state_reason` is `duplicate`. The issue must exist and be accessible to the authenticated user. Ignored when `state_reason` is not `duplicate`.","type":"integer"},"issue_field_values":{"description":"An array of issue field values to set on this issue. Each field value must include the field ID and the value to set. Only users with push access can set field values for issues","items":{"additionalProperties":false,"properties":{"confidence":{"description":"The confidence level for this field value choice.","enum":["low","medium","high"],"type":"string"},"field_id":{"description":"The ID of the issue field to set","type":"integer"},"rationale":{"description":"Optional reasoning for setting this field value.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"},"value":{"description":"The value to set for the field. For multi-select fields, provide an array of option names.","oneOf":[{"type":"string"},{"type":"number"},{"items":{"type":"string"},"type":"array"}]}},"required":["field_id","value"],"type":"object"},"type":"array"},"labels":{"description":"Labels to associate with this issue. Pass one or more labels to _replace_ the set of labels on this issue. Send an empty array (`[]`) to clear all labels from the issue. Only users with push access can set labels for issues. Without push access to the repository, label changes are silently dropped.","items":{"oneOf":[{"type":"string"},{"properties":{"color":{"nullable":true,"type":"string"},"confidence":{"description":"The confidence level for this label choice.","enum":["low","medium","high"],"type":"string"},"description":{"nullable":true,"type":"string"},"id":{"type":"integer"},"name":{"type":"string"},"rationale":{"description":"Optional reasoning for selecting this label.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"}},"type":"object"}]},"type":"array"},"milestone":{"nullable":true,"oneOf":[{"type":"string"},{"description":"The `number` of the milestone to associate this issue with or use `null` to remove the current milestone. Only users with push access can set the milestone for issues. Without push access to the repository, milestone changes are silently dropped.","type":"integer"}]},"state":{"description":"The open or closed state of the issue.","enum":["open","closed"],"type":"string"},"state_reason":{"description":"The reason for the state change. Ignored unless `state` is changed.","enum":["completed","not_planned","duplicate","reopened"],"example":"not_planned","nullable":true,"type":"string"},"title":{"description":"The title of the issue.","nullable":true,"oneOf":[{"type":"string"},{"type":"integer"}]},"type":{"description":"The issue type to associate with this issue. Only users with push access can set the type for issues. Without push access to the repository, type changes are silently dropped.","nullable":true,"oneOf":[{"description":"The name of the issue type.","example":"Epic","type":"string"},{"description":"The issue type with optional metadata.","properties":{"confidence":{"description":"The confidence level for this type choice.","enum":["low","medium","high"],"type":"string"},"rationale":{"description":"Optional reasoning for selecting this type.","type":"string"},"suggest":{"description":"If `true`, the change is stored as a pending suggestion for human review rather than applied directly.","type":"boolean"},"value":{"description":"The name of the issue type to associate with this issue, or `null` to remove the current issue type.","example":"Epic","nullable":true,"type":"string"}},"type":"object"}]}},"type":"object"}}},"required":false}}]}
</pre>

</details>

## Cluster: `openapi-pair:pulls/create`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `pull_requests`
- operation ID: `pulls/create`

### Current evidence: `chunk-e8fc96fbaa45f2c119f5c6ebb463aa1f2185ef34a62d159f349d65c167f4caca`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-e8fc96fbaa45f2c119f5c6ebb463aa1f2185ef34a62d159f349d65c167f4caca.json`
- content SHA256: `f72b074fe1ac60e522fde065d1d246287309664c0c37b15cbd26a3c0f89eeeb2`
- byte count: `4953`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/create`
- parent source ID: `openapi-current-2026-03-10:pulls/create`
- parent document ID: `openapi-current-pulls-create`
- parent normalized SHA256: `5e1ed31f0b69d6b685f9aa4e8ab57ef1bc459ecf4e21522bf9abd2cd7498a602`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\" and \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#create-a-pull-request"},"operationId":"pulls/create","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"base":"master","body":"Please pull these awesome changes in!","head":"octocat:new-feature","title":"Amazing new feature"}}},"schema":{"properties":{"base":{"description":"The name of the branch you want the changes pulled into. This should be an existing branch on the current repository. You cannot submit a pull request to one repository that requests a merge to a base of another repository.","type":"string"},"body":{"description":"The contents of the pull request.","type":"string"},"draft":{"description":"Indicates whether the pull request is a draft. See \"[Draft Pull Requests](https://docs.github.com/articles/about-pull-requests#draft-pull-requests)\" in the GitHub Help documentation to learn more.","type":"boolean"},"head":{"description":"The name of the branch where your changes are implemented. For cross-repository pull requests in the same network, namespace `head` with a user like this: `username:branch`.","type":"string"},"head_repo":{"description":"The name of the repository where the changes in the pull request were made. This field is required for cross-repository pull requests if both repositories are owned by the same organization.","example":"octo-org/octo-repo","format":"repo.nwo","type":"string"},"issue":{"description":"An issue in the repository to convert to a pull request. The issue title, body, and comments will become the title, body, and comments on the new pull request. Required unless `title` is specified.","example":1,"format":"int64","type":"integer"},"maintainer_can_modify":{"description":"Indicates whether [maintainers can modify](https://docs.github.com/articles/allowing-changes-to-a-pull-request-branch-created-from-a-fork/) the pull request.","type":"boolean"},"title":{"description":"The title of the new pull request. Required unless `issue` is specified.","type":"string"}},"required":["head","base"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request"}},"schema":{"$ref":"#/components/schemas/pull-request"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/pulls/1347","schema":{"type":"string"}}}},"403":{"$ref":"#/components/responses/forbidden"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Create a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls","triggersNotification":true}},"path":"/repos/{owner}/{repo}/pulls","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-42d7b7bbff67f5e75d5363b820cd6182d79785cad570a499b58e253942474944`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-42d7b7bbff67f5e75d5363b820cd6182d79785cad570a499b58e253942474944.json`
- content SHA256: `f72b074fe1ac60e522fde065d1d246287309664c0c37b15cbd26a3c0f89eeeb2`
- byte count: `4953`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/create`
- parent source ID: `openapi-historical-2022-11-28:pulls/create`
- parent document ID: `openapi-historical-pulls-create`
- parent normalized SHA256: `c34dcf357f0fa36c3ace11aa993384389df192b4cf1b39198e56da70fb86c17c`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see \"[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)\" and \"[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api).\"\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#create-a-pull-request"},"operationId":"pulls/create","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"base":"master","body":"Please pull these awesome changes in!","head":"octocat:new-feature","title":"Amazing new feature"}}},"schema":{"properties":{"base":{"description":"The name of the branch you want the changes pulled into. This should be an existing branch on the current repository. You cannot submit a pull request to one repository that requests a merge to a base of another repository.","type":"string"},"body":{"description":"The contents of the pull request.","type":"string"},"draft":{"description":"Indicates whether the pull request is a draft. See \"[Draft Pull Requests](https://docs.github.com/articles/about-pull-requests#draft-pull-requests)\" in the GitHub Help documentation to learn more.","type":"boolean"},"head":{"description":"The name of the branch where your changes are implemented. For cross-repository pull requests in the same network, namespace `head` with a user like this: `username:branch`.","type":"string"},"head_repo":{"description":"The name of the repository where the changes in the pull request were made. This field is required for cross-repository pull requests if both repositories are owned by the same organization.","example":"octo-org/octo-repo","format":"repo.nwo","type":"string"},"issue":{"description":"An issue in the repository to convert to a pull request. The issue title, body, and comments will become the title, body, and comments on the new pull request. Required unless `title` is specified.","example":1,"format":"int64","type":"integer"},"maintainer_can_modify":{"description":"Indicates whether [maintainers can modify](https://docs.github.com/articles/allowing-changes-to-a-pull-request-branch-created-from-a-fork/) the pull request.","type":"boolean"},"title":{"description":"The title of the new pull request. Required unless `issue` is specified.","type":"string"}},"required":["head","base"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request"}},"schema":{"$ref":"#/components/schemas/pull-request"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World/pulls/1347","schema":{"type":"string"}}}},"403":{"$ref":"#/components/responses/forbidden"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Create a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls","triggersNotification":true}},"path":"/repos/{owner}/{repo}/pulls","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:pulls/get`

- evaluation role: `intervention_tuning_case`
- cluster kind: `openapi_version_pair`
- source family: `pull_requests`
- operation ID: `pulls/get`

### Current evidence: `chunk-f195cc3e0ba24c3ae8273d49e92e001fac39dcfd9fa3a7eafad7a7f95ff85781`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-f195cc3e0ba24c3ae8273d49e92e001fac39dcfd9fa3a7eafad7a7f95ff85781.json`
- content SHA256: `a6f2fe0014e765551fc8255891b5a5886e0161b8b61169411eef1e3c6d452d97`
- byte count: `4883`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/get`
- parent source ID: `openapi-current-2026-03-10:pulls/get`
- parent document ID: `openapi-current-pulls-get`
- parent normalized SHA256: `c8937fe736c0d6840b15542bc99720047cc7c9192ce1522762892e8e90b21182`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nLists details of a pull request by providing its number.\n\nWhen you get, [create](https://docs.github.com/rest/pulls/pulls/#create-a-pull-request), or [edit](https://docs.github.com/rest/pulls/pulls#update-a-pull-request) a pull request, GitHub creates a merge commit to test whether the pull request can be automatically merged into the base branch. This test commit is not added to the base branch or the head branch. You can review the status of the test commit using the `mergeable` key. For more information, see \"[Checking mergeability of pull requests](https://docs.github.com/rest/guides/getting-started-with-the-git-database-api#checking-mergeability-of-pull-requests)\".\n\nThe value of the `mergeable` attribute can be `true`, `false`, or `null`. If the value is `null`, then GitHub has started a background job to compute the mergeability. After giving the job time to complete, resubmit the request. When the job finishes, you will see a non-`null` value for the `mergeable` attribute in the response. If `mergeable` is `true`, then `merge_commit_sha` will be the SHA of the _test_ merge commit.\n\nThe value of the `merge_commit_sha` attribute changes depending on the state of the pull request. Before merging a pull request, the `merge_commit_sha` attribute holds the SHA of the _test_ merge commit. After merging a pull request, the `merge_commit_sha` attribute changes depending on how you merged the pull request:\n\n*   If merged as a [merge commit](https://docs.github.com/articles/about-merge-methods-on-github/), `merge_commit_sha` represents the SHA of the merge commit.\n*   If merged via a [squash](https://docs.github.com/articles/about-merge-methods-on-github/#squashing-your-merge-commits), `merge_commit_sha` represents the SHA of the squashed commit on the base branch.\n*   If [rebased](https://docs.github.com/articles/about-merge-methods-on-github/#rebasing-and-merging-your-commits), `merge_commit_sha` represents the commit that the base branch was updated to.\n\nPass the appropriate [media type](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types) to fetch diff and patch formats.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.\n- **`application/vnd.github.diff`**: For more information, see \"[git-diff](https://git-scm.com/docs/git-diff)\" in the Git documentation. If a diff is corrupt, contact us through the [GitHub Support portal](https://support.github.com/). Include the repository name and pull request ID in your message.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#get-a-pull-request"},"operationId":"pulls/get","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request"}},"schema":{"$ref":"#/components/schemas/pull-request"}}},"description":"Pass the appropriate [media type](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types) to fetch diff and patch formats."},"304":{"$ref":"#/components/responses/not_modified"},"404":{"$ref":"#/components/responses/not_found"},"406":{"$ref":"#/components/responses/unacceptable"},"500":{"$ref":"#/components/responses/internal_error"},"503":{"$ref":"#/components/responses/service_unavailable"}},"summary":"Get a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls"}},"path":"/repos/{owner}/{repo}/pulls/{pull_number}","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-ded348a713590dacd422877d3fd903bf33666202b0b1128840cad1d1971792cd`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-ded348a713590dacd422877d3fd903bf33666202b0b1128840cad1d1971792cd.json`
- content SHA256: `a6f2fe0014e765551fc8255891b5a5886e0161b8b61169411eef1e3c6d452d97`
- byte count: `4883`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/get`
- parent source ID: `openapi-historical-2022-11-28:pulls/get`
- parent document ID: `openapi-historical-pulls-get`
- parent normalized SHA256: `e582f2d00143682260e685aebb7bc4f89d21c07bdc8c272e01930c90a5d36277`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nLists details of a pull request by providing its number.\n\nWhen you get, [create](https://docs.github.com/rest/pulls/pulls/#create-a-pull-request), or [edit](https://docs.github.com/rest/pulls/pulls#update-a-pull-request) a pull request, GitHub creates a merge commit to test whether the pull request can be automatically merged into the base branch. This test commit is not added to the base branch or the head branch. You can review the status of the test commit using the `mergeable` key. For more information, see \"[Checking mergeability of pull requests](https://docs.github.com/rest/guides/getting-started-with-the-git-database-api#checking-mergeability-of-pull-requests)\".\n\nThe value of the `mergeable` attribute can be `true`, `false`, or `null`. If the value is `null`, then GitHub has started a background job to compute the mergeability. After giving the job time to complete, resubmit the request. When the job finishes, you will see a non-`null` value for the `mergeable` attribute in the response. If `mergeable` is `true`, then `merge_commit_sha` will be the SHA of the _test_ merge commit.\n\nThe value of the `merge_commit_sha` attribute changes depending on the state of the pull request. Before merging a pull request, the `merge_commit_sha` attribute holds the SHA of the _test_ merge commit. After merging a pull request, the `merge_commit_sha` attribute changes depending on how you merged the pull request:\n\n*   If merged as a [merge commit](https://docs.github.com/articles/about-merge-methods-on-github/), `merge_commit_sha` represents the SHA of the merge commit.\n*   If merged via a [squash](https://docs.github.com/articles/about-merge-methods-on-github/#squashing-your-merge-commits), `merge_commit_sha` represents the SHA of the squashed commit on the base branch.\n*   If [rebased](https://docs.github.com/articles/about-merge-methods-on-github/#rebasing-and-merging-your-commits), `merge_commit_sha` represents the commit that the base branch was updated to.\n\nPass the appropriate [media type](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types) to fetch diff and patch formats.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.\n- **`application/vnd.github.diff`**: For more information, see \"[git-diff](https://git-scm.com/docs/git-diff)\" in the Git documentation. If a diff is corrupt, contact us through the [GitHub Support portal](https://support.github.com/). Include the repository name and pull request ID in your message.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#get-a-pull-request"},"operationId":"pulls/get","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request"}},"schema":{"$ref":"#/components/schemas/pull-request"}}},"description":"Pass the appropriate [media type](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types) to fetch diff and patch formats."},"304":{"$ref":"#/components/responses/not_modified"},"404":{"$ref":"#/components/responses/not_found"},"406":{"$ref":"#/components/responses/unacceptable"},"500":{"$ref":"#/components/responses/internal_error"},"503":{"$ref":"#/components/responses/service_unavailable"}},"summary":"Get a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls"}},"path":"/repos/{owner}/{repo}/pulls/{pull_number}","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:pulls/list`

- evaluation role: `held_out_release_case`
- cluster kind: `openapi_version_pair`
- source family: `pull_requests`
- operation ID: `pulls/list`

### Current evidence: `chunk-0d1569942ce3eb27dd225f5c465d8d55795c6773041393e19ff2e8ff40b9e5b3`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-0d1569942ce3eb27dd225f5c465d8d55795c6773041393e19ff2e8ff40b9e5b3.json`
- content SHA256: `bfbd7fa08af332127ae9dedcd397087cf3358a919bbc27c79c1fd617e92bb7a9`
- byte count: `3531`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/list`
- parent source ID: `openapi-current-2026-03-10:pulls/list`
- parent document ID: `openapi-current-pulls-list`
- parent normalized SHA256: `770354bbf3af74f90ef8df5d0f9d5b8fc1b1e742e429b8a3cec11cb4159fba78`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists pull requests in a specified repository.\n\nDraft pull requests are available in public repositories with GitHub\nFree and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing\nplans, and in public and private repositories with GitHub Team and GitHub Enterprise\nCloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products)\nin the GitHub Help documentation.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#list-pull-requests"},"operationId":"pulls/list","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"description":"Either `open`, `closed`, or `all` to filter by state.","in":"query","name":"state","required":false,"schema":{"default":"open","enum":["open","closed","all"],"type":"string"}},{"description":"Filter pulls by head user or head organization and branch name in the format of `user:ref-name` or `organization:ref-name`. For example: `github:new-script-format` or `octocat:test-branch`.","in":"query","name":"head","required":false,"schema":{"type":"string"}},{"description":"Filter pulls by base branch name. Example: `gh-pages`.","in":"query","name":"base","required":false,"schema":{"type":"string"}},{"description":"What to sort results by. `popularity` will sort by the number of comments. `long-running` will sort by date created and will limit the results to pull requests that have been open for more than a month and have had activity within the past month.","in":"query","name":"sort","required":false,"schema":{"default":"created","enum":["created","updated","popularity","long-running"],"type":"string"}},{"description":"The direction of the sort. Default: `desc` when sort is `created` or sort is not specified, otherwise `asc`.","in":"query","name":"direction","required":false,"schema":{"enum":["asc","desc"],"type":"string"}},{"$ref":"#/components/parameters/per-page"},{"$ref":"#/components/parameters/page"}],"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request-simple-items"}},"schema":{"items":{"$ref":"#/components/schemas/pull-request-simple"},"type":"array"}}},"description":"Response","headers":{"Link":{"$ref":"#/components/headers/link"}}},"304":{"$ref":"#/components/responses/not_modified"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"List pull requests","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls"}},"path":"/repos/{owner}/{repo}/pulls","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-d6f84e700ca07621d49f9acf93a7b400c99920d86bb9400a2284f79570f46e41`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-d6f84e700ca07621d49f9acf93a7b400c99920d86bb9400a2284f79570f46e41.json`
- content SHA256: `bfbd7fa08af332127ae9dedcd397087cf3358a919bbc27c79c1fd617e92bb7a9`
- byte count: `3531`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/list`
- parent source ID: `openapi-historical-2022-11-28:pulls/list`
- parent document ID: `openapi-historical-pulls-list`
- parent normalized SHA256: `d7558ccbbcf1289a2641f9cdd6007d958b0e1c3b24a1ce9761e18c46d37ec191`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Lists pull requests in a specified repository.\n\nDraft pull requests are available in public repositories with GitHub\nFree and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing\nplans, and in public and private repositories with GitHub Team and GitHub Enterprise\nCloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products)\nin the GitHub Help documentation.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#list-pull-requests"},"operationId":"pulls/list","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"description":"Either `open`, `closed`, or `all` to filter by state.","in":"query","name":"state","required":false,"schema":{"default":"open","enum":["open","closed","all"],"type":"string"}},{"description":"Filter pulls by head user or head organization and branch name in the format of `user:ref-name` or `organization:ref-name`. For example: `github:new-script-format` or `octocat:test-branch`.","in":"query","name":"head","required":false,"schema":{"type":"string"}},{"description":"Filter pulls by base branch name. Example: `gh-pages`.","in":"query","name":"base","required":false,"schema":{"type":"string"}},{"description":"What to sort results by. `popularity` will sort by the number of comments. `long-running` will sort by date created and will limit the results to pull requests that have been open for more than a month and have had activity within the past month.","in":"query","name":"sort","required":false,"schema":{"default":"created","enum":["created","updated","popularity","long-running"],"type":"string"}},{"description":"The direction of the sort. Default: `desc` when sort is `created` or sort is not specified, otherwise `asc`.","in":"query","name":"direction","required":false,"schema":{"enum":["asc","desc"],"type":"string"}},{"$ref":"#/components/parameters/per-page"},{"$ref":"#/components/parameters/page"}],"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request-simple-items"}},"schema":{"items":{"$ref":"#/components/schemas/pull-request-simple"},"type":"array"}}},"description":"Response","headers":{"Link":{"$ref":"#/components/headers/link"}}},"304":{"$ref":"#/components/responses/not_modified"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"List pull requests","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls"}},"path":"/repos/{owner}/{repo}/pulls","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:pulls/remove-requested-reviewers`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `pull_requests`
- operation ID: `pulls/remove-requested-reviewers`

### Current evidence: `chunk-dfd55afaa0a00a80b6074c48a0605b597cb4aabe4060b7d06eb3020d245a0dcb`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-dfd55afaa0a00a80b6074c48a0605b597cb4aabe4060b7d06eb3020d245a0dcb.json`
- content SHA256: `4597da7d6c6c539e65ba213db794dd1e9deee7d1768c4720d2eabf2e177ba588`
- byte count: `1573`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/remove-requested-reviewers`
- parent source ID: `openapi-current-2026-03-10:pulls/remove-requested-reviewers`
- parent document ID: `openapi-current-pulls-remove-requested-reviewers`
- parent normalized SHA256: `8d87bbba1a3b0d1ef4d0ac1d00356656f64a1799fb3760e71e13d9293773c082`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"Removes review requests from a pull request for a given set of users and/or teams.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/review-requests#remove-requested-reviewers-from-a-pull-request"},"operationId":"pulls/remove-requested-reviewers","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"reviewers":["octocat","hubot","other_user"],"team_reviewers":["justice-league"]}}},"schema":{"properties":{"reviewers":{"description":"An array of user `login`s that will be removed.","items":{"type":"string"},"type":"array"},"team_reviewers":{"description":"An array of team `slug`s that will be removed.","items":{"type":"string"},"type":"array"}},"required":["reviewers"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request-simple"}},"schema":{"$ref":"#/components/schemas/pull-request-simple"}}},"description":"Response"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Remove requested reviewers from a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"review-requests"}},"path":"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-f9d283e08561bb7d1da3ce9d16ea579e71b25546ce4f648653fee458bf70314a`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-f9d283e08561bb7d1da3ce9d16ea579e71b25546ce4f648653fee458bf70314a.json`
- content SHA256: `4597da7d6c6c539e65ba213db794dd1e9deee7d1768c4720d2eabf2e177ba588`
- byte count: `1573`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/remove-requested-reviewers`
- parent source ID: `openapi-historical-2022-11-28:pulls/remove-requested-reviewers`
- parent document ID: `openapi-historical-pulls-remove-requested-reviewers`
- parent normalized SHA256: `c498c4d05a767c809894384cd06775f68aad3caab1e3baf9000776cd1cdfc35f`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"delete","operation":{"description":"Removes review requests from a pull request for a given set of users and/or teams.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/review-requests#remove-requested-reviewers-from-a-pull-request"},"operationId":"pulls/remove-requested-reviewers","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"reviewers":["octocat","hubot","other_user"],"team_reviewers":["justice-league"]}}},"schema":{"properties":{"reviewers":{"description":"An array of user `login`s that will be removed.","items":{"type":"string"},"type":"array"},"team_reviewers":{"description":"An array of team `slug`s that will be removed.","items":{"type":"string"},"type":"array"}},"required":["reviewers"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request-simple"}},"schema":{"$ref":"#/components/schemas/pull-request-simple"}}},"description":"Response"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Remove requested reviewers from a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"review-requests"}},"path":"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:pulls/update`

- evaluation role: `intervention_tuning_case`
- cluster kind: `openapi_version_pair`
- source family: `pull_requests`
- operation ID: `pulls/update`

### Current evidence: `chunk-3b49054d748e4cfbf79ad140015fe2c6d73db66c9185f434fbced3a37c84d285`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-3b49054d748e4cfbf79ad140015fe2c6d73db66c9185f434fbced3a37c84d285.json`
- content SHA256: `4ec84cd2445c6c12c52fbd3eb0ac7c1c2eceeded37b5eb41affeaa84804939c9`
- byte count: `3312`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/update`
- parent source ID: `openapi-current-2026-03-10:pulls/update`
- parent document ID: `openapi-current-pulls-update`
- parent normalized SHA256: `a387285970ab70014f0e23a1a44d666f7360682debbce979de9c7748d13e3ce1`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#update-a-pull-request"},"operationId":"pulls/update","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"base":"master","body":"updated body","state":"open","title":"new title"}}},"schema":{"properties":{"base":{"description":"The name of the branch you want your changes pulled into. This should be an existing branch on the current repository. You cannot update the base branch on a pull request to point to another repository.","type":"string"},"body":{"description":"The contents of the pull request.","type":"string"},"maintainer_can_modify":{"description":"Indicates whether [maintainers can modify](https://docs.github.com/articles/allowing-changes-to-a-pull-request-branch-created-from-a-fork/) the pull request.","type":"boolean"},"state":{"description":"State of this Pull Request. Either `open` or `closed`.","enum":["open","closed"],"type":"string"},"title":{"description":"The title of the pull request.","type":"string"}},"type":"object"}}},"required":false},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request"}},"schema":{"$ref":"#/components/schemas/pull-request"}}},"description":"Response"},"403":{"$ref":"#/components/responses/forbidden"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Update a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls"}},"path":"/repos/{owner}/{repo}/pulls/{pull_number}","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-39b03b894e1f89fc54ff1bcdd8fa4d9173d2c040436a2ae1f2daa1ecf7449406`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-39b03b894e1f89fc54ff1bcdd8fa4d9173d2c040436a2ae1f2daa1ecf7449406.json`
- content SHA256: `4ec84cd2445c6c12c52fbd3eb0ac7c1c2eceeded37b5eb41affeaa84804939c9`
- byte count: `3312`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `pull_requests`
- linked operations: `pulls/update`
- parent source ID: `openapi-historical-2022-11-28:pulls/update`
- parent document ID: `openapi-historical-pulls-update`
- parent normalized SHA256: `13eaac7070b50969f62116ad56c4c534aaa3fdb9aa4b9b59c3730c853bf97353`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"Draft pull requests are available in public repositories with GitHub Free and GitHub Free for organizations, GitHub Pro, and legacy per-repository billing plans, and in public and private repositories with GitHub Team and GitHub Enterprise Cloud. For more information, see [GitHub's products](https://docs.github.com/github/getting-started-with-github/githubs-products) in the GitHub Help documentation.\n\nTo open or update a pull request in a public repository, you must have write access to the head or the source branch. For organization-owned repositories, you must be a member of the organization that owns the repository to open or update a pull request.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw markdown body. Response will include `body`. This is the default if you do not pass any specific media type.\n- **`application/vnd.github.text+json`**: Returns a text only representation of the markdown body. Response will include `body_text`.\n- **`application/vnd.github.html+json`**: Returns HTML rendered from the body's markdown. Response will include `body_html`.\n- **`application/vnd.github.full+json`**: Returns raw, text, and HTML representations. Response will include `body`, `body_text`, and `body_html`.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/pulls/pulls#update-a-pull-request"},"operationId":"pulls/update","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/pull-number"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"base":"master","body":"updated body","state":"open","title":"new title"}}},"schema":{"properties":{"base":{"description":"The name of the branch you want your changes pulled into. This should be an existing branch on the current repository. You cannot update the base branch on a pull request to point to another repository.","type":"string"},"body":{"description":"The contents of the pull request.","type":"string"},"maintainer_can_modify":{"description":"Indicates whether [maintainers can modify](https://docs.github.com/articles/allowing-changes-to-a-pull-request-branch-created-from-a-fork/) the pull request.","type":"boolean"},"state":{"description":"State of this Pull Request. Either `open` or `closed`.","enum":["open","closed"],"type":"string"},"title":{"description":"The title of the pull request.","type":"string"}},"type":"object"}}},"required":false},"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/pull-request"}},"schema":{"$ref":"#/components/schemas/pull-request"}}},"description":"Response"},"403":{"$ref":"#/components/responses/forbidden"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Update a pull request","tags":["pulls"],"x-github":{"category":"pulls","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"pulls"}},"path":"/repos/{owner}/{repo}/pulls/{pull_number}","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:repos/accept-invitation-for-authenticated-user`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `repositories_and_repository_webhooks`
- operation ID: `repos/accept-invitation-for-authenticated-user`

### Current evidence: `chunk-ede821e5fd4be2c5bc48ef65d813c5b920a05a004a017e5efbe55fde9b584d89`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-ede821e5fd4be2c5bc48ef65d813c5b920a05a004a017e5efbe55fde9b584d89.json`
- content SHA256: `1414854dea122d11ba84197733c609c68e149fa95092f6757a248debb4fb5628`
- byte count: `927`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/accept-invitation-for-authenticated-user`
- parent source ID: `openapi-current-2026-03-10:repos/accept-invitation-for-authenticated-user`
- parent document ID: `openapi-current-repos-accept-invitation-for-authenticated-user`
- parent normalized SHA256: `5b3fbe0dfac45f4d5490741cd3236b47ad2f09b8cfa1e719f33c663c2cccb37b`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/collaborators/invitations#accept-a-repository-invitation"},"operationId":"repos/accept-invitation-for-authenticated-user","parameters":[{"$ref":"#/components/parameters/invitation-id"}],"responses":{"204":{"description":"Response"},"304":{"$ref":"#/components/responses/not_modified"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"409":{"$ref":"#/components/responses/conflict"},"451":{"$ref":"#/components/responses/validation_failed"}},"summary":"Accept a repository invitation","tags":["repos"],"x-github":{"category":"collaborators","enabledForGitHubApps":false,"githubCloudOnly":false,"subcategory":"invitations"}},"path":"/user/repository_invitations/{invitation_id}","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-0c19021a77142567363f0be9647755d3aef4e2b61df218536ab5b6a8e9f676fd`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-0c19021a77142567363f0be9647755d3aef4e2b61df218536ab5b6a8e9f676fd.json`
- content SHA256: `15edef10deec038d4ea37ff9ce5630d3e82a90fd5d83eac13b7b50bdecdccbf7`
- byte count: `869`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/accept-invitation-for-authenticated-user`
- parent source ID: `openapi-historical-2022-11-28:repos/accept-invitation-for-authenticated-user`
- parent document ID: `openapi-historical-repos-accept-invitation-for-authenticated-user`
- parent normalized SHA256: `7b946666fd031ab97f8344d80cdceb79bad69268f7629c2c620a8a2d9fb08946`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"patch","operation":{"description":"","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/collaborators/invitations#accept-a-repository-invitation"},"operationId":"repos/accept-invitation-for-authenticated-user","parameters":[{"$ref":"#/components/parameters/invitation-id"}],"responses":{"204":{"description":"Response"},"304":{"$ref":"#/components/responses/not_modified"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"409":{"$ref":"#/components/responses/conflict"}},"summary":"Accept a repository invitation","tags":["repos"],"x-github":{"category":"collaborators","enabledForGitHubApps":false,"githubCloudOnly":false,"subcategory":"invitations"}},"path":"/user/repository_invitations/{invitation_id}","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:repos/create-for-authenticated-user`

- evaluation role: `held_out_release_case`
- cluster kind: `openapi_version_pair`
- source family: `repositories_and_repository_webhooks`
- operation ID: `repos/create-for-authenticated-user`

### Current evidence: `chunk-0a98ac5e1a4daa0e51e91dc08bb8787b274704ce635586deb431fb9ebf7c4a5a`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-0a98ac5e1a4daa0e51e91dc08bb8787b274704ce635586deb431fb9ebf7c4a5a.json`
- content SHA256: `1e6b3a02c76635e9900f7cb260f1d61fd517058c88e31f09ee873e8b94e93e49`
- byte count: `5509`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/create-for-authenticated-user`
- parent source ID: `openapi-current-2026-03-10:repos/create-for-authenticated-user`
- parent document ID: `openapi-current-repos-create-for-authenticated-user`
- parent normalized SHA256: `5b0df5ff085872d4b1e4dcfe07827a9cb07d00f701550bf6f4f4bcb1ef6eb66c`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository for the authenticated user.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-a-repository-for-the-authenticated-user"},"operationId":"repos/create-for-authenticated-user","parameters":[],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repo!","homepage":"https://github.com","is_template":true,"name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"},"allow_merge_commit":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"},"allow_rebase_merge":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"},"allow_squash_merge":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"},"auto_init":{"default":false,"description":"Whether the repository is initialized with a minimal README.","type":"boolean"},"delete_branch_on_merge":{"default":false,"description":"Whether to delete head branches when pull requests are merged","example":false,"type":"boolean"},"description":{"description":"A short description of the repository.","type":"string"},"gitignore_template":{"description":"The desired language or platform to apply to the .gitignore.","example":"Haskell","type":"string"},"has_discussions":{"default":false,"description":"Whether discussions are enabled.","example":true,"type":"boolean"},"has_downloads":{"default":true,"description":"Whether downloads are enabled.","example":true,"type":"boolean"},"has_issues":{"default":true,"description":"Whether issues are enabled.","example":true,"type":"boolean"},"has_projects":{"default":true,"description":"Whether projects are enabled.","example":true,"type":"boolean"},"has_wiki":{"default":true,"description":"Whether the wiki is enabled.","example":true,"type":"boolean"},"homepage":{"description":"A URL with more information about the repository.","type":"string"},"is_template":{"default":false,"description":"Whether this repository acts as a template that can be used to generate new repositories.","example":true,"type":"boolean"},"license_template":{"description":"The license keyword of the open source license for this repository.","example":"mit","type":"string"},"merge_commit_message":{"description":"The default value for a merge commit message.\n\n- `PR_TITLE` - default to the pull request's title.\n- `PR_BODY` - default to the pull request's body.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","PR_TITLE","BLANK"],"type":"string"},"merge_commit_title":{"description":"Required when using `merge_commit_message`.\n\nThe default value for a merge commit title.\n\n- `PR_TITLE` - default to the pull request's title.\n- `MERGE_MESSAGE` - default to the classic title for a merge message (e.g., Merge pull request #123 from branch-name).","enum":["PR_TITLE","MERGE_MESSAGE"],"type":"string"},"name":{"description":"The name of the repository.","example":"Team Environment","type":"string"},"private":{"default":false,"description":"Whether the repository is private.","type":"boolean"},"squash_merge_commit_message":{"description":"The default value for a squash merge commit message:\n\n- `PR_BODY` - default to the pull request's body.\n- `COMMIT_MESSAGES` - default to the branch's commit messages.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","COMMIT_MESSAGES","BLANK"],"type":"string"},"squash_merge_commit_title":{"description":"Required when using `squash_merge_commit_message`.\n\nThe default value for a squash merge commit title:\n\n- `PR_TITLE` - default to the pull request's title.\n- `COMMIT_OR_PR_TITLE` - default to the commit's title (if only one commit) or the pull request's title (when more than one commit).","enum":["PR_TITLE","COMMIT_OR_PR_TITLE"],"type":"string"},"team_id":{"description":"The id of the team that will be granted access to this repository. This is only valid when creating a repository in an organization.","type":"integer"}},"required":["name"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/full-repository"}},"schema":{"$ref":"#/components/schemas/full-repository"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World","schema":{"type":"string"}}}},"304":{"$ref":"#/components/responses/not_modified"},"400":{"$ref":"#/components/responses/bad_request"},"401":{"$ref":"#/components/responses/requires_authentication"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"422":{"$ref":"#/components/responses/validation_failed"},"451":{"$ref":"#/components/responses/validation_failed"}},"summary":"Create a repository for the authenticated user","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":false,"githubCloudOnly":false,"subcategory":"repos"}},"path":"/user/repos","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-24feb9ae2816561bfb66d549dd480b574ec3cf2cc2ff6950630ff7a883b7ec56`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-24feb9ae2816561bfb66d549dd480b574ec3cf2cc2ff6950630ff7a883b7ec56.json`
- content SHA256: `2fffea0b72cf4c3c8c84438902709bd78afd8e44c61402e3d69ee2bcb2a21f29`
- byte count: `5451`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/create-for-authenticated-user`
- parent source ID: `openapi-historical-2022-11-28:repos/create-for-authenticated-user`
- parent document ID: `openapi-historical-repos-create-for-authenticated-user`
- parent normalized SHA256: `2d0cb5d0e6461144e084f217cec5eb4e38697351a95611a9af6b281b9cdc200a`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository for the authenticated user.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-a-repository-for-the-authenticated-user"},"operationId":"repos/create-for-authenticated-user","parameters":[],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repo!","homepage":"https://github.com","is_template":true,"name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Whether to allow Auto-merge to be used on pull requests.","example":false,"type":"boolean"},"allow_merge_commit":{"default":true,"description":"Whether to allow merge commits for pull requests.","example":true,"type":"boolean"},"allow_rebase_merge":{"default":true,"description":"Whether to allow rebase merges for pull requests.","example":true,"type":"boolean"},"allow_squash_merge":{"default":true,"description":"Whether to allow squash merges for pull requests.","example":true,"type":"boolean"},"auto_init":{"default":false,"description":"Whether the repository is initialized with a minimal README.","type":"boolean"},"delete_branch_on_merge":{"default":false,"description":"Whether to delete head branches when pull requests are merged","example":false,"type":"boolean"},"description":{"description":"A short description of the repository.","type":"string"},"gitignore_template":{"description":"The desired language or platform to apply to the .gitignore.","example":"Haskell","type":"string"},"has_discussions":{"default":false,"description":"Whether discussions are enabled.","example":true,"type":"boolean"},"has_downloads":{"default":true,"description":"Whether downloads are enabled.","example":true,"type":"boolean"},"has_issues":{"default":true,"description":"Whether issues are enabled.","example":true,"type":"boolean"},"has_projects":{"default":true,"description":"Whether projects are enabled.","example":true,"type":"boolean"},"has_wiki":{"default":true,"description":"Whether the wiki is enabled.","example":true,"type":"boolean"},"homepage":{"description":"A URL with more information about the repository.","type":"string"},"is_template":{"default":false,"description":"Whether this repository acts as a template that can be used to generate new repositories.","example":true,"type":"boolean"},"license_template":{"description":"The license keyword of the open source license for this repository.","example":"mit","type":"string"},"merge_commit_message":{"description":"The default value for a merge commit message.\n\n- `PR_TITLE` - default to the pull request's title.\n- `PR_BODY` - default to the pull request's body.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","PR_TITLE","BLANK"],"type":"string"},"merge_commit_title":{"description":"Required when using `merge_commit_message`.\n\nThe default value for a merge commit title.\n\n- `PR_TITLE` - default to the pull request's title.\n- `MERGE_MESSAGE` - default to the classic title for a merge message (e.g., Merge pull request #123 from branch-name).","enum":["PR_TITLE","MERGE_MESSAGE"],"type":"string"},"name":{"description":"The name of the repository.","example":"Team Environment","type":"string"},"private":{"default":false,"description":"Whether the repository is private.","type":"boolean"},"squash_merge_commit_message":{"description":"The default value for a squash merge commit message:\n\n- `PR_BODY` - default to the pull request's body.\n- `COMMIT_MESSAGES` - default to the branch's commit messages.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","COMMIT_MESSAGES","BLANK"],"type":"string"},"squash_merge_commit_title":{"description":"Required when using `squash_merge_commit_message`.\n\nThe default value for a squash merge commit title:\n\n- `PR_TITLE` - default to the pull request's title.\n- `COMMIT_OR_PR_TITLE` - default to the commit's title (if only one commit) or the pull request's title (when more than one commit).","enum":["PR_TITLE","COMMIT_OR_PR_TITLE"],"type":"string"},"team_id":{"description":"The id of the team that will be granted access to this repository. This is only valid when creating a repository in an organization.","type":"integer"}},"required":["name"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/full-repository"}},"schema":{"$ref":"#/components/schemas/full-repository"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World","schema":{"type":"string"}}}},"304":{"$ref":"#/components/responses/not_modified"},"400":{"$ref":"#/components/responses/bad_request"},"401":{"$ref":"#/components/responses/requires_authentication"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Create a repository for the authenticated user","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":false,"githubCloudOnly":false,"subcategory":"repos"}},"path":"/user/repos","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:repos/create-in-org`

- evaluation role: `intervention_tuning_case`
- cluster kind: `openapi_version_pair`
- source family: `repositories_and_repository_webhooks`
- operation ID: `repos/create-in-org`

### Current evidence: `chunk-0866e576fcc08a7d8b93d77a2710ca186b1b7ab008a0c3332a53230283b04136`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-0866e576fcc08a7d8b93d77a2710ca186b1b7ab008a0c3332a53230283b04136.json`
- content SHA256: `a32adb5a509dd1fd47fd8419404734d650e1e596a082195d5f9bdb91648be572`
- byte count: `6723`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/create-in-org`
- parent source ID: `openapi-current-2026-03-10:repos/create-in-org`
- parent document ID: `openapi-current-repos-create-in-org`
- parent normalized SHA256: `e079fbc97d479f2bd8ab6db247f14bf639df0129550f81951096b6d52ecfb59c`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository in the specified organization. The authenticated user must be a member of the organization.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-an-organization-repository"},"operationId":"repos/create-in-org","parameters":[{"$ref":"#/components/parameters/org"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repository","has_issues":true,"has_projects":true,"has_wiki":true,"homepage":"https://github.com","name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Either `true` to allow auto-merge on pull requests, or `false` to disallow auto-merge.","type":"boolean"},"allow_merge_commit":{"default":true,"description":"Either `true` to allow merging pull requests with a merge commit, or `false` to prevent merging pull requests with merge commits.","type":"boolean"},"allow_rebase_merge":{"default":true,"description":"Either `true` to allow rebase-merging pull requests, or `false` to prevent rebase-merging.","type":"boolean"},"allow_squash_merge":{"default":true,"description":"Either `true` to allow squash-merging pull requests, or `false` to prevent squash-merging.","type":"boolean"},"auto_init":{"default":false,"description":"Pass `true` to create an initial commit with empty README.","type":"boolean"},"custom_properties":{"additionalProperties":true,"description":"The custom properties for the new repository. The keys are the custom property names, and the values are the corresponding custom property values.","type":"object"},"delete_branch_on_merge":{"default":false,"description":"Either `true` to allow automatically deleting head branches when pull requests are merged, or `false` to prevent automatic deletion. **The authenticated user must be an organization owner to set this property to `true`.**","type":"boolean"},"description":{"description":"A short description of the repository.","type":"string"},"gitignore_template":{"description":"Desired language or platform [.gitignore template](https://github.com/github/gitignore) to apply. Use the name of the template without the extension. For example, \"Haskell\".","type":"string"},"has_downloads":{"default":true,"description":"Whether downloads are enabled.","example":true,"type":"boolean"},"has_issues":{"default":true,"description":"Either `true` to enable issues for this repository or `false` to disable them.","type":"boolean"},"has_projects":{"default":true,"description":"Either `true` to enable projects for this repository or `false` to disable them. **Note:** If you're creating a repository in an organization that has disabled repository projects, the default is `false`, and if you pass `true`, the API returns an error.","type":"boolean"},"has_wiki":{"default":true,"description":"Either `true` to enable the wiki for this repository or `false` to disable it.","type":"boolean"},"homepage":{"description":"A URL with more information about the repository.","type":"string"},"is_template":{"default":false,"description":"Either `true` to make this repo available as a template repository or `false` to prevent it.","type":"boolean"},"license_template":{"description":"Choose an [open source license template](https://choosealicense.com/) that best suits your needs, and then use the [license keyword](https://docs.github.com/articles/licensing-a-repository/#searching-github-by-license-type) as the `license_template` string. For example, \"mit\" or \"mpl-2.0\".","type":"string"},"merge_commit_message":{"description":"The default value for a merge commit message.\n\n- `PR_TITLE` - default to the pull request's title.\n- `PR_BODY` - default to the pull request's body.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","PR_TITLE","BLANK"],"type":"string"},"merge_commit_title":{"description":"Required when using `merge_commit_message`.\n\nThe default value for a merge commit title.\n\n- `PR_TITLE` - default to the pull request's title.\n- `MERGE_MESSAGE` - default to the classic title for a merge message (e.g., Merge pull request #123 from branch-name).","enum":["PR_TITLE","MERGE_MESSAGE"],"type":"string"},"name":{"description":"The name of the repository.","type":"string"},"private":{"default":false,"description":"Whether the repository is private.","type":"boolean"},"squash_merge_commit_message":{"description":"The default value for a squash merge commit message:\n\n- `PR_BODY` - default to the pull request's body.\n- `COMMIT_MESSAGES` - default to the branch's commit messages.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","COMMIT_MESSAGES","BLANK"],"type":"string"},"squash_merge_commit_title":{"description":"Required when using `squash_merge_commit_message`.\n\nThe default value for a squash merge commit title:\n\n- `PR_TITLE` - default to the pull request's title.\n- `COMMIT_OR_PR_TITLE` - default to the commit's title (if only one commit) or the pull request's title (when more than one commit).","enum":["PR_TITLE","COMMIT_OR_PR_TITLE"],"type":"string"},"team_id":{"description":"The id of the team that will be granted access to this repository. This is only valid when creating a repository in an organization.","type":"integer"},"use_squash_pr_title_as_default":{"default":false,"deprecated":true,"description":"Either `true` to allow squash-merge commits to use pull request title, or `false` to use commit message. **This property is closing down. Please use `squash_merge_commit_title` instead.","type":"boolean"},"visibility":{"description":"The visibility of the repository.","enum":["public","private"],"type":"string"}},"required":["name"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/full-repository"}},"schema":{"$ref":"#/components/schemas/full-repository"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World","schema":{"type":"string"}}}},"403":{"$ref":"#/components/responses/forbidden"},"422":{"$ref":"#/components/responses/validation_failed"},"451":{"$ref":"#/components/responses/validation_failed"}},"summary":"Create an organization repository","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"repos"}},"path":"/orgs/{org}/repos","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-9415dcdaefed1c781040a1a24f82567f5cd9976d4b6936bfe2b187819aebba7d`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-9415dcdaefed1c781040a1a24f82567f5cd9976d4b6936bfe2b187819aebba7d.json`
- content SHA256: `a5232c486d47fe775a94c9f15db85c9e92ea1a7354df49b4c98194940aa18616`
- byte count: `6665`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/create-in-org`
- parent source ID: `openapi-historical-2022-11-28:repos/create-in-org`
- parent document ID: `openapi-historical-repos-create-in-org`
- parent normalized SHA256: `7eae32289ebbc359cc98a527bf3ae9d2940fe6f4a49139a5fa86ba4d47a14ed7`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"post","operation":{"description":"Creates a new repository in the specified organization. The authenticated user must be a member of the organization.\n\nOAuth app tokens and personal access tokens (classic) need the `public_repo` or `repo` scope to create a public repository, and `repo` scope to create a private repository.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/repos#create-an-organization-repository"},"operationId":"repos/create-in-org","parameters":[{"$ref":"#/components/parameters/org"}],"requestBody":{"content":{"application/json":{"examples":{"default":{"value":{"description":"This is your first repository","has_issues":true,"has_projects":true,"has_wiki":true,"homepage":"https://github.com","name":"Hello-World","private":false}}},"schema":{"properties":{"allow_auto_merge":{"default":false,"description":"Either `true` to allow auto-merge on pull requests, or `false` to disallow auto-merge.","type":"boolean"},"allow_merge_commit":{"default":true,"description":"Either `true` to allow merging pull requests with a merge commit, or `false` to prevent merging pull requests with merge commits.","type":"boolean"},"allow_rebase_merge":{"default":true,"description":"Either `true` to allow rebase-merging pull requests, or `false` to prevent rebase-merging.","type":"boolean"},"allow_squash_merge":{"default":true,"description":"Either `true` to allow squash-merging pull requests, or `false` to prevent squash-merging.","type":"boolean"},"auto_init":{"default":false,"description":"Pass `true` to create an initial commit with empty README.","type":"boolean"},"custom_properties":{"additionalProperties":true,"description":"The custom properties for the new repository. The keys are the custom property names, and the values are the corresponding custom property values.","type":"object"},"delete_branch_on_merge":{"default":false,"description":"Either `true` to allow automatically deleting head branches when pull requests are merged, or `false` to prevent automatic deletion. **The authenticated user must be an organization owner to set this property to `true`.**","type":"boolean"},"description":{"description":"A short description of the repository.","type":"string"},"gitignore_template":{"description":"Desired language or platform [.gitignore template](https://github.com/github/gitignore) to apply. Use the name of the template without the extension. For example, \"Haskell\".","type":"string"},"has_downloads":{"default":true,"description":"Whether downloads are enabled.","example":true,"type":"boolean"},"has_issues":{"default":true,"description":"Either `true` to enable issues for this repository or `false` to disable them.","type":"boolean"},"has_projects":{"default":true,"description":"Either `true` to enable projects for this repository or `false` to disable them. **Note:** If you're creating a repository in an organization that has disabled repository projects, the default is `false`, and if you pass `true`, the API returns an error.","type":"boolean"},"has_wiki":{"default":true,"description":"Either `true` to enable the wiki for this repository or `false` to disable it.","type":"boolean"},"homepage":{"description":"A URL with more information about the repository.","type":"string"},"is_template":{"default":false,"description":"Either `true` to make this repo available as a template repository or `false` to prevent it.","type":"boolean"},"license_template":{"description":"Choose an [open source license template](https://choosealicense.com/) that best suits your needs, and then use the [license keyword](https://docs.github.com/articles/licensing-a-repository/#searching-github-by-license-type) as the `license_template` string. For example, \"mit\" or \"mpl-2.0\".","type":"string"},"merge_commit_message":{"description":"The default value for a merge commit message.\n\n- `PR_TITLE` - default to the pull request's title.\n- `PR_BODY` - default to the pull request's body.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","PR_TITLE","BLANK"],"type":"string"},"merge_commit_title":{"description":"Required when using `merge_commit_message`.\n\nThe default value for a merge commit title.\n\n- `PR_TITLE` - default to the pull request's title.\n- `MERGE_MESSAGE` - default to the classic title for a merge message (e.g., Merge pull request #123 from branch-name).","enum":["PR_TITLE","MERGE_MESSAGE"],"type":"string"},"name":{"description":"The name of the repository.","type":"string"},"private":{"default":false,"description":"Whether the repository is private.","type":"boolean"},"squash_merge_commit_message":{"description":"The default value for a squash merge commit message:\n\n- `PR_BODY` - default to the pull request's body.\n- `COMMIT_MESSAGES` - default to the branch's commit messages.\n- `BLANK` - default to a blank commit message.","enum":["PR_BODY","COMMIT_MESSAGES","BLANK"],"type":"string"},"squash_merge_commit_title":{"description":"Required when using `squash_merge_commit_message`.\n\nThe default value for a squash merge commit title:\n\n- `PR_TITLE` - default to the pull request's title.\n- `COMMIT_OR_PR_TITLE` - default to the commit's title (if only one commit) or the pull request's title (when more than one commit).","enum":["PR_TITLE","COMMIT_OR_PR_TITLE"],"type":"string"},"team_id":{"description":"The id of the team that will be granted access to this repository. This is only valid when creating a repository in an organization.","type":"integer"},"use_squash_pr_title_as_default":{"default":false,"deprecated":true,"description":"Either `true` to allow squash-merge commits to use pull request title, or `false` to use commit message. **This property is closing down. Please use `squash_merge_commit_title` instead.","type":"boolean"},"visibility":{"description":"The visibility of the repository.","enum":["public","private"],"type":"string"}},"required":["name"],"type":"object"}}},"required":true},"responses":{"201":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/full-repository"}},"schema":{"$ref":"#/components/schemas/full-repository"}}},"description":"Response","headers":{"Location":{"example":"https://api.github.com/repos/octocat/Hello-World","schema":{"type":"string"}}}},"403":{"$ref":"#/components/responses/forbidden"},"422":{"$ref":"#/components/responses/validation_failed"}},"summary":"Create an organization repository","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"repos"}},"path":"/orgs/{org}/repos","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:repos/get-content`

- evaluation role: `evaluation_development_case`
- cluster kind: `openapi_version_pair`
- source family: `repositories_and_repository_webhooks`
- operation ID: `repos/get-content`

### Current evidence: `chunk-04e27893cade7a2cb64b06cc387db4cefb1c887db971ddfdc6082b8c136a206b`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-04e27893cade7a2cb64b06cc387db4cefb1c887db971ddfdc6082b8c136a206b.json`
- content SHA256: `bd74a3a44a18c360a7075be54a0df85b8a161e729a5f6223bb7b70e6c2095eb6`
- byte count: `5834`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/get-content`
- parent source ID: `openapi-current-2026-03-10:repos/get-content`
- parent document ID: `openapi-current-repos-get-content`
- parent normalized SHA256: `9f5117b075cf7e367030262f8445474db11dd4f9600929252db2e186dcbaac8c`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Gets the contents of a file or directory in a repository. Specify the file path or directory with the `path` parameter. If you omit the `path` parameter, you will receive the contents of the repository's root directory.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw file contents for files and symlinks.\n- **`application/vnd.github.html+json`**: Returns the file contents in HTML. Markup languages are rendered to HTML using GitHub's open-source [Markup library](https://github.com/github/markup).\n- **`application/vnd.github.object+json`**: Returns the contents in a consistent object format regardless of the content type. For example, instead of an array of objects for a directory, the response will be an object with an `entries` attribute containing the array of objects.\n\nIf the content is a directory: The response will be an array of objects, one object for each item in the directory.\n\nIf the content is a symlink and the symlink's target is a normal file in the repository, then the API responds with the content of the file. Otherwise, the API responds with an object describing the symlink itself.\n\nIf the content is a submodule, the `submodule_git_url` field identifies the location of the submodule repository, and the `sha` identifies a specific commit within the submodule repository. Git uses the given URL when cloning the submodule repository, and checks out the submodule at that specific commit. If the submodule repository is not hosted on github.com, the Git URLs (`git_url` and `_links[\"git\"]`) and the github.com URLs (`html_url` and `_links[\"html\"]`) will have null values.\n\n**Notes**:\n\n- To get a repository's contents recursively, you can [recursively get the tree](https://docs.github.com/rest/git/trees#get-a-tree).\n- This API has an upper limit of 1,000 files for a directory. If you need to retrieve\nmore files, use the [Git Trees API](https://docs.github.com/rest/git/trees#get-a-tree).\n- Download URLs expire and are meant to be used just once. To ensure the download URL does not expire, please use the contents API to obtain a fresh download URL for each download.\n- If the requested file's size is:\n  - 1 MB or smaller: All features of this endpoint are supported.\n  - Between 1-100 MB: Only the `raw` or `object` custom media types are supported. Both will work as normal, except that when using the `object` media type, the `content` field will be an empty\nstring and the `encoding` field will be `\"none\"`. To get the contents of these larger files, use the `raw` media type.\n  - Greater than 100 MB: This endpoint is not supported.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/contents#get-repository-content"},"operationId":"repos/get-content","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"description":"path parameter","in":"path","name":"path","required":true,"schema":{"type":"string"},"x-multi-segment":true},{"description":"The name of the commit/branch/tag. Default: the repository’s default branch.","in":"query","name":"ref","required":false,"schema":{"type":"string"}}],"requestBody":{"content":{"application/json":{"examples":{"response-if-content-is-a-directory":{"summary":"Content is a directory"},"response-if-content-is-a-directory-github-object":{"summary":"Content is a directory using the object media type"},"response-if-content-is-a-file":{"summary":"Content is a file"},"response-if-content-is-a-file-github-object":{"summary":"Content is a file using the object media type"},"response-if-content-is-a-submodule":{"summary":"Content is a submodule"},"response-if-content-is-a-symlink":{"summary":"Content is a symlink"}}}},"required":false},"responses":{"200":{"content":{"application/json":{"examples":{"response-if-content-is-a-directory":{"$ref":"#/components/examples/content-file-response-if-content-is-a-directory"},"response-if-content-is-a-file":{"$ref":"#/components/examples/content-file-response-if-content-is-a-file"},"response-if-content-is-a-submodule":{"$ref":"#/components/examples/content-file-response-if-content-is-a-submodule"},"response-if-content-is-a-symlink":{"$ref":"#/components/examples/content-file-response-if-content-is-a-symlink"}},"schema":{"discriminator":{"mapping":{"array":"#/components/schemas/content-directory","file":"#/components/schemas/content-file","submodule":"#/components/schemas/content-submodule","symlink":"#/components/schemas/content-symlink"},"propertyName":"type"},"oneOf":[{"$ref":"#/components/schemas/content-directory"},{"$ref":"#/components/schemas/content-file"},{"$ref":"#/components/schemas/content-symlink"},{"$ref":"#/components/schemas/content-submodule"}]}},"application/vnd.github.object":{"examples":{"response-if-content-is-a-directory-github-object":{"$ref":"#/components/examples/content-file-response-if-content-is-a-directory-object"},"response-if-content-is-a-file-github-object":{"$ref":"#/components/examples/content-file-response-if-content-is-a-file"}},"schema":{"$ref":"#/components/schemas/content-tree"}}},"description":"Response"},"302":{"$ref":"#/components/responses/found"},"304":{"$ref":"#/components/responses/not_modified"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"}},"summary":"Get repository content","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"contents"}},"path":"/repos/{owner}/{repo}/contents/{path}","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-f81fe01e0fd1af16f295885b6ad3405931469127e81de12ef9c0861b6ce04066`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-f81fe01e0fd1af16f295885b6ad3405931469127e81de12ef9c0861b6ce04066.json`
- content SHA256: `2ec3e7698b1a9639410a99f1268f56100cfcf0038ce8f5b543c9a5d82a867484`
- byte count: `6143`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/get-content`
- parent source ID: `openapi-historical-2022-11-28:repos/get-content`
- parent document ID: `openapi-historical-repos-get-content`
- parent normalized SHA256: `2fc3e99522e2ea0d897ee64e66706be5149918260c99918cd5b8f52326eb1235`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"Gets the contents of a file or directory in a repository. Specify the file path or directory with the `path` parameter. If you omit the `path` parameter, you will receive the contents of the repository's root directory.\n\nThis endpoint supports the following custom media types. For more information, see \"[Media types](https://docs.github.com/rest/using-the-rest-api/getting-started-with-the-rest-api#media-types).\"\n\n- **`application/vnd.github.raw+json`**: Returns the raw file contents for files and symlinks.\n- **`application/vnd.github.html+json`**: Returns the file contents in HTML. Markup languages are rendered to HTML using GitHub's open-source [Markup library](https://github.com/github/markup).\n- **`application/vnd.github.object+json`**: Returns the contents in a consistent object format regardless of the content type. For example, instead of an array of objects for a directory, the response will be an object with an `entries` attribute containing the array of objects.\n\nIf the content is a directory, the response will be an array of objects, one object for each item in the directory. When listing the contents of a directory, submodules have their \"type\" specified as \"file\". Logically, the value _should_ be \"submodule\". This behavior exists [for backwards compatibility purposes](https://git.io/v1YCW). In the next major version of the API, the type will be returned as \"submodule\".\n\nIf the content is a symlink and the symlink's target is a normal file in the repository, then the API responds with the content of the file. Otherwise, the API responds with an object describing the symlink itself.\n\nIf the content is a submodule, the `submodule_git_url` field identifies the location of the submodule repository, and the `sha` identifies a specific commit within the submodule repository. Git uses the given URL when cloning the submodule repository, and checks out the submodule at that specific commit. If the submodule repository is not hosted on github.com, the Git URLs (`git_url` and `_links[\"git\"]`) and the github.com URLs (`html_url` and `_links[\"html\"]`) will have null values.\n\n**Notes**:\n\n- To get a repository's contents recursively, you can [recursively get the tree](https://docs.github.com/rest/git/trees#get-a-tree).\n- This API has an upper limit of 1,000 files for a directory. If you need to retrieve\nmore files, use the [Git Trees API](https://docs.github.com/rest/git/trees#get-a-tree).\n- Download URLs expire and are meant to be used just once. To ensure the download URL does not expire, please use the contents API to obtain a fresh download URL for each download.\n- If the requested file's size is:\n  - 1 MB or smaller: All features of this endpoint are supported.\n  - Between 1-100 MB: Only the `raw` or `object` custom media types are supported. Both will work as normal, except that when using the `object` media type, the `content` field will be an empty\nstring and the `encoding` field will be `\"none\"`. To get the contents of these larger files, use the `raw` media type.\n  - Greater than 100 MB: This endpoint is not supported.","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/contents#get-repository-content"},"operationId":"repos/get-content","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"description":"path parameter","in":"path","name":"path","required":true,"schema":{"type":"string"},"x-multi-segment":true},{"description":"The name of the commit/branch/tag. Default: the repository’s default branch.","in":"query","name":"ref","required":false,"schema":{"type":"string"}}],"requestBody":{"content":{"application/json":{"examples":{"response-if-content-is-a-directory":{"summary":"Content is a directory"},"response-if-content-is-a-directory-github-object":{"summary":"Content is a directory using the object media type"},"response-if-content-is-a-file":{"summary":"Content is a file"},"response-if-content-is-a-file-github-object":{"summary":"Content is a file using the object media type"},"response-if-content-is-a-submodule":{"summary":"Content is a submodule"},"response-if-content-is-a-symlink":{"summary":"Content is a symlink"}}}},"required":false},"responses":{"200":{"content":{"application/json":{"examples":{"response-if-content-is-a-directory":{"$ref":"#/components/examples/content-file-response-if-content-is-a-directory"},"response-if-content-is-a-file":{"$ref":"#/components/examples/content-file-response-if-content-is-a-file"},"response-if-content-is-a-submodule":{"$ref":"#/components/examples/content-file-response-if-content-is-a-submodule"},"response-if-content-is-a-symlink":{"$ref":"#/components/examples/content-file-response-if-content-is-a-symlink"}},"schema":{"discriminator":{"mapping":{"array":"#/components/schemas/content-directory","file":"#/components/schemas/content-file","submodule":"#/components/schemas/content-submodule","symlink":"#/components/schemas/content-symlink"},"propertyName":"type"},"oneOf":[{"$ref":"#/components/schemas/content-directory"},{"$ref":"#/components/schemas/content-file"},{"$ref":"#/components/schemas/content-symlink"},{"$ref":"#/components/schemas/content-submodule"}]}},"application/vnd.github.object":{"examples":{"response-if-content-is-a-directory-github-object":{"$ref":"#/components/examples/content-file-response-if-content-is-a-directory-object"},"response-if-content-is-a-file-github-object":{"$ref":"#/components/examples/content-file-response-if-content-is-a-file"}},"schema":{"$ref":"#/components/schemas/content-tree"}}},"description":"Response"},"302":{"$ref":"#/components/responses/found"},"304":{"$ref":"#/components/responses/not_modified"},"403":{"$ref":"#/components/responses/forbidden"},"404":{"$ref":"#/components/responses/not_found"}},"summary":"Get repository content","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"contents"}},"path":"/repos/{owner}/{repo}/contents/{path}","path_parameters":[]}}]}
</pre>

</details>

## Cluster: `openapi-pair:repos/list-attestations`

- evaluation role: `held_out_release_case`
- cluster kind: `openapi_version_pair`
- source family: `repositories_and_repository_webhooks`
- operation ID: `repos/list-attestations`

### Current evidence: `chunk-86c17157604102e82f7090de928de56d4222dae94608aed1a989cfab92eac54b`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-86c17157604102e82f7090de928de56d4222dae94608aed1a989cfab92eac54b.json`
- content SHA256: `938ad4d1b5bcd27266990a4ab41c699eae54855fb5512dbf1b151372b3016084`
- byte count: `2471`
- source state: `current`
- authority: `authoritative`
- corpus data role: `corpus_source`
- API version/snapshot: `2026-03-10`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/list-attestations`
- parent source ID: `openapi-current-2026-03-10:repos/list-attestations`
- parent document ID: `openapi-current-repos-list-attestations`
- parent normalized SHA256: `f6a9010b9876a943c4531542df109c2ddceda4f5167d0b1fe78c88635e076c8a`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"List a collection of artifact attestations with a given subject digest that are associated with a repository.\n\nThe authenticated user making the request must have read access to the repository. In addition, when using a fine-grained access token the `attestations:read` permission is required.\n\n**Please note:** in order to offer meaningful security benefits, an attestation's signature and timestamps **must** be cryptographically verified, and the identity of the attestation signer **must** be validated. Attestations can be verified using the [GitHub CLI `attestation verify` command](https://cli.github.com/manual/gh_attestation_verify). For more information, see [our guide on how to use artifact attestations to establish a build's provenance](https://docs.github.com/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds).","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/attestations#list-attestations"},"operationId":"repos/list-attestations","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/per-page"},{"$ref":"#/components/parameters/pagination-before"},{"$ref":"#/components/parameters/pagination-after"},{"description":"The parameter should be set to the attestation's subject's SHA256 digest, in the form `sha256:HEX_DIGEST`.","in":"path","name":"subject_digest","required":true,"schema":{"type":"string"},"x-multi-segment":true},{"description":"Optional filter for fetching attestations with a given predicate type.\nThis option accepts `provenance`, `sbom`, `release`, or freeform text\nfor custom predicate types.","in":"query","name":"predicate_type","required":false,"schema":{"type":"string"}}],"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/list-attestations"}},"schema":{"properties":{"attestations":{"items":{"properties":{"bundle_url":{"type":"string"},"initiator":{"type":"string"},"repository_id":{"type":"integer"}},"type":"object"},"type":"array"}},"type":"object"}}},"description":"Response"}},"summary":"List attestations","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"attestations"}},"path":"/repos/{owner}/{repo}/attestations/{subject_digest}","path_parameters":[]}}]}
</pre>

</details>

### Historical evidence: `chunk-c85c8bef9f92d7e2fe88eef66094a668f65db06cd9086f31f562d3dcb2cce665`

- chunk kind: `openapi_operation_core`
- content path: `datasets/chunks/phase3d_v1/openapi/operation_core/chunk-c85c8bef9f92d7e2fe88eef66094a668f65db06cd9086f31f562d3dcb2cce665.json`
- content SHA256: `905c60b671996e2ca9f4306593a03c9fd8a11bd659e08e56e2637e4b9d3522d4`
- byte count: `2907`
- source state: `historical_comparison`
- authority: `historical`
- corpus data role: `historical_source`
- API version/snapshot: `2022-11-28`
- source commit/version: `3cef12e8a02d612ad032473d4fb87266f2befeae`
- semantic families: `repositories_and_repository_webhooks`
- linked operations: `repos/list-attestations`
- parent source ID: `openapi-historical-2022-11-28:repos/list-attestations`
- parent document ID: `openapi-historical-repos-list-attestations`
- parent normalized SHA256: `b43929268133e1baf918f72ad2a5a9f8b538050f3dc7d75e6d124436e913c494`

<details>
<summary>Evidence content</summary>

<pre>
{"fragments":[{"path":[],"value":{"method":"get","operation":{"description":"List a collection of artifact attestations with a given subject digest that are associated with a repository.\n\nThe authenticated user making the request must have read access to the repository. In addition, when using a fine-grained access token the `attestations:read` permission is required.\n\n**Please note:** in order to offer meaningful security benefits, an attestation's signature and timestamps **must** be cryptographically verified, and the identity of the attestation signer **must** be validated. Attestations can be verified using the [GitHub CLI `attestation verify` command](https://cli.github.com/manual/gh_attestation_verify). For more information, see [our guide on how to use artifact attestations to establish a build's provenance](https://docs.github.com/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds).","externalDocs":{"description":"API method documentation","url":"https://docs.github.com/rest/repos/attestations#list-attestations"},"operationId":"repos/list-attestations","parameters":[{"$ref":"#/components/parameters/owner"},{"$ref":"#/components/parameters/repo"},{"$ref":"#/components/parameters/per-page"},{"$ref":"#/components/parameters/pagination-before"},{"$ref":"#/components/parameters/pagination-after"},{"description":"The parameter should be set to the attestation's subject's SHA256 digest, in the form `sha256:HEX_DIGEST`.","in":"path","name":"subject_digest","required":true,"schema":{"type":"string"},"x-multi-segment":true},{"description":"Optional filter for fetching attestations with a given predicate type.\nThis option accepts `provenance`, `sbom`, `release`, or freeform text\nfor custom predicate types.","in":"query","name":"predicate_type","required":false,"schema":{"type":"string"}}],"responses":{"200":{"content":{"application/json":{"examples":{"default":{"$ref":"#/components/examples/list-attestations"}},"schema":{"properties":{"attestations":{"items":{"properties":{"bundle":{"description":"The attestation's Sigstore Bundle.\nRefer to the [Sigstore Bundle Specification](https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_bundle.proto) for more information.","properties":{"dsseEnvelope":{"additionalProperties":true,"properties":{},"type":"object"},"mediaType":{"type":"string"},"verificationMaterial":{"additionalProperties":true,"properties":{},"type":"object"}},"type":"object"},"bundle_url":{"type":"string"},"initiator":{"type":"string"},"repository_id":{"type":"integer"}},"type":"object"},"type":"array"}},"type":"object"}}},"description":"Response"}},"summary":"List attestations","tags":["repos"],"x-github":{"category":"repos","enabledForGitHubApps":true,"githubCloudOnly":false,"subcategory":"attestations"}},"path":"/repos/{owner}/{repo}/attestations/{subject_digest}","path_parameters":[]}}]}
</pre>

</details>
