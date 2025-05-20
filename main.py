import streamlit as st
import json
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
    help="Choose 'Serious Formal Complaint' for regulatory and strong language."
)

# --- LETTER STRUCTURE (trimmed for preview) ---
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
            "When and where did it happen?",
            "Who was affected?",
            "What actions were taken?",
            "What outcome are you requesting?"
        ],
        "General care concerns": [
            "What is the concern?",
            "How long has this been an issue?",
            "Who have you spoken to?",
            "What would a satisfactory response include?"
        ]
    },
    "Family Advocacy Letter": {
        "Request a meeting": [
            "Who do you want to meet with?",
            "What’s the reason or topic?",
            "Any deadlines or time sensitivity?",
            "Preferred outcome?"
        ],
        "Disagree with discharge": [
            "Who is being discharged?",
            "What are your objections?",
            "Has a safe discharge plan been provided?",
            "What are you requesting instead?"
        ]
    }
}

# --- EMOTION + PREAMBLE LOGIC ---
def detect_emotion(answers):
    emotional_keywords = ["angry", "ignored", "worried", "frustrated", "distressed", "unsafe", "shocked", "unheard"]
    return [word for word in emotional_keywords if any(word in a.lower() for a in answers.values())]

def generate_preamble(tone, category, emotion_flags):
    if tone == "Serious Formal Complaint":
        return "I am writing to formally raise serious concerns regarding the following matter."
    elif "worried" in emotion_flags or "unsafe" in emotion_flags:
        return "I am deeply concerned about the following situation, which I feel requires urgent attention."
    elif "angry" in emotion_flags:
        return "This letter reflects our distress and strong dissatisfaction with the care being provided."
    else:
        return f"I would like to bring forward a {category.lower()} matter that I hope will be reviewed and addressed promptly."

def wrap_answers(answers):
    return "\n".join([f"{q}\nThe user shared: \"{a.strip()}\"\n" for q, a in answers.items() if a.strip()])

# --- PROMPT GENERATOR ---
def generate_prompt(category, subcategory, answers, user_name, tone):
    emotion_flags = detect_emotion(answers)
    preamble = generate_preamble(tone, category, emotion_flags)
    summary = wrap_answers(answers)

    base_context = (
        "You are a formal letter writer helping a care advocate, family member or legal deputy draft a serious letter to a care provider, hospital, or regulatory body.\n\n"
        "They are raising concerns that may relate to safeguarding, unsafe discharge, care needs, or general quality. Be factual, supportive, clear, and firm."
    )

    letter_body = f"""
Letter Category: {category}
Issue Type: {subcategory}

{preamble}

{summary}

The letter should:
- Use emotionally intelligent but clear language
- Include clear expectations of reply or action
- Reflect urgency where implied
- Remain respectful but assertive

End the letter with:
Sincerely,
{user_name}
"""
    return f"{base_context}\n\n{letter_body}"

# --- FORM UI ---
st.title("📄 Care Clarity Letter Generator")

selected_category = st.selectbox("Choose a letter category:", list(letter_structure.keys()))

if selected_category:
    subcategories = list(letter_structure[selected_category].keys())
    selected_subcategory = st.selectbox(f"Select the issue under '{selected_category}':", subcategories)

    if selected_subcategory:
        st.markdown("---")
        st.subheader("📝 Please answer these for your letter")

        user_answers = {}
        for question in letter_structure[selected_category][selected_subcategory]:
            user_answers[question] = st.text_area(question, key=question)

        user_name = st.text_input("Your Name")

        if st.button("Generate Letter"):
            with st.spinner("Creating your letter..."):
                prompt = generate_prompt(selected_category, selected_subcategory, user_answers, user_name, tone)
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6
                    )
                    letter = response.choices[0].message.content
                    st.success("Letter ready:")
                    st.text_area("Generated Letter", letter, height=400)
                except Exception as e:
                    st.error(f"OpenAI error: {e}")
