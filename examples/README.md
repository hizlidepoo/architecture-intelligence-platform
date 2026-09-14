# Reference fixture landscape

This directory contains the reference architecture that AIP uses for the local Quick Start and tests.

## Topology

- order-service calls product-service operation getProduct.
- order-service publishes payment-q, consumed by payment-service.
- payment-service publishes invoice-q, consumed by invoice-service.
- unused-q intentionally has no consumer.
- unknown-producer-q intentionally has no known producer.

## Service fixtures

- order-service: openapi.yaml, asyncapi.yaml, architecture.yaml.
- product-service: openapi.yaml.
- payment-service: asyncapi.yaml.
- invoice-service: asyncapi.yaml.

OpenAPI files describe HTTP operations. AsyncAPI files describe message channels, publishers, subscribers, messages, and queue metadata. architecture.yaml captures explicit service-to-service calls that API specifications do not express by themselves.

runtime-demo has its own README. mcp-clients contains client-specific MCP examples.

For development and test usage, see ../docs/development.md. For adapter contracts, see ../docs/adapter-development.md.
