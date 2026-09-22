# MK-1 H1a Confirmatory Preflight Trigger v0.1

TRIGGER_H1A_CONFIRMATORY_PREFLIGHT_v0.1

Bound pre-confirmatory files:

- spec blob `8cbeff53c5f7ac2b91312621c9fdaaef5c57bb63`
- evaluator blob `3492ccda1ef6c297d8626da080c4faaf302fb2b3`
- evaluator test blob `cdfd5600098a35c2e30cf0c3960fb6d770482ec7`
- preflight workflow blob `1bbd1113ae7daac6a562bdf5d761484446743e6f`

This trigger authorizes fixture-only zero-pristine QA.

It does not authorize PRISTINE_CONFIRMATORY model inference.


Repair provenance:

- run `35787209043` classified `INVALID_PREFLIGHT_IMPORT_PATH`;
- failure occurred during pytest collection before any scientific artifact download;
- evaluator/spec/test blobs unchanged;
- workflow-only repair: set `PYTHONPATH=.`;
- repaired workflow commit: `d8278bf13d09c066fd42d7d1d29e1f069950b224`.
