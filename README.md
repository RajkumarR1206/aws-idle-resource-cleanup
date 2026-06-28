# AWS Idle Resource Cleanup (FinOps Automation)

## Problem
In cloud-native environments, engineers frequently terminate EC2 instances but forget to delete the attached EBS volumes or release allocated Elastic IPs. AWS charges hourly rates for these unattached, idle resources. Across large organization accounts, this cloud waste silently drains thousands of dollars monthly.

Manual audits take hours of clicking through the AWS Console across multiple regions, leading to delayed visibility and wasted capital.

## The Solution
This automated Python script utilizes the Boto3 SDK to scan the active AWS region, instantly identify unattached EBS volumes (available state) and unassociated Elastic IPs, and safely purge them. What takes an operator hours to audit happens programmatically in seconds.

## Features
Unlike basic scripts that blindly delete infrastructure, this tool incorporates software engineering best practices required by enterprise DevOps teams:

1. **Dynamic Region Awareness:** Automatically detects the host environment's execution region (`AWS_DEFAULT_REGION`) instead of relying on brittle, hardcoded strings.
2. **Safe Dry-Run Mode:** Built-in safety toggle (`DRY_RUN = True`) allows teams to audit and log exactly what would be deleted before executing any destructive actions.
3. **Robust Error Handling:** API calls are wrapped in defensive `try/except` blocks. If a single resource fails to delete due to IAM permissions or locks, the script logs the error and gracefully moves to the next item instead of crashing the pipeline.

## Prerequisites & Setup
The script requires Python 3 and the official AWS SDK.

```bash
# Install dependencies
pip3 install boto3
```

## How to Run

### 1. Audit Mode (Dry-Run)
Ensure `DRY_RUN = True` is set at the top of `zombie_sweeper.py`. This safely scans and logs idle infrastructure without making changes.

```bash
python3 zombie_sweeper.py
```

### 2. Execution Mode (Live Clean)
Set `DRY_RUN = False` to execute live resource reclamation.

```bash
python3 zombie_sweeper.py
```

## Real-World Execution Output

```text
=========================================
STARTING ZOMBIE SWEEPER | REGION: us-east-1
DRY_RUN: False
=========================================

[*] Scanning for unattached EBS volumes...
  FOUND WASTE: EBS Volume vol-0a6d9d821b7a71080 is idle!
  [ACTION] Deleting volume vol-0a6d9d821b7a71080...
  Deleted vol-0a6d9d821b7a71080.

-----------------------------------------

[*] Scanning for unassociated Elastic IPs...
  FOUND WASTE: Elastic IP 18.213.36.198 is idle!
  [ACTION] Releasing Elastic IP 18.213.36.198...
  Released 18.213.36.198.

=========================================
SWEEPER RUN COMPLETE
=========================================
```
