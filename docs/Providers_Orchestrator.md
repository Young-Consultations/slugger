## Provider integration with Orchestrator

The Orchestrator class (slugger.orchestrator.core.Orchestrator) resolves an
AI provider at construction time using ProviderFactory and exposes it via the
`provider` property.

When running agents through Orchestrator.run_agent or Orchestrator.run_pipeline,
it injects the configured provider instance into the agent's inputs under the
key `_provider`. Agents may read this value to call the provider or to access
provider configuration.

This approach keeps existing Agent interfaces unchanged while enabling explicit
provider injection and dependency injection for testing.
