# OCI to CheckMK Integration Project - TODO List

## 1. Setup & Research

- [ ] Set up project structure and dependencies (requirements.txt, virtual environment setup)
- [ ] Research and document OCI SDK authentication methods (config file, instance principal, etc.)
- [ ] Research CheckMK integration options (Special Agent, local checks, or Piggyback mechanism)
- [ ] **Explore OCI SDK for ExadataCC and VMClusters data fetching**

## 2. Core Development

- [ ] Implement OCI client initialization with authentication
- [ ] Create inventory collection module for OCI resources (Compute, DB, Network, Storage)
  - [ ] ExadataCC (Cloud@Customer) resources
  - [ ] VM Clusters
  - [ ] Other database resources
- [ ] Implement metrics collection from OCI Monitoring service
- [ ] Design and implement data transformation to CheckMK format
- [ ] Create CheckMK agent/special agent output formatter

## 3. Polish & Production-Ready

- [ ] Implement error handling and logging
- [ ] Add configuration file support (YAML/JSON for OCI regions, resources to monitor, etc.)
- [ ] Create main CLI script for running the integration

## 4. Quality & Documentation

- [ ] Write unit tests for core functionality
- [ ] Create documentation (README, setup guide, configuration examples)
- [ ] Test integration end-to-end with CheckMK instance

## Project Goals

- Fetch inventory data from Oracle OCI (focus on ExadataCC and VMClusters)
- Collect metrics from OCI Monitoring
- Transform and share data with CheckMK monitoring system
- Use OCI Python SDK for API interactions

## Notes

- Primary focus: ExadataCC (Exadata Cloud@Customer) and VMClusters
- Integration approach: CheckMK Special Agent (recommended)
- Authentication: Multiple methods supported by OCI SDK
