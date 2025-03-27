Customer Issue:
The email and identity need to be passed together when calling onUserLogin. While this functions correctly on the website, the mobile app is pushing the identity to Clevertap while the user is still anonymous (before they sign up with their email).

When the user attempts to log in with their email, it triggers an identity error on their Web profile. This issue is widespread across their apps.


Solution:
RubySeven will need to release a new app build that ensures the identity and email are only pushed when the user signs up or logs in. We will audit the app to ensure this change is implemented correctly.

On our end, we will identify profiles with identity errors, demerge them, and manually merge the correct profiles using the scripts from this repository. This will be done one app at a time.


Steps to take with the scripts:
1. eventDownloader.py
Uses https://us1.api.clevertap.com/1/profiles.json. It will take in an account id and token and target the Identity Error event. 

It will create two CSV:
profiles_with_identity_identity_error.csv - User Profiles that contain an Identity
profiles_with_objectid_identity_error.csv - User Profiles that don't have an Identity but do contain an objectId in the API response

The badKs column will contain the user profiles that caused the Identity Error. 

We will use these CSV in the demergeApiScript.py.


2. getUserProfilesWithIdentityErrorById.py
Uses https://us1.api.clevertap.com/1/profiles.json. It will take in an account id and token and pull the objectIds of the profiles that actually caused the Identity error. We will use these CSV in the uploadUserProfileApi.py.

It will create 1 CSV: BadKs_Identity_ObjectID.csv


3. demergeApiScript.py
Uses https://us1.api.clevertap.com/1/demerge/profiles.json. It will take in an account id and token and target the badKs column in profiles_with_identity_identity_error.csv and profiles_with_objectid_identity_error.csv. It will demerge these profiles, removing the identity and only keeping the objectId. 


4. uploadUserProfileApi.py
Uses https://us1.api.clevertap.com/1/upload. It will take in an account id and token and target the objectIds column in BadKs_Identity_ObjectID.csv. 

It will map the identity from profiles_with_identity_identity_error.csv to the corresponding objectId from BadKs_Identity_ObjectID.csv and push it to the correct profiles. Note that this will only work for profiles_with_identity_identity_error.csv, because you cannot push an objectId to another profile with an objectId using the api. It will upload it as a user property. 


Apps Completed:
TEST-FoxPlay Casino: https://us1.dashboard.clevertap.com/779-6W4-9Z7Z/main