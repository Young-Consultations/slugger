# Requirements Traceability Matrix

## Traceability convention

This matrix provides planning-level coverage from vision goal to future verification. Detailed `AC-*` text is authoritative in [FunctionalRequirements.md](FunctionalRequirements.md); measurable quality criteria are in [NonFunctionalRequirements.md](NonFunctionalRequirements.md). Future test case IDs (`FTC-*`) are test-design placeholders, not implementation prescriptions.

| Vision goal | Business objective | Functional requirements | Nonfunctional requirements | Acceptance criteria | Future tests |
| --- | --- | --- | --- | --- | --- |
| VG-01 Governed transformation | BO-01, BO-03 | FR-INT-01, FR-SCP-01, FR-PRM-01, FR-PRV-01, FR-VAL-01, FR-DEP-01, FR-EXE-01, FR-TST-01, FR-SMK-01, FR-PUB-01 | NFR-PER-01–03, NFR-REL-01/05, NFR-USA-01 | AC-INT-01a–c; AC-SCP-01a–c; AC-PRM-01a–c; AC-PRV-01a–c; AC-VAL-01a–c; AC-DEP-01a–c; AC-EXE-01a–c; AC-TST-01a–c; AC-SMK-01a–c; AC-PUB-01a–c | FTC-E2E-01 golden CLI; FTC-E2E-02 unsupported scope; FTC-GATE-01 each gate blocks; FTC-UX-01 outcome comprehension |
| VG-02 Traceability/evidence | BO-02 | FR-RUN-01/02, FR-PRM-01, FR-ART-01, FR-EVD-01, FR-ERR-01, FR-LCM-01 | NFR-REL-03/04, NFR-OBS-01–06, NFR-INT-02, NFR-DOC-*, NFR-AI-01/03 | AC-RUN-01a–c; AC-RUN-02a–c; AC-ART-01a–c; AC-EVD-01a–d; AC-ERR-01a–c; AC-LCM-01a–c | FTC-TRC-01 correlation completeness; FTC-EVD-01 tamper; FTC-EVD-02 partial truth; FTC-LOG-01 secret/redaction; FTC-LCM-01 impact chain |
| VG-03 Human authority | BO-02, BO-05 | FR-INT-02, FR-EVD-01, FR-PUB-01/02, FR-GOV-01, FR-LCM-02 | NFR-SEC-01, NFR-USA-01/02, NFR-ACC-01, NFR-CMP-*, NFR-DOC-02 | AC-INT-02a–c; AC-EVD-01b/d; AC-PUB-01b; AC-PUB-02a/c; AC-GOV-01a–c; AC-LCM-02c | FTC-AUTH-01 withdrawn approval; FTC-AUTH-02 local label; FTC-PR-01 draft-only; FTC-PR-02 no merge authority; FTC-UX-02 residual decision |
| VG-04 Safe isolation | BO-03 | FR-PRV-01, FR-WS-01/02, FR-ART-01, FR-VAL-01, FR-DEP-01, FR-EXE-01, FR-PUB-01 | NFR-SEC-01–08, NFR-PER-03/04, NFR-REL-01, NFR-CFG-02 | AC-PRV-01b/c; AC-WS-01a–c; AC-WS-02a–c; AC-ART-01b/c; AC-VAL-01a–c; AC-DEP-01a–c; AC-EXE-01a–c; AC-PUB-01a | FTC-SEC-01 path/link corpus; FTC-SEC-02 secret canary; FTC-SEC-03 process/egress; FTC-SEC-04 dependency tamper; FTC-SRC-01 source unchanged |
| VG-05 Reliable recovery | BO-04 | FR-RUN-01/02, FR-SMK-01, FR-IDM-01, FR-REC-01, FR-ERR-01 | NFR-REL-02–05, NFR-REC-01/02, NFR-SCL-*, NFR-OBS-02/06, NFR-TST-02 | AC-RUN-01a/b; AC-RUN-02a/b; AC-SMK-01a; AC-IDM-01a–d; AC-REC-01a–c; AC-ERR-01a–c | FTC-IDM-01 sequential duplicate; FTC-IDM-02 concurrent race; FTC-REC-01 kill each boundary; FTC-REC-02 stale evidence; FTC-TGT-01 ambiguous state preserved |
| VG-06 Composable evolution | BO-06 | FR-CAT-01, FR-PRV-01, FR-LCM-01/02, FR-EXT-01 | NFR-MNT-01–03, NFR-EXT-01, NFR-INT-01/02, NFR-PORT-01, NFR-DEP-01, NFR-AUT-*, NFR-AI-02/03 | AC-CAT-01a–c; AC-PRV-01a; AC-LCM-01a–c; AC-LCM-02a–c; AC-EXT-01a–c | FTC-ARC-01 MVP without experimental; FTC-CON-01 contract versions; FTC-EXT-01 substitute provider; FTC-PROM-01 promotion pack; FTC-AUT-01 headless run |
| VG-07 Organizational boundary | BO-05 | FR-INT-01/02, FR-PUB-02, FR-GOV-01 | NFR-INT-01, NFR-DEP-02, NFR-OBS-03, NFR-CFG-01 | AC-INT-01a–c; AC-INT-02a–c; AC-PUB-02d; AC-GOV-01a–c | FTC-CTR-01 canonical fixture; FTC-CTR-02 unknown major; FTC-BOUND-01 external repos absent; FTC-BOUND-02 no portfolio mutation |

## Business-rule verification map

| Test family | Rules covered |
| --- | --- |
| FTC-AUTH | BR-01–06, BR-14, BR-18 |
| FTC-GATE / FTC-SEC | BR-08–12, BR-23/24, BR-27/30 |
| FTC-IDM / FTC-TGT | BR-13, BR-15–17, BR-19, BR-21/22 |
| FTC-PROM / FTC-ARC | BR-07, BR-20, BR-25/26, BR-31/32 |
| FTC-EVD / FTC-LOG | BR-12, BR-28/29 |

## Future test-case definitions

| ID | Verification intent | Required evidence |
| --- | --- | --- |
| FTC-E2E-01 | Approved reference CLI reaches one draft with runnable promised behavior | Canonical input, phase record, manifest, install/test/smoke evidence, target objects |
| FTC-GATE-01 | Independently fail/error/skip/stale each required gate | No target mutation plus categorized result for every injection |
| FTC-SEC-01 | Exercise traversal, normalization, link, special-file, size and malicious-content corpus | 100% defined prohibited cases blocked before execution |
| FTC-SEC-02 | Seed secrets in all credential boundaries and adversarial output | No seed in retained/displayed/published material |
| FTC-IDM-01 | Sequential redelivery after completion | No provider reinvocation; same owned draft returned |
| FTC-IDM-02 | Concurrent identical deliveries and publication race | At most one managed draft; unsafe state preserved |
| FTC-REC-01 | Abrupt termination at every phase boundary | Restore last durable boundary; no partial pass |
| FTC-EVD-01 | Alter candidate, input, manifest and evidence | Every alteration detected before reuse/publication |
| FTC-CTR-01 | Validate approved canonical request/result fixtures | Lossless identity/semantics and valid result |
| FTC-CTR-02 | Supply unknown/breaking contract and missing validator | Pre-generation rejection with no mutation |
| FTC-PR-01 | Inspect created/updated review object | Draft-only, exact files, marker, evidence and human next action |
| FTC-TGT-01 | Enumerate branch/PR ambiguity and ownership conflicts | No destructive reconciliation; actionable block |
| FTC-ARC-01 | Remove/disable experimental dependencies | Supported MVP installs, starts and runs unaffected |
| FTC-EXT-01 | Execute common provider conformance using substitute | Equivalent normalized errors/evidence and no policy expansion |
| FTC-UX-01 | Representative users interpret run summary | Meets NFR-USA-01 comprehension floor |
| FTC-PROM-01 | Audit proposed capability against BR-20 | Complete signed promotion evidence or remains experimental |

## Coverage governance

Before release, test management SHALL refine placeholders into owned test specifications with environment, fixtures, preconditions, expected results and retained evidence. A report SHALL show 100% P0/P1 requirement and rule coverage. Any human-only check requires rationale and accountable sign-off; no P0 negative/fail-closed path may remain human-only.
