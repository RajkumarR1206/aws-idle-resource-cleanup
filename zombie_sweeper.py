import boto3
import os

DRY_RUN = False  

def cleanup_zombie_resources():
    # Automatically detect the region CloudShell is running in, fallback to us-east-1
    current_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    # Initialize the client using the dynamically detected region
    ec2 = boto3.client('ec2', region_name=current_region)
    
    print("=========================================")
    print(f"STARTING ZOMBIE SWEEPER | REGION: {current_region}")
    print(f"DRY_RUN: {DRY_RUN}")
    print("=========================================\n")

    # ---------------------------------------------------------
    # TASK 1: Find and Cleanup Unattached EBS Volumes
    # ---------------------------------------------------------
    print("[*] Scanning for unattached EBS volumes...")
    volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
    unattached_volumes = volumes.get('Volumes', [])
    
    if not unattached_volumes:
        print("✓ No unattached EBS volumes found.")
    else:
        for volume in unattached_volumes:
            vol_id = volume['VolumeId']
            print(f"❗ FOUND WASTE: EBS Volume {vol_id} is idle!")
            
            try:
                if DRY_RUN:
                    print(f"  [DRY RUN] Would delete volume {vol_id}...")
                else:
                    print(f"  [ACTION] Deleting volume {vol_id}...")
                    ec2.delete_volume(VolumeId=vol_id)
                    print(f"  ✓ Deleted {vol_id}.")
            except Exception as e:
                print(f"  ❌ FAILED to delete {vol_id}. Error: {str(e)}")

    print("\n-----------------------------------------\n")

    # ---------------------------------------------------------
    # TASK 2: Find and Cleanup Unassociated Elastic IPs
    # ---------------------------------------------------------
    print("[*] Scanning for unassociated Elastic IPs...")
    ips = ec2.describe_addresses()
    elastic_ips = ips.get('Addresses', [])
    unassociated_ip_count = 0
    
    for ip in elastic_ips:
        if 'AssociationId' not in ip:
            unassociated_ip_count += 1
            alloc_id = ip['AllocationId']
            public_ip = ip['PublicIp']
            print(f"❗ FOUND WASTE: Elastic IP {public_ip} is idle!")
            
            try:
                if DRY_RUN:
                    print(f"  [DRY RUN] Would release Elastic IP {public_ip}...")
                else:
                    print(f"  [ACTION] Releasing Elastic IP {public_ip}...")
                    ec2.release_address(AllocationId=alloc_id)
                    print(f"  ✓ Released {public_ip}.")
            except Exception as e:
                print(f"  ❌ FAILED to release {public_ip}. Error: {str(e)}")
            
    if unassociated_ip_count == 0:
        print("✓ No unassociated Elastic IPs found.")

    print("\n=========================================")
    print("SWEEPER RUN COMPLETE")
    print("=========================================")

if __name__ == "__main__":
    cleanup_zombie_resources()
