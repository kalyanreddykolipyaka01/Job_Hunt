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
import socket

# ---------------------------------------------------------
# 🔧 OPTIMIZATION: Increase default timeout to 10 minutes
# This fixes "The read operation timed out" on large sheets
# ---------------------------------------------------------
socket.setdefaulttimeout(600)

from spam_filters import (
    SPAM_KEYWORDS,
    SPAM_COMPANIES,
    SPAM_DESCRIPTION_KEYWORDS,
)

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------
LOGS = []

def log(msg: str):
    """Prints to console and appends to global log list for email."""
    print(msg)
    LOGS.append(str(msg))

# =========================================================
# FAST JOB SCRAPING CONFIG (RESUME-ALIGNED)
# Roles: .NET / Backend / Full Stack / Azure (4–5 yrs)
# =========================================================

# ---------------------------------------------------------
# 🎯 SEARCH ROLES (STRONG 6 ONLY)
# ---------------------------------------------------------
SEARCH_TERMS = [
    "Senior .NET Developer",
    "Backend Engineer .NET",
    "Software Engineer .NET",
    ".NET Full Stack Developer",
    "Azure .NET Developer",
    "SDE II .NET",
]

# ---------------------------------------------------------
# 🌎 SEARCH LOCATIONS (USA + 6 STATES + TOP CITIES + REMOTE)
# ---------------------------------------------------------
LOCATIONS = [
    # Country-level (broad coverage)
    "USA",
    "United States",

    # Strong states (high .NET hiring volume)
    "Texas, USA",
    "California, USA",
    "Washington, USA",
    "Florida, USA",
    "North Carolina, USA",
    "Illinois, USA",

    # Top cities inside those states
    # Texas
    "Austin, TX",
    "Dallas, TX",
    "Houston, TX",

    # California
    "San Francisco, CA",
    "San Jose, CA",
    "Los Angeles, CA",
    "San Diego, CA",

    # Washington
    "Seattle, WA",
    "Redmond, WA",

    # Florida
    "Tampa, FL",
    "Orlando, FL",
    "Miami, FL",

    # North Carolina
    "Charlotte, NC",
    "Raleigh, NC",

    # Illinois
    "Chicago, IL",

    # Remote-friendly
    "Remote, USA",
]

# ---------------------------------------------------------
# 🌐 JOB SITES
# ---------------------------------------------------------
SITES = [
    "indeed",
    "linkedin",
]

# ---------------------------------------------------------
# ⚙️ SCRAPE SETTINGS
# ---------------------------------------------------------
RESULTS_WANTED = 25       # Reduced for speed
HOURS_OLD = 26            # 24 hours + buffer
COUNTRY = "USA"

# ---------------------------------------------------------
# 📁 OUTPUT (optional local)
# ---------------------------------------------------------
OUTPUT_DIR = "jobs_data"
MASTER_FILE = "usa_dotnet_jobs_master.csv"

# ---------------------------------------------------------
# 🔴 FILTERING (IMPORTED)
# ---------------------------------------------------------
# spam_filters.py must contain:
# - SPAM_KEYWORDS
# - SPAM_COMPANIES
# - SPAM_DESCRIPTION_KEYWORDS


def scrape_all_jobs() -> pd.DataFrame:
    all_results = []

    for search in SEARCH_TERMS:
        for loc in LOCATIONS:
            log(f"🔍 Searching '{search}' in '{loc}'...")

            try:
                jobs = scrape_jobs(
                    site_name=SITES,
                    search_term=search,
                    location=loc,
                    results_wanted=RESULTS_WANTED,
                    hours_old=HOURS_OLD,
                    country_indeed=COUNTRY,
                    linkedin_fetch_description=False,
                    verbose=0,
                )
                df = pd.DataFrame(jobs)

                if not df.empty:
                    df["search_term_used"] = search
                    df["location_used"] = loc
                    all_results.append(df)
                    log(f"   ✅ Found {len(df)} jobs")
                else:
                    log("   ⚠ Found 0 jobs")

            except Exception as e:
                log(f"❌ Error scraping {search} in {loc}: {e}")

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


def clean_results(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    if "title" in df.columns:
        df["title"] = df["title"].astype(str).str.strip()

    spam_keywords_lower = [kw.lower() for kw in SPAM_KEYWORDS]
    spam_companies_lower = [kw.lower() for kw in SPAM_COMPANIES]
    spam_desc_lower = [kw.lower() for kw in SPAM_DESCRIPTION_KEYWORDS]

    def contains_spam_title(text) -> bool:
        t = str(text).lower()
        return any(kw in t for kw in spam_keywords_lower)

    def contains_spam_description(text) -> bool:
        t = str(text).lower()
        return any(kw in t for kw in spam_desc_lower)

    def company_is_spam(text) -> bool:
        t = str(text).lower()
        return any(kw in t for kw in spam_companies_lower)

    title_series = df.get("title", pd.Series("", index=df.index))
    desc_series = df.get("description", pd.Series("", index=df.index))
    comp_series = df.get("company", pd.Series("", index=df.index))

    mask = ~(
        title_series.apply(contains_spam_title) |
        desc_series.apply(contains_spam_description) |
        comp_series.apply(company_is_spam)
    )
    df = df[mask].copy()

    # Dedupe
    if "job_url" in df.columns:
        df.drop_duplicates(subset=["job_url"], inplace=True)

    # Sort newest first
    if "date_posted" in df.columns:
        df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
        df.sort_values("date_posted", ascending=False, inplace=True)

    return df


def _get_or_create_worksheet(sh, title, rows=100, cols=30):
    for w in sh.worksheets():
        if w.title == title:
            return w
    return sh.add_worksheet(title=title, rows=rows, cols=cols)


def apply_sheet_formatting(service, spreadsheet_id, sheet_id, df: pd.DataFrame):
    """Applies formatting in a single batch request."""
    requests = []

    # Row height
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": 0},
            "properties": {"pixelSize": 21},
            "fields": "pixelSize",
        }
    })

    # Auto-fit columns
    requests.append({
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": len(df.columns)
            }
        }
    })

    # Fixed widths
    fixed_100 = ["job_url_direct", "company_logo", "description", "emails", "company_url", "company_url_direct", "company_description"]
    for col_name in fixed_100:
        if col_name in df.columns:
            idx = df.columns.get_loc(col_name)
            requests.append({
                "updateDimensionProperties": {
                    "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": idx, "endIndex": idx + 1},
                    "properties": {"pixelSize": 100},
                    "fields": "pixelSize",
                }
            })

    fixed_250 = ["title", "company"]
    for col_name in fixed_250:
        if col_name in df.columns:
            idx = df.columns.get_loc(col_name)
            requests.append({
                "updateDimensionProperties": {
                    "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": idx, "endIndex": idx + 1},
                    "properties": {"pixelSize": 250},
                    "fields": "pixelSize",
                }
            })

    # Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"
        }
    })

    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        log(f"✨ Formatting applied to sheet ID {sheet_id}")
    except Exception as e:
        log(f"⚠ Formatting failed for sheet ID {sheet_id}: {e}")


def save_two_sheets_to_google_sheets(today_df: pd.DataFrame, sheet_url: str, creds_path: str):
    today_df = today_df.dropna(axis=1, how="all")

    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_url(sheet_url)
    spreadsheet_id = sh.id

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    now = datetime.now(ZoneInfo("America/Chicago"))
    today_name = f"Today-{now.strftime('%Y%m%d')}"
    master_name = "Master"

    ws_master = _get_or_create_worksheet(sh, master_name, rows=len(today_df) + 50, cols=len(today_df.columns) + 5)

    existing_master = pd.DataFrame()
    try:
        existing_master = pd.DataFrame(ws_master.get_all_records())
    except Exception:
        pass

    if not existing_master.empty and "job_url" in existing_master.columns and "job_url" in today_df.columns:
        existing_urls = set(existing_master["job_url"].astype(str))
        new_jobs_df = today_df[~today_df["job_url"].astype(str).isin(existing_urls)].copy()
        log(f"🔍 Found {len(new_jobs_df)} new jobs not in Master.")
    else:
        new_jobs_df = today_df.copy()
        log(f"🔍 Master empty or missing URL column. All {len(today_df)} jobs treated as new.")

    ws_today = _get_or_create_worksheet(sh, today_name, rows=len(new_jobs_df) + 50, cols=len(today_df.columns) + 5)

    ws_today.clear()
    set_with_dataframe(ws_today, new_jobs_df)

    if not existing_master.empty:
        combined = pd.concat([existing_master, new_jobs_df], ignore_index=True)
        if "job_url" in combined.columns:
            combined.drop_duplicates(subset=["job_url"], inplace=True)
    else:
        combined = new_jobs_df

    if "date_posted" in combined.columns:
        combined["date_posted"] = pd.to_datetime(combined["date_posted"], errors="coerce")
        combined.sort_values("date_posted", ascending=False, inplace=True)

    ws_master.clear()
    set_with_dataframe(ws_master, combined)

    log(f"✅ Saved to Google Sheets: {sh.title} → [{master_name}] and [{today_name}]")

    if not new_jobs_df.empty:
        apply_sheet_formatting(service, spreadsheet_id, ws_today.id, new_jobs_df)
    apply_sheet_formatting(service, spreadsheet_id, ws_master.id, combined)


def send_completion_email(to_email: str, sheet_url: str, gmail_user: str, gmail_app_password: str):
    try:
        yag = yagmail.SMTP(gmail_user, gmail_app_password)
        subject = "Job Scraping Completed"
        body = [
            "Your job scraping run has completed successfully.",
            "",
            f"Google Sheets link: {sheet_url}",
            "",
            "---------------------------------------------------",
            "EXECUTION LOGS:",
            "---------------------------------------------------",
            "\n".join(LOGS),
            "",
            "✅ Scrape completed! Good luck with your applications!"
        ]
        yag.send(to=to_email, subject=subject, contents=body)
        log(f"📧 Completion email sent to {to_email}")
    except Exception as e:
        log(f"⚠ Failed to send email: {e}")


if __name__ == "__main__":
    log("🚀 Starting USA-wide .NET Job Scrape...")

    raw = scrape_all_jobs()
    if raw.empty:
        log("⚠ No jobs found. Try adjusting HOURS_OLD or search terms.")
        raise SystemExit(0)

    cleaned = clean_results(raw)
    log(f"🧾 Total raw jobs scraped: {len(raw)}")
    log(f"✅ Total after cleaning & dedupe: {len(cleaned)}")

    sheet_url = os.getenv("SHEET_URL")
    creds_path = os.getenv("GSHEETS_CREDS_PATH", "service_account.json")

    if not sheet_url:
        log("❌ SHEET_URL is missing in .env")
        raise SystemExit(1)

    save_two_sheets_to_google_sheets(today_df=cleaned, sheet_url=sheet_url, creds_path=creds_path)

    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("MAIL_APP_PASSWORD")
    if gmail_app_password:
        gmail_app_password = gmail_app_password.replace(" ", "")
    to_email = os.getenv("TO_EMAIL")

    if gmail_user and gmail_app_password and to_email:
        send_completion_email(to_email, sheet_url, gmail_user, gmail_app_password)
    else:
        log("⚠ Email not sent: missing GMAIL_USER/MAIL_APP_PASSWORD/TO_EMAIL in env.")

    log("✅ Scrape completed! Good luck with your applications!")
