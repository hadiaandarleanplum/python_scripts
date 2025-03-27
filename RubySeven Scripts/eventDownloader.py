import requests
import json
import csv
from datetime import datetime, timedelta

# CleverTap API details
url = "https://us1.api.clevertap.com/1/profiles.json"
accid = "TEST-779-6W4-9Z7Z"
accpcode = "UFS-SKA-WHEL"
eventName = "Identity Error"

# Generate 30-day chunks between Jan 1, 2024 to Mar 24, 2025
start_date = datetime.strptime("20240101", "%Y%m%d")
end_date = datetime.strptime("20250327", "%Y%m%d")

chunks = []
current = start_date
while current < end_date:
    chunk_start = current
    chunk_end = min(current + timedelta(days=29), end_date)
    chunks.append((int(chunk_start.strftime("%Y%m%d")), int(chunk_end.strftime("%Y%m%d"))))
    current = chunk_end + timedelta(days=1)

print("🚀 Script started...")

# Functions
def queryCall(eventName, accid, accpc, dfrom, dto):
    payload = {"event_name": eventName, "from": dfrom, "to": dto}
    headers = {
        'X-CleverTap-Account-Id': accid,
        'X-CleverTap-Passcode': accpc,
        'Content-Type': "application/json",
        'cache-control': "no-cache",
    }

    print(f"\n🔄 Requesting: {eventName} from {dfrom} to {dto}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Response Code: {response.status_code}")

    if response.status_code != 200:
        print("❌ Error:", response.text)
        return []

    res = response.json()
    records = res.get("records") or res.get("profiles") or res.get("data") or res.get("events") or []
    cursor = res.get("cursor") or res.get("next_cursor")

    if cursor:
        print("🔄 Cursor found, fetching more...")
        records += fetch_all_data(cursor, accid, accpc)

    print(f"📊 Fetched {len(records)} records")
    return records

def fetch_all_data(cursor, accid, accpc):
    all_records = []
    while cursor:
        partialUrl = f"{url}?cursor={cursor}"
        headers = {
            'X-CleverTap-Account-Id': accid,
            'X-CleverTap-Passcode': accpc,
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }
        response = requests.get(partialUrl, headers=headers)
        if response.status_code != 200:
            print("❌ Cursor error:", response.text)
            break

        res = response.json()
        batch = res.get("records") or res.get("profiles") or []
        all_records.extend(batch)
        print(f"➕ {len(batch)} records")
        cursor = res.get("cursor") or res.get("next_cursor")
    return all_records

# Storage for combined data
known_profiles = []
unknown_profiles = []

# Loop over each chunk
for dfrom, dto in chunks:
    try:
        records = queryCall(eventName, accid, accpcode, dfrom, dto)
        for record in records:
            identity = record.get("identity")  # only use .get("identity")

            platform_info = record.get("platformInfo", [])
            badKs_list = []
            if isinstance(platform_info, list):
                for platform in platform_info:
                    if isinstance(platform, dict) and "badKs" in platform:
                        badKs_list.extend(platform["badKs"])

            # Deduplicate badKs
            seen = set()
            deduped_badKs = [x for x in badKs_list if not (x in seen or seen.add(x))]
            badKs_str = ", ".join(deduped_badKs) if deduped_badKs else "None"

            if identity:
                known_profiles.append({"identity": identity, "badKs": badKs_str})
            else:
                object_id = None
                for platform in platform_info:
                    if isinstance(platform, dict) and "objectId" in platform:
                        object_id = platform["objectId"]
                        break
                unknown_profiles.append({
                    "objectId": object_id or "No objectId found",
                    "badKs": badKs_str
                })
    except Exception as e:
        print(f"🔥 Error processing chunk {dfrom}–{dto}: {e}")

# Save known profiles
if known_profiles:
    with open("profiles_with_identity_identity_error.csv", "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["identity", "badKs"])
        writer.writeheader()
        writer.writerows(known_profiles)
    print("✅ Saved: profiles_with_identity_identity_error.csv")
else:
    print("⚠️ No known profiles found")

# Save unknown profiles
if unknown_profiles:
    with open("profiles_with_objectid_identity_error.csv", "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["objectId", "badKs"])
        writer.writeheader()
        writer.writerows(unknown_profiles)
    print("✅ Saved: profiles_with_objectid_identity_error.csv")
else:
    print("✅ No unknown profiles found")
