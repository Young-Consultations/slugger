<!--
  templates/UML.md
  Purpose: Detailed UML templates and guidance for documenting architecture and behavior.
  Replace placeholders and use PlantUML/Mermaid sources kept in version control.
-->

# UML Templates & Guidance

Purpose
- Provide reusable UML templates and best-practices for documenting system architecture, data models, and interaction flows.
- Store source (PlantUML / Mermaid) in version control so diagrams can be reviewed and diffed.

Recommended diagram types
- Context diagram: show system boundary and external actors.
- Component (Container) diagram: services, responsibilities, and major interfaces.
- Sequence diagram: message flows for critical use cases.
- Class diagram: domain model and relationships.
- Deployment diagram: runtime nodes and infrastructure mapping.

Conventions
- Name diagrams with a clear prefix and short description, e.g., `context-auth-service.puml` or `sequence-login.mmd`.
- Use consistent actor/component names across diagrams.
- Keep each diagram focused on a single concern.
- Provide a brief text summary alongside each diagram for accessibility and reviewers who cannot view images.

Storage & file layout (suggested)
- docs/diagrams/
  - plantuml/  (source .puml files)
  - mermaid/   (source .mmd files)
  - exports/   (png/svg/pdf for presentations)

PlantUML examples
- Sequence diagram example (PlantUML):

```puml
@startuml
actor User
participant "API Gateway" as API
participant "Auth Service" as Auth
participant "App Service" as App

User -> API: POST /v1/login
API -> Auth: validate(token)
Auth --> API: 200 OK
API -> App: POST /v1/action {user}
App --> API: 202 Accepted
API --> User: 202 Accepted
@enduml
```

- Class diagram example (PlantUML):

```puml
@startuml
class User {
  +id: UUID
  +name: string
  +email: string
}
class Order {
  +id: UUID
  +amount: Decimal
}
User "1" -- "*" Order : places
@enduml
```

Mermaid examples
- Sequence diagram example (Mermaid):

```mermaid
sequenceDiagram
    participant U as User
    participant API as API Gateway
    participant S as Service
    U->>API: POST /items
    API->>S: validate & create
    S-->>API: 201 Created
    API-->>U: 201 Created
```

- Class diagram example (Mermaid - limited):

```mermaid
classDiagram
    class User {
      +UUID id
      +String name
      +String email
    }
    class Order {
      +UUID id
      +Decimal amount
    }
    User "1" -- "*" Order : places
```

Accessibility & review
- Always include a plain-text caption and short description under the diagram so readers with visual impairments or in text-only environments understand intent.
- Keep the diagram source in the repo to enable diffs and history.

Versioning & maintenance
- When updating diagrams, update the summary and include the reason in the commit/PR.
- Prefer small incremental changes to large rewrites to make reviews easier.

