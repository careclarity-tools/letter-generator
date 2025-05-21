import streamlit as st
import json
from openai import OpenAI

# --- LICENSE KEY SETUP ---
VALID_KEYS_FILE = "valid_keys.json"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    license_key = st.text_input("🔐 Enter your license key", type="password")

    try:
        with open(VALID_KEYS_FILE, "r") as f:
            valid_keys = json.load(f)
    except FileNotFoundError:
        valid_keys = []

    if license_key in valid_keys:
        st.session_state.authenticated = True
        st.success("✅ Access granted. Welcome.")
    else:
        st.warning("⚠️ Invalid or already-used license key.")
        st.stop()

# --- OPENAI SETUP ---
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- GDPR Consent ---
st.markdown("### 📜 GDPR Consent")
gdpr_consent = st.checkbox("I consent to data processing (GDPR)")
if not gdpr_consent:
    st.warning("⚠️ You must consent to GDPR processing to continue.")
    st.stop()

st.divider()

# --- TONE TOGGLE ---
st.markdown("### ✍️ Choose Letter Tone")
tone = st.radio(
    "Select the tone for your letter:",
    ("Standard", "Serious Formal Complaint"),
    help="Choose 'Serious Formal Complaint' for regulatory and strong language."
)

st.divider()

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
            "What medication issue occurred — wrong dose, missed dose, or something else?",
            "Where and when did this happen, if you know?",
            "Who was affected by the error?",
            "What was done about it at the time, if anything?",
            "What do you feel should happen now as a result?"
        ]
    }
}

# --- FORM UI (updated) ---
selected_category = st.selectbox("📂 Choose your letter category:", list(letter_structure.keys()))

if selected_category:
    subcategories = list(letter_structure[selected_category].keys())
    selected_subcategory = st.selectbox(f"🔎 Select the issue type under '{selected_category}':", subcategories)

    if selected_subcategory:
        with st.form("letter_form"):
            with st.expander("📝 Please answer the following questions"):
                user_answers = {}
                for question in letter_structure[selected_category][selected_subcategory]:
                    user_answers[question] = st.text_area(question, key=question)

            user_name = st.text_input("✏️ Your Name")
            submitted = st.form_submit_button("Generate Letter")

            if submitted:
                def detect_emotion(answers):
                    keywords = ["devastated", "angry", "ignored", "worried", "frightened", "shocked", "unsafe", "unheard"]
                    return [kw for kw in keywords if any(kw in a.lower() for a in answers.values())]

                def generate_preamble(tone, category, emotion_flags):
                    if tone == "Serious Formal Complaint":
                        return "I am writing to raise a serious and formal concern regarding the matter below."
                    elif "worried" in emotion_flags or "unsafe" in emotion_flags:
                        return "I am reaching out with growing concern about the following issue."
                    elif "angry" in emotion_flags:
                        return "This letter reflects our strong frustration and need for accountability regarding recent events."
                    else:
                        return f"I would like to bring forward a {category.lower()} matter that requires your attention."

                def wrap_answers(answers):
                    return "\n\n".join(f"{q}\nThe user shared: \"{a.strip()}\"" for q, a in answers.items() if a.strip())

                def generate_prompt(category, subcategory, answers, user_name, tone):
                    emotion_flags = detect_emotion(answers)
                    preamble = generate_preamble(tone, category, emotion_flags)
                    summary_block = wrap_answers(answers)

                    base_intro = (
                        "You are an experienced care quality advocate who understands CQC regulations, safeguarding protocol, "
                        "mental capacity law, and service user rights. Your task is to write a formal letter addressing the concern.\n\n"
                    )

                    context_block = f"Letter Category: {category}\nIssue Type: {subcategory}\n\n"
                    if tone == "Serious Formal Complaint":
                        action_block = (
                            "The letter must:\n"
                            "- Use formal, direct language and regulatory terms\n"
                            "- Reference Regulation 13 or safeguarding law where relevant\n"
                            "- Demand documentation, escalation, and a timeline for response\n"
                            "- Close with phrases like 'formal complaint' or 'will not hesitate to escalate'\n\n"
                        )
                    else:
                        action_block = (
                            "The letter should be calm, assertive, and emotionally intelligent. It must:\n"
                            "- Clearly explain the issue and any risks\n"
                            "- Ask for follow-up and written response from a named person\n"
                            "- Suggest willingness to escalate only if ignored\n\n"
                        )

                    closing = f"Please end the letter with:\nSincerely,\n{user_name}"
                    return f"{base_intro}{preamble}\n\n{context_block}{summary_block}{action_block}{closing}"

                try:
                    prompt = generate_prompt(selected_category, selected_subcategory, user_answers, user_name, tone)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    letter = response.choices[0].message.content
                    st.text_area("📄 Generated Letter", letter, height=350)
                except Exception as e:
                    st.error(f"OpenAI error: {e}")

