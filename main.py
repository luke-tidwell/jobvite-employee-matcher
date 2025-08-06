from jobvite_api import fetch_candidate_data, fetch_offer_letters
from jobvite_database_utils import fetch_employees, find_match, complete_matching
import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()

server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
trusted = os.getenv("SQL_TRUSTED", "Yes") # Defaults to "Yes"

conn_str = (
    f"Driver={{SQL Server}};"
    f"Server={server};"
    f"Database={database};"
    f"Trusted_Connection={trusted};"
)

conn = pyodbc.connect(conn_str)


def main():
    try:
        candidates = fetch_candidate_data()
        offer_letters = fetch_offer_letters(candidates)
        employees = fetch_employees(conn)
        matched_candidates = complete_matching(candidates, employees)
        print("Matched Candidates Structure:", matched_candidates)
        for email, emp_number in matched_candidates:
            print(f"Candidate {email} -> Employee {emp_number or 'No match found'}")

        print("Job completed successfully.")
    except Exception as e:
        print(f"Error encountered: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()