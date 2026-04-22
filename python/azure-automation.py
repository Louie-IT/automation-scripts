#!/usr/bin/env python3
"""
Azure day-to-day automation helper.

Capabilities:
- inventory-vms: List VMs in a subscription (optionally by RG)
- start-vm: Start a specific VM
- stop-vm: Stop (deallocate) a specific VM
- list-rgs: List Resource Groups in the subscription

Usage examples:
  python3 automation-scripts/python/azure-automation.py inventory-vms \
      --subscription-id <SUB_ID> [--resource-group <RG>] [--verbose]

  python3 automation-scripts/python/azure-automation.py start-vm \
      --subscription-id <SUB_ID> --resource-group <RG> --name <VM_NAME>

  python3 automation-scripts/python/azure-automation.py stop-vm \
      --subscription-id <SUB_ID> --resource-group <RG> --name <VM_NAME>

  python3 automation-scripts/python/azure-automation.py list-rgs \
      --subscription-id <SUB_ID>

Prerequisites:
  - Azure credentials available via DefaultAzureCredential
  - Authenticate locally with: az login (or set up a service principal in CI)
"""

import argparse
import json
import sys
from typing import Dict, List, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import HttpResponseError


def get_clients(subscription_id: str):
    """
    Build Azure clients using DefaultAzureCredential.
    """
    credential = DefaultAzureCredential()
    compute = ComputeManagementClient(credential, subscription_id)
    resources = ResourceManagementClient(credential, subscription_id)
    return compute, resources


def list_vms(subscription_id: str, resource_group: Optional[str] = None, verbose: bool = False) -> List[Dict]:
    compute, _ = get_clients(subscription_id)
    vms_out: List[Dict] = []

    try:
        if resource_group:
            vms = compute.virtual_machines.list(resource_group)
        else:
            vms = compute.virtual_machines.list_all()

        for vm in vms:
            # Resolve RG and location
            rg = resource_group if resource_group else vm.id.split("/")[4]
            location = vm.location

            # Fetch instance view to get power state
            try:
                inst_view = compute.virtual_machines.instance_view(rg, vm.name)
                power_state = None
                for status in inst_view.statuses:
                    if status.code.startswith("PowerState"):
                        power_state = status.display_status
                        break
            except HttpResponseError:
                power_state = "Unknown"

            entry = {
                "name": vm.name,
                "resource_group": rg,
                "location": location,
                "power_state": power_state or "Unknown",
            }
            vms_out.append(entry)

        if verbose:
            print(json.dumps(vms_out, indent=2))
        else:
            # Compact output
            for vm in vms_out:
                print(f"{vm['name']}\t{vm['resource_group']}\t{vm['location']}\t{vm['power_state']}")
        return vms_out

    except HttpResponseError as e:
        print(f"Error listing VMs: {e}", file=sys.stderr)
        return []


def start_vm(subscription_id: str, resource_group: str, name: str):
    compute, _ = get_clients(subscription_id)
    print(f"Starting VM '{name}' in RG '{resource_group}'...")
    poller = compute.virtual_machines.begin_start(resource_group, name)
    poller.result()  # wait for completion
    print("Start complete.")


def stop_vm(subscription_id: str, resource_group: str, name: str):
    compute, _ = get_clients(subscription_id)
    print(f"Stopping (deallocating) VM '{name}' in RG '{resource_group}'...")
    poller = compute.virtual_machines.begin_deallocate(resource_group, name)
    poller.result()  # wait for completion
    print("Stop complete.")


def list_resource_groups(subscription_id: str, verbose: bool = False) -> List[Dict]:
    _, resources = get_clients(subscription_id)
    groups: List[Dict] = []
    for rg in resources.resource_groups.list():
        item = {
            "name": rg.name,
            "location": rg.location,
            "id": rg.id,
        }
        groups.append(item)
    if verbose:
        print(json.dumps(groups, indent=2))
    else:
        for g in groups:
            print(f"{g['name']}\t{g['location']}")
    return groups


def main():
    parser = argparse.ArgumentParser(description="Azure automation helpers (inventory and VM lifecycle).")
    subparsers = parser.add_subparsers(dest="command")

    # inventory-vms
    p_inv = subparsers.add_parser("inventory-vms", help="List VMs in a subscription.")
    p_inv.add_argument("--subscription-id", required=True, help="Azure Subscription ID.")
    p_inv.add_argument("--resource-group", required=False, help="Optional: filter by Resource Group.")
    p_inv.add_argument("--verbose", action="store_true", help="Verbose JSON output.")

    # start-vm
    p_start = subparsers.add_parser("start-vm", help="Start a VM.")
    p_start.add_argument("--subscription-id", required=True)
    p_start.add_argument("--resource-group", required=True)
    p_start.add_argument("--name", required=True)

    # stop-vm
    p_stop = subparsers.add_parser("stop-vm", help="Stop a VM.")
    p_stop.add_argument("--subscription-id", required=True)
    p_stop.add_argument("--resource-group", required=True)
    p_stop.add_argument("--name", required=True)

    # list-rgs
    p_rgs = subparsers.add_parser("list-rgs", help="List Resource Groups.")
    p_rgs.add_argument("--subscription-id", required=True)
    p_rgs.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "inventory-vms":
        list_vms(args.subscription_id, args.resource_group, args.verbose)
    elif args.command == "start-vm":
        start_vm(args.subscription_id, args.resource_group, args.name)
    elif args.command == "stop-vm":
        stop_vm(args.subscription_id, args.resource_group, args.name)
    elif args.command == "list-rgs":
        list_resource_groups(args.subscription_id, args.verbose)
    else:
        print("Unknown command", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
