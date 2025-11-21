#!/usr/bin/env python3
"""
Script to check GitHub repository activity status.
Checks if repositories exist and when they were last updated.
"""

import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse

def extract_repo_from_url(url):
    """Extract owner/repo from GitHub URL"""
    if 'github.com' not in url:
        return None
    path = urlparse(url).path.strip('/')
    parts = path.split('/')
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None

def check_repo_status(repo_path):
    """Check repository status and return info"""
    api_url = f"https://api.github.com/repos/{repo_path}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 404:
            return {"exists": False, "error": "Repository not found"}
        
        if response.status_code != 200:
            return {"exists": False, "error": f"HTTP {response.status_code}"}
        
        data = response.json()
        pushed_at = data.get('pushed_at')
        updated_at = data.get('updated_at')
        
        if pushed_at:
            pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            now = datetime.now(pushed_date.tzinfo)
            days_ago = (now - pushed_date).days
            is_active = days_ago < 365
            
            return {
                "exists": True,
                "pushed_at": pushed_at,
                "updated_at": updated_at,
                "days_ago": days_ago,
                "is_active": is_active,
                "name": data.get('full_name', repo_path),
                "description": data.get('description', '')
            }
        else:
            return {"exists": True, "pushed_at": None, "updated_at": updated_at}
            
    except Exception as e:
        return {"exists": False, "error": str(e)}

# Repositories to check
repos = [
    ("innocentmichael/sara", "https://github.com/innocentmichael/sara"),
    ("mikrowizard/mikrowizard", "https://github.com/mikrowizard/mikrowizard"),
    ("eworm-de/routeros-scripts", "https://github.com/eworm-de/routeros-scripts"),
    ("smkrv/mikrotik-domain-filter-script", "https://github.com/smkrv/mikrotik-domain-filter-script"),
    ("evgenios/routeros-api", "https://github.com/evgenios/routeros-api"),
    ("evgenios/routeros-api-php", "https://github.com/evgenios/routeros-api-php"),
    ("go-routeros/routeros", "https://github.com/go-routeros/routeros"),
    ("GNewbury1/RouterOS-API", "https://github.com/GNewbury1/RouterOS-API"),
    ("osamahfarhan/mikrotik-events", "https://github.com/osamahfarhan/mikrotik-events"),
    ("n3tuk/scripts-mikrotik", "https://github.com/n3tuk/scripts-mikrotik"),
    ("nymurbd/MikroTik-scripts", "https://github.com/nymurbd/MikroTik-scripts"),
    ("nshttpd/mikrotik-exporter", "https://github.com/nshttpd/mikrotik-exporter"),
    ("nshttpd/routeros_exporter", "https://github.com/nshttpd/routeros_exporter"),
    # New candidates
    ("ansible-collections/community.routeros", "https://github.com/ansible-collections/community.routeros"),
    ("luqasz/librouteros", "https://github.com/luqasz/librouteros"),
    ("socialwifi/RouterOS-API", "https://github.com/socialwifi/RouterOS-API"),
    ("ytti/oxidized", "https://github.com/ytti/oxidized"),
    ("rfmoz/mikrotik-to-influx", "https://github.com/rfmoz/mikrotik-to-influx"),
]

print("Checking repository statuses...\n")
results = {}

for repo_path, url in repos:
    print(f"Checking {repo_path}...", end=" ")
    status = check_repo_status(repo_path)
    results[repo_path] = status
    
    if not status.get("exists"):
        print(f"❌ NOT FOUND - {status.get('error', 'Unknown error')}")
    elif status.get("is_active"):
        print(f"✅ ACTIVE (last pushed {status.get('days_ago', '?')} days ago)")
    else:
        print(f"⚠️  INACTIVE (last pushed {status.get('days_ago', '?')} days ago)")
    
    # Small delay to avoid rate limiting
    import time
    time.sleep(0.5)

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
for repo_path, status in results.items():
    if not status.get("exists"):
        print(f"{repo_path}: ❌ NOT FOUND")
    elif status.get("is_active"):
        print(f"{repo_path}: ✅ ACTIVE")
    else:
        print(f"{repo_path}: ⚠️  INACTIVE ({status.get('days_ago', '?')} days since last push)")

# Save results to JSON for reference
with open('repo_status.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("\nResults saved to repo_status.json")

