# Consulting playbook migration plan

Target repository: `Young-Consultations/consulting-playbook`.

Do not delete `consulting/` from Slugger until the target repository exists, content has been migrated, links are updated, checks pass, and removal is delivered in a separate focused pull request.

## Classification

- `consulting/01-service-offer/**`: move to `proposals/`.
- `consulting/02-client-intake/**`: move to `engagements/`.
- `consulting/03-discovery-interviews/**`: move to `engagements/`.
- `consulting/04-assessment-checklist/**`: move to `assessments/` and `checklists/`.
- `consulting/05-evidence-collection/**`: move to `assessments/`.
- `consulting/06-findings-analysis/**`: move to `reports/`.
- `consulting/07-report-template/**`: move to `reports/`.
- `consulting/08-roadmap-template/**`: move to `roadmaps/`.
- `consulting/09-proposals-and-sow/**`: move to `proposals/`.
- `consulting/10-case-studies/slugger-internal-case-study-outline.md`: shared reference until Slugger case-study ownership is decided.
- `consulting/10-case-studies/case-study-template.md`: move to `reports/`.
- `consulting/11-knowledge-base/**`: copy to `docs/` first, then retain or deprecate Slugger copies after link migration.
- `consulting/README.md`: copy as a migration index, then deprecate in Slugger after extraction.
