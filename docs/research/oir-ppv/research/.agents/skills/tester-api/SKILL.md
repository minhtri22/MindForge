---
name: tester-api
description: >
  Tester rules for HTTP/API and protocol testing, including request/response contracts, malformed inputs, status/error behavior, authentication, idempotency, pagination, streaming, cancellation, retries, limits, and compatibility. Use together with tester-core.
---

# Tester API

## Dependency

Use together with `tester-core`.

## 1. Scope

Use for REST, OpenAI-compatible APIs, gateways, RPC-style interfaces, web services, and protocol adapters.

## 2. Contract Matrix

Test:

- method;
- path;
- headers;
- content type;
- request schema;
- required/optional fields;
- defaults;
- response schema;
- status codes;
- error schema;
- version behavior.

## 3. Input Classes

Include:

- valid minimum request;
- typical request;
- maximum supported request;
- empty request;
- missing required field;
- unknown field;
- wrong type;
- null;
- malformed JSON;
- oversized value;
- invalid encoding;
- duplicate semantic values;
- adversarial strings.

## 4. Error Semantics

Verify:

- correct status code;
- stable error shape;
- actionable message;
- no internal stack leak unless explicitly allowed;
- no partial state corruption;
- retryability is clear.

## 5. Idempotency / Retry

Where applicable test:

- same request repeated;
- retry after timeout;
- retry after connection drop;
- duplicate idempotency key;
- different body with same key;
- partial downstream success.

## 6. Pagination / Ordering

Verify:

- first/last page;
- empty page;
- exact boundary;
- repeated page token;
- invalid token;
- deterministic ordering where promised;
- no duplication/loss across pages.

## 7. Streaming

Where supported test:

- normal stream;
- early cancellation;
- server termination;
- client disconnect;
- malformed chunk;
- timeout;
- partial output;
- final usage/metadata behavior.

## 8. Authentication / Authorization

Where applicable test:

- missing credential;
- invalid credential;
- expired credential;
- insufficient permission;
- wrong tenant/user;
- credential leakage in logs/errors.

## 9. Compatibility

Test relevant client/API versions and backward compatibility.

## 10. Evidence

Capture exact:

- request;
- response;
- headers where relevant;
- status;
- timing;
- server logs/correlation ID if available.

Never expose real secrets in test reports.
