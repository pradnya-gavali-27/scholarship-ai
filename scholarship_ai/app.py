
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-for-local-development"
)

MAHADBT = "https://mahadbt.maharashtra.gov.in/"
NSP = "https://scholarships.gov.in/All-Scholarships"

COMMON_DOCUMENTS = [
    "Identity proof accepted by the scheme",
    "Recent passport-size photograph",
    "Bank passbook/details, if required",
    "Previous examination marksheet",
    "Current admission proof or bonafide certificate",
    "Fee receipt, if required",
]

CATEGORY_DOCUMENTS = {
    "SC": [
        "Caste certificate, if required",
        "Caste validity certificate, if required",
    ],
    "ST": [
        "Tribe certificate, if required",
        "Tribe validity certificate, if required",
    ],
    "OBC": [
        "Caste certificate, if required",
        "Non-creamy layer certificate, if applicable",
    ],
    "VJNT": [
        "Caste certificate, if required",
        "Non-creamy layer certificate, if applicable",
    ],
    "SBC": [
        "Caste certificate, if required",
        "Non-creamy layer certificate, if applicable",
    ],
    "EWS": ["Valid EWS certificate, if required"],
    "General": [],
    "Prefer not to say": [],
}


def get_document_checklist(profile):
    docs = COMMON_DOCUMENTS.copy()
    docs.extend(
        CATEGORY_DOCUMENTS.get(profile.get("category", ""), [])
    )

    if profile.get("income_certificate") == "No":
        docs.append("Income certificate, if required by the scheme")

    if profile.get("disability") == "Yes":
        docs.append("Disability certificate, if required")

    if profile.get("hostel") == "Yes":
        docs.append("Hostel certificate or residence proof, if required")

    return list(dict.fromkeys(docs))


def scholarship_response(category):
    """Return possible scholarship schemes to investigate."""

    schemes = {
        "SC": [
            "Government of India Post-Matric Scholarship for SC Students",
            "Post-Matric Tuition Fee and Examination Fee (Freeship)",
            "Central Sector Scheme of Top Class Education for SC Students",
        ],
        "ST": [
            "Post-Matric Scholarship Scheme for ST Students",
            "Tuition Fee and Examination Fee for Tribal Students (Freeship)",
            "National Fellowship and Scholarship for Higher Education of ST Students",
        ],
        "OBC": [
            "Post-Matric Scholarship to OBC Students (Maharashtra)",
            "Tuition Fees and Examination Fees to OBC Students",
            "PM YASASVI Top Class Education in College for OBC, EBC and DNT Students",
        ],
        "VJNT": [
            "Post-Matric Scholarship to VJNT Students",
            "Tuition Fees and Examination Fees to VJNT Students",
            "Other eligible VJNT schemes listed on MahaDBT",
        ],
        "SBC": [
            "Post-Matric Scholarship to SBC Students",
            "Tuition Fees and Examination Fees to SBC Students",
            "Other eligible SBC schemes listed on MahaDBT",
        ],
        "EWS": [
            "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti Scheme (EBC), if eligible",
            "Dr. Panjabrao Deshmukh Hostel Maintenance Allowance schemes, if eligible",
            "Other eligible schemes listed on MahaDBT",
        ],
        "GENERAL": [
            "State Government Open Merit Scholarship",
            "Assistance to Meritorious Students Scholarship",
            "PM-USP Central Sector Scheme of Scholarship for College and University Students",
            "Other eligible open-category schemes listed on MahaDBT",
        ],
        "DISABILITY": [
            "Pre-Matric Scholarship for Students with Disabilities",
            "Post-Matric Scholarship for Students with Disabilities",
            "Scholarship for Top Class Education for Students with Disabilities",
        ],
    }

    names = schemes.get(category)

    if not names:
        return (
            "Please tell me your state, category and current course "
            "so I can suggest relevant scholarship schemes.\n\n"
            f"MahaDBT: {MAHADBT}\n"
            f"National Scholarship Portal: {NSP}"
        )

    result = "Scholarship schemes you can investigate:\n\n"

    for number, name in enumerate(names, start=1):
        result += f"{number}. {name}\n"

    result += (
        "\nOfficial portals:\n"
        f"MahaDBT Maharashtra: {MAHADBT}\n"
        f"National Scholarship Portal: {NSP}\n\n"
        "Important: These are possible options, not confirmation of "
        "eligibility or current application availability. Eligibility "
        "depends on the scheme rules, course, income, academic year "
        "and institution. Verify the latest details on the official portal."
    )

    return result



def get_guidance_answer(message, profile=None):
    """Answer scholarship questions using local guidance and optional AI."""

    text = message.lower().strip()

    # Scholarship approval guarantee questions
    if any(term in text for term in [
        "guarantee", "will i receive", "will i get",
        "definitely receive", "definitely get",
        "sure to get", "surely get"
    ]):
        return (
            "Scholarship approval cannot be guaranteed. It depends on "
            "the scheme rules, your eligibility, document verification "
            "and the scholarship authority.\n\n"
            "Check the official scheme guidelines:\n"
            f"MahaDBT: {MAHADBT}\n"
            f"National Scholarship Portal: {NSP}"
        )

    # Application and form-filling questions
    if any(term in text for term in [
        "fill", "form", "application", "apply", "how to register"
    ]):
        return (
            "Here are the basic steps to apply for a scholarship:\n\n"
            "1. Open the official scholarship portal.\n"
            "2. Register or log in to your account.\n"
            "3. Select the scholarship scheme for which you may qualify.\n"
            "4. Enter your personal, academic and bank details accurately.\n"
            "5. Upload the required documents.\n"
            "6. Review the form before submitting it.\n"
            "7. Save your application number or acknowledgement.\n"
            "8. Track your application status on the portal.\n\n"
            "For Maharashtra scholarships, start here:\n"
            f"{MAHADBT}\n\n"
            "The exact steps and documents may differ by scheme. "
            "Never share your password or OTP with anyone."
        )

    # Deadline questions
    if any(term in text for term in [
        "deadline", "last date", "due date",
        "closing date", "application deadline"
    ]):
        return (
            "Scholarship deadlines vary by scheme and academic year. "
            "Check the latest dates on the official portals:\n\n"
            f"MahaDBT: {MAHADBT}\n"
            f"National Scholarship Portal: {NSP}"
        )

    # Detect student profile details in the message
    category = None

    if any(term in text for term in [
        "scheduled caste", "sc category", "sc student",
        "category sc", "category is sc"
    ]) or text == "sc":
        category = "SC"
    elif "obc" in text:
        category = "OBC"
    elif "vjnt" in text:
        category = "VJNT"
    elif "sbc" in text:
        category = "SBC"
    elif any(term in text for term in ["scheduled tribe", "st student"]):
        category = "ST"
    elif "ews" in text:
        category = "EWS"
    elif "disability" in text or "disabled" in text:
        category = "DISABILITY"
    elif "general category" in text or "open category" in text:
        category = "GENERAL"

    is_maharashtra = any(term in text for term in [
        "maharashtra", "maharashtra state"
    ])

    is_be_computer = any(term in text for term in [
        "be in computer engineering",
        "computer engineering",
        "b.e.",
        "bachelor of engineering"
    ])

    # Specific Maharashtra SC engineering student
    if category == "SC" and is_maharashtra and is_be_computer:
        return (
            "Based on your details — Maharashtra, SC category, "
            "BE Computer Engineering — you can investigate these options:\n\n"
            "1. Government of India Post-Matric Scholarship for SC Students.\n"
            "2. Post-Matric Tuition Fee and Examination Fee (Freeship).\n"
            "3. Central Sector Scheme of Top Class Education for SC Students, "
            "if your institution and other conditions qualify.\n\n"
            f"MahaDBT Maharashtra: {MAHADBT}\n"
            f"National Scholarship Portal: {NSP}\n\n"
            "These are options to investigate, not confirmation that you "
            "qualify. Eligibility may depend on family income, institution, "
            "course, academic year and other scheme rules. Check the current "
            "guidelines before applying."
        )

    # Category-specific scholarship questions
    finder_terms = [
        "scholarship", "scholarships", "which scheme",
        "which schemes", "scheme for", "schemes for",
        "available for", "find scholarship"
    ]

    short_followups = [
        "for sc", "for sc student", "for sc students",
        "sc", "sc student", "for obc", "for obc student",
        "obc student", "for st", "st student",
        "for vjnt", "vjnt student", "for sbc", "sbc student",
        "for ews", "ews student"
    ]

    if any(term in text for term in finder_terms) or text in short_followups:
        if category:
            return scholarship_response(category)

        return (
            "I can help find possible scholarships. Please tell me "
            "your state, category and current course.\n\n"
            f"MahaDBT: {MAHADBT}\n"
            f"National Scholarship Portal: {NSP}"
        )

    # Document questions
    if any(term in text for term in [
        "document", "documents", "certificate", "paper"
    ]):
        return (
            "Common documents may include identity proof, photograph, "
            "previous marksheet, admission proof and bank details if "
            "required. Income and category certificates may also be "
            "needed. Check the official scheme document list:\n"
            f"{MAHADBT}"
        )

    # Form errors and rejected applications
    if any(term in text for term in [
        "wrong", "error", "mistake", "invalid", "rejected"
    ]):
        return (
            "Check that your details match your documents, all required "
            "fields are complete, and uploaded files meet the portal's "
            "format and size rules. If the error continues, contact "
            "your institute or the scholarship helpdesk."
        )

    # Eligibility questions
    if any(term in text for term in [
        "eligible", "eligibility", "qualify"
    ]):
        return (
            "Eligibility depends on the exact scheme, course, academic year, "
            "state, income, category and institution. Check the current "
            "official guidelines. I cannot guarantee approval.\n\n"
            f"MahaDBT: {MAHADBT}"
        )

    # Optional AI integration
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                instructions=(
                    "You are Scholarship AI. Give concise, simple and "
                    "careful scholarship guidance. Never invent deadlines, "
                    "eligibility or benefits. Never guarantee approval. "
                    "Use official portals and ask for missing student details."
                ),
                input=message,
            )

            if response.output_text:
                return response.output_text

        except Exception:
            pass

    return (
        "Hi! I'm Scholarship AI. I can help with scholarship names, "
        "documents, eligibility, application forms and common errors.\n\n"
        "Tell me your state, category and current course for more "
        "focused guidance.\n\n"
        f"MahaDBT: {MAHADBT}\n"
        f"National Scholarship Portal: {NSP}"
    )



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/checklist", methods=["POST"])
def checklist():
    profile = {
        "education": request.form.get("education", ""),
        "state": request.form.get("state", ""),
        "category": request.form.get("category", ""),
        "income_certificate": request.form.get(
            "income_certificate", "Not sure"
        ),
        "disability": request.form.get("disability", "No"),
        "hostel": request.form.get("hostel", "No"),
    }

    documents = get_document_checklist(profile)

    return render_template(
        "index.html",
        profile=profile,
        documents=documents,
        checklist_shown=True,
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({
            "reply": "Please type a question first."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "reply": "Please keep your question under 2,000 characters."
        }), 400

    reply = get_guidance_answer(message)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
