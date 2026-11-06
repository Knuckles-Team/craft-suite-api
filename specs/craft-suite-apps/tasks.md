# CONN-CRAFT-SUITE-API-APPS — Implementation tasks

Governing spec: [spec.md](spec.md). Design: [plan.md](plan.md). Rows: [requirements.md](requirements.md).

- [ ] T001 [US1] CONN-CRAFT-SUITE-API-APPS-R001 The backend tier degrades when unconfigured.
- [ ] T002 [US1] CONN-CRAFT-SUITE-API-APPS-R002 Declare every app upstream.
- [ ] T003 [US1] CONN-CRAFT-SUITE-API-APPS-R003 Probe the app command-line tools for MCP support.
- [ ] T004 [US1] CONN-CRAFT-SUITE-API-APPS-R004 Behavior: local deployment runs each app as a stdio child.
- [ ] T005 [US1] CONN-CRAFT-SUITE-API-APPS-R005 Behavior: remote deployment reaches an app over streamable HTTP.
- [ ] T006 [US1] CONN-CRAFT-SUITE-API-APPS-R006 Behavior: bridge mode attaches an app to a running desktop session.
- [ ] T007 [US1] CONN-CRAFT-SUITE-API-APPS-R007 Behavior: the initial tool list stays small.
- [ ] T008 [US1] CONN-CRAFT-SUITE-API-APPS-R008 Wiring: the facade registers once and arbora loads one app at a time.
- [ ] T009 [US1] CONN-CRAFT-SUITE-API-APPS-R009 Acceptance: phase 1 proves the facade with three apps over stdio.
- [ ] T010 [US1] CONN-CRAFT-SUITE-API-APPS-R010 Acceptance: phase 2 proves the full registry, remote mode and bridge mode.
- [ ] T011 [US1] CONN-CRAFT-SUITE-API-APPS-R011 Acceptance: phase 3 proves the content tier.
- [ ] T012 [US1] CONN-CRAFT-SUITE-API-APPS-R012 Acceptance: phase 4 proves arbora integration.
- [ ] T013 [US4] CONN-CRAFT-SUITE-API-APPS-R013 Bind each app to the artifact exchange.
- [ ] T014 [US4] CONN-CRAFT-SUITE-API-APPS-R014 Deliver outputs to an object store and a file share.
- [ ] T015 [US4] CONN-CRAFT-SUITE-API-APPS-R015 Hot-path proof: an app call takes an exchange input and publishes its output.
- [ ] T016 [P] [US4] CONN-CRAFT-SUITE-API-APPS-R016 Skills tell the agent how to pass inputs and find outputs.
- [ ] T017 [US1] CONN-CRAFT-SUITE-API-APPS-R017 Every app engine command is its own tool.
- [ ] T018 [US1] CONN-CRAFT-SUITE-API-APPS-R018 Each app warms on its own; startup never blocks.
- [ ] T019 [US1] CONN-CRAFT-SUITE-API-APPS-R019 Command tool schemas are typed from the apps' parameter documentation.
- [ ] T020 [US4] CONN-CRAFT-SUITE-API-APPS-R020 Command tools run their arguments through the exchange and await background jobs.
- [ ] T021 [US1] CONN-CRAFT-SUITE-API-APPS-R018.1 Delete the local readiness probe; the SDK connector lifecycle owns the state.
- [ ] T022 [US1] CONN-CRAFT-SUITE-API-APPS-R018.2 Supply probes only: the backend and each app report a result, never a state.
- [ ] T023 [US1] CONN-CRAFT-SUITE-API-APPS-R018.3 Map the warm-up and backend outcomes onto the SDK lifecycle states.
- [ ] T024 [US1] CONN-CRAFT-SUITE-API-APPS-R018.5 The ready answer follows the warming state and shows every lifecycle state.
- [ ] T025 [US1] CONN-CRAFT-SUITE-API-APPS-R018.4 Wiring and hot-path proof: a broken backend never reports ready.
- [ ] T026 [US1] CONN-CRAFT-SUITE-API-APPS-R001.1 Backend readiness detail comes from the backend lifecycle.
