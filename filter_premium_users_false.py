import pandas as pd

# Load the CSV file
file_path = "/Users/hadiaandar/Documents/My_Python_scripts/filtered_file.csv"
data = pd.read_csv(file_path)

# Filter rows where isPremium is true
premium_users = data[data['isPremium'] == 'false']  # Ensure column name matches exactly

# Print the filtered data
print(premium_users)

# Save the filtered data to a new CSV file
output_path = "/Users/hadiaandar/Documents/My_Python_scripts/premium_users_false.csv"
premium_users.to_csv(output_path, index=False)
print(f"Filtered data saved to {output_path}")
