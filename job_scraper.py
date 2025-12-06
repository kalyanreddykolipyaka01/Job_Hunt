from datetime import datetime
from zoneinfo import ZoneInfo
from jobspy import scrape_jobs
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import yagmail
from dotenv import load_dotenv
import time
from googleapiclient.errors import HttpError
from spam_filters import (
    SPAM_KEYWORDS,
    SPAM_COMPANIES,
    SPAM_DESCRIPTION_KEYWORDS,
)

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------
# PERSONALIZED CONFIG 
# ---------------------------------------------------------

SEARCH_TERMS = [
    "machine learning engineer", "ml engineer", "mlops engineer",
    "data engineer", "data scientist", "data analyst",
    "ai engineer", "llm engineer", "python", "Artificial Intelligence",
    "numpy, pandas, scikit learn, matplotlib, TensorFlow",
    "backend developer", "fastapi",
    "RAG (Retrival Augmented Generation)",
    "MCP (Model Context Protocol)",
    "HuggingFace", "Sentiment Analysis",
    "React", "Next.js",
]

LOCATIONS = [
    "Toronto, Ontario, Canada",
    "Ontario, Canada",
    "Canada",
]

SITES = ["indeed", "linkedin"]

RESULTS_WANTED = int("100")
HOURS_OLD = int("26") # 24 hours + 2 extra for timezones & delays
COUNTRY = "Canada"

OUTPUT_DIR = "jobs_data"
MASTER_FILE = "canada_ml_jobs_master.csv"

# ---------------------------------------------------------
# 🔴 SPAM KEYWORDS - Filter out jobs YOU'RE NOT ELIGIBLE FOR
# ---------------------------------------------------------
# Based on your profile: New grad (April 2026), ~8 months internship experience
# Strong in: Python, ML/MLOps, Data Science, Cloud (AWS/Azure), no French, no P.Eng

# Spam filters are imported from spam_filters.py


def clean_results(df: pd.DataFrame):
    if df.empty:
        return df

    df["title"] = df["title"].str.strip()

    # Lowercase all spam keywords for comparison
    spam_keywords_lower = [kw.lower() for kw in SPAM_KEYWORDS]
    spam_companies_lower = [kw.lower() for kw in SPAM_COMPANIES]
    spam_desc_lower = [kw.lower() for kw in SPAM_DESCRIPTION_KEYWORDS]

    def contains_spam_title(text):
        text = str(text).lower()
        return any(kw in text for kw in spam_keywords_lower)

    def contains_spam_description(text):
        text = str(text).lower()
        return any(kw in text for kw in spam_desc_lower)

    # Company spam matcher
    def company_is_spam(text):
        text = str(text).lower()
        return any(kw in text for kw in spam_companies_lower)

    mask = ~(
        df["title"].apply(contains_spam_title) |
        df.get("description", pd.Series("", index=df.index)).apply(contains_spam_description) |
        df.get("company", pd.Series("", index=df.index)).apply(company_is_spam)
    )
    df = df[mask].copy()

    # 🔥 Keep this to prevent duplicates across sites & locations
    df.drop_duplicates(subset=["job_url"], inplace=True)

    # Sort by newest
    if "date_posted" in df.columns:
        df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
        df.sort_values("date_posted", ascending=False, inplace=True)

    return df


def save_to_google_sheets(df, sheet_url, creds_path):
    # Drop empty columns
    df = df.dropna(axis=1, how='all')
    # Authenticate and open sheet by URL (more reliable than title)
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_url(sheet_url)
    worksheet = sh.get_worksheet(0)  # First worksheet
    worksheet.clear()  # Optional: clear old data
    set_with_dataframe(worksheet, df)
    print(f"✅ Saved to Google Sheets: {sh.title}")

def autofit_columns(sheet_url: str, creds_path: str):
    # Extract spreadsheet ID from URL
    try:
        spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]
    except Exception:
        print("⚠ Could not parse spreadsheet ID from URL.")
        return

    # Auth scopes for Sheets and Drive
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)

    # Get first worksheet's sheetId via gspread
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_url(sheet_url)
    ws = sh.get_worksheet(0)
    sheet_id = ws._properties.get("sheetId")
    if sheet_id is None:
        print("⚠ Could not determine sheetId for first worksheet.")
        return

    service = build("sheets", "v4", credentials=creds)
    body = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                    }
                }
            }
        ]
    }

def retry_batch_update(service, spreadsheet_id: str, body: dict, max_retries: int = 3, initial_delay: float = 2.0):
    """
    Execute Sheets batchUpdate with simple exponential backoff retries.
    Retries on HttpError 429/5xx and socket timeouts.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            return
        except HttpError as e:
            status = getattr(e, 'status_code', None)
            if status and (status == 429 or 500 <= status < 600):
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
            # For non-retriable or final attempt, re-raise
            raise
        except Exception as e:
            msg = str(e).lower()
            if ("timeout" in msg or "timed out" in msg) and attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise


if __name__ == "__main__":
    print("\n🚀 Starting Canada-wide ML/AI Job Scrape...")

    raw = scrape_all_jobs()

    if raw.empty:
        print("⚠ No jobs found. Try adjusting HOURS_OLD or search terms.")
        exit()

    cleaned = clean_results(raw)

    print(f"\n🧾 Total raw jobs scraped: {len(raw)}")
    print(f"✅ Total after cleaning & dedupe: {len(cleaned)}")

    sheet_url = os.getenv("SHEET_URL")
    creds_path = os.getenv("GSHEETS_CREDS_PATH", "service_account.json")

    save_two_sheets_to_google_sheets(
        today_df=cleaned,
        sheet_url=sheet_url,
        creds_path=creds_path,
    )

    # send email notification (requires Gmail app password)
    # Set your details here or read from env vars
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("MAIL_APP_PASSWORD")
    if gmail_app_password:
        gmail_app_password = gmail_app_password.replace(" ", "")  # app passwords must be 16 chars without spaces
    to_email = os.getenv("TO_EMAIL")

    if gmail_user and gmail_app_password and to_email:
        send_completion_email(to_email, sheet_url, gmail_user, gmail_app_password)
    else:
        print("⚠ Email not sent: missing GMAIL_USER/MAIL_APP_PASSWORD/TO_EMAIL in env.")

    print("\n✅ Scrape completed! Good luck with your applications!\n")
