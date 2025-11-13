# OCI to CheckMK Integration

This project provides integration between Oracle Cloud Infrastructure (OCI) and CheckMK monitoring system, with a focus on Exadata Cloud@Customer (ExadataCC) and VM Clusters.

## Project Status

**Phase 1 Complete:** Working prototype that automatically discovers and scans all compartments in an OCI tenancy for ExadataCC infrastructure and VM Clusters.

**Current Phase:** Validation and testing with real OCI environments.

See [TODO.md](TODO.md) for complete project roadmap.

## Installation

### Using uv (recommended)

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Configuration

Configure OCI credentials in `~/.oci/config`:

```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaxxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaxxxxx
region=us-ashburn-1
```

## Usage

### Prototype Script

Run the prototype to fetch ExadataCC infrastructure and VM Cluster data from all compartments in your tenancy:

```bash
# Scan all compartments in the tenancy
python prototype_fetch_exadata.py

# Use a specific OCI config profile
python prototype_fetch_exadata.py --profile PRODUCTION

# Specify custom output file
python prototype_fetch_exadata.py --output my_data.json
```

**Command-line Options:**
- `--profile, -p` - OCI config profile to use (default: DEFAULT)
- `--output, -o` - Output JSON file name (default: exadata_data.json)

The script will:
- Automatically discover all compartments in your tenancy
- Scan each compartment for Exadata infrastructures
- Fetch detailed information for each infrastructure (hardware, resources, network, maintenance)
- List all VM clusters for each infrastructure
- Gather VM cluster details (software versions, IORM config, available patches)
- Display structured output organized by compartment
- Export complete data to JSON file

## IAM Permissions Required

Your OCI user/group needs the following permissions:

```
# For compartment discovery
Allow group ExadataAdmins to read compartments in tenancy

# For ExadataCC resources (apply to tenancy or specific compartments)
Allow group ExadataAdmins to read exadata-infrastructures in tenancy
Allow group ExadataAdmins to read vm-clusters in tenancy
Allow group ExadataAdmins to read vm-cluster-networks in tenancy
```

**Note:** The script requires read-only access to discover compartments and list ExadataCC resources. Using `read` instead of `manage` is more secure if you only need monitoring capabilities.

## Documentation

- [TODO.md](TODO.md) - Project roadmap and task list
- [RESEARCH_NOTES.md](RESEARCH_NOTES.md) - Detailed research findings about OCI SDK and ExadataCC

## Requirements

- Python 3.8+
- OCI Python SDK (`oci>=2.163.0`)
- Valid OCI credentials with appropriate permissions

## Development

Install with dev dependencies:

```bash
uv pip install -e ".[dev]"
```

This includes:
- pytest - Testing framework
- pytest-cov - Code coverage
- black - Code formatter
- ruff - Linter

Run tests:
```bash
pytest
```

Format code:
```bash
black .
```

Lint code:
```bash
ruff check .
```

## Features

### Current (Prototype)
- ✅ Automatic compartment discovery across entire tenancy
- ✅ ExadataCC infrastructure inventory collection
- ✅ VM Cluster inventory collection
- ✅ Detailed resource information (CPU, memory, storage)
- ✅ OCPU and unallocated resource tracking
- ✅ IORM configuration details
- ✅ Patch information for VM clusters
- ✅ JSON export for further processing
- ✅ Support for multiple OCI config profiles

### Planned
- 🔜 OCI Monitoring metrics collection
- 🔜 CheckMK Special Agent integration
- 🔜 Service discovery and check plugins
- 🔜 Alert thresholds and notifications
- 🔜 Configuration file support (YAML)
- 🔜 Caching and rate limiting
- 🔜 Comprehensive error handling and logging

## Next Steps

1. **Validate** the prototype with your OCI environment
2. **Research** CheckMK Special Agent architecture
3. **Implement** OCI Monitoring metrics collection
4. **Develop** CheckMK integration

See [TODO.md](TODO.md) for the complete roadmap.
