# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Operator Backend Connection Error**: Fixed "Cannot connect to host backend-service" error in AgenticSession execution
  - Added `backend-service-alias.yaml` to create service name mapping between hardcoded `backend-service` and actual `vteam-backend` service
  - Updated operator deployment with proper `BACKEND_API_URL` environment variable
  - AgenticSession workflows now complete successfully in local development
  - Resolves issue where claude-runner jobs failed to connect to backend API

### Added
- **Complete Operator Integration for Local Development**: 
  - Operator now builds and deploys automatically with `make dev-start`
  - Added 12 comprehensive operator tests (Infrastructure, Functionality, End-to-End)
  - New Makefile targets: `dev-logs-operator`, `dev-restart-operator`, `dev-operator-status`, `dev-test-operator`
  - Full AgenticSession workflow testing in local environment
  - Test coverage increased from 12 to 24 tests (100% pass rate)

### Changed
- Updated local development documentation to reflect operator integration
- Enhanced test suite with operator-specific test categories
- Local development environment now provides complete end-to-end functionality

### Technical Details
- **Root Cause**: Operator hardcoded to use `backend-service.vteam-dev.svc.cluster.local:8080` but local dev uses `vteam-backend` service
- **Solution**: ExternalName service alias + proper environment variable configuration
- **Impact**: Full AgenticSession workflow now functional in local development
- **Test Coverage**: All 24 tests passing, including 12 operator-specific tests

---

## Previous Releases

For changes prior to operator integration, see git commit history.
