# Jobvite Employee Matcher

Automated pipeline to fetch candidate and offer letter data from the Jobvite API, match candidates to employee records in the SQL database, and output match results for downstream HR processes.

---

## Why This Project

Modern HR operations often require seamless integration between applicant tracking systems and internal employee databases. This project was built to demonstrate practical skills in API integration, data normalization, and robust matching logic—solving a real-world problem of connecting candidate data from Jobvite with employee records for onboarding and compliance workflows.

---

## Features

- **Jobvite API Integration:** Securely fetches candidate and offer letter data using environment-based credential management.
- **Employee Data Matching:** Matches candidates to employee records using robust logic (supports partial/fuzzy matches on email, phone, and name).
- **Extensible & Modular:** Clear separation between API access, database utilities, and matching logic.
- **Caching:** Optionally caches API responses to minimize redundant calls.

---

## Tech Stack

- **Python 3.7+**
- **Jobvite API** (REST)
- **SQL Database** (accessed via `pyodbc`)
- **Environment Variable Management** (`python-dotenv`)

## How It Works

1. Fetches candidate and offer letter data from the Jobvite API.
2. Retrieves employee records from a SQL database.
3. Normalizes and matches candidate data to employee records using robust logic.
4. Outputs match results for downstream HR or onboarding processes.

---

## Code Structure
```
jobvite-employee-matcher/
├── main.py                    # Entry point: orchestrates API fetch, DB fetch, and matching
├── jobvite_api.py             # Handles Jobvite API integration and data caching
├── jobvite_database_utils.py  # Database connection, normalization, and matching logic
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variable file
└── README.md                  # Project documentation
```

---

## Contact

For questions or support, please open an issue or contact the repository maintainer.
