import pandas as pd

# Load the CSV file with better memory handling
file_path = "/Users/hadiaandar/Documents/My_Python_scripts/Mutual LLC isPremium exists find people.csv"

# Load the file with low_memory=False to handle mixed types
data = pd.read_csv(file_path, low_memory=False)

# Print the first few rows and columns to verify
print(data.head())
print(data.columns.tolist())

# Drop specific columns by name
columns_to_remove = ['Gender','DOB','accountStatus','birthdate','device','hadPremium','hasPremium','height','isVerified','itp','language','newPersonalInfoStarted','notif_announcements','notif_email','notif_promotions','number_of_interests_set','profileCompletion','userStatus','verfiedStatus','verifiedStatus','Unnamed: 23']  # List columns you want to drop
data = data.drop(columns=columns_to_remove)

# Save the updated data to a new file
output_path = "/Users/hadiaandar/Documents/My_Python_scripts/filtered_file.csv"
data.to_csv(output_path, index=False)
print(f"Columns removed and saved to {output_path}")




