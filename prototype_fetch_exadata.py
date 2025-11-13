#!/usr/bin/env python3
"""
Prototype script to fetch ExadataCC infrastructure and VM Cluster data from OCI.

This script demonstrates how to:
1. Authenticate with OCI using config file
2. Discover all compartments in the tenancy
3. List all Exadata infrastructures across all compartments
4. Get detailed information about each infrastructure
5. List VM clusters for each infrastructure
6. Display the data in a structured format

Usage:
    python prototype_fetch_exadata.py [--profile <profile_name>] [--output <output_file>]

Examples:
    # Scan all compartments in the tenancy
    python prototype_fetch_exadata.py

    # Use a specific OCI config profile
    python prototype_fetch_exadata.py --profile PRODUCTION

    # Specify custom output file
    python prototype_fetch_exadata.py --output my_data.json
"""

import oci
import sys
import json
import argparse
from typing import Dict, List, Optional


class ExadataDataFetcher:
    """Fetches ExadataCC infrastructure and VM cluster data from OCI."""

    def __init__(self, config_file: Optional[str] = None, profile: str = "DEFAULT"):
        """
        Initialize the ExadataDataFetcher.

        Args:
            config_file: Path to OCI config file (default: ~/.oci/config)
            profile: Profile name to use from config file
        """
        if config_file:
            self.config = oci.config.from_file(file_location=config_file, profile_name=profile)
        else:
            self.config = oci.config.from_file(profile_name=profile)

        # Validate configuration
        oci.config.validate_config(self.config)

        # Create clients
        self.db_client = oci.database.DatabaseClient(self.config)
        self.identity_client = oci.identity.IdentityClient(self.config)

        # Get tenancy ID from config
        self.tenancy_id = self.config["tenancy"]

    def list_all_compartments(self) -> List[Dict]:
        """
        List all compartments in the tenancy, including nested compartments.

        Returns:
            List of compartment objects with id, name, and lifecycle_state
        """
        try:
            print(f"Discovering compartments in tenancy: {self.tenancy_id}")

            all_compartments = []

            # Add root compartment (tenancy itself)
            tenancy = self.identity_client.get_tenancy(tenancy_id=self.tenancy_id).data
            all_compartments.append({
                "id": tenancy.id,
                "name": tenancy.name,
                "lifecycle_state": "ACTIVE",
                "is_root": True
            })

            # List all compartments recursively
            def list_compartments_recursive(parent_compartment_id):
                page = None
                while True:
                    response = self.identity_client.list_compartments(
                        compartment_id=parent_compartment_id,
                        compartment_id_in_subtree=True,
                        access_level="ACCESSIBLE",
                        page=page
                    )

                    for compartment in response.data:
                        # Only include ACTIVE compartments
                        if compartment.lifecycle_state == "ACTIVE":
                            all_compartments.append({
                                "id": compartment.id,
                                "name": compartment.name,
                                "lifecycle_state": compartment.lifecycle_state,
                                "is_root": False
                            })

                    page = response.next_page
                    if not page:
                        break

            list_compartments_recursive(self.tenancy_id)

            print(f"Found {len(all_compartments)} accessible compartment(s)\n")
            return all_compartments

        except oci.exceptions.ServiceError as e:
            print(f"Service Error: {e.status} - {e.message}")
            raise

    def list_exadata_infrastructures(self, compartment_id: str) -> List[Dict]:
        """
        List all Exadata infrastructures in a compartment.

        Args:
            compartment_id: OCI compartment OCID

        Returns:
            List of ExadataInfrastructure objects as dictionaries
        """
        try:
            all_infrastructures = []
            page = None

            while True:
                response = self.db_client.list_exadata_infrastructures(
                    compartment_id=compartment_id,
                    sort_by="DISPLAYNAME",
                    sort_order="ASC",
                    page=page
                )

                all_infrastructures.extend(response.data)
                page = response.next_page

                if not page:
                    break

            return all_infrastructures

        except oci.exceptions.ServiceError as e:
            print(f"Service Error: {e.status} - {e.message}")
            raise
        except oci.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise

    def get_exadata_infrastructure_details(self, exadata_infrastructure_id: str) -> Dict:
        """
        Get detailed information about an Exadata infrastructure.

        Args:
            exadata_infrastructure_id: ExadataInfrastructure OCID

        Returns:
            ExadataInfrastructure object with additional resource info
        """
        try:
            # Get basic infrastructure details
            infra = self.db_client.get_exadata_infrastructure(
                exadata_infrastructure_id=exadata_infrastructure_id
            ).data

            # Get OCPU information
            try:
                ocpu_info = self.db_client.get_exadata_infrastructure_ocpus(
                    exadata_infrastructure_id=exadata_infrastructure_id
                ).data
            except:
                ocpu_info = None

            # Get unallocated resources
            try:
                unallocated = self.db_client.get_exadata_infrastructure_un_allocated_resources(
                    exadata_infrastructure_id=exadata_infrastructure_id
                ).data
            except:
                unallocated = None

            return {
                "infrastructure": infra,
                "ocpu_info": ocpu_info,
                "unallocated_resources": unallocated
            }

        except oci.exceptions.ServiceError as e:
            print(f"Service Error fetching infrastructure details: {e.status} - {e.message}")
            raise

    def list_vm_clusters(self, compartment_id: str, exadata_infrastructure_id: Optional[str] = None) -> List[Dict]:
        """
        List VM clusters in a compartment, optionally filtered by infrastructure.

        Args:
            compartment_id: OCI compartment OCID
            exadata_infrastructure_id: Optional infrastructure OCID to filter by

        Returns:
            List of VmCluster objects
        """
        try:
            all_clusters = []
            page = None

            while True:
                response = self.db_client.list_vm_clusters(
                    compartment_id=compartment_id,
                    exadata_infrastructure_id=exadata_infrastructure_id,
                    sort_by="DISPLAYNAME",
                    sort_order="ASC",
                    page=page
                )

                all_clusters.extend(response.data)
                page = response.next_page

                if not page:
                    break

            return all_clusters

        except oci.exceptions.ServiceError as e:
            print(f"Service Error: {e.status} - {e.message}")
            raise

    def get_vm_cluster_details(self, vm_cluster_id: str) -> Dict:
        """
        Get detailed information about a VM cluster.

        Args:
            vm_cluster_id: VmCluster OCID

        Returns:
            VmCluster object with additional info
        """
        try:
            # Get basic cluster details
            cluster = self.db_client.get_vm_cluster(vm_cluster_id=vm_cluster_id).data

            # Get IORM configuration
            try:
                iorm_config = self.db_client.get_vm_cluster_iorm_config(
                    vm_cluster_id=vm_cluster_id
                ).data
            except:
                iorm_config = None

            # List available patches (limit to 5 most recent)
            try:
                patches = self.db_client.list_vm_cluster_patches(
                    vm_cluster_id=vm_cluster_id
                ).data[:5]
            except:
                patches = []

            return {
                "cluster": cluster,
                "iorm_config": iorm_config,
                "patches": patches
            }

        except oci.exceptions.ServiceError as e:
            print(f"Service Error fetching VM cluster details: {e.status} - {e.message}")
            raise

    def fetch_all_data(self) -> Dict:
        """
        Fetch all ExadataCC data from the tenancy.

        Scans all compartments in the tenancy for ExadataCC resources.

        Returns:
            Dictionary containing all infrastructure and VM cluster data organized by compartment
        """
        result = {
            "tenancy_id": self.tenancy_id,
            "compartments": []
        }

        # Get all compartments in the tenancy
        compartments_to_scan = self.list_all_compartments()

        # Scan each compartment for Exadata resources
        total_infrastructures = 0
        total_vm_clusters = 0

        for compartment in compartments_to_scan:
            comp_id = compartment["id"]
            comp_name = compartment["name"]

            print(f"Scanning compartment: {comp_name} ({comp_id})")

            # Get all infrastructures in this compartment
            infrastructures = self.list_exadata_infrastructures(comp_id)

            if not infrastructures:
                print(f"  No Exadata infrastructures found\n")
                continue

            print(f"  Found {len(infrastructures)} infrastructure(s)")
            total_infrastructures += len(infrastructures)

            compartment_data = {
                "compartment_id": comp_id,
                "compartment_name": comp_name,
                "infrastructures": []
            }

            for infra in infrastructures:
                print(f"  Processing infrastructure: {infra.display_name}")

                # Get detailed infrastructure info
                infra_details = self.get_exadata_infrastructure_details(infra.id)

                # Get VM clusters for this infrastructure
                vm_clusters = self.list_vm_clusters(
                    compartment_id=comp_id,
                    exadata_infrastructure_id=infra.id
                )

                # Get detailed info for each VM cluster
                vm_clusters_details = []
                for cluster in vm_clusters:
                    print(f"    Processing VM cluster: {cluster.display_name}")
                    cluster_details = self.get_vm_cluster_details(cluster.id)
                    vm_clusters_details.append(cluster_details)
                    total_vm_clusters += 1

                compartment_data["infrastructures"].append({
                    "details": infra_details,
                    "vm_clusters": vm_clusters_details
                })

            result["compartments"].append(compartment_data)
            print()

        print(f"\nTotal: {total_infrastructures} infrastructure(s), {total_vm_clusters} VM cluster(s)\n")
        return result


def format_infrastructure_summary(infra_data: Dict) -> str:
    """Format infrastructure data for display."""
    infra = infra_data["infrastructure"]
    ocpu_info = infra_data.get("ocpu_info")
    unallocated = infra_data.get("unallocated_resources")

    output = []
    output.append("=" * 80)
    output.append(f"INFRASTRUCTURE: {infra.display_name}")
    output.append("=" * 80)
    output.append(f"OCID: {infra.id}")
    output.append(f"State: {infra.lifecycle_state}")
    output.append(f"Shape: {infra.shape}")
    output.append(f"Availability Domain: {infra.availability_domain}")
    output.append(f"Created: {infra.time_created}")

    output.append("\nHARDWARE:")
    output.append(f"  Compute Servers: {infra.compute_count}")
    output.append(f"  Storage Servers: {infra.storage_count}")

    output.append("\nRESOURCES:")
    output.append(f"  CPUs: {infra.cpus_enabled} / {infra.max_cpu_count}")
    output.append(f"  Memory: {infra.memory_size_in_gbs} GB / {infra.max_memory_in_gbs} GB")
    output.append(f"  DB Node Storage: {infra.db_node_storage_size_in_gbs} GB")
    output.append(f"  Data Storage: {infra.data_storage_size_in_tbs} TB / {infra.max_data_storage_in_t_bs} TB")

    if ocpu_info:
        output.append("\nOCPU INFO:")
        output.append(f"  Total: {ocpu_info.total_cpu_count}")
        output.append(f"  Consumed: {ocpu_info.consumed_cpu_count}")

    if unallocated:
        output.append("\nUNALLOCATED:")
        output.append(f"  Available CPUs: {unallocated.available_cpus}")

    output.append("\nNETWORK:")
    output.append(f"  Admin CIDR: {infra.admin_network_cidr}")
    output.append(f"  InfiniBand CIDR: {infra.infini_band_network_cidr}")
    output.append(f"  Gateway: {infra.gateway}")

    output.append("\nSOFTWARE:")
    output.append(f"  Storage Server Version: {infra.storage_server_version}")
    output.append(f"  DB Server Version: {infra.db_server_version}")

    output.append("\nMAINTENANCE:")
    if infra.maintenance_slo_status:
        output.append(f"  SLO Status: {infra.maintenance_slo_status}")

    return "\n".join(output)


def format_vm_cluster_summary(cluster_data: Dict) -> str:
    """Format VM cluster data for display."""
    cluster = cluster_data["cluster"]
    iorm_config = cluster_data.get("iorm_config")

    output = []
    output.append("\n  " + "-" * 76)
    output.append(f"  VM CLUSTER: {cluster.display_name}")
    output.append("  " + "-" * 76)
    output.append(f"  OCID: {cluster.id}")
    output.append(f"  State: {cluster.lifecycle_state}")
    output.append(f"  Shape: {cluster.shape}")
    output.append(f"  Cluster Type: {cluster.vm_cluster_type}")

    output.append("\n  SOFTWARE:")
    output.append(f"    Grid Infrastructure: {cluster.gi_version}")
    output.append(f"    System Version: {cluster.system_version}")

    output.append("\n  RESOURCES:")
    output.append(f"    CPUs Enabled: {cluster.cpus_enabled}")
    output.append(f"    OCPUs Enabled: {cluster.ocpus_enabled}")
    output.append(f"    Memory: {cluster.memory_size_in_gbs} GB")
    output.append(f"    DB Node Storage: {cluster.db_node_storage_size_in_gbs} GB")
    output.append(f"    Data Storage: {cluster.data_storage_size_in_tbs} TB")

    output.append("\n  CONFIGURATION:")
    output.append(f"    License Model: {cluster.license_model}")
    output.append(f"    Local Backup: {cluster.is_local_backup_enabled}")
    output.append(f"    Sparse Diskgroup: {cluster.is_sparse_diskgroup_enabled}")
    output.append(f"    Storage Management: {cluster.storage_management_type}")
    output.append(f"    Compute Model: {cluster.compute_model}")

    if cluster.db_servers:
        output.append(f"\n  DATABASE SERVERS: {len(cluster.db_servers)}")

    if iorm_config:
        output.append(f"\n  IORM:")
        output.append(f"    State: {iorm_config.lifecycle_state}")
        output.append(f"    Objective: {iorm_config.objective}")

    return "\n".join(output)


def main():
    """Main function to run the prototype."""
    parser = argparse.ArgumentParser(
        description="Fetch ExadataCC infrastructure and VM Cluster data from all compartments in OCI tenancy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan all compartments in the tenancy
  python prototype_fetch_exadata.py

  # Use a specific OCI config profile
  python prototype_fetch_exadata.py --profile PRODUCTION

  # Specify custom output file
  python prototype_fetch_exadata.py --output my_data.json
        """
    )

    parser.add_argument(
        "--profile",
        "-p",
        help="OCI config profile to use (default: DEFAULT)",
        default="DEFAULT"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file name (default: exadata_data.json)",
        default="exadata_data.json"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("OCI ExadataCC Data Fetcher - Prototype")
    print("=" * 80)
    print()

    try:
        # Initialize fetcher
        fetcher = ExadataDataFetcher(profile=args.profile)

        # Fetch all data from all compartments
        data = fetcher.fetch_all_data()

        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()

        if not data["compartments"]:
            print("No Exadata infrastructures found.")
            return

        # Display results
        for compartment_data in data["compartments"]:
            print(f"\nCOMPARTMENT: {compartment_data['compartment_name']}")
            print(f"OCID: {compartment_data['compartment_id']}")
            print("=" * 80)

            for infra_data in compartment_data["infrastructures"]:
                print(format_infrastructure_summary(infra_data["details"]))

                if infra_data["vm_clusters"]:
                    print(f"\n  VM CLUSTERS: {len(infra_data['vm_clusters'])}")
                    for cluster_data in infra_data["vm_clusters"]:
                        print(format_vm_cluster_summary(cluster_data))
                else:
                    print("\n  No VM clusters found for this infrastructure.")

                print("\n")

        # Also save raw data to JSON for inspection
        output_file = args.output
        print(f"Saving raw data to {output_file}...")

        # Convert OCI objects to dict for JSON serialization
        json_data = {
            "tenancy_id": data["tenancy_id"],
            "compartments": []
        }

        for compartment_data in data["compartments"]:
            compartment_dict = {
                "compartment_id": compartment_data["compartment_id"],
                "compartment_name": compartment_data["compartment_name"],
                "infrastructures": []
            }

            for infra_data in compartment_data["infrastructures"]:
                infra_dict = {
                    "infrastructure": {
                        "id": infra_data["details"]["infrastructure"].id,
                        "display_name": infra_data["details"]["infrastructure"].display_name,
                        "lifecycle_state": infra_data["details"]["infrastructure"].lifecycle_state,
                        "shape": infra_data["details"]["infrastructure"].shape,
                        "compute_count": infra_data["details"]["infrastructure"].compute_count,
                        "storage_count": infra_data["details"]["infrastructure"].storage_count,
                        "cpus_enabled": infra_data["details"]["infrastructure"].cpus_enabled,
                        "max_cpu_count": infra_data["details"]["infrastructure"].max_cpu_count,
                        "memory_size_in_gbs": infra_data["details"]["infrastructure"].memory_size_in_gbs,
                        "data_storage_size_in_tbs": infra_data["details"]["infrastructure"].data_storage_size_in_tbs,
                    },
                    "vm_clusters": []
                }

                for cluster_data in infra_data["vm_clusters"]:
                    cluster_dict = {
                        "id": cluster_data["cluster"].id,
                        "display_name": cluster_data["cluster"].display_name,
                        "lifecycle_state": cluster_data["cluster"].lifecycle_state,
                        "gi_version": cluster_data["cluster"].gi_version,
                        "cpus_enabled": cluster_data["cluster"].cpus_enabled,
                        "memory_size_in_gbs": cluster_data["cluster"].memory_size_in_gbs,
                        "data_storage_size_in_tbs": cluster_data["cluster"].data_storage_size_in_tbs,
                    }
                    infra_dict["vm_clusters"].append(cluster_dict)

                compartment_dict["infrastructures"].append(infra_dict)

            json_data["compartments"].append(compartment_dict)

        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"Data saved successfully!")

    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
