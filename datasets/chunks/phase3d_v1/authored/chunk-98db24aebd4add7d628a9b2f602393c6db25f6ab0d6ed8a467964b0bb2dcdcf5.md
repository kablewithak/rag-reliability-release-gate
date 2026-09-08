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
