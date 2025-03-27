import requests
import csv
import json
import time
import os

# CleverTap API details
url = "https://us1.api.clevertap.com/1/profile.json"
csv_input_files = ["profiles_with_identity_identity_error.csv", "profiles_with_objectid_identity_error.csv"]
csv_output_filename = "BadKs_Identity_ObjectID.csv"
accid = "TEST-779-6W4-9Z7Z"
accpcode = "UFS-SKA-WHEL"

# Check if both input files exist
for file in csv_input_files:
    if not os.path.exists(file):
        print(f"❌ Error: File '{file}' not found in the current directory.")
        exit(1)

def read_badKs_from_multiple_csvs(input_files):
    """Read 'badKs' column and extract unique values as identities from multiple files."""
    identities = set()
    for input_file in input_files:
        with open(input_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "badKs" in row and row["badKs"]:
                    badKs_list = row["badKs"].split(", ")
                    for identity in badKs_list:
                        identities.add(identity.strip())
    return list(identities)

def fetch_user_profile(identity, accid, accpc, retries=3, delay=2):
    """Fetch user profile from CleverTap API with retries and error handling."""
    headers = {
        'X-CleverTap-Account-Id': accid,
        'X-CleverTap-Passcode': accpc,
        'Content-Type': "application/json",
        'cache-control': "no-cache",
    }
    params = {"identity": identity}

    for attempt in range(retries):
        print(f"Fetching profile for identity: {identity} (Attempt {attempt+1})")
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            res_json = response.json()

            if "record" not in res_json or res_json["record"] is None:
                print(f"⚠️ No record found for identity: {identity}")
                return {"identity": identity, "objectIds": "None"}

            record = res_json["record"]
            platform_info = record.get("platformInfo", [])

            object_ids = [platform.get("objectId", "Unknown") for platform in platform_info] if platform_info else ["None"]
            return {"identity": identity, "objectIds": ", ".join(object_ids)}
        
        elif response.status_code in [503, 429]:
            print(f"⚠️ Temporary issue for {identity}, retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            print(f"❌ Failed to fetch profile for {identity}: {response.status_code} - {response.text}")
            return {"identity": identity, "objectIds": "Error"}

    return {"identity": identity, "objectIds": "Failed after retries"}

# Main execution
print("🚀 Script started...")

identities = read_badKs_from_multiple_csvs(csv_input_files)
print(f"🔍 Found {len(identities)} unique identities from badKs to fetch.")

profiles = []
for identity in identities:
    profile = fetch_user_profile(identity, accid, accpcode)
    profiles.append(profile)

# Save to CSV
if profiles:
    with open(csv_output_filename, 'w', newline="", encoding="utf-8") as output_file:
        fieldnames = ["identity", "objectIds"]
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(profiles)

    print(f"📂 Data saved to {csv_output_filename}")
else:
    print("⚠️ No data to save.")
