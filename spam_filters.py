"""
Centralized spam + experience filters for job scraping.

Goal (per your request):
- Keep ONLY jobs that match a .NET Full Stack profile
- Filter to ONLY 4–5 years experience roles (reject <4 and >5)

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


# ======================================
# 2) EXPERIENCE FILTER (ONLY 4–5 YEARS)
# ======================================
#
# Strategy:
# - Block explicit <4 years (0–3 years patterns)
# - Block explicit >5 years (6+ years patterns)
# - Require an allow hit for 4 or 5 years patterns
#
# Note: Many postings say "3-5 years" or "2-5 years". Your requirement is strict 4–5.
#       So "3-5 years" will be rejected (because it includes <4).
#

# allow 4–5 years mentions
ALLOW_4_5_REGEX = re.compile(
    r"""
    (
        \b4\s*[\+]\s*years\b |
        \b5\s*[\+]\s*years\b |
        \b4\s*years\b |
        \b5\s*years\b |
        \b4\s*[-–to]+\s*5\s*years\b |
        \b4\s*[-–to]+\s*5\s*yrs\b |
        \b4\s*yrs\b |
        \b5\s*yrs\b
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

# block ranges that include <4, e.g., "2-5 years", "3 to 5 years"
BLOCK_RANGE_INCLUDES_LOW_REGEX = re.compile(
    r"""
    (
        \b(0|1|2|3)\s*[-–to]+\s*(4|5)\s*(years|yrs)\b |
        \b(0|1|2|3)\s*[-–to]+\s*(5|6|7|8|9|1[0-9])\s*(years|yrs)\b |
        \b(0|1|2|3)\s*to\s*(4|5)\s*(years|yrs)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# =========================
# 3) .NET ROLE POSITIVE HINT
# =========================
#
# Optional: ensures jobs have at least one .NET signal.
# You can disable this by setting REQUIRE_DOTNET_SIGNAL = False
#
REQUIRE_DOTNET_SIGNAL = True

DOTNET_SIGNALS = [
    ".net", "dotnet", "c#", "asp.net", "aspnet",
    "entity framework", "ef core", "asp.net core",
    "web api", "mvc",
]


# =========================
# 4) CORE FILTER FUNCTIONS
# =========================

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


def _contains_any(text: str, keywords: list[str]) -> bool:
    t = _norm(text)
    return any(k.lower() in t for k in keywords)


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

    # Require explicit 4/5 year hit
    if not ALLOW_4_5_REGEX.search(text):
        return False, "Rejected: no explicit 4–5 years requirement found"

    return True, "Accepted: matches 4–5 years"


def should_skip_job(title: str, company: str, description: str) -> Tuple[bool, str]:
    """
    Returns (skip, reason)
    """
    t = _norm(title)
    c = (company or "").strip()
    d = _norm(description)

    # Company spam
    if c and c.strip() in SPAM_COMPANIES:
        return True, "Spam company"

    # Spam keywords in title/description
    combined = f"{t}\n{d}"
    if _contains_any(combined, SPAM_KEYWORDS):
        return True, "Spam keyword / role mismatch"

    # Spammy descriptions
    if _contains_any(d, SPAM_DESCRIPTION_KEYWORDS):
        return True, "Spam description"

    # Experience filter: only 4–5 years
    ok_exp, exp_reason = experience_is_4_to_5_only(description=d, title=t)
    if not ok_exp:
        return True, exp_reason

    # Optional: ensure .NET signal exists
    if REQUIRE_DOTNET_SIGNAL and not matches_dotnet_signal(title=t, description=d):
        return True, "Rejected: missing .NET/C#/ASP.NET signal"

    return False, "Accepted"


# =========================
# 5) QUICK SELF-TEST (OPTIONAL)
# =========================
if __name__ == "__main__":
    samples = [
        {
            "title": "Software Engineer (.NET) - 4+ years",
            "company": "GoodCo",
            "description": "We need C#, .NET 8, ASP.NET Core Web API. Minimum 4+ years experience."
        },
        {
            "title": "Senior Software Engineer",
            "company": "GoodCo",
            "description": "Requirements: 6+ years of experience with Java and Spring Boot."
        },
        {
            "title": "Software Engineer",
            "company": "GoodCo",
            "description": "2-5 years experience required. React + Node."
        },
        {
            "title": "Junior Developer",
            "company": "GoodCo",
            "description": "Entry level, 1+ years. C#."
        },
    ]

    for s in samples:
        skip, reason = should_skip_job(s["title"], s["company"], s["description"])
        print(f"{'SKIP' if skip else 'KEEP'} | {s['title']} | {reason}")
