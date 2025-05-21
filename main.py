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
            "What medication issue occurred — wrong dose, missed dose, or something else?",
            "Where and when did this happen, if you know?",
            "Who was affected by the error?",
            "What was done about it at the time, if anything?",
            "What do you feel should happen now as a result?"
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
    },
    "Escalation & Regulatory": {
        "Notify safeguarding board": [
            "What incident or risk are you reporting?",
            "Who is affected?",
            "Have you reported it to the care provider?",
            "Why are you escalating it externally now?"
        ],
        "Raise formal concern with CQC": [
            "What concern do you want CQC to investigate?",
            "Where is the setting and who is affected?",
            "Is this a single incident or ongoing pattern?",
            "Have you tried resolving this locally first?"
        ],
        "Escalate to Integrated Care Board (ICB)": [
            "What issue are you escalating?",
            "What support or funding is being denied?",
            "Have you followed the correct steps so far?",
            "Why is ICB intervention needed now?"
        ]
    },
    "Advocate Support Requests": {
        "Seek mental capacity advocate (IMCA)": [
            "What decision is being made?",
            "Does the person lack capacity for it?",
            "Are they unbefriended (no close family/friends)?",
            "What outcome are you hoping for?"
        ],
        "Request independent advocate (IMHA)": [
            "What mental health issue is involved?",
            "Is the person detained or sectioned?",
            "What kind of support is needed from advocacy?",
            "Have they had an advocate before?"
        ],
        "Challenge under Human Rights Act": [
            "What decision or treatment is breaching rights?",
            "Whose rights are affected?",
            "Which right (Article 8, 5, etc.) is relevant?",
            "What action are you requesting?"
        ]
    },
    "Delays & Practical Barriers": {
        "Chase delayed referral or appointment": [
            "Who is waiting for what (referral/test/support)?",
            "How long has the delay been?",
            "What impact is the delay having?",
            "Have you contacted the provider already?"
        ],
        "Dispute funding refusal (LA/NHS)": [
            "What funding was denied?",
            "What is the person’s current care situation?",
            "Why do you believe the refusal is unfair?",
            "Have you received a written explanation?"
        ],
        "Request carer support plan": [
            "Are you a family carer?",
            "What support are you struggling to provide?",
            "Has a carer’s assessment ever been done?",
            "What help would make a difference?"
        ]
    }
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

    temperature = 0.3 if tone == "Serious Formal Complaint" else 0.7

    if tone == "Serious Formal Complaint":
        action_block = (
            "Please write this letter in a direct, formal, and legally aware tone. The letter should:\n"
            "- Be factual and to the point, avoiding unnecessary elaboration.\n"
            "- Still reflect concern for the well-being of the individual or team involved, "
            "without sounding dismissive or cold.\n"
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
            full_prompt = generate_prompt(selected_category, selected_subcategory, user_answers, user_name, tone)

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.3 if tone == "Serious Formal Complaint" else 0.7
                )
                generated_letter = response.choices[0].message.content
                st.text_area("Generated Letter", generated_letter, height=300)
            except Exception as e:
                st.error(f"OpenAI error: {e}")
