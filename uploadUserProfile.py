import requests
import json

# Define the CleverTap API URL
url = "https://us1.api.clevertap.com/1/upload"

# Define the headers from the image
headers = {
    "X-CleverTap-Account-Id": "WRZ-KK5-656Z",
    "X-CleverTap-Passcode": "IOK-RWZ-OPUL",
    "Content-Type": "application/json"
}

# Define the base payload
base_payload = {
    "d": []
}

# Generate 500 profiles with unique objectIds
for i in range(1, 501):
    profile = {
        "objectId": str(i),
        "type": "profile",
        "profileData": {
            "Email": "hadia.andar@clevertap.com"
        }
    }
    base_payload["d"].append(profile)

# Send the data in chunks if necessary (e.g., CleverTap may limit payload size)
batch_size = 100
for start in range(0, len(base_payload["d"]), batch_size):
    batch_payload = {
        "d": base_payload["d"][start:start + batch_size]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(batch_payload), timeout=10)

        if response.status_code == 200:
            print(f"Batch {start // batch_size + 1}: Success")
        else:
            print(f"Batch {start // batch_size + 1}: Failed with status code {response.status_code}")
            print(response.text)
    except requests.exceptions.Timeout:
        print(f"Batch {start // batch_size + 1}: Request timed out. Retrying...")
        try:
            response = requests.post(url, headers=headers, data=json.dumps(batch_payload), timeout=10)
            if response.status_code == 200:
                print(f"Batch {start // batch_size + 1}: Retry Success")
            else:
                print(f"Batch {start // batch_size + 1}: Retry Failed with status code {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Batch {start // batch_size + 1}: Retry failed with error: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"Batch {start // batch_size + 1}: Connection error occurred: {e}")
        print("Check your network connection or the API endpoint.")
    except Exception as e:
        print(f"Batch {start // batch_size + 1}: An unexpected error occurred: {e}")
        print("Investigate the error and ensure the request is properly formatted.")
