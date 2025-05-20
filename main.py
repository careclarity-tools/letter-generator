import streamlit as st
import openai
import toml
import os

# Load API key and license keys from secrets.toml
secrets = toml.load("secrets.toml")
openai.api_key = secrets["openai"]["api_key"]
valid_keys = secrets["license_keys"]["valid"]

# UI Setup
st.set_page_config(page_title="Care Clarity Letter Generator", layout="centered")
st.markdown("""
<style>
    .main {background-color: #f9f9fb; padding: 20px; border-radius: 10px;}
    .stTextInput>div>div>input {
        border: 1px solid #ccc;
        border-radius: 10px;
    }
    .stSelectbox>div>div>div>div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("💌 Care Clarity Letter Generator")
st.markdown("""
Welcome to the Care Clarity Letter Generator. This tool helps you generate over 50 care-related letter types, tailored for real-world use in UK health and social care settings. To get started:
1. Enter your license key
2. Confirm GDPR consent
3. Choose tone, category, and enter your details
""")

# License Gate
license_key = st.text_input("🔐 License Key", type="password")
if license_key not in valid_keys:
    st.warning("Please enter a valid license key to unlock the generator.")
    st.stop()

# GDPR Consent
gdpr_consent = st.checkbox("✅ I confirm GDPR-compliant use and data consent.")
if not gdpr_consent:
    st.warning("You must confirm GDPR compliance to proceed.")
    st.stop()

# Tone selector
tone = st.selectbox("🎯 Choose your letter tone", ["Polite", "Firm", "Formal Complaint"])

# Category and Subcategory
category_map = {
    "Care Complaints": ["Neglect", "Medication Error", "Unkind Staff", "Cleanliness", "Delayed Response"],
    "Care Referrals": ["GP", "Social Worker", "Mental Health Team", "District Nurse"],
    "Family Escalation": ["DOLS Review", "Safeguarding", "Hospital Discharge", "Care Plan Review", "Reassessment"],
    "Thank You Letters": ["Care Home", "Carer", "Nurse", "Doctor", "Support Worker"],
    "Advocacy Letters": ["Request Meeting", "Disagree With Decision", "Support Planning", "Funding Challenge"],
    "General Support": ["Missing Belongings", "Laundry Issues", "Dietary Concerns", "Room Condition", "Staffing Levels"],
    "Behavioural Concerns": ["Aggression", "Verbal Abuse", "Inappropriate Behaviour"],
    "Mental Capacity": ["Capacity Dispute", "Best Interests Decision", "IMCA Involvement"],
    "Staffing and Training": ["Understaffing", "Untrained Staff", "Staff Turnover"],
    "Environment & Safety": ["Trip Hazard", "Unsafe Room", "Infection Control"]
}

st.markdown("## 📂 Letter Type")
category = st.selectbox("Choose a letter category", list(category_map.keys()))
subcategory = st.selectbox("Choose a subcategory", category_map[category])

# Custom Inputs
st.markdown("## 🧾 Your Information")
user_name = st.text_input("Your full name")
recipient = st.text_input("Recipient (e.g. The Manager)")
details = st.text_area("Describe the situation or concern in a few sentences")

# Generate
if st.button("✍️ Generate Letter"):
    if not all([user_name.strip(), recipient.strip(), details.strip()]):
        st.error("🚨 Please fill in all fields before generating.")
    else:
        prompt = f"""
You are a UK care consultant writing a {tone.lower()} letter for a family member using a support service. The letter falls under:
- Category: {category}
- Subcategory: {subcategory}

The issue described is:
"""{details}"""

The letter must:
- Be emotionally intelligent and professional
- Address the issue clearly, using real-world UK care terminology
- Represent the family member {user_name} and be addressed to {recipient}
- Include a clear call to action or next step

Format the letter accordingly and use plain language where possible.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=750
            )
            st.success("✅ Letter generated successfully:")
            st.text_area("📄 Generated Letter", value=response.choices[0].message.content, height=400)
        except Exception as e:
            st.error(f"❌ An error occurred while generating the letter: {e}")
