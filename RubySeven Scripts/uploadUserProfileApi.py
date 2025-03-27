import pandas as pd
import requests
import os

# Load the CSV files
user_profiles_df = pd.read_csv("BadKs_Identity_ObjectID.csv")
identity_df = pd.read_csv("profiles_with_identity_identity_error.csv")
objectid_df = pd.read_csv("profiles_with_objectid_identity_error.csv")

# Convert BadKs_Identity_ObjectID to a dictionary for quick lookup, handling empty or None values
object_id_map = dict(zip(user_profiles_df["identity"].fillna(''), user_profiles_df["objectIds"].fillna('')))

# Function to map badKs identities to their respective objectIds
def map_object_ids(badKs_str):
    if pd.isna(badKs_str):
        return ""
    badKs_list = str(badKs_str).split(", ")
    mapped_ids = [str(object_id_map.get(badK.strip(), "Not Found")) for badK in badKs_list]
    return ", ".join([id for id in mapped_ids if id != 'Not Found' and id != ''])

# Generate mapped_objectIds for identity_df and objectid_df
identity_df["mapped_objectIds"] = identity_df["badKs"].apply(map_object_ids)
objectid_df["mapped_objectIds"] = objectid_df["badKs"].apply(map_object_ids)

# Save the updated dataframe to a new CSV file
updated_csv_path = "updated_profiles_with_identity_error.csv"
identity_df.to_csv(updated_csv_path, index=False)

print("Updated data has been saved to 'updated_profiles_with_identity_error.csv'")

# Initialize a log dataframe
log_data = []

# API Configuration
API_URL = "https://us1.api.clevertap.com/1/upload"
HEADERS = {
    "X-CleverTap-Account-Id": "TEST-779-6W4-9Z7Z",
    "X-CleverTap-Passcode": "UFS-SKA-WHEL",
    "Content-Type": "application/json; charset=utf-8"
}

# Process profiles_with_identity_identity_error.csv in batches
batch_size = 10
for start in range(0, len(identity_df), batch_size):
    batch_df = identity_df.iloc[start:start + batch_size]
    for _, row in batch_df.iterrows():
        object_ids_list = str(row.get("mapped_objectIds", "")).split(", ") if row.get("mapped_objectIds") else []

        if pd.isna(row.get("identity")) or not row.get("identity"):
            print(f"Skipping row with badKs: {row.get('badKs')} as identity is missing")
            continue

        for object_id in object_ids_list:
            if not object_id or object_id == 'Not Found':
                print(f"Invalid Object ID for identity {row.get('identity')}. Skipping.")
                continue

            payload = {
                "d": [
                    {
                        "objectId": object_id,
                        "type": "profile",
                        "profileData": {
                            "identity": row.get("identity")
                        }
                    }
                ]
            }
            try:
                response = requests.post(API_URL, json=payload, headers=HEADERS)
                log_data.append({
                    'identity': row.get('identity'),
                    'objectId': object_id,
                    'status_code': response.status_code,
                    'response_text': response.text
                })
                print(f"Uploaded {row.get('identity')} (Object ID: {object_id}): {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error uploading {row.get('identity')} (Object ID: {object_id}): {e}")

# Process profiles_with_objectid_identity_error.csv in batches
# Commented out as requested
# for start in range(0, len(objectid_df), batch_size):
#     batch_df = objectid_df.iloc[start:start + batch_size]
#     for _, row in batch_df.iterrows():
#         object_id_from_error_csv = row.get("objectId")
#         object_id_from_mapping = object_id_map.get(str(row.get("badKs", "")))

#         if not object_id_from_error_csv or object_id_from_error_csv == 'Not Found':
#             print(f"Skipping row with missing or invalid objectId")
#             continue

#         if object_id_from_mapping and object_id_from_mapping != "Not Found" and object_id_from_mapping != "None":
#             payload = {
#                 "d": [
#                     {
#                         "objectId": object_id_from_error_csv,
#                         "type": "profile",
#                         "profileData": {
#                             "objectId": object_id_from_mapping
#                         }
#                     }
#                 ]
#             }
#             try:
#                 response = requests.post(API_URL, json=payload, headers=HEADERS)
#                 log_data.append({
#                     'badKs': row.get('badKs'),
#                     'objectId': object_id_from_error_csv,
#                     'mapped_objectId': object_id_from_mapping,
#                     'status_code': response.status_code,
#                     'response_text': response.text
#                 })
#                 print(f"Uploaded Object ID {object_id_from_error_csv} with mapped Object ID {object_id_from_mapping}: {response.status_code}, {response.text}")
#             except Exception as e:
#                 print(f"Error uploading Object ID {object_id_from_error_csv} with mapped Object ID {object_id_from_mapping}: {e}")
#         else:
#             print(f"No valid mapping found for objectId {object_id_from_error_csv}. Skipping.")

# Save logs to a CSV file
try:
    log_df = pd.DataFrame(log_data)
    log_df.to_csv("upload_log.csv", index=False)
    print("Upload log has been saved to 'upload_log.csv'")
except Exception as e:
    print(f"Error while saving upload log: {e}")

print("All batches completed successfully.")
