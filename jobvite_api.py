import requests
import json
import os
from dotenv import load_dotenv
import base64
from datetime import datetime, timedelta

load_dotenv()

API_USER = os.getenv("USER_NAME")
API_KEY = os.getenv("ACCESS_KEY")
API_SECRET = os.getenv("SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")
COMPANY_ID = os.getenv("COMPANY_ID")

def fetch_candidate_data(use_cache=True):
    """Fetches Jobvite candidate data for applicants who have been sent an offer letter."""
    cache_file = "candidate_data.json"

    # Check if cache exists and load it instead of calling API
    if use_cache and os.path.exists(cache_file):
        print("Loading cached data from file...")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching data from API...")
    endpoint = "/candidate"
    count = 500
    start = 1
    all_candidates = []

    while True:
        params = {
            "api": API_KEY,
            "secret": API_SECRET,
            "start": start,
            "count": count
        }

        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        data = response.json()

        if "candidates" not in data:
            print("Unexpected response format:", data)
            break

        candidates = data["candidates"]

        all_candidates.extend(candidates)

        # Stop pagination if fewer results than requested count
        if len(candidates) < count:
            break

        # Increment start for the next page
        start += count

    valid_states = {
        "UKG Pro Onboarding Error",
        "UKG Pro Onboarding Success"
    }

    filtered_candidates = [
        candidate for candidate in all_candidates
        if candidate.get("application", {}).get("workflowState") in valid_states
    ]

    print(f"Total candidates fetched: {len(filtered_candidates)}")

    # Cache the data to a file for faster debugging
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(filtered_candidates, f, indent=4)

    return filtered_candidates

def fetch_offer_letters(candidates, save_path="offer_letters", days_back=30, use_cache=False):
    """Fetches Jobvite applicants who have been sent an offer letter or are in later workflow stages."""
    cache_file = "offer_letter_data.json"

    # Check if cache exists and load it instead of calling API
    if use_cache and os.path.exists(cache_file):
        print("Loading cached offer letter data from file...")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching offer letter data from API...")
    endpoint = "/offerLetter"
    offer_letters = []

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Calculate the Unix timestamp for 'days_back' days ago
    cutoff_date = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)

    for candidate in candidates:
        application_id = candidate.get("application", {}).get("eId")
        if not application_id:
            print(f"Skipping candidate {candidate.get('id', 'Unknown')} due to missing applicationId")
            continue

        params = {
            "api": API_KEY,
            "secret": API_SECRET,
            "companyId": COMPANY_ID,
            "applicationId": application_id,
            "offerSignatureType": "ESIGNATURE"
        }

        # Make the API request
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)

        if response.status_code == 200:
            offer_data = response.json()

            # Convert "offerLetterCreated" from timestamp to datetime
            offer_created_timestamp = offer_data.get("eSignature", {}).get("offerLetterCreated")
            if offer_created_timestamp:
                offer_created_date = datetime.fromtimestamp(offer_created_timestamp / 1000)

                # Check if offer letter was created within the last X days
                if offer_created_timestamp >= cutoff_date:
                    print(f"Offer letter for candidate {candidate.get('id')} created on {offer_created_date}")
                    offer_letters.append(offer_data)

                    # Extract the file name and encoded content
                    offer_completed_timestamp = offer_data.get("eSignature", {}).get("offerLetterCompleted")
                    completed_date = datetime.fromtimestamp(offer_completed_timestamp / 1000)
                    completed_date_str = completed_date.strftime("%Y%m%d")
                    offerLetterName = offer_data.get("offerLetterName")

                    file_name = f"OfferLetter_{application_id}_{completed_date_str}_{offerLetterName}"
                    encoded_pdf = offer_data.get("eSignature", {}).get("offerLetter")

                    if encoded_pdf:
                        # Decode the base64 content and save the file
                        pdf_path = os.path.join(save_path, file_name)
                        with open(pdf_path, "wb") as pdf_file:
                            pdf_file.write(base64.b64decode(encoded_pdf))
                        print(f"Saved offer letter: {pdf_path}")
                    else:
                        print(f"No PDF content found for application {application_id}")

            else:
                print(f"No creation date found for application {application_id}")

        else:
            print(
                f"Error fetching offer letter for application {application_id}: {response.status_code}, {response.text}")

    print(f"Total offer letters fetched: {len(offer_letters)}")

    # Cache the data to a file for faster debugging
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(offer_letters, f, indent=4)

    return offer_letters