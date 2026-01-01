"""
Centralized spam + experience + title filters for job scraping.

Your requirements (final):
1) Keep ONLY these exact role families (title allowlist):
   - Senior .NET Developer
   - Backend Engineer .NET
   - Software Engineer .NET
   - .NET Full Stack Developer
   - Azure .NET Developer
   - SDE II .NET

2) Reject Principal+ roles (and similar): Principal, Staff, Lead, Architect, Director, VP, etc.
   (Senior is OK. SDE II is OK.)

3) Experience: ONLY 4–5 years
   - Reject <4 (0–3, junior, entry, associate, etc.)
   - Reject >5 (6+, staff/principal etc.)
   - Reject ranges that include <4 (2-5, 3-5, 1-4, etc.)
   - Require an explicit 4/5 mention (strict).

How to use:
- Import this file in your scraper
- Call `should_skip_job(title, company, description)` for each job
"""

from __future__ import annotations
import re
from typing import Tuple


# =========================
# 1) SPAM / MISMATCH FILTERS
# =========================

SPAM_KEYWORDS = [
    # Extreme seniority / exec
    "distinguished", "chief architect", "vp engineering", "head of engineering",
    "director of engineering", "cto",

    # Wrong stacks / non-.NET primary
    "php", "laravel",
    "ruby", "ruby on rails", "rails",
    "django", "flask",
    "spring boot", "kotlin",
    "golang", "go developer",
    "rust",
    "wordpress",

    # Mobile / embedded / hardware
    "embedded", "firmware", "fpga", "hardware engineer", "iot", "robotics",

    # Non-engineering roles
    "product manager", "project manager", "program manager",
    "scrum master", "delivery manager", "business analyst",
    "account manager", "sales", "marketing", "hr", "recruiter",
    "talent acquisition",

    # DBA / infra-only
    "database administrator", "dba", "system administrator",
    "network engineer", "telecom", "infrastructure architect",

    # QA-only roles
    "qa engineer", "qa analyst", "test engineer", "automation tester",
    "sdet", "qa lead", "test lead",

    # Design / media
    "ui designer", "ux designer", "graphic designer", "video editor", "videographer",

    # Academic / research
    "research scientist", "postdoc", "phd",

    # Internship / student (you want full-time)
    "intern", "internship", "co-op", "co op", "student", "trainee", "apprentice",
    "new grad", "graduate",

    # Clearance
    "security clearance", "top secret", "ts/sci", "clearance required",

    # Language requirements
    "french required", "bilingual french", "fluent french",
]

SPAM_COMPANIES = [
    "Prime Jobs", "Next Jobs", "Jobs Ai", "Get Hired", "Crossover", "Recruit Loop",
    "Talent Pulse", "Get Jobs", "Jobsmast", "Hiring Hub", "Tech Jobs Fast",
    "YO IT CONSULTING", "DataAnnotation", "Mercor", "Talent Connect", "Talent Orbit",
    "S M Software Solutions Inc", "Lumenalta", "Crossing Hurdles", "Hire Sync",
    "Hire Wave", "HireFast", "Work Vista", "Hunter Bond", "Twine", "Talently",
    "Gnapi Technologies", "Peroptyx", "FutureSight", "HiJob.work",
]

SPAM_DESCRIPTION_KEYWORDS = [
    "quick money", "quick cash", "easy money",
    "get paid instantly", "commission only", "unlimited commission",
    "pay per task", "training fee", "registration fee",
    "telegram", "whatsapp", "crypto payment",
]


# =========================
# 2) TITLE FILTERS (YOUR EXACT ROLES + BLOCK PRINCIPAL+)
# =========================

# Reject principal+ roles (and similar). Senior is OK. SDE II is OK.
BLOCK_PRINCIPAL_PLUS_REGEX = re.compile(
    r"""
    \b(
        principal |
        staff |
        lead |
        tech\s*lead |
        team\s*lead |
        architect |
        sr\.?\s*staff |
        distinguished |
        fellow |
        director |
        head |
        vp |
        vice\s+president |
        cto
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Title must match one of your role families
ROLE_ALLOWLIST_REGEX = re.compile(
    r"""
    ^\s*(
        senior\s+\.net\s+developer |
        backend\s+engineer\s+\.net |
        software\s+engineer\s+\.net |
        \.net\s+full\s*stack\s+developer |
        azure\s+\.net\s+developer |
        sde[\s\-]*(ii|2)\s+\.net
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ======================================
# 3) EXPERIENCE FILTER (ONLY 4–5 YEARS)
# ======================================

# allow 4–5 years mentions (strict)
ALLOW_4_5_REGEX = re.compile(
    r"""
    (
        \b(minimum|at\s*least)\s*(4|5)\s*(years|yrs)\b |
        \b(4|5)\s*(years|yrs)\s*of\s*experience\b |
        \b(4|5)\s*[\+]\s*(years|yrs)\b |
        \b4\s*[-–to]+\s*5\s*(years|yrs)\b |
        \b4\s*(years|yrs)\b |
        \b5\s*(years|yrs)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# block any explicit "0–3 years" requirement
BLOCK_LOW_REGEX = re.compile(
    r"""
    (
        \b(0|1|2|3)\s*[\+]\s*(years|yrs)\b |
        \b(0|1|2|3)\s*(years|yrs)\b |
        \bentry[-\s]*level\b |
        \bjunior\b |
        \bjr\b |
        \bassociate\b |
        \bnew\s*grad\b |
        \bgraduate\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# block any explicit "6+ years" or higher requirement
BLOCK_HIGH_REGEX = re.compile(
    r"""
    (
        \b(6|7|8|9)\s*[\+]\s*(years|yrs)\b |
        \b(6|7|8|9)\s*(years|yrs)\b |
        \b1[0-9]\s*[\+]\s*(years|yrs)\b |
        \b1[0-9]\s*(years|yrs)\b |
        \b15\s*[\+]\s*(years|yrs)\b |
        \bstaff\b |
        \bprincipal\b |
        \bdistinguished\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# block ranges that include <4, e.g., "2-5 years", "3 to 5 years", "3-5+ years"
BLOCK_RANGE_INCLUDES_LOW_REGEX = re.compile(
    r"""
    (
        \b(0|1|2|3)\s*[-–to]+\s*(4|5)\s*(\+?\s*)?(years|yrs)\b |
        \b(0|1|2|3)\s*to\s*(4|5)\s*(\+?\s*)?(years|yrs)\b |
        \b(0|1|2|3)\s*[-–to]+\s*(5|6|7|8|9|1[0-9])\s*(\+?\s*)?(years|yrs)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# =========================
# 4) .NET ROLE POSITIVE HINT
# =========================
#
# Keeps job only if title/description contains .NET signals.
#
REQUIRE_DOTNET_SIGNAL = True

DOTNET_SIGNALS = [
    ".net", "dotnet", "dot net",
    "c#", "c sharp",
    "asp.net", "aspnet", "asp.net core", ".net core",
    "entity framework", "ef core",
    "web api", "minimal api", "mvc",
]


# =========================
# 5) CORE FILTER FUNCTIONS
# =========================

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _normalize_company(s: str | None) -> str:
    t = _norm(s)
    t = re.sub(r"[\.,\(\)\-_/]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

# Precompile patterns (reduce false positives for short tokens like "hr")
_SPAM_PATTERNS = [
    # If keyword contains spaces, treat as substring; else require whole-word match
    re.compile(re.escape(k.lower())) if " " in k else re.compile(rf"\b{re.escape(k.lower())}\b")
    for k in SPAM_KEYWORDS
]
_DESC_SPAM_PATTERNS = [re.compile(re.escape(k.lower())) for k in SPAM_DESCRIPTION_KEYWORDS]

_SPAM_COMPANY_SET = {_normalize_company(c) for c in SPAM_COMPANIES}

def _matches_any_pattern(text: str, patterns: list[re.Pattern]) -> bool:
    t = _norm(text)
    return any(p.search(t) for p in patterns)

def matches_dotnet_signal(title: str, description: str) -> bool:
    text = f"{_norm(title)}\n{_norm(description)}"
    return any(sig in text for sig in DOTNET_SIGNALS)

def experience_is_4_to_5_only(description: str, title: str = "") -> Tuple[bool, str]:
    """
    Returns (is_match, reason)
    """
    text = f"{_norm(title)}\n{_norm(description)}"

    # Hard blocks first
    if BLOCK_LOW_REGEX.search(text):
        return False, "Rejected: experience too low / junior keywords"
    if BLOCK_HIGH_REGEX.search(text):
        return False, "Rejected: experience too high / staff/principal/6+ yrs"
    if BLOCK_RANGE_INCLUDES_LOW_REGEX.search(text):
        return False, "Rejected: range includes <4 years (e.g., 2-5, 3-5)"

    # Require explicit 4/5 year hit (strict)
    if not ALLOW_4_5_REGEX.search(text):
        return False, "Rejected: no explicit 4–5 years requirement found"

    return True, "Accepted: matches 4–5 years"

def should_skip_job(title: str, company: str, description: str) -> Tuple[bool, str]:
    """
    Returns (skip, reason)
    """
    t = _norm(title)
    d = _norm(description)
    c_norm = _normalize_company(company)

    # 1) Spam company (normalized exact match)
    if c_norm and c_norm in _SPAM_COMPANY_SET:
        return True, "Spam company"

    # 2) Reject principal+ (title)
    if BLOCK_PRINCIPAL_PLUS_REGEX.search(t):
        return True, "Rejected: principal/staff/lead/architect level"

    # 3) Allow only your exact role families (title must match)
    if not ROLE_ALLOWLIST_REGEX.search(t):
        return True, "Rejected: title not in your exact role list"

    # 4) Spam keywords in title/description
    combined = f"{t}\n{d}"
    if _matches_any_pattern(combined, _SPAM_PATTERNS):
        return True, "Spam keyword / role mismatch"

    # 5) Spammy descriptions
    if _matches_any_pattern(d, _DESC_SPAM_PATTERNS):
        return True, "Spam description"

    # 6) Experience filter: only 4–5 years
    ok_exp, exp_reason = experience_is_4_to_5_only(description=d, title=t)
    if not ok_exp:
        return True, exp_reason

    # 7) Optional: ensure .NET signal exists
    if REQUIRE_DOTNET_SIGNAL and not matches_dotnet_signal(title=t, description=d):
        return True, "Rejected: missing .NET/C#/ASP.NET signal"

    return False, "Accepted"


# =========================
# 6) QUICK SELF-TEST (OPTIONAL)
# =========================
if __name__ == "__main__":
    samples = [
        {
            "title": "Senior .NET Developer",
            "company": "GoodCo",
            "description": "We need C#, .NET 8, ASP.NET Core Web API. Minimum 4+ years experience."
        },
        {
            "title": "Principal .NET Developer",
            "company": "GoodCo",
            "description": "Principal role. 8+ years experience in .NET."
        },
        {
            "title": "Software Engineer .NET",
            "company": "GoodCo",
            "description": "Requirements: 6+ years of experience with .NET and Azure."
        },
        {
            "title": "Backend Engineer .NET",
            "company": "GoodCo",
            "description": "2-5 years experience required. .NET + React."
        },
        {
            "title": ".NET Full Stack Developer",
            "company": "GoodCo",
            "description": "At least 5 years of experience. ASP.NET Core, EF Core, React."
        },
        {
            "title": "Azure .NET Developer",
            "company": "GoodCo",
            "description": "4 to 5 years of experience required. Azure, C#, .NET."
        },
        {
            "title": "SDE-2 .NET",
            "company": "GoodCo",
            "description": "Minimum 4 years experience. .NET, C#."
        },
    ]

    for s in samples:
        skip, reason = should_skip_job(s["title"], s["company"], s["description"])
        print(f"{'SKIP' if skip else 'KEEP'} | {s['title']} | {reason}")
