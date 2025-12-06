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

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------
# PERSONALIZED CONFIG 
# ---------------------------------------------------------

SEARCH_TERMS = [
    "machine learning engineer",
    "ml engineer",
    "mlops engineer",
    "data engineer",
    "data scientist",
    "data analyst",
    "ai engineer",
    "llm engineer",
    "nlp engineer",
    "python",
    "Artificial Intelligence",
    "numpy, pandas, scikit learn, matplotlib, TensorFlow",
    "backend developer fastapi",
    "RAG (Retrival Augmented Generation)",
    "MCP (Model Context Protocol)",
    "HuggingFace",
    "React",
    "Next.js",
    "Sentiment Analysis"
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

SPAM_KEYWORDS = [
    # Seniority Levels (5+ years required)
    "senior", "sr.", "sr ", "principal", "lead", "staff", 
    "director", "head of", "vice president", "vp", "chief", 
    "executive", "distinguished", "fellow",
    
    # Experience Level Indicators
    "intermediate", "5+ years", "5 years", "6+ years", "7+ years", 
    "8+ years", "10+ years", "experienced professional",
    
    # Management/Leadership
    "manager", "mgr", "management", "supervisor", "team lead",
    
    # Architecture (typically 8+ years)
    "architect", "architecture lead", "solutions architect",
    "enterprise architect", "technical architect",
    
    # Specialized Roles Requiring Specific Degrees/Certifications
    "civil engineer", "mechanical engineer", "electrical engineer",
    "fpga engineer", "hardware engineer", "embedded systems",
    "industrial engineer", "chemical engineer", "process engineer",
    "broadcast", "manufacturing science", "production engineer", "III",
    
    # Professional Designations You Don't Have
    "p.eng", "p. eng", "professional engineer", "cpa", "chartered",
    "licensed professional", "registered engineer", "cfa",
    
    # Security Clearance Required
    "secret clearance", "top secret", "security clearance required",
    "clearance eligible", "defense", "military clearance",
    
    # Language Requirements
    "bilingual french", "fluent french", "french required",
    "french mandatory", "bilinguisme", "bilingue",
    
    # Business/Non-Technical Roles
    "product manager", "product management", "business analyst",
    "project manager", "program manager", "scrum master",
    "account manager", "sales", "marketing", "hr specialist",
    "people services", "recruitment", "talent acquisition",
    
    # Specialized Fields Outside Your Domain
    "Java Developer", "Video Editor", "Videographer", "devops lead", "site reliability lead", "infrastructure architect",
    "database administrator", "dba", "system administrator",
    "network engineer", "telecommunications", "telecom",
    "quality assurance lead", "qa lead", "test lead", "Android",
    
    # Academic/Research (PhD required)
    "research scientist", "research lead", "postdoc", "post-doctoral",
    
    # Internships/Co-op (if you want full-time only)
    "intern", "internship", "co-op", "co op", "student position",
    "summer student", "coop", "stage", "stagiaire",
    
    # Healthcare/Medical/Clinical
    "clinical", "healthcare practitioner", "medical", "pharmaceutical",
    "nursing", "therapy", "counseling",
    
    # Finance-Specific (requiring CFA/professional certifications)
    "portfolio manager", "investment analyst", "financial advisor",
    "wealth management",
    
    # Education/Teaching
    "professor", "instructor", "teacher", "tutor", "lecturer",
    "curriculum developer", "education specialist",
]

# Additional spam/fake companies filter (matches `company` column)
SPAM_COMPANIES = [
    "Prime Jobs", "Next Jobs", "Jobs Ai", "Get Hired", "Crossover",
    "Get Jobs", "Jobsmast", "Hiring Hub", "Tech Jobs Fast",
]

# Dedicated spam keywords for description (phrases common in spammy descriptions)
SPAM_DESCRIPTION_KEYWORDS = [
    "weekly payout",
    "quick money",
]

# ---------------------------------------------------------


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

    try:
        retry_batch_update(service, spreadsheet_id, body)
        print("🪄 Auto-fit columns applied.")
    except Exception as e:
        print(f"⚠ Auto-fit failed: {e}")

def _get_or_create_worksheet(sh, title, rows=100, cols=30):
    ws = None
    for w in sh.worksheets():
        if w.title == title:
            ws = w
            break
    if ws is None:
        ws = sh.add_worksheet(title=title, rows=rows, cols=cols)
    return ws

def save_two_sheets_to_google_sheets(today_df, sheet_url, creds_path):
    # Drop fully empty columns
    today_df = today_df.dropna(axis=1, how='all')

    # Auth and open
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_url(sheet_url)
    # Robust spreadsheet id from gspread (avoid brittle URL parsing)
    spreadsheet_id = sh.id
    # Build Sheets API service once and reuse
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    # Worksheet names
    # Use Toronto timezone for date in sheet name
    toronto_now = datetime.now(ZoneInfo("America/Toronto"))
    today_name = f"Today-{toronto_now.strftime('%Y%m%d')}"
    master_name = "Master"

    # Ensure worksheets exist sized roughly to data
    ws_today = _get_or_create_worksheet(
        sh,
        today_name,
        rows=max(100, len(today_df) + 50),
        cols=max(30, len(today_df.columns) + 5),
    )
    ws_master = _get_or_create_worksheet(
        sh,
        master_name,
        rows=max(100, len(today_df) + 50),  # Estimate for now
        cols=max(30, len(today_df.columns) + 5),
    )

    # Clear and write today's data
    ws_today.clear()
    set_with_dataframe(ws_today, today_df)
    # Freeze header row so Sheets recognizes row 1 as headers
    try:
        ws_today.freeze(rows=1)
    except Exception:
        pass

    # For Master: read existing, append today's, dedupe, and write back
    try:
        existing_master = pd.DataFrame(ws_master.get_all_records())
        if not existing_master.empty:
            combined = pd.concat([existing_master, today_df], ignore_index=True)
            combined.drop_duplicates(subset=["job_url"], inplace=True)
        else:
            combined = today_df
    except Exception:
        # If reading fails, just use today's data
        combined = today_df

    ws_master.clear()
    set_with_dataframe(ws_master, combined)
    # Freeze header row on Master as well
    try:
        ws_master.freeze(rows=1)
    except Exception:
        pass

    print(f"✅ Saved to Google Sheets: {sh.title} → [" + master_name + "] and [" + today_name + "]")

    # Auto-fit both worksheets
    for ws in (ws_master, ws_today):
        try:
            sheet_id = ws._properties.get("sheetId")
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
            retry_batch_update(service, spreadsheet_id, body)
            # Set row height to 21px for all existing rows (explicit endIndex)
            end_index = ws.row_count
            set_row_height_with_service(service, spreadsheet_id, sheet_id, end_index=end_index, pixel_size=21)

        except Exception as e:
            print(f"⚠ Auto-fit or row-height set failed for '{ws.title}': {e}")

    # After auto-fit, override specific columns to fixed 100px
    def column_indexes_from_names(df_cols: list[str], target_names: list[str]) -> list[int]:
        name_to_index = {name: idx for idx, name in enumerate(df_cols)}
        return [name_to_index[name] for name in target_names if name in name_to_index]

    target_cols = ["job_url_direct", "company_logo", "description"]

    # Today sheet fixed widths
    today_indexes = column_indexes_from_names(list(today_df.columns), target_cols)
    if today_indexes:
        try:
            set_column_widths_with_service(service, spreadsheet_id, ws_today._properties.get("sheetId"), today_indexes, pixel_size=100)
        except Exception as e:
            print(f"⚠ Failed to set column widths on '{ws_today.title}': {e}")

    # Master sheet fixed widths (based on combined DataFrame)
    try:
        combined_cols = list(combined.columns)
        master_indexes = column_indexes_from_names(combined_cols, target_cols)
        if master_indexes:
            set_column_widths_with_service(service, spreadsheet_id, ws_master._properties.get("sheetId"), master_indexes, pixel_size=100)
    except Exception as e:
        print(f"⚠ Failed to set column widths on '{ws_master.title}': {e}")


def send_completion_email(to_email: str, sheet_url: str, gmail_user: str, gmail_app_password: str):
    try:
        yag = yagmail.SMTP(gmail_user, gmail_app_password)
        subject = "Job Scraping Completed"
        body = [
            "Your job scraping run has completed successfully.",
            "",
            f"Google Sheets link: {sheet_url}",
        ]
        yag.send(to=to_email, subject=subject, contents=body)
        print(f"📧 Completion email sent to {to_email}")
    except Exception as e:
        print(f"⚠ Failed to send email: {e}")


def set_row_height_with_service(service, spreadsheet_id: str, sheet_id: int, end_index: int, pixel_size: int = 21):
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": 0,
                        "endIndex": end_index,
                    },
                    "properties": {"pixelSize": pixel_size},
                    "fields": "pixelSize",
                }
            }
        ]
    }
    retry_batch_update(service, spreadsheet_id, body)


def set_column_widths_with_service(service, spreadsheet_id: str, sheet_id: int, column_indexes: list[int], pixel_size: int = 100):
    requests = []
    for idx in column_indexes:
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": idx,
                    "endIndex": idx + 1,
                },
                "properties": {"pixelSize": pixel_size},
                "fields": "pixelSize",
            }
        })

    if not requests:
        return

    body = {"requests": requests}
    retry_batch_update(service, spreadsheet_id, body)

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
