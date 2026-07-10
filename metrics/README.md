# metrics/

This directory contains metrics collection, aggregation, and reporting components for the Slugger system.

## Purpose

Metrics provide quantitative visibility into workflow performance, AI usage costs, agent effectiveness, and system health. They drive continuous improvement and cost management.

## Metrics Captured

| Metric | Description |
|--------|-------------|
| Execution time | Time taken per agent invocation and workflow phase |
| Token usage | Input and output tokens consumed per model call |
| Estimated cost | Estimated AI inference cost per run |
| Agent success rate | Ratio of successful to failed agent invocations |
| Artifact generation rate | Number of artifacts produced per workflow |
| Retry count | Number of retries per agent invocation |
| Workflow completion rate | Percentage of workflows completed successfully |

## Conventions

- Metrics are emitted as structured events through the observability system.
- Aggregated metrics are stored as JSON or CSV files under `metrics/data/`.
- Dashboards or reports are generated from this data.

## Related

- `observability/` — the event infrastructure that feeds metrics
- `logs/` — complementary log data for qualitative analysis
