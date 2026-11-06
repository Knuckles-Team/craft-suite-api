# CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT data model

This spec adds ontology classes and generated content files. It adds no persisted type.

- Pack classes (`craft_suite_api/ontology/artcraft.ttl`, CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R002): `:App` under `:Application`, `:AppTool` under `:Tool`, `:UseCase` under `:Task`.
- Pack properties: `:ofApp`, `:forApp`, `:usesToolName`, `:appNamespace`, `:appVersion`.
- App ontology files (`craft_suite_api/ontology/artcraft-<app>.ttl`, CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R003): one `:App` individual, the app's domain classes and one `:UseCase` individual per functionality.
- App source (`content/apps/<app>.yml`, CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R005): authored summary, domain classes and functionalities.
- Tool snapshot (`content/snapshots/<app>.tools.json`, CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R006): generated, sorted tool names, descriptions and input schemas, with the app version.

- Lifecycle property (`craft_suite_api/ontology/artcraft.ttl`, CONN-CRAFT-SUITE-API-CONNECTOR-CONTENT-R010.1): `:lifecycleState` on `:App` and the backend component, range the SDK ConnectorLifecycle state classes. No state class is declared here.
