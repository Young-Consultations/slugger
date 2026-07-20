# Custom Provider Example

This sample shows how to register a provider implementation with Slugger's provider registry and call the typed generation interface without requiring network credentials.

## Running

```bash
cd examples/custom_provider
python run.py
```

## What it shows

* Creating a `ProviderConfig` for a deterministic local provider.
* Registering a provider with `ProviderRegistry`.
* Calling `generate()` with a `GenerationRequest` and reading a `GenerationResult`.

Use this pattern when adapting an internal model gateway or another AI provider behind Slugger's provider interface.
