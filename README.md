# Job Hunt — Full Setup Guide

Automated daily ML/AI job scraper for Canada. It scrapes job boards, filters out senior/irrelevant roles, uploads results to Google Sheets (Master + Today tabs), formats the sheet (auto-fit columns, fixed widths for selected columns, row height, freeze header), and sends a completion email.

This guide walks someone who forked the repo through step-by-step setup from scratch.

## 1) Fork and Clone
- Fork this repository to your GitHub account.
- Clone the fork to your local machine.

```pwsh
git clone <your-fork-url>
cd Job_Hunt
```

## 2) Create a Google Sheet
- Go to Google Sheets and create a new spreadsheet.
- Note the spreadsheet URL (it looks like `https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#...`).
- The script will create a tab named `Master` and a daily tab like `Today-YYYYMMDD` automatically.

## 3) Create a Google Cloud Service Account + JSON Key
You need a service account with access to Google Sheets.

- In Google Cloud Console, create (or choose) a project.
- Enable APIs: Google Sheets API and Google Drive API.
- Create a Service Account.
- Create a JSON key for this Service Account and download it.
- The Service Account has an email like `sa-name@project-id.iam.gserviceaccount.com`.

Detailed Console steps:
- Go to `https://console.cloud.google.com/` and select your project (or create one).
- Open “APIs & Services” → “Library”:
	- Search and enable `Google Sheets API`.
	- Search and enable `Google Drive API`.
- Open “IAM & Admin” → “Service Accounts” → “Create service account”:
	- Name it (e.g., `sheets-uploader`) and click “Create and continue”.
	- Optional: grant basic role `Editor` for simplicity (scopes are enforced by key usage in this app).
	- Click “Done”.
- In the service account list, click the service account → “Keys” → “Add key” → “Create new key” → choose `JSON` → “Create”.
	- Save the downloaded JSON; this is the content you will paste into the GitHub secret `GSHEETS_CREDS_JSON`.
	- The file contains fields like `client_email` which is your service account email.

Share the Sheet with the Service Account:
- Open your spreadsheet.
- Click Share and add the Service Account email with Editor permission.

## 4) Prepare GitHub Actions Secrets
Open your fork’s repository on GitHub → Settings → Secrets and variables → Actions → New repository secret.

Add the following secrets:
- `GSHEETS_CREDS_JSON`: Paste the full JSON content of the service account key file.
- `SHEET_URL` & `GSHEETS_CREDS_PATH`: The Google Sheet URL you created.
- `GMAIL_USER`: Your Gmail address (sender).
- `MAIL_APP_PASSWORD`: Your Gmail App Password (not your regular password). Create one in Google Account → Security → App passwords.
- `TO_EMAIL`: The email to receive the completion notification.

Notes:
- The workflow writes `service_account.json` from `GSHEETS_CREDS_JSON` at runtime and validates it.
- Your Sheet must be shared with the Service Account email, otherwise uploads will fail with permissions errors.

### Create a Gmail App Password
Gmail requires an App Password when sending mail from scripts.

Prerequisites:
- Two-factor authentication (2-Step Verification) must be enabled for your Google account.

Steps:
1. Open `https://myaccount.google.com/security`.
2. Under `"Signing in to Google"`, enable `2-Step Verification` if not already on.
3. After enabling, go back to `Security` and click `App passwords`.
4. Sign in if prompted. In `Select app`, choose `Mail`; in `Select device`, choose `Other (Custom name)` and enter something like `Job_Hunt`.
5. Click `Generate`. Google shows a 16-character password (e.g., `abcd efgh ijkl mnop`).
6. Copy that value and remove spaces (the script also strips spaces automatically). Use this as `MAIL_APP_PASSWORD`.

Tips:
- If `App passwords` doesn’t appear, ensure 2-Step Verification is enabled and your account type supports app passwords.
- App passwords can be revoked anytime under the same `App passwords` page.

## 5) Local Environment (Optional)
You can also run locally for testing.

Install dependencies:
```pwsh
pip install -r requirements.txt
```

Provide environment variables via `.env` (optional for local runs):
```pwsh
"SHEET_URL=<your-google-sheet-url>"
"GSHEETS_CREDS_PATH=service_account.json"  # path to local JSON key if you want to run locally
"GMAIL_USER=<your-gmail>"
"MAIL_APP_PASSWORD=<your-gmail-app-password>"  # 16 chars, no spaces
"TO_EMAIL=<recipient-email>"
```

Run the scraper:
```pwsh
python job_scraper.py
```

## 6) Configure Automation (GitHub Actions)
The workflow file is at `.github/workflows/scrape.yml`.

- It installs Python dependencies and runs `python job_scraper.py` with the secrets you configured.
- Schedule: The workflow is set to run daily at approximately 8:00 AM Toronto time (UTC-based scheduling). If DST affects exact timing, you can add or adjust cron entries.
- You can also trigger it manually: Actions tab → `Daily Job Scrape` → Run workflow.

## 7) What the Script Does
- Scrapes jobs from Indeed and LinkedIn using your configured search terms and locations.
- Filters out spam/irrelevant roles:
	- Title spam via `SPAM_KEYWORDS` (e.g., senior/manager roles).
	- Company spam via `SPAM_COMPANIES`.
	- Description spam via `SPAM_DESCRIPTION_KEYWORDS` (common phrases).
- Deduplicates by `job_url` and sorts by newest.
- Writes to Google Sheets:
	- Creates/updates `Master` and `Today-YYYYMMDD` tabs.
	- Auto-fit columns.
	- Sets fixed widths (100px) for `job_url_direct`, `company_logo`, and `description`.
	- Sets row height to 21px and freezes the header row.
- Emails a completion notice to `TO_EMAIL`.

## 8) Customization
- Edit `SEARCH_TERMS`, `LOCATIONS`, and `SITES` in `job_scraper.py` to change sources and queries.
- Update spam lists:
	- `SPAM_KEYWORDS` (title-based filtering).
	- `SPAM_COMPANIES` (matches `company` column).
	- `SPAM_DESCRIPTION_KEYWORDS` (description-specific phrases).
- Adjust `RESULTS_WANTED` and `HOURS_OLD` for volume and recency.

## 9) Common Pitfalls
- "Spreadsheet not found" → Use the Sheet URL and ensure the Service Account email has Editor access.
- JSON decode error in Actions → Verify `GSHEETS_CREDS_JSON` secret contains valid JSON with no extra wrapping/quotes.
- Gmail send fails → Use a Gmail App Password, not your login password; confirm `GMAIL_USER`, `MAIL_APP_PASSWORD`, and `TO_EMAIL` secrets are set.
- Missing columns → The script safely skips width overrides for columns that aren’t present in the current run.

## 10) Verify and Monitor
- Check the Actions tab for scheduled and manual runs.
- Open the spreadsheet to see `Master` and the latest `Today-YYYYMMDD` tab.
- Confirm completion emails arrive at `TO_EMAIL`.

---

If you want me to set exact 8:00 AM Toronto daily without seasonal duplication, I can switch the workflow to an hourly cron with a timezone gate so it executes only when local time is 08:00.
