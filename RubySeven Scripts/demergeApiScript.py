import requests
import csv
import json
import time
import os

# CleverTap API details
API_URL = "https://us1.api.clevertap.com/1/demerge/profiles.json"
ACCOUNT_ID = "TEST-779-6W4-9Z7Z"  # Replace with your actual Account ID
ACCOUNT_PASSCODE = "UFS-SKA-WHEL"  # Replace with your actual Passcode

# File paths
CSV_FILES = [
    "profiles_with_identity_identity_error.csv",
    "profiles_with_objectid_identity_error.csv"
]
OUTPUT_CSV = "Demerge_API_Results.csv"  # Output file with API results
ERROR_LOG = "ErrorFile.json"  # Optional: Not currently used

def read_badKs_from_csvs(input_files):
    """Read 'badKs' column from multiple CSVs and extract unique values."""
    identities = set()
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"❌ Error: File '{input_file}' not found.")
            continue
        with open(input_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "badKs" in row and row["badKs"]:
                    badKs_list = row["badKs"].split(", ")
                    for identity in badKs_list:
                        identities.add(identity.strip())
    return list(identities)

def call_demerge_api(account_id, account_passcode, identities, retries=3, delay=2):
    """Call the demerge API for a batch of identities."""
    headers = {
        'X-CleverTap-Account-Id': account_id,
        'X-CleverTap-Passcode': account_passcode,
        'Content-Type': "application/json; charset=utf-8",
    }

    data = json.dumps({"identities": identities})

    for attempt in range(retries):
        print(f"🔄 Calling demerge API for batch: {identities[:3]}... (Attempt {attempt+1})")
        response = requests.post(API_URL, headers=headers, data=data)

        print(f"API Response Code: {response.status_code}")
        print(f"API Response Body: {response.text}")

        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "success":
                return {"identities": ", ".join(identities), "status": "Success", "response": response.text}
        
        elif response.status_code in [503, 429]:
            print(f"⚠️ Temporary issue for batch {identities[:3]}, retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            print(f"❌ Failed to process batch {identities[:3]}: {response.status_code} - {response.text}")

    return {"identities": ", ".join(identities), "status": "Failed", "response": response.text}

# Main execution
print("🚀 Script started...")

all_identities = read_badKs_from_csvs(CSV_FILES)
print(f"🔍 Found {len(all_identities)} unique identities from badKs to process.")

BATCH_SIZE = 10
results = []

for i in range(0, len(all_identities), BATCH_SIZE):
    batch = all_identities[i:i + BATCH_SIZE]
    result = call_demerge_api(ACCOUNT_ID, ACCOUNT_PASSCODE, batch)
    results.append(result)

# Save results to CSV
if results:
    with open(OUTPUT_CSV, 'w', newline="", encoding="utf-8") as output_file:
        fieldnames = ["identities", "status", "response"]
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(results)

    print(f"📂 Data saved to {OUTPUT_CSV}")
else:
    print("⚠️ No data to save.")
