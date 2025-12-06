"""
Centralized spam filters for job scraping.

Edit these lists to adjust filtering without touching the main script.
"""

# 🔴 SPAM KEYWORDS - Filter out jobs YOU'RE NOT ELIGIBLE FOR
# Based on your profile: New grad (April 2026), ~8 months internship experience
# Strong in: Python, ML/MLOps, Data Science, Cloud (AWS/Azure), no French, no P.Eng

SPAM_KEYWORDS = [
    # Seniority Levels (5+ years required)
    "senior", "sr.", "sr ", "principal", "lead", "staff",
    "director", "head of", "vice president", "vp", "chief",
    "executive", "distinguished", "fellow",

    # Experience Level Indicators
    "intermediate", "experienced professional",

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

    # More Keywords
    "Crisis Responder", "Behaviour Analyst", "Social Worker", "Case Manager",
    "Occupational Therapist", "Speech Language Pathologist", "Audiologist", "Rehabilitation Specialist",
    "Mental Health Worker", "Addiction Counselor", "Therapeutic Support Staff", "Child and Youth Worker",
    "Early Childhood Educator", "Educational Assistant", "Special Education Teacher", "Learning Support Specialist",
    "Guidance Counselor", "Career Advisor", "Academic Advisor", "School Psychologist",  "School Nurse",
    "Librarian", "Library Technician", "Archivist", "Museum Curator",   "Conservation Technician", "Exhibit Designer", "Art Handler",
    "Gallery Manager", "Registrar", "Collections Manager", "Education Coordinator", "Public Programs Specialist", "Development Officer", "Fundraising Coordinator",
    "Grant Writer", "Donor Relations Manager", "Event Planner", "Volunteer Coordinator", "Membership Coordinator",
    "Communications Specialist", "Public Relations Officer", "Marketing Coordinator", "Social Media Manager",
    "Content Creator", "Copywriter", "Editor", "Proofreader", "Translator", "Interpreter",
    "Technical Writer", "Journalist", "Reporter", "News Anchor", "Broadcast Technician",
    "Camera Operator", "Sound Engineer", "Lighting Technician", "Video Producer", "Film Editor", "Production Assistant",
    "Set Designer", "Costume Designer", "Makeup Artist", "Script Supervisor", "Location Scout",
    "Casting Director", "Talent Agent", "Art Director", "Creative Director", "Visual Effects Artist", "Animator", "Game Designer",

    "Psychotherapist", "Psychologist", "Counselor", "Counsellor",
    "Addictions Counselor", "Substance Use Counselor",
    "Caseworker", "Case Worker", "Support Worker",
    "Personal Support Worker", "PSW",
    "Residential Support Worker", "Shelter Worker",
    "Housing Support Worker", "Outreach Worker",
    "Community Support Worker", "Community Worker",
    "Family Support Worker", "Family Therapist",
    "Youth Counselor", "Youth Counsellor", "Youth Worker",
    "Child Protection Worker", "Crisis Intervention",
    "Crisis Support Worker", "Recreation Therapist",
    "Clinical Supervisor", "Clinical Coordinator",
    "Registered Nurse", "RN", "Registered Practical Nurse", "RPN",
    "Nurse Practitioner", "Nursing Assistant", "Health Care Aide",
    "Psychiatric Nurse", "Public Health Nurse",
    "Behaviour Therapist", "Rehabilitation Counselor",
    "Addiction Worker", "Mental Health Counselor",
    "Psychometrist",

    "Teacher", "Elementary Teacher", "High School Teacher",
    "Secondary Teacher", "College Instructor", "College Professor",
    "University Professor", "Faculty Member", "Lecturer",
    "Instructor", "Tutor", "Teaching Assistant",
    "Professor Emeritus", "Adjunct Professor",
    "Department Chair", "Principal", "Vice Principal",
    "Dean", "School Administrator", "School Principal",
    "Education Assistant", "Instructional Coach",
    "Curriculum Developer", "Curriculum Specialist",
    "Education Specialist", "Learning Specialist",
    "Student Success Advisor", "Student Services Officer",
    "Residence Life Coordinator", "Residence Advisor",
    "Camp Counsellor", "Camp Counselor",

    "Curatorial Assistant", "Curatorial Associate",
    "Curatorial Fellow", "Heritage Interpreter",
    "Heritage Officer", "Heritage Planner",
    "Museum Educator", "Museum Technician",
    "Collections Assistant", "Collections Technician",
    "Records Manager", "Records Technician",
    "Documentalist", "Archivist Assistant",

    "Development Coordinator", "Development Associate",
    "Development Manager", "Major Gifts Officer",
    "Philanthropy Officer", "Stewardship Officer",
    "Campaign Manager", "Campaign Coordinator",
    "Outreach Coordinator", "Community Engagement Coordinator",
    "Community Organizer", "Program Coordinator",
    "Program Facilitator", "Program Manager",
    "Event Coordinator", "Conference Coordinator",
    "Conference Planner", "Special Events Coordinator",
    "Volunteer Manager", "Volunteer Program Manager",

    "Communications Officer", "Communications Manager",
    "Communications Advisor", "Communications Consultant",
    "Brand Manager", "Brand Strategist",
    "Digital Marketing Specialist", "Digital Marketer",
    "SEO Specialist", "SEM Specialist",
    "Media Relations Officer", "Press Secretary",
    "Spokesperson", "Campaign Communications",
    "Public Affairs Specialist", "Public Information Officer",
    "Community Relations Coordinator",

    "Stage Manager", "Assistant Stage Manager",
    "Theatre Technician", "Theatre Manager",
    "Props Master", "Props Assistant",
    "Scenic Artist", "Storyboard Artist",
    "Storyboarder", "Sound Designer",
    "Foley Artist", "Post Production Supervisor",
    "Colorist", "Gaffer", "Best Boy",
    "Grip", "Production Designer",
    "Production Coordinator", "Production Manager",
]

# Additional spam/fake companies filter (matches `company` column)
SPAM_COMPANIES = [
    "Prime Jobs", "Next Jobs", "Jobs Ai", "Get Hired", "Crossover",
    "Get Jobs", "Jobsmast", "Hiring Hub", "Tech Jobs Fast", "YO IT CONSULTING"
]

# Dedicated spam keywords for description (phrases common in spammy descriptions)
SPAM_DESCRIPTION_KEYWORDS = [
    "quick money", "5+ years", "5 years", "6+ years", "7+ years",
    "8+ years", "10+ years"
]
