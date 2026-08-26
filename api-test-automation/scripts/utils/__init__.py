# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.9
"""API Test Automation Utils Package — v1.8

Modules:
  - parser: OpenAPI/Postman spec parser
  - deep_parser: Deep constraint extractor (enum, boundary, format, anyOf/oneOf)
  - generator: Rule-driven test case generator (MVP)
  - smart_generator: Smart case generator (boundary, equivalence, enum, pairwise, state-machine, exception)
  - data_factory: Test data factory with versioning and auto-cleanup (v1.8: +alert_dedup R-30)
  - reporter: Multi-format test report generator (v1.6: +html ECharts)
  - nl_parser: Natural language interface parser
  - error_handler: Friendly error handling
  - schema_checker: JSON Schema validator
  - client: httpx client wrapper with retry
  - assertion_engine: Multi-layer response assertion engine (v1.6: +inferred, +yaml, +jsonpath)
  - test_performance: Concurrent performance testing with TPS/P50/P95/P99 (v1.7: +baseline/regression R-15~R-17)
  - test_security: OWASP Top 10 basic security testing (v1.6: +rate_limit, +multi_role R-18~R-20)
  - retry: Failed retry handler with exponential backoff (R-28)
  - dependency_checker: Environment dependency checker (R-29)
  - auth_manager: JWT/Token/Basic/APIKey/OAuth2 multi-account auth center (F5)
  - change_detector: Test case dedup + manifest diff (12.1/12.2)
  - pdf_image_parser: PDF text extraction + image OCR (F1 PDF/截图)
  - client: httpx client wrapper with retry + async support (N1)
  - reporter: Multi-format report + trend comparison + failure categorization (13.1/13.2)
"""
