

import streamlit as st
import json
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# --- LICENSE KEY SETUP ---
VALID_KEYS_FILE = "valid_keys.json"

# Function for authentication
def authenticate_user():
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
def setup_openai():
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    return client

# --- GDPR CONSENT ---
def consent_to_gdpr():
    gdpr_consent = st.checkbox("I consent to data processing (GDPR)")
    if not gdpr_consent:
        st.warning("You must consent to GDPR processing to continue.")
        st.stop()

# --- TONE TOGGLE ---
def select_tone():
    tone = st.radio(
        "Select the tone for your letter:",
        ("Standard", "Serious Formal Complaint"),
        help="Choose 'Serious Formal Complaint' for stronger escalation language."
    )
    return tone

# --- DYNAMIC QUESTION DESIGN ---
def get_questionnaire_for_tone_with_refined_empathy(category, subcategory, tone):
    # Add dynamic generation based on subcategory
    questions = []
    if category == "Care Complaint Letter":
        if subcategory == "Neglect or injury":
            questions = [
                f"First and foremost, we are truly sorry to hear about this situation. Could you describe how the neglect or injury made you or your loved one feel?",
                f"We understand how distressing this must be. Can you share details surrounding the incident, such as where it happened and who was involved?",
                f"We appreciate your openness. What steps would you like to see taken to improve the situation and prevent future harm?"
            ]
        elif subcategory == "Medication errors":
            questions = [
                f"First and foremost, we are truly sorry for the medication error. Can you describe how this mistake affected your loved one or others involved?",
                f"We know this must have been difficult. Can you provide details about the error, such as the medication involved and the timeline?",
                f"What actions would you like to see taken to prevent this from happening again and ensure your loved one's safety?"
            ]
    # Add more subcategories here...
    return questions

# --- LETTER GENERATION WITH EMPATHY ---
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

# --- PDF DOWNLOAD FUNCTIONALITY ---
def generate_pdf(letter_text):
    # Create a PDF from the letter text
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(30, 750, letter_text)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

# --- MAIN UI ---
def run_app():
    authenticate_user()
    client = setup_openai()
    consent_to_gdpr()
    tone = select_tone()

    selected_category = st.selectbox("Choose your letter category:", list(letter_structure.keys()))

    if selected_category:
        subcategories = list(letter_structure[selected_category].keys())
        selected_subcategory = st.selectbox(f"Select the issue type under '{selected_category}':", subcategories)

        if selected_subcategory:
            st.markdown("---")
            st.subheader("📝 Please answer the following:")
            user_answers = {}
            questions = get_questionnaire_for_tone_with_refined_empathy(selected_category, selected_subcategory, tone)

            def update_preview():
                preview_prompt = generate_prompt_with_refined_empathy(selected_category, selected_subcategory, user_answers, user_name, tone)
                st.session_state.preview = preview_prompt  

            for question in questions:
                response = st.text_area(question, key=question, on_change=update_preview)
                user_answers[question] = response

            user_name = st.text_input("Your Name", on_change=update_preview)

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
                full_prompt = st.session_state.preview

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": full_prompt}],
                        temperature=0.7
                    )
                    generated_letter = response.choices[0].message.content

                    st.subheader("Letter Preview:")
                    st.text_area("Generated Letter", generated_letter, height=300)

                    # Downloadable PDF Option
                    pdf_buffer = generate_pdf(generated_letter)
                    st.download_button(
                        label="Download Letter (PDF)",
                        data=pdf_buffer,
                        file_name="generated_letter.pdf",
                        mime="application/pdf"
                    )

                    # Text Download
                    st.download_button(
                        label="Download Letter (Text)",
                        data=generated_letter,
                        file_name="generated_letter.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"OpenAI error: {e}")

# Run the app
if __name__ == "__main__":
    run_app()




       


     
    
       
        
   
