# Design Patterns Used in Slugger

## Ports and Adapters
Core abstractions define stable ports while providers, GitHub services, memory backends, and plugins implement adapters.

## Artifact-First Collaboration
Agents communicate by producing and consuming artifacts instead of calling each other directly.

## Registry Pattern
Component, provider, agent, and plugin registries decouple discovery from use.

## Strategy Pattern
Validators, memory backends, and provider implementations are selected at runtime through configuration and injected interfaces.

## Template Method for Agents
Base agent lifecycle logic handles validation and observability while concrete agents implement focused execution behavior.
