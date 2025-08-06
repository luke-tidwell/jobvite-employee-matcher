from dotenv import load_dotenv
import os
import pyodbc
import re

load_dotenv()

server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
trusted = os.getenv("SQL_TRUSTED", "Yes") # Defaults to "Yes"

conn = (
    f"Driver={{SQL Server}};"
    f"Server={server};"
    f"Database={database};"
    f"Trusted_Connection={trusted};"
)

def normalize_phone(phone):
    """
    Normalize a phone number to the format (xxx) xxx-xxxx.

    This function:
      - Removes all non-digit characters from the input.
      - Removes the US country code '1' if the number has 11 digits.
      - Ensures the resulting number has exactly 10 digits.
      - Returns the phone number formatted as (xxx) xxx-xxxx.
      - If the input doesn't result in 10 digits, returns the original phone string.
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Remove leading '1' if it's a US country code
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]

    # Ensure we have exactly 10 digits
    if len(digits) != 10:
        return phone

    # Format the number as (xxx) xxx-xxxx
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

def safe_string_match(val1, val2):
    """
    Returns True if both val1 and val2 are non-empty (non-null) and exactly the same.
    Otherwise returns False.
    """
    if not val1 or not val2:
        return False
    return val1 == val2

def fetch_employees(conn):
    """Fetch all non-terminated employees from dbo.Employee"""
    query = "SELECT employee_number, first_name, last_name, email, phone_number FROM dbo.Employee WHERE Status <> 'T'"
    cursor = conn.cursor()
    cursor.execute(query)
    employees = cursor.fetchall()

    # Convert to list of dicts
    return [
        {"employee_number": row.employee_number, "first_name": row.first_name,
         "last_name": row.last_name, "email": row.email, "phone_number": row.phone_number}
        for row in employees
    ]


def find_match(candidate, employees):
    """
        Find the best employee match for a candidate based on:
          - first name
          - last name
          - email
          - phone number (either homePhone or mobile from candidate)
        """
    best_partial_match = None

    # Extract candidate fields
    candidate_first = candidate.get("first_name", "")
    candidate_last = candidate.get("last_name", "")
    candidate_email = candidate.get("email", "") # Should be only person email, maverik emails can be ignored
    candidate_home_phone = candidate.get("homePhone", "")
    candidate_mobile_phone = candidate.get("mobile", "")

    normalized_home = normalize_phone(candidate_home_phone)
    normalized_mobile = normalize_phone(candidate_mobile_phone)

    for employee in employees:
        # The phone match is True if EITHER home or mobile matches the employee phone
        phone_match = (
                safe_string_match(normalized_home, employee.get("phone_number")) or
                safe_string_match(normalized_mobile, employee.get("phone_number"))
        )

        matches = {
            "first_name": safe_string_match(candidate_first, employee.get("first_name")),
            "last_name": safe_string_match(candidate_last, employee.get("last_name")),
            "email": safe_string_match(candidate_email, employee.get("email")),
            "phone": phone_match
        }

        match_count = sum(matches.values())

        # Perfect match on all four fields
        if match_count == 4:
            return employee["employee_number"]
        # Partial match (2 or 3), but skip if it's only first+last name
        if match_count in [2, 3]:
            if match_count == 2 and matches["first_name"] and matches["last_name"]:
                continue
            best_partial_match = employee["employee_number"]

    return best_partial_match

def complete_matching(candidates, employees):
    """Matches a list of candidates to employees and returns a dictionary mapping."""
    matched_candidates = []

    for candidate in candidates:
        print(f"Checking candidate: {candidate.get('email', 'No email')}")

        emp_number = find_match(candidate, employees)

        if emp_number:
            print(f"✅ Match found: {candidate['email']} -> {emp_number}")
        else:
            print(f"❌ No match for: {candidate['email']}")

        matched_candidates.append((candidate["email"], emp_number))

    print("Final Matched Candidates:", matched_candidates)

    return matched_candidates
