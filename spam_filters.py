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
    "Java Developer", "Java", ".net", "Video Editor", "Videographer", "devops lead",
    "site reliability lead", "infrastructure architect", "Paramedic", "Care", 
    "database administrator", "dba", "system administrator", "Front Desk Agent",
    "network engineer", "telecommunications", "telecom", "contract", "women"
    "quality assurance lead", "qa lead", "test lead", "Android", "Aerospace Engineer",

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

    # 🚫 Social / Mental Health / Support Roles
    "Crisis Responder", "Behaviour Analyst", "Social Worker", "Case Manager",
    "Occupational Therapist", "Speech Language Pathologist", "Audiologist",
    "Rehabilitation Specialist", "Mental Health Worker", "Addiction Counselor",
    "Therapeutic Support Staff", "Child and Youth Worker",
    "Early Childhood Educator", "Educational Assistant",
    "Special Education Teacher", "Learning Support Specialist",
    "Guidance Counselor", "Career Advisor", "Academic Advisor",
    "School Psychologist", "School Nurse",

    # 📚 Library / Museum / Heritage
    "Librarian", "Library Technician", "Archivist", "Museum Curator",
    "Conservation Technician", "Exhibit Designer", "Art Handler",
    "Gallery Manager", "Registrar", "Collections Manager",
    "Education Coordinator", "Public Programs Specialist",
    "Development Officer", "Fundraising Coordinator",
    "Grant Writer", "Donor Relations Manager", "Membership Coordinator",

    # 📣 Comms / Marketing / Media / Content
    "Communications Specialist", "Public Relations Officer",
    "Marketing Coordinator", "Social Media Manager",
    "Content Creator", "Copywriter", "Editor", "Proofreader",
    "Translator", "Interpreter", "Technical Writer", "Journalist",
    "Reporter", "News Anchor", "Broadcast Technician",
    "Camera Operator", "Sound Engineer", "Lighting Technician",
    "Video Producer", "Film Editor", "Production Assistant",

    # 🎭 Creative / Arts / Production
    "Set Designer", "Costume Designer", "Makeup Artist",
    "Script Supervisor", "Location Scout", "Casting Director",
    "Talent Agent", "Art Director", "Creative Director",
    "Visual Effects Artist", "Animator", "Game Designer",

    # 🧠 Mental Health / Clinical Support
    "Psychotherapist", "Psychologist", "Counselor", "Counsellor",
    "Addictions Counselor", "Substance Use Counselor",
    "Caseworker", "Case Worker", "Support Worker",
    "Personal Support Worker", "PSW", "Residential Support Worker",
    "Shelter Worker", "Housing Support Worker", "Outreach Worker",
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

    # 🎓 Education / School / Academic
    "Teacher", "Elementary Teacher", "High School Teacher",
    "Secondary Teacher", "College Instructor", "College Professor",
    "University Professor", "Faculty Member", "Lecturer",
    "Instructor", "Teaching Assistant",
    "Professor Emeritus", "Adjunct Professor",
    "Department Chair", "Principal", "Vice Principal",
    "Dean", "School Administrator", "School Principal",
    "Education Assistant", "Instructional Coach",
    "Curriculum Specialist", "Learning Specialist",
    "Student Success Advisor", "Student Services Officer",
    "Residence Life Coordinator", "Residence Advisor",
    "Camp Counsellor", "Camp Counselor",

    # 🏛 Museum / Heritage (more)
    "Curatorial Assistant", "Curatorial Associate",
    "Curatorial Fellow", "Heritage Interpreter", "Heritage Officer",
    "Heritage Planner", "Museum Educator", "Museum Technician",
    "Collections Assistant", "Collections Technician",
    "Records Manager", "Records Technician", "Documentalist",
    "Archivist Assistant",

    # 🎯 Nonprofit / Fundraising / Events / Outreach
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

    # 📣 Comms / Brand / Marketing (more)
    "Communications Officer", "Communications Manager",
    "Communications Advisor", "Communications Consultant",
    "Brand Manager", "Brand Strategist",
    "Digital Marketing Specialist", "Digital Marketer",
    "SEO Specialist", "SEM Specialist",
    "Media Relations Officer", "Press Secretary",
    "Spokesperson", "Campaign Communications",
    "Public Affairs Specialist", "Public Information Officer",
    "Community Relations Coordinator",

    # 🎭 Theatre / Stage / Production Crew
    "Stage Manager", "Assistant Stage Manager",
    "Theatre Technician", "Theatre Manager",
    "Props Master", "Props Assistant",
    "Scenic Artist", "Storyboard Artist",
    "Storyboarder", "Sound Designer",
    "Foley Artist", "Post Production Supervisor",
    "Colorist", "Gaffer", "Best Boy",
    "Grip", "Production Designer",
    "Production Coordinator", "Production Manager",

    # 🏗️ Non-software Engineering (mechanical/civil/etc.)
    "Manufacturing Engineer", "Manufacturing Engineering",
    "Manufacturing Analyst", "Industrial Engineer",
    "Mechanical Systems Engineer", "Structural Engineer",
    "Geotechnical Engineer", "Mining Engineer", "Miner",
    "Rock Mechanics Engineer", "Hydraulic Engineer",
    "Hydraulics Engineer", "HVDC Engineer", "Power Engineer",
    "Substation Engineer", "Building Engineer",
    "HVAC Engineer", "HVAC Engineering",
    "Process Improvement Engineer", "Applied Dynamics Engineer",
    "Aviation Engineer", "Aircraft Structural", "Aircraft Dynamics",
    "Hydromechanical Engineer", "Airworthiness Engineer",
    "Thermodynamics Engineer", "Thermal Engineer", "Fluid Engineer",
    "Nuclear Operator", "Nuclear Engineer",
    "Microfluidics Engineer", "Stationary Engineer",
    "Conveyance Engineer",

    # 🛠 Trades / Technicians / Plant
    "Machining Specialist", "Assembler", "Assembly",
    "Valve Technician", "Robot Programmer", "Robotics Technician",
    "CNC", "Millwright", "Injection Molding",
    "Paint Technician", "Welding Specialist",
    "Quality Continuous Improvement Technician",
    "Transport Sustaining Engineer", "Shop Technician",
    "Machine Operator", "Operator",
    "Plant Technician", "Maintenance Technician",

    # 🧪 Lab / Wet-lab / Bio / Physical Sciences
    "Microbiologist", "Clinical Research",
    "Research Assistant (Physical Sciences)",
    "Lab Technician", "Scientist (wet lab)",
    "Biomedical", "Health Content Editor",

    # 🧾 Accounting / Bookkeeping (pure finance ops)
    "accounting specialist", "accounts payable",
    "accounts receivable", "bookkeeper",

    # 🗂️ Admin / Office (non-technical)
    "Administrator", "Scheduling Coordinator", "Renewal Administrator",
    "Service Administrator", "Shop Administrator",
    "Office Administrator", "Housing Administrative",
    "Reporting Analyst (non-technical)",

    # ⚖️ Legal / Governance
    "Legal Counsel", "Lawyer", "Regulatory Affairs",
    "Governance",

    # 🎨 Generic non-tech design
    "Designer (non-UI)", "Motion Designer",
    "Graphic Designer", "Brand/UI Designer",

    # 🚚 Supply Chain / Logistics / Procurement
    "Supply Chain", "Procurement", "Logistics",
    "Operations Analyst (non-technical)",
    "Replenishment Analyst", "Vendor Analyst",

    # 🔐 Physical Security (not cyber)
    "Security Guard", "Guard", "Security Officer",

    # 👷 Misc unrelated jobs
    "Mechanic", "Bowling Mechanic",
    "Warehouse", "Factory", "Laborer",
    "Bartender", "Cook", "Driver",
    "Field Technician",
    "Estimator", "Scheduler",
]

# Additional spam/fake companies filter (matches `company` column)
SPAM_COMPANIES = [
    "Prime Jobs", "Next Jobs", "Jobs Ai", "Get Hired", "Crossover", "Recruit Loop", "Talent Pulse",
    "Get Jobs", "Jobsmast", "Hiring Hub", "Tech Jobs Fast", "YO IT CONSULTING", "DataAnnotation", "Mercor",
    "Talent Connect", "Recruit Loop", "Talent Orbit", "Talent Pulse", "S M Software Solutions Inc", "Lumenalta",
    "Crossing Hurdles", "Hire Sync", "Hire Wave", "HireFast", "Work Vista", "Hunter Bond", "Twine", "Talently",
    "Gnapi Technologies", "Peroptyx", "FutureSight", "HiJob.work", "jobbit", "Akkodis", 

    "EviSmart™", "Spait Infotech Private Limited", "Themesoft Inc.",
    "V-Soft Consulting Group, Inc.", "Compunnel Inc.", "Avanciers", "Avanciers Inc.", "Avancier's Inc.",  # covers all variations
    "Apexon", "Iris Software Inc.", "Galent", "n2psystems",
    "Resonaite", "Astra-North Infoteck Inc.",
    "Seven Hills Group Technologies Inc.", "Dexian", "DISYS",  # Dexian = former DISYS
    "Raas Infotek", "Kumaran Systems", "Luxoft", "Synechron",
    "Collabera", "Flexton Inc.", "Agilus Work Solutions",
    "Procom", "TEKsystems", "Robert Half",
    "Randstad Digital", "Randstad Digital Americas",
    "Hays", "Insight Global", "Andiamo", "Swoon",
    "HCR Permanent Search", "Signature IT World Inc.",
    "Nexus Systems Group", "Altis Technology", "excelHR",
    "BeachHead", "Bevertec", "Robertson & Company Ltd.",        
]

# Dedicated spam keywords for description (phrases common in spammy descriptions)
SPAM_DESCRIPTION_KEYWORDS = [
    "quick money", "5+ years",  "6+ years", "7+ years", "8+ years", "10+ years", 
    "9 years", "6 years", "7 years", "8 years",
]
