


import streamlit as st
import json
import os
from openai import OpenAI

# --- LICENSE KEY SETUP ---
VALID_KEYS_FILE = "valid_keys.json"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    license_key = st.text_input("Enter your license key", type="password")

    try:
        with open(VALID_KEYS_FILE, "r") as f:
            valid_keys = json.load(f)
    except FileNotFoundError:
        valid_keys = []

    if license_key in valid_keys:
        st.session_state.authenticated = True
        st.success("Access granted. Welcome.")
    else:
        st.warning("Invalid or already-used license key.")
        st.stop()

# --- OPENAI SETUP (with hardened fallback) ---
api_key = st.secrets.get("openai", {}).get("api_key", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key)

# --- GDPR Consent ---
gdpr_consent = st.checkbox("I consent to data processing (GDPR)")
if not gdpr_consent:
    st.warning("You must consent to GDPR processing to continue.")
    st.stop()

# --- TONE TOGGLE ---
tone = st.radio(
    "Select the tone for your letter:",
    ("Standard", "Serious Formal Complaint"),
    help="Choose 'Serious Formal Complaint' if you want regulatory language and strong escalation wording."
)

# --- LETTER STRUCTURE (trimmed for this demo build) ---
letter_structure = {
    "Care Complaint Letter": {
        "Neglect or injury": [
            "Who was harmed?",
            "Where did it happen?",
            "What happened?",
            "What was the result?",
            "Have you raised this already?"
        ]
    },
    "Thank You & Positive Feedback": {
        "Praise for a staff member": [
            "What did they do well?",
            "When and where?",
            "What impact did it have?",
            "Do you want management to be notified?"
        ]
    }
}

# --- PROMPT LOGIC ---
def generate_prompt(category, subcategory, answers, user_name, tone):
    base_intro = (
        "You are an experienced care quality advocate who understands CQC regulations, safeguarding protocol, "
        "mental capacity considerations, and the rights of service users. Your task is to generate a formal letter "
        "that addresses a care-related concern raised by a family member, advocate, or staff whistleblower.\n\n"
    )

    context_block = f"Letter Category: {category}\nIssue Type: {subcategory}\n\n"

    summary_block = ""
    for q, a in answers.items():
        if a.strip():
            summary_block += f"{q}\n{a.strip()}\n\n"

    temperature = 0.3 if tone == "Serious Formal Complaint" else 0.7

    if tone == "Serious Formal Complaint":
        action_block = (
            "Please write this letter in a direct, formal, and legally aware tone. The letter should:\n"
            "- Be factual and to the point, avoiding unnecessary elaboration.\n"
            "- Still reflect concern for the well-being of the individual or team involved.\n"
            "- Explicitly state concern for duty of care or CQC standards.\n"
            "- Use language that is respectful yet assertive.\n"
            "- Mention escalation options if necessary.\n\n"
        )
    else:
        action_block = (
            "Please write this letter in a calm, emotionally intelligent tone. The letter should:\n"
            "- Clearly explain the concern\n"
            "- Highlight risk or impact\n"
            "- Request investigation and response\n\n"
        )

    closing = f"Please end the letter with:\nSincerely,\n{user_name}"
    return base_intro + context_block + summary_block + action_block + closing

# --- UI ---
selected_category = st.selectbox("Choose your letter category:", list(letter_structure.keys()))
if selected_category:
    subcategories = list(letter_structure[selected_category].keys())
    selected_subcategory = st.selectbox(f"Select the issue type under '{selected_category}':", subcategories)
    if selected_subcategory:
        st.markdown("---")
        st.subheader("📝 Please answer the following:")
        user_answers = {q: st.text_area(q) for q in letter_structure[selected_category][selected_subcategory]}
        user_name = st.text_input("Your Name")
        if st.button("Generate Letter"):
            prompt = generate_prompt(selected_category, selected_subcategory, user_answers, user_name, tone)
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                st.text_area("Generated Letter", response.choices[0].message.content, height=300)
            except Exception as e:
                st.error(f"OpenAI error: {e}")


