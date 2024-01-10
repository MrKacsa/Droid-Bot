import requests
import random
import time

# Replace with your Airtable API key, base ID, and table name
AIRTABLE_API_KEY = "patpq80rM3ZxRPWtV.3ba8c84a11be2930de466b5faa1ebf9ccb21456b45d9608bbec59a61461e1c66"
BASE_ID = "keyxwkJVoWKLaqRT0"
TABLE_NAME = "tblZXnOTSZfEUmA2r"

# Airtable API endpoint
API_ENDPOINT = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json",
}

def init_airtable():
    # Check if Airtable API key and base ID are provided
    if AIRTABLE_API_KEY == "YOUR_API_KEY" or BASE_ID == "YOUR_BASE_ID":
        raise Exception("Please replace 'YOUR_API_KEY' and 'YOUR_BASE_ID' with your actual values.")
    # Verify that the base exists (optional)
    response = requests.get(API_ENDPOINT, headers=HEADERS)
    if response.status_code != 200:
        raise Exception("Airtable base not found or API key is invalid.")
    print("Airtable initialized successfully.")

def create_giveaway(title, item, duration, winners, hosted_by, additional_details):
    # Create the record for the new giveaway
    data = {
        "fields": {
            "Title": title,
            "Item": item,
            "Duration": duration,
            "Winners": winners,
            "Hosted By": hosted_by,
            "Additional Details": additional_details,
        }
    }

    response = requests.post(API_ENDPOINT, json=data, headers=HEADERS)

    if response.status_code == 200:
        print("Giveaway created successfully.")
        return response.json()
    else:
        print("Failed to create giveaway.")
        return None

def main():
    init_airtable()  # Initialize Airtable
    # Example usage to create a giveaway
    title = "Example Giveaway"
    item = "Awesome Prize"
    duration = 3600  # 1 hour in seconds
    winners = 1
    hosted_by = "Your Bot Name"
    additional_details = "Must be a follower to enter."

    giveaway_data = create_giveaway(title, item, duration, winners, hosted_by, additional_details)

    if giveaway_data:
        # Now you can use giveaway_data to access the record ID or any other information you need.
        giveaway_id = giveaway_data["id"]
        print(f"Giveaway ID: {giveaway_id}")

if __name__ == "__main__":
    main()
