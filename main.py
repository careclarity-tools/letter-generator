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

# --- OPENAI SETUP (with fallback) ---
api_key = st.secrets["openai"]["api_key"] if "openai" in st.secrets else os.getenv("OPENAI_API_KEY")
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

# --- LETTER STRUCTURE ---
letter_structure = {
    "Care Complaint Letter": {
        "Neglect or injury": [
            "Who was harmed?",
            "Where did it happen?",
            "What happened?",
            "What was the result?",
            "Have you raised this already?"
        ],
        "Medication errors": [
            "What was the error?",
            "When and where?",
            "Who was affected?",
            "What actions were taken?",
            "What do you want done now?"
        ],
        "Staff conduct": [
            "What happened?",
            "Who was involved?",
            "Was this one-time or ongoing?",
            "What was the impact?",
            "Have you spoken to the provider?"
        ],
        "Cleanliness or environment": [
            "What hygiene issue or risk occurred?",
            "Who did it affect?",
            "What date/time was this?",
            "Has it been addressed?",
            "Are you seeking specific action?"
        ],
        "General standards of care": [
            "What care concerns do you have?",
            "Is this recent or long-standing?",
            "Any dates/incidents worth noting?",
            "What changes are you requesting?"
        ]
    },
    "Thank You & Positive Feedback": {
        "Praise for a staff member": [
            "What did they do well?",
            "When and where?",
            "What impact did it have?",
            "Do you want management to be notified?"
        ],
        "Thank a team or home": [
            "What overall praise would you like to give?",
            "Is there a specific moment worth mentioning?",
            "Would you like to stay in contact?"
        ],
        "Positive discharge feedback": [
            "What made the discharge go well?",
            "Who was involved?",
            "Any specific comments you'd like to share?"
        ],
        "Support during end-of-life care": [
            "Who provided support?",
            "What actions stood out?",
            "Would you like this shared with leadership?"
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
            "- Still reflect concern for the well-being of the individual or team involved, without sounding dismissive or cold.\n"
            "- Explicitly state concern for duty of care or CQC standards.\n"
            "- Use language that is respectful yet assertive, with clear expectations for response.\n"
            "- Reference relevant regulations or safeguarding principles where appropriate.\n"
            "- Mention escalation options such as safeguarding boards or CQC, but in a professional manner.\n\n"
        )
    else:
        action_block = (
            "Please write this letter in a calm, assertive, and emotionally intelligent tone. The letter should:\n"
            "- Clearly explain the concern or incident\n"
            "- Highlight any risk to the individual or others\n"
            "- Request investigation, documentation, and appropriate escalation\n"
            "- Mention any reports already made to safeguarding teams or regulators if noted\n"
            "- Specify that a written response and named accountability are expected within a reasonable timeframe\n"
            "- Close with a readiness to escalate if the matter is not taken seriously\n\n"
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




