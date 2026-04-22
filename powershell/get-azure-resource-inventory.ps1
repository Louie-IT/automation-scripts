# Get a full list of Azure resources quickly.

param(
    [switch]$Verbose = $false
)

$resources = Get-AzResource

$report = foreach ($r in $resources) {
    [PSCustomObject]@{
        Name           = $r.Name
        ResourceGroup  = $r.ResourceGroupName
        ResourceType   = $r.ResourceType
        Subscription   = $r.SubscriptionId
        Location       = $r.Location
        }
    }

$report | ConvertTo-Csv -NoTypeInformation | Out-File "inventory.csv"

    if ($Verbose) {

        $report | Format-Table
    }

    Write-Host "Inventory written to inventory.csv"
