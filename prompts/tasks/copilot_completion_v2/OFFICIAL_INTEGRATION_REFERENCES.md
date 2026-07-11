# Official Integration References

Copilot Agent must verify current official documentation at implementation time. These references
were current when this plan was generated.

## OpenAI Codex

- Codex SDK: https://developers.openai.com/codex/sdk
- Codex with the Agents SDK and Codex CLI MCP server:
  https://developers.openai.com/codex/guides/agents-sdk
- Codex CLI: https://developers.openai.com/codex/cli
- Codex CLI authentication: https://developers.openai.com/codex/auth
- Codex CLI reference, including `codex mcp-server`:
  https://developers.openai.com/codex/cli/reference

Implementation direction for this Python repository:
- Prefer a dedicated Codex-agent adapter using Codex CLI as an MCP server through the OpenAI
  Agents SDK, or a documented `codex exec` subprocess adapter.
- Keep generic OpenAI model generation separate from the Codex coding-agent contract.
- Do not retain the current `/chat/completions` wrapper under the claim that it is a full Codex
  agent integration.

## Canva

- Canva Connect API authentication:
  https://www.canva.dev/docs/connect/authentication/
- Canva autofill guide:
  https://www.canva.dev/docs/connect/autofill-guide/
- Canva MCP:
  https://www.canva.dev/docs/mcp/
- Canva Connect API scopes:
  https://www.canva.dev/docs/connect/appendix/scopes/

Implementation direction:
- Use OAuth 2.0 Authorization Code with PKCE for user authorization where the Connect API is used.
- Use only documented design, template/autofill, asset, and export capabilities.
- Feature-flag preview endpoints and provide a manual design handoff when a required operation is
  not supported.

## GitHub

- GitHub REST API: https://docs.github.com/en/rest
- Pull requests: https://docs.github.com/en/rest/pulls
- Workflow runs: https://docs.github.com/en/rest/actions/workflow-runs
- Releases: https://docs.github.com/en/rest/releases/releases
- Secure GitHub Actions use:
  https://docs.github.com/en/actions/reference/security/secure-use

Implementation direction:
- Use versioned REST requests and fine-grained permissions.
- Store external resource IDs for idempotent retries and resume.
- Do not let automation approve or merge its own pull request.
