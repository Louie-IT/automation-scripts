---

# **Automation Scripts for Azure**

A small collection of practical automation scripts written in **PowerShell**, **Bash**, and **Python**. These examples reflect common day‑to‑day tasks when working with Azure - such as gathering resource inventories, managing virtual machines, and interacting with subscriptions and resource groups.

The scripts are lightweight, easy to run, and demonstrate different approaches to Azure automation across multiple tools and environments.

---

## **What’s Included**

### **PowerShell**
**`automation-scripts/powershell/get-azure-resource-inventory.ps1`**  
Lists Azure resources—optionally filtered by Resource Group—with details such as:
- Name  
- Type  
- Location  
- Power state (for VMs)

Outputs a clean table by default, with `--verbose` providing JSON.

---

### **Bash**
**`automation-scripts/bash/inventory.sh`**  
A quick az CLI–based resource inventory script that prints a readable table and writes results to `inventory.txt`.

---

### **Python**
**`automation-scripts/python/azure-automation.py`**  
A small Python CLI tool that supports:

- `inventory-vms` - list VMs (optionally by Resource Group)  
- `start-vm` - start a VM  
- `stop-vm` - stop a VM  
- `list-rgs` - list all Resource Groups  

It uses **DefaultAzureCredential**, so it works seamlessly with:
- `az login` during local development  
- Service principals in CI environments  

Output is tab‑delimited by default, with JSON available via `--verbose`.

---

## **Prerequisites**

- **Python 3.8+**  
  Install dependencies:  
  ```
  pip install azure-identity azure-mgmt-resource azure-mgmt-compute
  ```
- **PowerShell 7+ (pwsh)**
- **Azure CLI** (optional but helpful for local authentication)  
  ```
  az login
  ```
- **Authentication**  
  Scripts rely on `DefaultAzureCredential`, which supports:
  - Local dev via `az login`
  - Environment‑based credentials in CI

---

## **What to Expect**

- **PowerShell:**  
  Table output by default; JSON with `--verbose`.

- **Bash:**  
  A simple table plus an `inventory.txt` file.

- **Python:**  
  - VM inventory: tab‑delimited list or JSON  
  - VM start/stop: progress messages and confirmation  
  - Resource Groups: simple list or JSON  

---
