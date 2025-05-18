mport streamlit as st
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
    "Family Advocacy Letter": {
        "Request a meeting": [
            "Who do you want to meet with?",
            "What is the purpose of the meeting?",
            "Any preferred dates/times?",
            "Is this urgent or routine?"
        ],
        "Disagree with discharge": [
            "Who is being discharged?",
            "What are your concerns?",
            "What support is missing?",
            "Have you spoken to the discharge team?"
        ],
        "Challenge capacity assessment": [
            "What is your loved one’s diagnosis?",
            "Why do you believe the assessment is flawed?",
            "What outcome are you seeking?",
            "Have you discussed this with professionals already?"
        ],
        "Request second opinion": [
            "What was the first opinion or assessment?",
            "Why do you feel a second opinion is necessary?",
            "What changes in care would this affect?",
            "Have you made a formal request before?"
        ],
        "Follow-up after safeguarding": [
            "What was the original concern?",
            "What outcome are you checking on?",
            "Any dates/people involved?",
            "Has there been any communication since?"
        ]
    },
    "Referral Support Letter": {
        "Request community support": [
            "What support do you believe is needed?",
            "Who is the individual needing it?",
            "Have they had this support before?",
            "Why now?"
        ],
        "Request MDT review": [
            "What is the reason for requesting an MDT?",
            "Who is involved in the care?",
            "Are there conflicting opinions?",
            "What is the ideal next step?"
        ],
        "Referral to CHC/NHS Continuing Care": [
            "Why do you think CHC is appropriate?",
            "What needs are you highlighting?",
            "Have assessments already started?",
            "Are you requesting a Fast Track?"
        ],
        "Referral for reassessment": [
            "What has changed in the person’s condition?",
            "When was the last assessment?",
            "What result are you hoping for?"
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
    },
    "Hospital & Discharge": {
        "Discharge objection": [
            "What discharge is being planned?",
            "Why is it not safe/suitable?",
            "Have you communicated with the ward?",
            "What would be a better plan?"
        ],
        "Hospital complaint": [
            "What happened?",
            "Where (ward/hospital)?",
            "What impact did this have?",
            "Have you already raised this?"
        ],
        "Request delayed discharge support": [
            "Who is awaiting discharge?",
            "What barriers exist?",
            "Have you asked for social worker input?"
        ],
        "Hospital to home unsafe discharge": [
            "Who was discharged unsafely?",
            "What went wrong?",
            "What was the result?",
            "What are you requesting now?"
        ]
    },
    "Workplace Grievance Letter": {
        "Threatening or inappropriate language by management": [
            "Who made the comment?",
            "What exactly was said?",
            "How did this affect you or others?",
            "Was this addressed with anyone?",
            "Are you seeking an apology, formal review, or other outcome?"
        ],
        "Unfair or inconsistent application of policy": [
            "What policy or rule was inconsistently applied?",
            "Who was affected, and how?",
            "Were you treated differently than others?",
            "Have you raised this before?"
        ],
        "Blocked from development or training opportunities": [
            "What opportunity were you blocked from?",
            "Were you qualified or eligible for it?",
            "Do you know who was chosen instead?",
            "What explanation (if any) were you given?"
        ],
        "Concerns ignored or dismissed": [
            "What concern did you raise?",
            "How was it received?",
            "Was it recorded or followed up?",
            "Has this happened before?"
        ],
        "Work-related stress or decline in mental health": [
            "What aspects of work have affected your mental health?",
            "Have you taken time off because of this?",
            "Was your condition previously stable?",
            "Have you told anyone at work?"
        ],
        "Favouritism or unfair team dynamics": [
            "What patterns or treatment are you noticing?",
            "Who appears to benefit unfairly?",
            "Has this affected your trust or morale?",
            "Have you been excluded or overlooked?"
        ],
        "Poor communication or lack of transparency": [
            "What information was not shared or miscommunicated?",
            "How did this affect you or the team?",
            "Was this raised with a supervisor or HR?"
        ]
    },
    "Other Letters": {
        "Safeguarding concern": [
            "What concern do you want to report?",
            "Who is at risk?",
            "When and where did this happen?",
            "Have you contacted the safeguarding team?"
        ],
        "LPA/Deputy involvement letter": [
            "What role do you hold (LPA/Deputy)?",
            "What decisions are being challenged?",
            "What outcome are you requesting?"
        ],
        "Request for care review": [
            "Why is a review needed?",
            "What has changed?",
            "What result are you hoping for?",
            "Who needs to be involved?"
        ],
        "GP concern": [
            "Who is the GP or practice?",
            "What is the concern?",
            "What impact is this having?",
            "Are you requesting referral or action?"
        ],
        "CQC notification (family use)": [
            "What is the setting?",
            "What concern are you reporting?",
            "Is this ongoing or resolved?",
            "Do you want a callback or acknowledgment?"
        ]
    }
}


# --- ENHANCEMENT LOGIC ---
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
    formatted = ""
    for q, a in answers.items():
        if a.strip():
            formatted += f"{q}\nThe user shared: \"{a.strip()}\"\n\n"
    return formatted

# --- PROMPT GENERATOR ---
def generate_prompt(category, subcategory, answers, user_name, tone):
    emotion_flags = detect_emotion(answers)
    preamble = generate_preamble(tone, category, emotion_flags)
    summary_block = wrap_answers(answers)

    base_intro = (
        "You are an experienced care quality advocate who understands that the person writing this may have already tried to resolve the matter informally, but now feels it must be recorded in writing for acknowledgment or further support. who understands CQC regulations, safeguarding protocol, "
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

# --- FORM UI ---
selected_category = st.selectbox("Choose your letter category:", list(letter_structure.keys()))

if selected_category:
    subcategories = list(letter_structure[selected_category].keys())
    selected_subcategory = st.selectbox(f"Select the issue type under '{selected_category}':", subcategories)

    if selected_subcategory:
        st.markdown("---")
        st.subheader("📝 Please answer the following:")
        user_answers = {}
        for question in letter_structure[selected_category][selected_subcategory]:
            response = st.text_area(question, key=question)
            user_answers[question] = response

        user_name = st.text_input("Your Name")

        if st.button("Generate Letter"):
            prompt = generate_prompt(selected_category, selected_subcategory, user_answers, user_name, tone)
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                letter = response.choices[0].message.content
                st.text_area("Generated Letter", letter, height=350)
            except Exception as e:
                st.error(f"OpenAI error: {e}")


     
 
