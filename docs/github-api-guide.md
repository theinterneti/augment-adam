# GitHub API Guide for Repository Management

This guide provides instructions for using the GitHub API to manage repository settings, particularly branch protection rules.

## Table of Contents

1. [Authentication](#authentication)
2. [Branch Protection Rulesets](#branch-protection-rulesets)
3. [Common API Operations](#common-api-operations)
4. [Troubleshooting](#troubleshooting)
5. [Best Practices](#best-practices)

## Authentication

Before using the GitHub API, you need to authenticate. There are several ways to authenticate:

### Personal Access Token (PAT)

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Create a new token with appropriate permissions
3. Use the token in your API requests:

```bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/...
```

### GitHub CLI

If you have GitHub CLI installed, you can authenticate and use it for API calls:

```bash
# Login
gh auth login

# Make API calls
gh api repos/OWNER/REPO/rulesets
```

## Branch Protection Rulesets

Branch protection rulesets allow you to enforce rules on branches in your repository.

### Creating a Branch Protection Ruleset

To create a branch protection ruleset, you need to make a POST request to the GitHub API:

```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets \
  -d @github-ruleset.json
```

Where `github-ruleset.json` contains your ruleset configuration:

```json
{
  "name": "Protect main branch",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "required_approving_review_count": 1,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          {
            "context": "test (3.8)",
            "integration_id": null
          },
          {
            "context": "test (3.9)",
            "integration_id": null
          },
          {
            "context": "test (3.10)",
            "integration_id": null
          },
          {
            "context": "pre-commit",
            "integration_id": null
          },
          {
            "context": "coverage",
            "integration_id": null
          }
        ]
      }
    },
    {
      "type": "required_signatures"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "required_linear_history"
    }
  ]
}
```

### Getting All Repository Rulesets

To list all rulesets for a repository:

```bash
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets
```

### Getting a Specific Ruleset

To get details about a specific ruleset:

```bash
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets/RULESET_ID
```

### Updating a Ruleset

To update an existing ruleset:

```bash
curl -L \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets/RULESET_ID \
  -d @updated-ruleset.json
```

### Deleting a Ruleset

To delete a ruleset:

```bash
curl -L \
  -X DELETE \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets/RULESET_ID
```

## Common API Operations

### Creating a Repository

```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user/repos \
  -d '{"name":"REPO_NAME","private":true,"description":"DESCRIPTION"}'
```

### Creating a Branch

```bash
# First, get the SHA of the commit to branch from
SHA=$(curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/git/refs/heads/main | \
  jq -r .object.sha)

# Then create the branch
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/git/refs \
  -d "{\"ref\":\"refs/heads/NEW_BRANCH\",\"sha\":\"$SHA\"}"
```

### Creating a Pull Request

```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/pulls \
  -d '{"title":"TITLE","body":"DESCRIPTION","head":"HEAD_BRANCH","base":"BASE_BRANCH"}'
```

## Troubleshooting

### Common Errors

1. **Authentication Errors (401)**
   - Check that your token is valid and has the necessary permissions
   - Ensure your token hasn't expired

2. **Permission Errors (403)**
   - Verify that your token has the required scopes
   - Check that you have the necessary permissions on the repository

3. **Not Found Errors (404)**
   - Verify that the repository exists and is accessible to you
   - Check that the resource (branch, ruleset, etc.) exists

4. **Validation Errors (422)**
   - Check your JSON payload for syntax errors
   - Ensure all required fields are provided
   - Verify that field values are valid

### Debugging Tips

1. Use the `-v` flag with curl to see detailed request and response information:
   ```bash
   curl -v -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/...
   ```

2. Use jq to format JSON responses for better readability:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/... | jq
   ```

## Best Practices

1. **Use Fine-Grained Tokens**: Create tokens with the minimum necessary permissions
2. **Store Tokens Securely**: Never commit tokens to your repository
3. **Use Conditional Requests**: Use ETags and conditional requests to reduce API rate limit usage
4. **Paginate Results**: Use pagination for endpoints that return large amounts of data
5. **Handle Rate Limits**: Check rate limit headers and implement backoff strategies
6. **Use Idempotent Operations**: Design scripts to be idempotent (can be run multiple times without side effects)
7. **Automate with GitHub Actions**: Use GitHub Actions for automated repository management

## Additional Resources

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub API Rate Limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [GitHub API Authentication](https://docs.github.com/en/rest/overview/other-authentication-methods)
