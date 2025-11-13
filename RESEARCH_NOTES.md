# OCI SDK Research Notes - ExadataCC and VMClusters

## Overview

This document contains research findings for using the Oracle OCI Python SDK to fetch data about Exadata Cloud@Customer (ExadataCC) and VM Clusters.

## SDK Module and Client

- **Module:** `oci.database`
- **Client:** `oci.database.DatabaseClient`
- **Installation:** `pip install oci`

## ExadataCC Architecture

```
ExadataInfrastructure (Physical hardware at customer site)
  └── VmClusterNetwork (Network configuration)
      └── VmCluster (Virtual machine cluster)
          └── Databases
```

### Key Relationship Points:
1. VmCluster requires ExadataInfrastructure - infrastructure must be created first
2. VmCluster requires VmClusterNetwork - network must be configured before VM cluster
3. One Infrastructure can host multiple VmClusters
4. VmClusters consume resources from the parent infrastructure

## Authentication Methods

### Method 1: Config File (Recommended for Development)
```python
import oci

# Load config from default location (~/.oci/config)
config = oci.config.from_file()

# Or specify custom profile
config = oci.config.from_file(
    file_location="~/.oci/config",
    profile_name="PRODUCTION"
)

# Validate configuration
oci.config.validate_config(config)

# Create database client
db_client = oci.database.DatabaseClient(config)
```

**Config File Format (~/.oci/config):**
```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaxxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaxxxxx
region=us-ashburn-1
```

### Method 2: Instance Principals (for OCI Compute Instances)
```python
import oci

# Use instance principals for authentication
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
db_client = oci.database.DatabaseClient(config={}, signer=signer)
```

## API Methods for ExadataInfrastructure

### List Operations
```python
# List all Exadata infrastructures in a compartment
list_exadata_infrastructures(
    compartment_id,
    limit=None,
    page=None,
    sort_by=None,  # "DISPLAYNAME" or "TIMECREATED"
    sort_order=None,  # "ASC" or "DESC"
    lifecycle_state=None,
    display_name=None
)
```

### Get Operations
```python
# Get specific infrastructure details
get_exadata_infrastructure(exadata_infrastructure_id)

# Get OCPU information
get_exadata_infrastructure_ocpus(exadata_infrastructure_id)

# Get unallocated resources
get_exadata_infrastructure_un_allocated_resources(exadata_infrastructure_id)
```

## API Methods for VmCluster

### List Operations
```python
# List VM clusters
list_vm_clusters(
    compartment_id,
    exadata_infrastructure_id=None,  # Filter by infrastructure
    limit=None,
    page=None,
    sort_by=None,  # "DISPLAYNAME" or "TIMECREATED"
    sort_order=None,  # "ASC" or "DESC"
    lifecycle_state=None,
    display_name=None
)
```

### Get Operations
```python
# Get VM cluster details
get_vm_cluster(vm_cluster_id)

# Get IORM configuration
get_vm_cluster_iorm_config(vm_cluster_id)

# List VM cluster networks
list_vm_cluster_networks(
    exadata_infrastructure_id,
    compartment_id,
    limit=None,
    page=None,
    sort_by=None,
    sort_order=None,
    lifecycle_state=None,
    display_name=None
)

# Get VM cluster network details
get_vm_cluster_network(exadata_infrastructure_id, vm_cluster_network_id)
```

### Patch Information
```python
# List available patches
list_vm_cluster_patches(vm_cluster_id)

# Get specific patch details
get_vm_cluster_patch(vm_cluster_id, patch_id)

# List available updates
list_vm_cluster_updates(vm_cluster_id)
```

## ExadataInfrastructure Data Fields

### Identity & Status
- `id` - Infrastructure OCID
- `compartment_id` - Compartment OCID
- `display_name` - User-friendly name
- `lifecycle_state` - ACTIVE, CREATING, UPDATING, DELETING, FAILED, etc.
- `lifecycle_details` - Additional state information
- `availability_domain` - AD location
- `time_created` - Creation timestamp

### Hardware Configuration
- `shape` - Infrastructure shape
- `compute_count` - Number of compute servers
- `storage_count` - Number of storage servers
- `additional_compute_count` - Additional compute servers
- `additional_storage_count` - Additional storage servers
- `database_server_type` - DB server type
- `storage_server_type` - Storage server type
- `compute_model` - ECPU or OCPU

### Resource Specifications
- `cpus_enabled` - Enabled CPU cores
- `max_cpu_count` - Maximum CPU capacity
- `memory_size_in_gbs` - Current memory allocation
- `max_memory_in_gbs` - Maximum memory capacity
- `db_node_storage_size_in_gbs` - DB node storage
- `data_storage_size_in_tbs` - Data storage capacity
- `max_data_storage_in_t_bs` - Maximum data storage

### Network Configuration
- `admin_network_cidr` - Admin network CIDR
- `infini_band_network_cidr` - InfiniBand CIDR
- `netmask` - Network mask
- `gateway` - Gateway address
- `corporate_proxy` - Proxy configuration
- `dns_server` - List of DNS servers (max 3)
- `ntp_server` - List of NTP servers (max 3)

### Software Versions
- `storage_server_version` - Storage server software version
- `db_server_version` - DB server software version
- `monthly_db_server_version` - Monthly DB server version

### Infrastructure Details
- `rack_serial_number` - Rack serial number
- `csi_number` - CSI number
- `time_zone` - Time zone
- `is_multi_rack_deployment` - Multi-rack flag
- `is_cps_offline_report_enabled` - CPS offline reporting flag

### Maintenance
- `last_maintenance_run_id` - Last maintenance run OCID
- `next_maintenance_run_id` - Next maintenance run OCID
- `maintenance_window` - Maintenance window configuration
- `maintenance_slo_status` - OK or DEGRADED

### Tags
- `freeform_tags` - User-defined tags (dict)
- `defined_tags` - Oracle-managed tags (dict)
- `system_tags` - System-generated tags (dict)

## VmCluster Data Fields

### Identity & Status
- `id` - VM cluster OCID
- `compartment_id` - Compartment OCID
- `display_name` - User-friendly name
- `lifecycle_state` - PROVISIONING, AVAILABLE, UPDATING, TERMINATING, TERMINATED, FAILED, MAINTENANCE_IN_PROGRESS
- `lifecycle_details` - Additional state info
- `time_created` - Creation timestamp
- `availability_domain` - AD location

### Infrastructure References
- `exadata_infrastructure_id` - Parent infrastructure OCID
- `vm_cluster_network_id` - Network OCID
- `shape` - Infrastructure shape
- `time_zone` - Time zone

### Software Configuration
- `gi_version` - Grid Infrastructure version
- `gi_software_image_id` - GI software image OCID
- `system_version` - Operating system version

### Resource Specifications
- `cpus_enabled` - Enabled CPU cores
- `ocpus_enabled` - Enabled OCPU cores
- `memory_size_in_gbs` - Memory allocation
- `db_node_storage_size_in_gbs` - Node storage
- `data_storage_size_in_tbs` - Data storage in TB
- `data_storage_size_in_gbs` - Data storage in GB

### Configuration
- `is_local_backup_enabled` - Local backup flag
- `is_sparse_diskgroup_enabled` - Sparse diskgroup flag
- `license_model` - LICENSE_INCLUDED or BRING_YOUR_OWN_LICENSE
- `ssh_public_keys` - List of SSH public keys
- `db_servers` - List of database server OCIDs
- `vm_cluster_type` - REGULAR or DEVELOPER
- `storage_management_type` - ASM or EXASCALE
- `compute_model` - ECPU or OCPU

### Advanced Configuration
- `data_collection_options` - Data collection config (diagnostics, health monitoring, incident logs)
- `file_system_configuration_details` - File system details
- `cloud_automation_update_details` - Automation configuration
- `exascale_db_storage_vault_id` - Storage vault OCID

### Maintenance
- `last_patch_history_entry_id` - Last patch OCID

### Tags
- `freeform_tags` - User tags (dict)
- `defined_tags` - Oracle tags (dict)
- `system_tags` - System tags (dict)

## Important Considerations

### 1. Lifecycle States
Resources can be in various states. Always check `lifecycle_state`:
- PROVISIONING - Being created
- AVAILABLE - Ready for use
- UPDATING - Being modified
- TERMINATING - Being deleted
- TERMINATED - Deleted
- FAILED - Operation failed
- MAINTENANCE_IN_PROGRESS - Under maintenance

### 2. Pagination
Most list operations support pagination for large result sets:
```python
all_clusters = []
page = None
while True:
    response = db_client.list_vm_clusters(
        compartment_id=compartment_id,
        page=page
    )
    all_clusters.extend(response.data)
    page = response.next_page
    if not page:
        break
```

### 3. Error Handling
Always wrap API calls in try-except blocks:
```python
try:
    response = db_client.get_vm_cluster(vm_cluster_id)
except oci.exceptions.ServiceError as e:
    print(f"Error: {e.status} - {e.message}")
except oci.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 4. IAM Permissions Required
```
Allow group ExadataAdmins to manage exadata-infrastructures in compartment ExaCC
Allow group ExadataAdmins to manage vm-clusters in compartment ExaCC
Allow group ExadataAdmins to read vm-cluster-networks in compartment ExaCC
```

### 5. Resource Dependencies
- ExadataInfrastructure must be ACTIVE before creating VmCluster
- VmClusterNetwork must be VALIDATED before creating VmCluster
- Cannot delete infrastructure with active VM clusters

### 6. Rate Limiting
OCI has rate limits. Use retry strategy:
```python
from oci.retry import DEFAULT_RETRY_STRATEGY

db_client = oci.database.DatabaseClient(
    config,
    retry_strategy=DEFAULT_RETRY_STRATEGY
)
```

### 7. Regional Resources
Exadata resources are regional. Ensure config uses correct region.

## Example Code Pattern

### Basic Pattern for Listing Resources
```python
#!/usr/bin/env python3
import oci
import sys

def list_exadata_resources(compartment_id):
    # Load configuration
    config = oci.config.from_file()
    oci.config.validate_config(config)

    # Create database client
    db_client = oci.database.DatabaseClient(config)

    try:
        # List Exadata infrastructures
        infra_response = db_client.list_exadata_infrastructures(
            compartment_id=compartment_id,
            sort_by="DISPLAYNAME",
            sort_order="ASC"
        )

        for infra in infra_response.data:
            print(f"Infrastructure: {infra.display_name}")
            print(f"  OCID: {infra.id}")
            print(f"  State: {infra.lifecycle_state}")
            print(f"  CPUs: {infra.cpus_enabled}/{infra.max_cpu_count}")
            print(f"  Memory: {infra.memory_size_in_gbs} GB")
            print(f"  Storage: {infra.data_storage_size_in_tbs} TB")

            # List VM clusters for this infrastructure
            vm_response = db_client.list_vm_clusters(
                compartment_id=compartment_id,
                exadata_infrastructure_id=infra.id
            )

            for cluster in vm_response.data:
                print(f"  VM Cluster: {cluster.display_name}")
                print(f"    OCID: {cluster.id}")
                print(f"    State: {cluster.lifecycle_state}")
                print(f"    GI Version: {cluster.gi_version}")
                print(f"    CPUs: {cluster.cpus_enabled}")
                print(f"    Memory: {cluster.memory_size_in_gbs} GB")

    except oci.exceptions.ServiceError as e:
        print(f"Service Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <compartment_ocid>")
        sys.exit(1)

    compartment_id = sys.argv[1]
    list_exadata_resources(compartment_id)
```

## Next Steps for Integration

1. Determine which metrics are needed for CheckMK
2. Decide on data transformation format
3. Implement CheckMK Special Agent output format
4. Add OCI Monitoring service integration for metrics
5. Implement caching/polling strategy
6. Add configuration file for regions, compartments, resources to monitor
