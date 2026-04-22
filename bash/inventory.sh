#!/usr/bin/env bash
set -euo pipefail

echo "Azure Resource Inventory (sample)"
az resource list --query "[].{name:name, type:type, location:location, group:resourceGroup}" -o table > inventory.txt
echo "Inventory written to inventory.txt"
