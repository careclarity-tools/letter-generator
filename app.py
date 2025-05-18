
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

# --- GDPR CONSENT ---
gdpr_consent = st.checkbox("I consent to data processing (GDPR)")
if not gdpr_consent:
    st.warning("You must consent to GDPR processing to continue.")
    st.stop()

# --- TONE TOGGLE ---
tone = st.radio(
    "Select the tone for your letter:",
    ("Standard", "Serious Formal Complaint"),
    help="Choose 'Serious Formal Complaint' for stronger escalation language."
)

# --- FULL LETTER STRUCTURE (30+ Letters) ---
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
    # Add additional letter categories as needed
}

# --- TONE-BASED QUESTION DESIGN WITH EMPATHY ---
def get_questionnaire_for_tone_with_refined_empathy(category, subcategory, tone):
    if tone == "Standard":
        return [
            f"First and foremost, we are truly sorry to hear about this situation. Could you describe how it made you or your loved one feel?",
            f"We understand how distressing this must be. Can you share some details surrounding the issue '{subcategory}'?",
            f"We appreciate your openness in sharing this. Would you like to include any specific requests on how this situation can be improved or addressed?"
        ]
    else:  # Serious Formal Complaint tone
        return [
            f"Please describe the details of the '{subcategory}' incident, including dates, times, and all involved. Your detailed input will help guide us in resolving the issue.",
            f"What was the direct impact of this issue on your loved one or others in the care setting?",
            "What specific actions do you want taken, and do you believe any regulatory bodies should be notified?"
        ]

# --- LETTER GENERATION WITH EMPATHY AND LOGIC ---
def generate_prompt_with_refined_empathy(category, subcategory, answers, user_name, tone):
    base_intro = (
        "You are an experienced care quality advocate who understands CQC regulations, safeguarding protocol, "
        "mental capacity considerations, and the rights of service users. This letter aims to address the concern raised "
        "by a family member, advocate, or staff whistleblower. We understand this is an emotional journey, and your input "
        "is deeply appreciated.\n\n"
    )

    context_block = f"Letter Category: {category}\nIssue Type: {subcategory}\n\n"

    summary_block = ""
    for q, a in answers.items():
        if a.strip():
            summary_block += f"{q}\n{a.strip()}\n\n"

    if tone == "Serious Formal Complaint":
        action_block = (
            "Please write this letter in a formal, legally aware tone. The letter should:\n"
            "- Reference Regulation 13 or safeguarding principles where relevant\n"
            "- Explicitly state concern for duty of care or CQC standards\n"
            "- Request documentation (body maps, reports, policies) if applicable\n"
            "- Demand a named point of accountability and timeline\n"
            "- Note possible escalation to safeguarding boards, CQC, or ombudsman\n"
            "- Include closing phrases such as 'will not hesitate to escalate' or 'formal complaint'\n\n"
        )
    else:  # Standard Tone
        action_block = (
            "Please write this letter in a calm, assertive, and emotionally intelligent tone. The letter should:\n"
            "- Acknowledge the emotional impact of the situation on the individual or family\n"
            "- Explain the concern or incident with empathy and understanding\n"
            "- Highlight any risk to the individual or others\n"
            "- Request investigation, documentation, and appropriate escalation\n"
            "- Mention any reports made to safeguarding teams or regulators\n"
            "- Ensure a written response with named accountability within a reasonable timeframe\n"
            "- Close with a readiness to escalate if the matter is not taken seriously\n\n"
        )

    closing = f"Please end the letter with:\n\nThank you for your attention to this important matter. We are committed to supporting you.\n\nSincerely,\n{user_name}"

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
        questions = get_questionnaire_for_tone_with_refined_empathy(selected_category, selected_subcategory, tone)
        for question in questions:
            response = st.text_area(question, key=question)
            user_answers[question] = response

        user_name = st.text_input("Your Name")

        # --- ERROR HANDLING ---
        def validate_inputs():
            missing_fields = [q for q, a in user_answers.items() if not a.strip()]
            if missing_fields:
                st.error(f"Please complete all fields: {', '.join(missing_fields)}")
                return False
            if not user_name.strip():
                st.error("Please provide your name.")
                return False
            return True

        if st.button("Generate Letter") and validate_inputs():
            full_prompt = generate_prompt_with_refined_empathy(selected_category, selected_subcategory, user_answers, user_name, tone)

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.7
                )
                generated_letter = response.choices[0].message.content

                # --- REAL-TIME PREVIEW ---
                st.subheader("Letter Preview:")
                st.text_area("Generated Letter", generated_letter, height=300)
            except Exception as e:
                st.error(f"OpenAI error: {e}")  





       


     
    
       
        
   
