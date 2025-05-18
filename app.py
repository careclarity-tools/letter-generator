
       import streamlit as st
import json
from openai import OpenAI

# --- LICENSE KEY SETUP ---
VALID_KEYS_FILE = "valid_keys.json"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication check
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

# --- OPENAI SETUP ---
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- GDPR Consent ---
gdpr_consent = st.checkbox("I consent to data processing (GDPR)")
if not gdpr_consent:
    st.warning("You must consent to GDPR processing to continue.")
    st.stop()

# --- TONE TOGGLE ---
tone = st.radio(
    "Select the tone for your letter:",
    ("Standard", "Serious Formal Complaint"),
    help="Choose 'Serious Formal Complaint' for regulatory language and strong escalation wording."
)

# --- LETTER STRUCTURE ---
letter_structure = {
    "Care Complaint Letter": {
        "Neglect or injury": [
            "Who was harmed?", "Where did it happen?", "What happened?", "What was the result?", "Have you raised this already?"
        ],
        "Medication errors": [
            "What was the error?", "When and where?", "Who was affected?", "What actions were taken?", "What do you want done now?"
        ],
        "Staff conduct": [
            "What happened?", "Who was involved?", "Was this one-time or ongoing?", "What was the impact?", "Have you spoken to the provider?"
        ]
        # Add additional subcategories as needed
    },
    "Family Advocacy Letter": {
        "Request a meeting": [
            "Who do you want to meet with?", "What is the purpose of the meeting?", "Any preferred dates/times?", "Is this urgent or routine?"
        ],
        "Disagree with discharge": [
            "Who is being discharged?", "What are your concerns?", "What support is missing?", "Have you spoken to the discharge team?"
        ]
        # Add additional subcategories as needed
    }
    # Add more categories as necessary
}

# --- ADVANCED TONE-AWARE PROMPT LOGIC ---
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

    if tone == "Serious Formal Complaint":
        action_block = (
            "Please write this letter in a direct, formal, and legally aware tone. The letter should:\n"
            "- Reference Regulation 13 or safeguarding principles where relevant\n"
            "- Explicitly state concern for duty of care or CQC standards\n"
            "- Request documentation (body maps, reports, policies) if applicable\n"
            "- Demand a named point of accountability and timeline\n"
            "- Note possible escalation to safeguarding boards, CQC, or ombudsman\n"
            "- Include closing phrases such as 'will not hesitate to escalate' or 'formal complaint'\n\n"
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

# --- FORM UI ---
selected_category = st.selectbox("Choose your letter category:", list(letter_structure.keys()))

if selected_category:
    subcategories = list(letter_structure[selected_category].keys())
    selected_subcategory = st.selectbox(f"Select the issue type under '{selected_category}':", subcategories)

    if selected_subcategory:
        st.markdown("---")
        st.subheader("📝 Please answer the following questions:")
        user_answers = {}
        for question in letter_structure[selected_category][selected_subcategory]:
            response = st.text_area(question, key=question)
            user_answers[question] = response

        user_name = st.text_input("Your Name")

        if st.button("Generate Letter"):
            full_prompt = generate_prompt(selected_category, selected_subcategory, user_answers, user_name, tone)

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.7
                )
                generated_letter = response.choices[0].message.content
                st.text_area("Generated Letter", generated_letter, height=300)
            except Exception as e:
                st.error(f"Error with OpenAI API: {e}")



     
 
