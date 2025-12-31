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
import socket
from googleapiclient.errors import HttpError

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

def log(msg):
    """Prints to console and appends to global log list for email."""
    print(msg)
    LOGS.append(str(msg))

# =========================================================
# FULL JOB SCRAPING CONFIG
# Profile-aligned: .NET Full Stack Developer (4–5 yrs)
# Stack: C#, .NET 8/6, ASP.NET Core, Web API, Azure, AWS,
#        Microservices, React, Angular, Docker, CI/CD
# =========================================================

# ---------------------------------------------------------
# 🎯 SEARCH ROLES (STRICTLY BASED ON YOUR RESUME)
# ---------------------------------------------------------
SEARCH_TERMS = [
    # Core .NET / C#
    ".NET Developer",
    "C# Developer",
    ".NET Software Engineer",
    "Software Engineer .NET",
    "Software Developer .NET",
    ".NET Application Developer",
    "C# Application Developer",

    # ASP.NET Core / Web API
    "ASP.NET Core Developer",
    "ASP.NET Core Web API Developer",
    ".NET Web API Developer",
    "C# API Developer",
    "REST API Developer .NET",

    # Backend-focused
    "Backend .NET Developer",
    "C# Backend Developer",
    ".NET Backend Engineer",
    "Backend Software Engineer .NET",

    # Full Stack (React / Angular)
    ".NET Full Stack Developer",
    "Full Stack Developer .NET",
    "Full Stack Engineer .NET",
    "Full Stack Software Engineer .NET",
    "React .NET Developer",
    "Angular .NET Developer",
    "Full Stack C# Developer",

    # Cloud / Azure / AWS
    "Azure .NET Developer",
    "Azure Backend Developer",
    "Azure Software Engineer .NET",
    "Cloud Developer .NET",
    "Cloud Software Engineer .NET",
    "AWS .NET Developer",
    "AWS Backend Developer",

    # Microservices / Distributed Systems
    "Microservices .NET Developer",
    ".NET Microservices Developer",
    "Distributed Systems Engineer .NET",

    # DevOps-aware .NET
    ".NET Developer Azure DevOps",
    ".NET Developer CI/CD",
    ".NET Developer Docker",

    # Enterprise / Banking-style titles
    "Enterprise .NET Developer",
    "Enterprise Software Engineer .NET",
    "Banking Application Developer .NET",

    # Generic (filtered later by experience + stack)
    "Software Engineer",
    "Backend Software Engineer",
    "Full Stack Software Engineer",
]

# ---------------------------------------------------------
# 🌎 SEARCH LOCATIONS (MAX JOB COVERAGE – USA)
# ---------------------------------------------------------
LOCATIONS = [
    "United States",

    # Major tech states
    "California, USA",
    "Texas, USA",
    "Washington, USA",
    "New York, USA",
    "Virginia, USA",
    "Georgia, USA",
    "Illinois, USA",
    "Massachusetts, USA",
    "Colorado, USA",
    "Arizona, USA",
    "Florida, USA",
    "North Carolina, USA",
    "New Jersey, USA",
    "Pennsylvania, USA",
    "Ohio, USA",
    "Minnesota, USA",
    "Wisconsin, USA",
    "Michigan, USA",

    # Texas metros
    "Austin, TX",
    "Dallas, TX",
    "Houston, TX",
    "San Antonio, TX",
    "Plano, TX",
    "Irving, TX",

    # California metros
    "San Francisco, CA",
    "San Jose, CA",
    "Sunnyvale, CA",
    "Santa Clara, CA",
    "Mountain View, CA",
    "Los Angeles, CA",
    "San Diego, CA",
    "Irvine, CA",

    # Washington (Azure-heavy)
    "Seattle, WA",
    "Redmond, WA",
    "Bellevue, WA",

    # New York / NJ
    "New York, NY",
    "Manhattan, NY",
    "Brooklyn, NY",
    "Jersey City, NJ",

    # Virginia / DMV
    "Reston, VA",
    "Herndon, VA",
    "Arlington, VA",
    "Tysons, VA",
    "Fairfax, VA",

    # Illinois
    "Chicago, IL",
    "Naperville, IL",

    # North Carolina
    "Charlotte, NC",
    "Raleigh, NC",
    "Durham, NC",

    # Florida
    "Orlando, FL",
    "Tampa, FL",
    "Miami, FL",
    "Jacksonville, FL",

    # Georgia
    "Atlanta, GA",

    # Massachusetts
    "Boston, MA",
    "Cambridge, MA",

    # Colorado
    "Denver, CO",
    "Boulder, CO",

    # Arizona
    "Phoenix, AZ",
    "Tempe, AZ",

    # Midwest .NET strongholds
    "Kansas City, MO",
    "Kansas City, KS",
    "St. Louis, MO",
    "Columbus, OH",
    "Cleveland, OH",
    "Cincinnati, OH",
    "Minneapolis, MN",
    "Madison, WI",
    "Milwaukee, WI",
    "Detroit, MI",

    # Remote-friendly
    "Remote, USA",
    "United States (Remote)",
    "Hybrid, USA",
]

# ---------------------------------------------------------
# 🌐 JOB SITES
# ---------------------------------------------------------
# indeed   -> safest
# linkedin -> may require cookies / throttling
# glassdoor -> may block aggressively
# jobright -> good if supported by your scraper

SITES = [
    "indeed",
    "linkedin",
]

# ---------------------------------------------------------
# ⚙️ SCRAPE SETTINGS
# ---------------------------------------------------------
RESULTS_WANTED = 50
HOURS_OLD = 26          # 24 hours + buffer
COUNTRY = "USA"

# ---------------------------------------------------------
# 📁 OUTPUT
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
# - STRICT experience filter: ONLY 4–5 years
#
# Example usage in main script:
# from spam_filters import should_skip_job
#
# if should_skip_job(title, company, description)[0]:
#     continue


def scrape_all_jobs():
    all_results = []

    for search in SEARCH_TERMS:
        for loc in LOCATIONS:
            print(f"\n🔍 Searching '{search}' in '{loc}'...")

            try:
                jobs = scrape_jobs(
                    site_name=SITES,
                    search_term=search,
                    location=loc,
                    results_wanted=RESULTS_WANTED,
                    hours_old=HOURS_OLD,
                    country_indeed=COUNTRY,
                    linkedin_fetch_description=False,
                    verbose=1,
                )
                df = pd.DataFrame(jobs)

                # Store metadata for analysis later
                if not df.empty:
                    df["search_term_used"] = search
                    df["location_used"] = loc
                    all_results.append(df)

            except Exception as e:
                print(f"❌ Error scraping {search} in {loc}: {e}")

    if not all_results:
        return pd.DataFrame()

    final_df = pd.concat(all_results, ignore_index=True)
    return final_df


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


def _get_or_create_worksheet(sh, title, rows=100, cols=30):
    ws = None
    for w in sh.worksheets():
        if w.title == title:
            ws = w
            break
    if ws is None:
        ws = sh.add_worksheet(title=title, rows=rows, cols=cols)
    return ws

def apply_sheet_formatting(service, spreadsheet_id, sheet_id, df):
    """
    Applies all formatting (Auto-fit, Row Height, Column Widths) in a SINGLE batch request.
    This is much faster and prevents timeouts.
    """
    requests = []

    # 1. Set Row Height to 21px for all rows
    requests.append({
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": 0,
            },
            "properties": {"pixelSize": 21},
            "fields": "pixelSize",
        }
    })

    # 2. Auto-fit all columns
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

    # 3. Set fixed width (100px) for specific large columns
    target_cols = ["job_url_direct", "company_logo", "description", "emails", "company_url", "company_url_direct", "company_description"]
    for col_name in target_cols:
        if col_name in df.columns:
            try:
                idx = df.columns.get_loc(col_name)
                requests.append({
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": idx,
                            "endIndex": idx + 1,
                        },
                        "properties": {"pixelSize": 100},
                        "fields": "pixelSize",
                    }
                })
            except Exception:
                pass # Column might not exist or be duplicate

    # 4. Set fixed width (250px) for specific large columns
    target_cols = ["title", "company"]
    for col_name in target_cols:
        if col_name in df.columns:
            try:
                idx = df.columns.get_loc(col_name)
                requests.append({
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": idx,
                            "endIndex": idx + 1,
                        },
                        "properties": {"pixelSize": 250},
                        "fields": "pixelSize",
                    }
                })
            except Exception:
                pass # Column might not exist or be duplicate

    # 5. Freeze Header Row
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {"frozenRowCount": 1}
            },
            "fields": "gridProperties.frozenRowCount"
        }
    })

    body = {"requests": requests}
    
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        log(f"✨ Formatting applied to sheet ID {sheet_id}")
    except Exception as e:
        log(f"⚠ Formatting failed for sheet ID {sheet_id}: {e}")


def save_two_sheets_to_google_sheets(today_df, sheet_url, creds_path):
    # Drop fully empty columns
    today_df = today_df.dropna(axis=1, how='all')

    # Auth and open
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_url(sheet_url)
    spreadsheet_id = sh.id
    
    # Build Sheets API service
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    # Worksheet names
    toronto_now = datetime.now(ZoneInfo("America/Toronto"))
    today_name = f"Today-{toronto_now.strftime('%Y%m%d')}"
    master_name = "Master"

    # Ensure Master worksheet exists
    ws_master = _get_or_create_worksheet(
        sh, master_name, rows=len(today_df)+50, cols=len(today_df.columns)+5
    )

    # --- READ EXISTING MASTER ---
    existing_master = pd.DataFrame()
    try:
        existing_master = pd.DataFrame(ws_master.get_all_records())
    except Exception:
        pass

    # --- FILTER NEW JOBS ---
    # Only keep jobs in today_df that are NOT in existing_master
    if not existing_master.empty and "job_url" in existing_master.columns and "job_url" in today_df.columns:
        existing_urls = set(existing_master["job_url"].astype(str))
        new_jobs_df = today_df[~today_df["job_url"].astype(str).isin(existing_urls)].copy()
        log(f"🔍 Found {len(new_jobs_df)} new jobs not in Master.")
    else:
        new_jobs_df = today_df.copy()
        log(f"🔍 Master empty or missing URL column. All {len(new_jobs_df)} jobs treated as new.")

    # Ensure Today worksheet exists
    ws_today = _get_or_create_worksheet(
        sh, today_name, rows=len(new_jobs_df)+50, cols=len(today_df.columns)+5
    )

    # --- WRITE TODAY SHEET ---
    ws_today.clear()
    set_with_dataframe(ws_today, new_jobs_df)
    
    # --- WRITE MASTER SHEET ---
    if not existing_master.empty:
        combined = pd.concat([existing_master, new_jobs_df], ignore_index=True)
        # Dedupe just in case
        combined.drop_duplicates(subset=["job_url"], inplace=True)
    else:
        combined = new_jobs_df

    # Re-sort Master by date
    if "date_posted" in combined.columns:
        combined["date_posted"] = pd.to_datetime(combined["date_posted"], errors="coerce")
        combined.sort_values("date_posted", ascending=False, inplace=True)

    ws_master.clear()
    set_with_dataframe(ws_master, combined)

    log(f"✅ Saved to Google Sheets: {sh.title} → [{master_name}] and [{today_name}]")

    # --- APPLY FORMATTING (Optimized) ---
    if not new_jobs_df.empty:
        apply_sheet_formatting(service, spreadsheet_id, ws_today.id, new_jobs_df)
    
    apply_sheet_formatting(service, spreadsheet_id, ws_master.id, combined)


def send_completion_email(to_email: str, sheet_url: str, gmail_user: str, gmail_app_password: str):
    try:
        yag = yagmail.SMTP(gmail_user, gmail_app_password)
        subject = "Job Scraping Completed"
        
        # Join logs for the email body
        log_content = "\n".join(LOGS)
        
        body = [
            "Your job scraping run has completed successfully.",
            "",
            f"Google Sheets link: {sheet_url}",
            "",
            "---------------------------------------------------",
            "EXECUTION LOGS:",
            "---------------------------------------------------",
            log_content,
            "",
            "✅ Scrape completed! Good luck with your applications!"
        ]
        yag.send(to=to_email, subject=subject, contents=body)
        log(f"📧 Completion email sent to {to_email}")
    except Exception as e:
        log(f"⚠ Failed to send email: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Canada-wide ML/AI Job Scrape...")

    raw = scrape_all_jobs()

    if raw.empty:
        log("⚠ No jobs found. Try adjusting HOURS_OLD or search terms.")
        exit()

    cleaned = clean_results(raw)

    log(f"\n🧾 Total raw jobs scraped: {len(raw)}")
    log(f"✅ Total after cleaning & dedupe: {len(cleaned)}")

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
        log("⚠ Email not sent: missing GMAIL_USER/MAIL_APP_PASSWORD/TO_EMAIL in env.")

    log("\n✅ Scrape completed! Good luck with your applications!\n")
