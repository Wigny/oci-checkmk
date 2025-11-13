# OCI to CheckMK Integration Project - TODO List

## Phase 1: Setup & Prototype - COMPLETED ✓

- [x] Set up project structure and dependencies (pyproject.toml with uv support)
- [x] Explore OCI SDK for ExadataCC and VMClusters data fetching
- [x] Build working prototype that fetches ExadataCC and VMCluster data
- [x] Implement automatic compartment discovery across tenancy
- [x] Create basic documentation (README, RESEARCH_NOTES)

## Phase 2: Validation & Testing (CURRENT)

- [ ] **Validate prototype with real OCI environment**
- [ ] **Test prototype against actual ExadataCC infrastructure**
- [ ] Verify all data fields are captured correctly
- [ ] Identify any missing data or edge cases
- [ ] Document any API limitations or issues discovered

## Phase 3: CheckMK Integration Research

- [ ] Research CheckMK Special Agent architecture and requirements
- [ ] Understand CheckMK agent output format (piggyback vs direct)
- [ ] Study CheckMK service discovery mechanisms
- [ ] Review CheckMK plugin development best practices
- [ ] Identify which ExadataCC metrics map to CheckMK services

## Phase 4: OCI Monitoring Integration

- [ ] Research OCI Monitoring service API for metrics
- [ ] Identify available metrics for ExadataCC infrastructure
- [ ] Identify available metrics for VM Clusters
- [ ] Implement metrics collection from OCI Monitoring
- [ ] Add time-series data aggregation (if needed)
- [ ] Handle metric pagination and rate limiting

## Phase 5: CheckMK Agent/Special Agent Development

- [ ] Design CheckMK agent output format for ExadataCC
- [ ] Implement CheckMK special agent script structure
- [ ] Create piggyback data formatter for infrastructure hierarchy
- [ ] Map OCI data to CheckMK service checks
- [ ] Implement check results with OK/WARN/CRIT/UNKNOWN states
- [ ] Add performance data (metrics) to check outputs
- [ ] Create CheckMK check plugins for custom services

## Phase 6: Production Features

- [ ] Implement proper error handling and retries
- [ ] Add structured logging (JSON format for production)
- [ ] Create configuration file support (YAML)
  - [ ] OCI authentication settings
  - [ ] Compartment filtering options
  - [ ] Metric collection settings
  - [ ] CheckMK server settings
- [ ] Add caching mechanism to avoid excessive API calls
- [ ] Implement rate limiting and backoff strategies
- [ ] Add command-line interface improvements

## Phase 7: Refactoring & Code Quality

- [ ] Refactor prototype into modular structure
  - [ ] `oci_client.py` - OCI SDK wrapper
  - [ ] `collectors.py` - Data collection logic
  - [ ] `formatters.py` - CheckMK output formatting
  - [ ] `config.py` - Configuration management
  - [ ] `main.py` - CLI entry point
- [ ] Add type hints throughout codebase
- [ ] Implement data models using dataclasses or Pydantic
- [ ] Add proper exception handling hierarchy

## Phase 8: Testing & Quality Assurance

- [ ] Write unit tests for OCI data collection
- [ ] Write unit tests for CheckMK formatting
- [ ] Create integration tests with mocked OCI responses
- [ ] Add test coverage reporting
- [ ] Set up pre-commit hooks (black, ruff)
- [ ] Add GitHub Actions or CI/CD pipeline

## Phase 9: Documentation & Deployment

- [ ] Write comprehensive README with setup instructions
- [ ] Create CheckMK integration guide
- [ ] Document OCI IAM permissions required
- [ ] Add configuration examples for different scenarios
- [ ] Create troubleshooting guide
- [ ] Write deployment guide for CheckMK server
- [ ] Add architecture diagrams

## Phase 10: End-to-End Testing & Release

- [ ] Test with CheckMK server in lab environment
- [ ] Verify service discovery works correctly
- [ ] Test alert generation and notifications
- [ ] Performance testing with large tenancies
- [ ] Create installation package/script
- [ ] Prepare release notes
- [ ] Tag first release version

## Project Goals

- Fetch inventory data from Oracle OCI (focus on ExadataCC and VMClusters)
- Collect metrics from OCI Monitoring
- Transform and share data with CheckMK monitoring system
- Use OCI Python SDK for API interactions

## Notes

- Primary focus: ExadataCC (Exadata Cloud@Customer) and VMClusters
- Integration approach: CheckMK Special Agent (recommended)
- Authentication: Multiple methods supported by OCI SDK
