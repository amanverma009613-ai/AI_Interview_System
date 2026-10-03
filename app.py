from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.utils import secure_filename
from pathlib import Path

import re
import json
import os


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "ai-interview-system-secret-key"


# ============================================================
# BASE DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

PROFILE_PHOTO_FOLDER = (
    BASE_DIR / "static" / "profile_photos"
)

PROFILE_PHOTO_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ALLOWED FILES
# ============================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}


# ============================================================
# OPENAI AI SETUP
# ============================================================

try:

    from openai import OpenAI

    client = OpenAI()

    AI_MODEL = "gpt-6-astra"

except Exception as e:

    client = None

    AI_MODEL = "gpt-6-astra"

    print(
        "OpenAI setup warning:",
        e
    )


# ============================================================
# 12 SUPPORTED DOMAINS
# ============================================================

DOMAINS = [

    "IT & Software",

    "Data Analyst",

    "Business & Management",

    "Hotel & Restaurant",

    "HR",

    "General / Other",

    "Marketing & Sales",

    "Finance & Accounting",

    "Healthcare & Medical",

    "Legal & Law",

    "Design & Creative",

    "Engineering & Technical"

]


# ============================================================
# DOMAIN ALIASES
# ============================================================

domain_aliases = {

    "IT & Software":
        "IT & Software",

    "Software Development":
        "IT & Software",

    "Web Development":
        "IT & Software",

    "Data Analyst":
        "Data Analyst",

    "Business":
        "Business & Management",

    "Business & Management":
        "Business & Management",

    "Hotel & Restaurant":
        "Hotel & Restaurant",

    "Hotel & Hospitality":
        "Hotel & Restaurant",

    "HR":
        "HR",

    "General / HR":
        "HR",

    "Other":
        "General / Other",

    "General / Other":
        "General / Other",

    "Marketing & Sales":
        "Marketing & Sales",

    "Finance & Accounting":
        "Finance & Accounting",

    "Healthcare & Medical":
        "Healthcare & Medical",

    "Legal & Law":
        "Legal & Law",

    "Design & Creative":
        "Design & Creative",

    "Engineering & Technical":
        "Engineering & Technical"
}


# ============================================================
# FALLBACK QUESTIONS
# ============================================================

DOMAIN_QUESTIONS = {

    "IT & Software": [

        "Tell me about yourself and your interest in IT and software.",

        "What is the difference between frontend and backend development?",

        "What is an API and why is it used?",

        "What is the difference between a list and a tuple in Python?",

        "How do you debug an application when an error occurs?",

        "What is object-oriented programming?",

        "What is the difference between SQL and NoSQL databases?",

        "What is Git and why is it useful?",

        "How do you handle errors in a software application?",

        "What is the difference between GET and POST requests?",

        "What is Flask?",

        "How would you make a website responsive?",

        "What is database normalization?",

        "What is the purpose of testing software?",

        "Describe a technical project you have worked on."

    ],


    "Data Analyst": [

        "Tell me about yourself and your interest in Data Analytics.",

        "What is the difference between INNER JOIN and LEFT JOIN in SQL?",

        "How do you handle missing values in a dataset?",

        "What is the difference between descriptive and predictive analytics?",

        "How would you explain a Power BI dashboard to a non-technical manager?",

        "What is a primary key in SQL?",

        "What is a DataFrame in Pandas?",

        "How do you identify duplicate records?",

        "What is data visualization?",

        "How do you validate the quality of a dataset?",

        "What is the difference between mean, median and mode?",

        "How would you find trends in a dataset?",

        "What is KPI?",

        "How is Excel useful for data analysis?",

        "Describe a data analysis project you have worked on."

    ],


    "Business & Management": [

        "Tell me about yourself and your interest in business.",

        "How do you prioritize multiple tasks?",

        "Describe a time when you solved a difficult problem.",

        "How do you handle disagreement with a team member?",

        "What makes data useful for business decision-making?",

        "What is business intelligence?",

        "How do you manage deadlines?",

        "How would you handle an unhappy client?",

        "What makes a good team leader?",

        "How do you make decisions under pressure?",

        "What is strategic planning?",

        "How would you improve a business process?",

        "How do you measure business performance?",

        "How do you handle failure?",

        "Describe a project where you demonstrated leadership."

    ],


    "Hotel & Restaurant": [

        "Tell me about yourself and why you are interested in hospitality.",

        "How would you handle an unhappy guest?",

        "What would you do if several guests needed help at the same time?",

        "How do you maintain professionalism under pressure?",

        "How would you handle a mistake made during a guest's stay?",

        "How do you provide excellent customer service?",

        "How would you handle a difficult customer?",

        "What would you do during a busy shift?",

        "How important is teamwork in hospitality?",

        "How do you handle customer complaints?",

        "What does hospitality mean to you?",

        "How would you deal with an unexpected situation?",

        "How do you maintain cleanliness and professionalism?",

        "How would you handle a reservation problem?",

        "Why should we hire you for a hospitality role?"

    ],


    "HR": [

        "Tell me about yourself.",

        "What are your strengths and areas you want to improve?",

        "Why should we select you?",

        "Where do you see yourself in the next few years?",

        "Describe a challenging situation and how you handled it.",

        "How do you handle criticism?",

        "How do you work in a team?",

        "What motivates you?",

        "How do you handle pressure?",

        "Why do you want this job?",

        "What are your career goals?",

        "How do you handle conflict?",

        "What makes you a good candidate?",

        "Tell me about a failure and what you learned.",

        "Why should we hire you as a fresher?"

    ],


    "General / Other": [

        "Tell me about yourself.",

        "What are your strengths?",

        "What is one area you want to improve?",

        "Why should we select you?",

        "Where do you see yourself in five years?",

        "Describe a challenging situation you handled.",

        "How do you handle pressure?",

        "How do you learn new skills?",

        "How do you work with others?",

        "What motivates you?",

        "How do you handle failure?",

        "What are your career goals?",

        "How do you solve problems?",

        "What is your biggest achievement?",

        "Why should we hire you?"

    ],


    "Marketing & Sales": [

        "Tell me about yourself and your interest in marketing and sales.",

        "What is digital marketing?",

        "What is a target audience?",

        "How would you promote a new product?",

        "How do you handle rejection in sales?",

        "What is a marketing funnel?",

        "What is SEO?",

        "What is social media marketing?",

        "How would you measure a marketing campaign?",

        "What is customer segmentation?",

        "How would you convince a customer to buy a product?",

        "What is brand awareness?",

        "How do you handle a difficult customer?",

        "What makes a good sales person?",

        "Describe a marketing or sales project."

    ],


    "Finance & Accounting": [

        "Tell me about yourself and your interest in finance.",

        "What is the difference between assets and liabilities?",

        "What is a balance sheet?",

        "What is a profit and loss statement?",

        "What is cash flow?",

        "What is budgeting?",

        "What is financial analysis?",

        "What is the difference between revenue and profit?",

        "What is depreciation?",

        "How do you maintain accuracy in financial data?",

        "What is working capital?",

        "What is an income statement?",

        "How is Excel useful in finance?",

        "How would you identify an error in financial data?",

        "Describe a finance or accounting project."

    ],


    "Healthcare & Medical": [

        "Tell me about yourself and your interest in healthcare.",

        "Why are communication skills important in healthcare?",

        "How would you handle a difficult patient?",

        "How do you maintain confidentiality?",

        "How do you handle pressure?",

        "Why is teamwork important in healthcare?",

        "How would you respond to an emergency situation?",

        "How do you maintain accuracy in healthcare records?",

        "How would you communicate with a patient's family?",

        "What is patient-centered care?",

        "How do technology and healthcare work together?",

        "How would you handle a mistake?",

        "How do you prioritize tasks?",

        "What makes a good healthcare professional?",

        "Describe a healthcare-related project or experience."

    ],


    "Legal & Law": [

        "Tell me about yourself and your interest in law.",

        "Why is legal research important?",

        "What is a contract?",

        "What is the difference between civil and criminal law?",

        "How do you analyze a legal problem?",

        "Why is confidentiality important in legal work?",

        "How do you manage multiple cases or tasks?",

        "What makes a good legal professional?",

        "How do you prepare for legal research?",

        "How do you communicate complex legal information?",

        "How do you handle pressure?",

        "How do you maintain accuracy in legal documents?",

        "How do you handle disagreement?",

        "What is legal ethics?",

        "Describe a legal research project."

    ],


    "Design & Creative": [

        "Tell me about yourself and your interest in design.",

        "What design tools do you use?",

        "How do you understand a client's requirements?",

        "What is user experience?",

        "What is user interface design?",

        "How do you handle design feedback?",

        "How do you choose colors and typography?",

        "What is responsive design?",

        "How do you manage creative deadlines?",

        "How do you handle creative disagreements?",

        "What makes a design effective?",

        "How do you research users?",

        "How do you present a design to a client?",

        "How do you improve an existing design?",

        "Describe a design project you have worked on."

    ],


    "Engineering & Technical": [

        "Tell me about yourself and your engineering interests.",

        "How do you approach solving a technical problem?",

        "How do you troubleshoot equipment or systems?",

        "Why is documentation important in engineering?",

        "How do you ensure accuracy in technical work?",

        "How do you manage deadlines?",

        "How do you handle technical failure?",

        "How do you work with a technical team?",

        "What is quality control?",

        "Why is safety important in engineering?",

        "How do you learn new technologies?",

        "How do you analyze technical requirements?",

        "How do you communicate technical information?",

        "How do you test a technical solution?",

        "Describe an engineering or technical project."

    ]

}


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


def allowed_image(filename):

    return (
        "."
        in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


# ============================================================
# RESUME TEXT EXTRACTION
# ============================================================

def extract_text(path):

    extension = path.suffix.lower()

    try:

        # -----------------------------
        # TXT
        # -----------------------------

        if extension == ".txt":

            return path.read_text(
                encoding="utf-8",
                errors="ignore"
            )


        # -----------------------------
        # PDF
        # -----------------------------

        if extension == ".pdf":

            from pypdf import PdfReader

            reader = PdfReader(
                str(path)
            )

            text = ""

            for page in reader.pages:

                text += (
                    page.extract_text()
                    or ""
                )

                text += "\n"

            return text


        # -----------------------------
        # DOCX
        # -----------------------------

        if extension == ".docx":

            from docx import Document

            document = Document(
                str(path)
            )

            lines = []

            for paragraph in document.paragraphs:

                if paragraph.text.strip():

                    lines.append(
                        paragraph.text.strip()
                    )

            return "\n".join(lines)


    except Exception as e:

        print(
            "Resume extraction error:",
            e
        )

        return ""


    return ""


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = text or ""

    text = text.replace(
        "\x00",
        " "
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n",
        text
    )

    return text.strip()


# ============================================================
# DETECT NAME
# ============================================================

def detect_name(text):

    lines = [

        line.strip()

        for line in text.splitlines()

        if line.strip()

    ]


    # First look for:
    # Name: Aman Verma

    for line in lines[:20]:

        match = re.match(
            r"^(?:name|full name)\s*[:\-]\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            if 2 <= len(name.split()) <= 5:

                return name


    # Ignore common headings

    ignored = {

        "resume",
        "cv",
        "curriculum vitae",
        "profile",
        "resume profile",

    }


    # Usually candidate name is near top

    for line in lines[:10]:

        clean = re.sub(
            r"[^A-Za-z .'-]",
            "",
            line
        ).strip()

        words = clean.split()


        if (
            2 <= len(words) <= 5
            and
            clean.lower()
            not in ignored
        ):

            # Avoid section headings

            if not any(
                keyword in clean.lower()
                for keyword in [
                    "objective",
                    "education",
                    "skills",
                    "experience",
                    "contact",
                    "email",
                    "phone",
                    "summary"
                ]
            ):

                return clean


    return "Not detected"


# ============================================================
# DETECT SKILLS
# ============================================================

def detect_skills(text):

    skill_list = [

        "Python",
        "Java",
        "C",
        "C++",
        "C#",
        "JavaScript",
        "HTML",
        "CSS",

        "Flask",
        "Django",

        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",

        "Excel",
        "Power BI",
        "Tableau",

        "Pandas",
        "NumPy",
        "Matplotlib",

        "Machine Learning",
        "ML",
        "Artificial Intelligence",
        "AI",

        "Data Analysis",
        "Data Visualization",
        "Statistics",

        "Git",
        "GitHub",

        "AWS",
        "Azure",

        "Communication",
        "Leadership",
        "Problem Solving",

        "Figma",
        "Canva",
        "Photoshop",

        "Digital Marketing",
        "SEO",

        "Accounting",
        "Financial Analysis"

    ]


    found = []

    lower_text = text.lower()


    for skill in skill_list:

        if skill.lower() in lower_text:

            if skill == "C" and re.search(
                r"\bc\b",
                lower_text
            ) is None:

                continue

            if skill == "AI" and "artificial intelligence" in lower_text:

                continue

            found.append(skill)


    return found


# ============================================================
# DETECT EDUCATION
# ============================================================

def detect_education(text):

    lines = [

        line.strip()

        for line in text.splitlines()

        if line.strip()

    ]


    education_keywords = [

        "education",
        "academic",
        "qualification",
        "degree",
        "b.sc",
        "bsc",
        "b.tech",
        "btech",
        "m.sc",
        "msc",
        "m.tech",
        "mtech",
        "b.com",
        "bcom",
        "m.com",
        "mcom",
        "mba",
        "bba",
        "college",
        "university"

    ]


    result = []


    for index, line in enumerate(lines):

        if any(
            keyword in line.lower()
            for keyword in education_keywords
        ):

            start = index
            end = min(
                index + 5,
                len(lines)
            )

            for item in lines[start:end]:

                if item not in result:

                    result.append(item)


    if not result:

        # Search common degree patterns

        for line in lines:

            if re.search(
                r"\b(B\.?Sc|BSc|B\.?Tech|BTech|M\.?Sc|MSc|MBA|BBA|B\.?Com|BCom)\b",
                line,
                re.IGNORECASE
            ):

                result.append(line)


    if result:

        return " | ".join(
            result[:5]
        )


    return "Not detected"


# ============================================================
# DETECT EXPERIENCE
# ============================================================

def detect_experience(text):

    lines = [

        line.strip()

        for line in text.splitlines()

        if line.strip()

    ]


    experience_headings = [

        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internship",
        "internships",
        "work history"

    ]


    stop_headings = [

        "education",
        "skills",
        "projects",
        "certifications",
        "certificate",
        "achievements",
        "interests",
        "languages",
        "contact",
        "references"

    ]


    result = []


    # -----------------------------------------
    # Find experience section
    # -----------------------------------------

    for index, line in enumerate(lines):

        normalized = re.sub(
            r"[^a-z ]",
            "",
            line.lower()
        ).strip()


        if any(
            heading == normalized
            or heading in normalized
            for heading in experience_headings
        ):

            for next_line in lines[
                index + 1:
                index + 10
            ]:

                normalized_next = re.sub(
                    r"[^a-z ]",
                    "",
                    next_line.lower()
                ).strip()


                if any(
                    stop == normalized_next
                    for stop in stop_headings
                ):

                    break


                if next_line:

                    result.append(
                        next_line
                    )


            if result:

                break


    # -----------------------------------------
    # Fallback: internship/job/project lines
    # -----------------------------------------

    if not result:

        for line in lines:

            if any(
                word in line.lower()
                for word in [
                    "intern",
                    "internship",
                    "developer",
                    "analyst",
                    "engineer",
                    "manager",
                    "trainee",
                    "worked at",
                    "working at"
                ]
            ):

                result.append(line)


    if result:

        return " | ".join(
            result[:6]
        )


    return "Fresher / Not detected"


# ============================================================
# RESUME ANALYSIS
# ============================================================

def analyze_resume(text):

    text = clean_text(text)


    skills = detect_skills(
        text
    )


    analysis = {

        "name":
            detect_name(text),

        "skills":
            skills,

        "education":
            detect_education(text),

        "experience":
            detect_experience(text)

    }


    return analysis


# ============================================================
# AI RESUME ANALYSIS
# ============================================================

def ai_analyze_resume(text):

    local_analysis = analyze_resume(
        text
    )


    if client is None:

        return local_analysis


    prompt = f"""
You are an AI resume analyzer.

Analyze the following resume and return ONLY valid JSON.

Required JSON format:

{{
    "name": "candidate name",
    "skills": ["skill1", "skill2"],
    "education": "education details",
    "experience": "experience details"
}}

Rules:

1. Extract the candidate's actual name.
2. Extract skills actually present in the resume.
3. Extract education actually present.
4. Extract work experience/internship.
5. Do not invent information.
6. If something is not found, write "Not detected".
7. If there is no work experience, write "Fresher / Not detected".

Resume:

{text[:12000]}
"""


    try:

        response = client.responses.create(

            model=AI_MODEL,

            input=prompt

        )


        output = response.output_text.strip()


        # Remove markdown JSON if AI returns it

        output = re.sub(
            r"^```json\s*",
            "",
            output,
            flags=re.IGNORECASE
        )

        output = re.sub(
            r"\s*```$",
            "",
            output
        )


        data = json.loads(
            output
        )


        if not isinstance(
            data,
            dict
        ):

            return local_analysis


        return {

            "name":
                data.get(
                    "name",
                    local_analysis["name"]
                ),

            "skills":
                data.get(
                    "skills",
                    local_analysis["skills"]
                ),

            "education":
                data.get(
                    "education",
                    local_analysis["education"]
                ),

            "experience":
                data.get(
                    "experience",
                    local_analysis["experience"]
                )

        }


    except Exception as e:

        print(
            "AI resume analysis error:",
            e
        )

        # Local fallback

        return local_analysis


# ============================================================
# AI QUESTION GENERATOR
# ============================================================

def generate_ai_questions(
    resume_text,
    resume_analysis,
    domain,
    num_questions
):

    fallback = DOMAIN_QUESTIONS.get(
        domain,
        DOMAIN_QUESTIONS["General / Other"]
    )


    fallback = fallback[:num_questions]


    if client is None:

        return fallback


    skills = ", ".join(
        resume_analysis.get(
            "skills",
            []
        )
    )


    name = resume_analysis.get(
        "name",
        "Not detected"
    )


    education = resume_analysis.get(
        "education",
        "Not detected"
    )


    experience = resume_analysis.get(
        "experience",
        "Not detected"
    )


    prompt = f"""
You are an expert AI interview question generator.

Create personalized interview questions for a candidate.

Domain:
{domain}

Candidate Name:
{name}

Skills:
{skills}

Education:
{education}

Experience:
{experience}

Resume:
{resume_text[:10000]}

Generate EXACTLY {num_questions} interview questions.

Requirements:

1. Questions must match the selected domain.
2. Questions should use information from the candidate's resume where possible.
3. Mix HR, technical/domain and practical questions.
4. Avoid asking the same question twice.
5. Questions should be suitable for a fresher or entry-level candidate if the resume shows no experience.
6. Return ONLY a valid JSON array of strings.

Example:

[
    "Question 1",
    "Question 2",
    "Question 3"
]
"""


    try:

        response = client.responses.create(

            model=AI_MODEL,

            input=prompt

        )


        output = response.output_text.strip()


        output = re.sub(
            r"^```json\s*",
            "",
            output,
            flags=re.IGNORECASE
        )

        output = re.sub(
            r"\s*```$",
            "",
            output
        )


        questions = json.loads(
            output
        )


        if (
            isinstance(
                questions,
                list
            )
            and
            len(questions) >= num_questions
        ):

            questions = [

                str(question).strip()

                for question in questions[:num_questions]

                if str(question).strip()

            ]


            if len(questions) == num_questions:

                return questions


    except Exception as e:

        print(
            "AI question generation error:",
            e
        )


    print(
        "Using fallback questions."
    )


    return fallback


# ============================================================
# RULE-BASED FEEDBACK FALLBACK
# ============================================================

def feedback_for(answer):

    answer = (
        answer
        or ""
    ).strip()


    if not answer:

        return {

            "score": 0,

            "strengths": [
                "No answer was submitted."
            ],

            "improvements": [
                "Write a complete answer before submitting."
            ],

            "better":
                "Start with a direct answer, add one example, and finish with the result or learning."

        }


    words = re.findall(
        r"\b[\w'-]+\b",
        answer
    )


    word_count = len(
        words
    )


    sentences = len(
        re.findall(
            r"[.!?]+",
            answer
        )
    )


    score = 45


    if word_count >= 25:

        score += 20

    elif word_count >= 12:

        score += 10


    if sentences >= 2:

        score += 10


    if any(
        word in answer.lower()
        for word in [
            "because",
            "for example",
            "result",
            "learned",
            "experience"
        ]
    ):

        score += 10


    if any(
        word in answer.lower()
        for word in [
            "i ",
            "my ",
            "we "
        ]
    ):

        score += 5


    score = min(
        score,
        95
    )


    strengths = []

    improvements = []


    if word_count >= 20:

        strengths.append(
            "The answer has enough detail to evaluate."
        )

    else:

        improvements.append(
            "Add more detail and a specific example."
        )


    if sentences >= 2:

        strengths.append(
            "The answer is presented in multiple sentences."
        )

    else:

        improvements.append(
            "Use 2–4 clear sentences instead of one short statement."
        )


    if any(
        word in answer.lower()
        for word in [
            "for example",
            "experience",
            "result",
            "learned"
        ]
    ):

        strengths.append(
            "The answer includes an example, experience, result or learning point."
        )

    else:

        improvements.append(
            "Add a real example and explain the result or learning."
        )


    return {

        "score":
            score,

        "strengths":
            strengths,

        "improvements":
            improvements,

        "better":
            "A stronger answer should directly answer the question, include a relevant example, and end with the outcome or learning."

    }


# ============================================================
# AI ANSWER EVALUATION
# ============================================================

def evaluate_answer_with_ai(
    question,
    answer,
    domain,
    resume_analysis
):

    fallback = feedback_for(
        answer
    )


    if client is None:

        return fallback


    prompt = f"""
You are an expert AI interview evaluator.

Evaluate the candidate's answer.

Interview Domain:
{domain}

Question:
{question}

Candidate Answer:
{answer}

Candidate Resume Information:
Name: {resume_analysis.get("name", "Not detected")}
Skills: {", ".join(resume_analysis.get("skills", []))}
Education: {resume_analysis.get("education", "Not detected")}
Experience: {resume_analysis.get("experience", "Not detected")}

Return ONLY valid JSON.

Required format:

{{
    "score": 0,
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "improvements": [
        "improvement 1",
        "improvement 2"
    ],
    "better": "A better version of the answer"
}}

Scoring:

0-30 = Very weak
31-50 = Needs improvement
51-70 = Average
71-85 = Good
86-100 = Excellent

Evaluate:

- Relevance
- Correctness
- Clarity
- Completeness
- Communication
- Practical examples
- Domain knowledge

Do not invent candidate experience.
"""


    try:

        response = client.responses.create(

            model=AI_MODEL,

            input=prompt

        )


        output = response.output_text.strip()


        output = re.sub(
            r"^```json\s*",
            "",
            output,
            flags=re.IGNORECASE
        )

        output = re.sub(
            r"\s*```$",
            "",
            output
        )


        data = json.loads(
            output
        )


        score = int(
            data.get(
                "score",
                fallback["score"]
            )
        )


        score = max(
            0,
            min(
                score,
                100
            )
        )


        strengths = data.get(
            "strengths",
            fallback["strengths"]
        )


        improvements = data.get(
            "improvements",
            fallback["improvements"]
        )


        better = data.get(
            "better",
            fallback["better"]
        )


        return {

            "score":
                score,

            "strengths":
                strengths,

            "improvements":
                improvements,

            "better":
                better

        }


    except Exception as e:

        print(
            "AI answer evaluation error:",
            e
        )

        return fallback


# ============================================================
# PUBLIC HOME
# ============================================================

@app.route("/")
def public_home():

    return render_template(
        "index.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()


        if email:

            username = email.split(
                "@"
            )[0]


            username = username.replace(
                ".",
                " "
            ).replace(
                "_",
                " "
            )


            session[
                "user_name"
            ] = username.title()


        else:

            session[
                "user_name"
            ] = "User"

        # Keep profile available after login
        if not session.get("profile"):
            session["profile"] = {
                "name": session.get("user_name", "User"),
                "email": email,
                "phone": "",
                "education": "",
                "career_goal": "",
                "photo": None
            }


        return redirect(
            url_for("home")
        )


    return render_template(
        "index.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            "User"
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip()


        session[
            "user_name"
        ] = name or "User"


        session[
            "user_email"
        ] = email

        # Save basic profile automatically at registration
        existing_profile = session.get("profile", {})
        session["profile"] = {
            "name": name or "User",
            "email": email,
            "phone": existing_profile.get("phone", ""),
            "education": existing_profile.get("education", ""),
            "career_goal": existing_profile.get("career_goal", ""),
            "photo": existing_profile.get("photo")
        }


        return redirect(
            url_for("home")
        )


    return render_template(
        "index.html"
    )


# ============================================================
# LOGGED-IN HOME
# ============================================================

@app.route("/home")
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    feedback = session.get(
        "feedback",
        []
    )


    questions = session.get(
        "questions",
        []
    )


    average = 0


    if feedback:

        average = round(
            sum(
                item.get(
                    "score",
                    0
                )
                for item in feedback
            )
            /
            len(feedback)
        )


    return render_template(

        "dashboard.html",

        average=average,

        total_questions=len(
            questions
        ),

        domain=session.get(
            "domain",
            "Not Started"
        ),

        feedback=feedback

    )


# ============================================================
# RESUME PAGE
# ============================================================

@app.route("/resume")
def resume():

    success = session.pop(
        "resume_success",
        None
    )


    error = session.pop(
        "resume_error",
        None
    )


    return render_template(

        "resume.html",

        resume_analysis=session.get(
            "resume_analysis"
        ),

        resume_filename=session.get(
            "resume_filename"
        ),

        success=success,

        error=error

    )


# ============================================================
# UPLOAD RESUME
# ============================================================

@app.route(
    "/upload",
    methods=["GET", "POST"]
)
def upload():

    if request.method == "POST":

        file = request.files.get(
            "resume"
        )


        # -----------------------------------------
        # No file
        # -----------------------------------------

        if (
            not file
            or
            file.filename == ""
        ):

            session[
                "resume_error"
            ] = "Please select a resume file."


            return redirect(
                url_for("resume")
            )


        # -----------------------------------------
        # Invalid file
        # -----------------------------------------

        if not allowed_file(
            file.filename
        ):

            session[
                "resume_error"
            ] = "Allowed formats: PDF, DOCX or TXT."


            return redirect(
                url_for("resume")
            )


        # -----------------------------------------
        # Save file
        # -----------------------------------------

        filename = secure_filename(
            file.filename
        )


        saved_file = (
            UPLOAD_FOLDER
            /
            filename
        )


        file.save(
            saved_file
        )


        # -----------------------------------------
        # Extract resume text
        # -----------------------------------------

        resume_text = extract_text(
            saved_file
        )


        resume_text = clean_text(
            resume_text
        )


        # -----------------------------------------
        # Empty / unreadable resume
        # -----------------------------------------

        if not resume_text:

            session[
                "resume_error"
            ] = (
                "Resume uploaded, but no readable text was found. "
                "Please upload a text-based PDF, DOCX or TXT file."
            )


            return redirect(
                url_for("resume")
            )


        # -----------------------------------------
        # Save resume information
        # -----------------------------------------

        session[
            "resume_filename"
        ] = filename


        session[
            "resume_text"
        ] = resume_text[:12000]


        # IMPORTANT:
        # Analysis is NOT done here.
        # User must click Analyze Resume.

        session.pop(
            "resume_analysis",
            None
        )


        session[
            "resume_success"
        ] = (
            f"Resume '{filename}' uploaded successfully!"
        )


        return redirect(
            url_for("resume")
        )


    return redirect(
        url_for("resume")
    )


# ============================================================
# ANALYZE RESUME
# ============================================================

@app.route(
    "/analyze-resume",
    methods=["POST"]
)
def analyze_resume_route():

    resume_text = session.get(
        "resume_text"
    )


    # -----------------------------------------
    # Resume not uploaded
    # -----------------------------------------

    if not resume_text:

        session[
            "resume_error"
        ] = (
            "Please upload your resume first."
        )


        return redirect(
            url_for("resume")
        )


    # -----------------------------------------
    # AI Resume Analysis
    # -----------------------------------------

    analysis = ai_analyze_resume(
        resume_text
    )


    session[
        "resume_analysis"
    ] = analysis


    session[
        "resume_success"
    ] = (
        "Resume analysis completed successfully!"
    )


    return redirect(
        url_for("resume")
    )


# ============================================================
# INTERVIEW HOME / SETUP
# ============================================================

@app.route(
    "/interview-home"
)
def interview_home():

    return render_template(

        "interview_home.html",

        domains=DOMAINS,

        resume_filename=session.get(
            "resume_filename"
        ),

        resume_analysis=session.get(
            "resume_analysis"
        )

    )


# ============================================================
# SELECT DOMAIN + QUESTION COUNT
# ============================================================

@app.route(
    "/select-domain",
    methods=["GET", "POST"]
)
def select_domain():

    if request.method == "POST":

        # -----------------------------------------
        # Resume required
        # -----------------------------------------

        if not session.get(
            "resume_text"
        ):

            session[
                "resume_error"
            ] = (
                "Please upload your resume first."
            )


            return redirect(
                url_for("resume")
            )


        # -----------------------------------------
        # Get domain
        # -----------------------------------------

        selected_domain = request.form.get(
            "domain",
            "General / Other"
        )


        domain = domain_aliases.get(
            selected_domain,
            "General / Other"
        )


        # -----------------------------------------
        # Get question count
        # -----------------------------------------

        try:

            num_questions = int(
                request.form.get(
                    "num_questions",
                    5
                )
            )

        except ValueError:

            num_questions = 5


        if num_questions not in [
            5,
            10,
            15,
            20
        ]:

            num_questions = 5


        # -----------------------------------------
        # Resume analysis
        # -----------------------------------------

        resume_analysis = session.get(
            "resume_analysis"
        )


        if not resume_analysis:

            resume_analysis = analyze_resume(
                session.get(
                    "resume_text",
                    ""
                )
            )


            session[
                "resume_analysis"
            ] = resume_analysis


        # -----------------------------------------
        # Generate AI questions
        # -----------------------------------------

        questions = generate_ai_questions(

            session.get(
                "resume_text",
                ""
            ),

            resume_analysis,

            domain,

            num_questions

        )


        # -----------------------------------------
        # Save interview data
        # -----------------------------------------

        session[
            "domain"
        ] = domain


        session[
            "num_questions"
        ] = len(
            questions
        )


        session[
            "questions"
        ] = questions


        session[
            "answers"
        ] = []


        session[
            "feedback"
        ] = []


        # -----------------------------------------
        # Start interview
        # -----------------------------------------

        return redirect(
            url_for("interview")
        )


    return render_template(

        "interview_home.html",

        domains=DOMAINS

    )


# ============================================================
# INTERVIEW
# ============================================================

@app.route(
    "/interview",
    methods=["GET", "POST"]
)
def interview():

    questions = session.get(
        "questions",
        []
    )


    answers = session.get(
        "answers",
        []
    )


    feedback = session.get(
        "feedback",
        []
    )


    # -----------------------------------------
    # No interview started
    # -----------------------------------------

    if not questions:

        return redirect(
            url_for("interview_home")
        )


    # -----------------------------------------
    # Submit answer
    # -----------------------------------------

    if request.method == "POST":

        answer = request.form.get(
            "answer",
            ""
        ).strip()


        # Current question number

        current_index = len(
            answers
        )


        if current_index < len(
            questions
        ):

            current_question = questions[
                current_index
            ]


            # -----------------------------------------
            # AI Answer Evaluation
            # -----------------------------------------

            analysis = session.get(
                "resume_analysis",
                {}
            )


            answer_feedback = (
                evaluate_answer_with_ai(

                    current_question,

                    answer,

                    session.get(
                        "domain",
                        "General / Other"
                    ),

                    analysis

                )
            )


            answers.append(
                answer
            )


            feedback.append(
                answer_feedback
            )


            session[
                "answers"
            ] = answers


            session[
                "feedback"
            ] = feedback


        # -----------------------------------------
        # All questions completed
        # -----------------------------------------

        if len(answers) >= len(
            questions
        ):

            return redirect(
                url_for("results")
            )


        # -----------------------------------------
        # Next question
        # -----------------------------------------

        return redirect(
            url_for(
                "interview",
                q=len(answers)
            )
        )


    # -----------------------------------------
    # Current question index
    # -----------------------------------------

    try:

        index = int(
            request.args.get(
                "q",
                len(answers)
            )
        )

    except ValueError:

        index = len(answers)


    if index < 0:

        index = 0


    if index >= len(
        questions
    ):

        index = len(
            questions
        ) - 1


    return render_template(

        "interview.html",

        question=questions[index],

        number=index + 1,

        total=len(questions),

        domain=session.get(
            "domain",
            "General / Other"
        )

    )


# ============================================================
# RESULTS
# ============================================================

@app.route("/results")
def results():

    feedback = session.get(
        "feedback",
        []
    )


    answers = session.get(
        "answers",
        []
    )


    questions = session.get(
        "questions",
        []
    )


    if not feedback:

        return redirect(
            url_for("dashboard")
        )


    scores = [

        item.get(
            "score",
            0
        )

        for item in feedback

    ]


    average = round(
        sum(scores)
        /
        len(scores)
    )


    return render_template(

        "results.html",

        feedback=feedback,

        answers=answers,

        questions=questions,

        average=average,

        domain=session.get(
            "domain",
            "General / Other"
        )

    )


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    # Existing profile
    profile_data = session.get("profile", {})

    # Automatically create profile from registered/login user
    if not profile_data:
        profile_data = {
            "name": session.get("user_name", "User"),
            "email": session.get("user_email", ""),
            "phone": "",
            "education": "",
            "career_goal": "",
            "photo": None
        }
        session["profile"] = profile_data
    else:
        profile_data.setdefault("name", session.get("user_name", "User"))
        profile_data.setdefault("email", session.get("user_email", ""))
        profile_data.setdefault("phone", "")
        profile_data.setdefault("education", "")
        profile_data.setdefault("career_goal", "")
        profile_data.setdefault("photo", None)
        session["profile"] = profile_data


    if request.method == "POST":

        # -----------------------------------------
        # Basic information
        # -----------------------------------------

        name = request.form.get(
            "name",
            ""
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip()


        phone = request.form.get(
            "phone",
            ""
        ).strip()


        education = request.form.get(
            "education",
            ""
        ).strip()


        career_goal = request.form.get(
            "career_goal",
            ""
        ).strip()


        # -----------------------------------------
        # Save profile photo
        # -----------------------------------------

        photo = request.files.get(
            "photo"
        )


        photo_filename = profile_data.get(
            "photo"
        )


        if (
            photo
            and
            photo.filename
        ):

            if allowed_image(
                photo.filename
            ):

                original_name = secure_filename(
                    photo.filename
                )


                # Unique filename

                extension = (
                    original_name
                    .rsplit(
                        ".",
                        1
                    )[1]
                    .lower()
                )


                photo_filename = (
                    "profile_"
                    +
                    str(
                        abs(
                            hash(
                                name
                                +
                                email
                                +
                                original_name
                            )
                        )
                    )
                    +
                    "."
                    +
                    extension
                )


                photo_path = (
                    PROFILE_PHOTO_FOLDER
                    /
                    photo_filename
                )


                photo.save(
                    photo_path
                )


            else:

                session[
                    "profile_error"
                ] = (
                    "Only JPG, JPEG and PNG images are allowed."
                )


                return redirect(
                    url_for("profile")
                )


        # -----------------------------------------
        # Save profile
        # -----------------------------------------

        profile_data = {

            "name":
                name,

            "email":
                email,

            "phone":
                phone,

            "education":
                education,

            "career_goal":
                career_goal,

            "photo":
                photo_filename

        }


        session[
            "profile"
        ] = profile_data


        # Update logged-in name

        if name:
            session[
                "user_name"
            ] = name

        if email:
            session[
                "user_email"
            ] = email


        session[
            "profile_success"
        ] = (
            "Profile updated successfully!"
        )


        return redirect(
            url_for("profile")
        )


    success = session.pop(
        "profile_success",
        None
    )


    error = session.pop(
        "profile_error",
        None
    )


    return render_template(

        "profile.html",

        profile=profile_data,

        success=success,

        error=error

    )


# ============================================================
# PERFORMANCE
# ============================================================

@app.route("/performance")
def performance():

    feedback = session.get(
        "feedback",
        []
    )


    questions = session.get(
        "questions",
        []
    )


    scores = [

        item.get(
            "score",
            0
        )

        for item in feedback

    ]


    average = 0


    if scores:

        average = round(
            sum(scores)
            /
            len(scores)
        )


    return render_template(

        "performance.html",

        average=average,

        total_questions=len(
            questions
        ),

        domain=session.get(
            "domain",
            "Not Started"
        ),

        feedback=feedback

    )


# ============================================================
# HELP
# ============================================================

@app.route("/help")
def help_page():

    return render_template(
        "help.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()


    return redirect(
        url_for("public_home")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        " AI INTERVIEW SYSTEM"
    )

    print(
        "========================================"
    )

    print(
        "OpenAI API Key Loaded:",
        bool(
            os.getenv(
                "OPENAI_API_KEY"
            )
        )
    )

    print(
        "Server: http://127.0.0.1:5000"
    )

    print(
        "========================================\n"
    )


    app.run(
        debug=True
    )