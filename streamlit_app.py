import os
import json
import tempfile
import requests
import streamlit as st
import streamlit.components.v1 as components
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from orchestrator.orchestrator import run_all_agents
from agents.at_home_agent import generate_precautions
from firebase_config import firebase_config
from vertexai.generative_models import GenerativeModel
import vertexai
from datetime import datetime, timezone
import http.cookies
import pdfkit
import re

from io import BytesIO
from streamlit.components.v1 import html
from streamlit_js_eval import streamlit_js_eval, get_geolocation




def clean_text(text):
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...',
        '•': '', '*': '', '™': '', '®': '', '©': '',
        '☐': '', '☑': '', '✅': '', '✓': '', '✔️': '',
        '□': '', '■': '', '▪': '', '◻': '', '◼': '', '⬜': '', '⬛': ''
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def format_to_list(text):
    lines = [line.strip("•*- ") for line in text.splitlines() if line.strip()]
    return "<ul>" + "".join(f"<li>{line}</li>" for line in lines) + "</ul>"


def generate_clean_pdf(case, timestamp, reflection, precautions):
    enhanced_reflection = []
    current_list_items = []

    def flush_list():
        if current_list_items:
            enhanced_reflection.append("<ul>" + "".join(current_list_items) + "</ul>")
            current_list_items.clear()

    for line in reflection.splitlines():
        raw_line = line
        clean_line = clean_text(line.strip().strip("*").strip("☐◻□"))

        # Simple section or topic headers
        if re.match(r"^\d+[\.\)]\s", clean_line) or (clean_line.endswith(":") and len(clean_line.split()) <= 10):
            flush_list()
            header = re.sub(r"^\d+[\.\)]\s*", "", clean_line).rstrip(":")
            enhanced_reflection.append(f"<p><strong>{clean_text(header)}:</strong></p>")

        # Bullets
        elif raw_line.strip().startswith("- "):
            current_list_items.append(f"<li>{clean_text(clean_line[2:])}</li>")

        # Bold label + explanation
        elif "**" in raw_line and ":" in raw_line:
            flush_list()
            match = re.match(r"\*\*(.+?)\*\*:\s*(.*)", raw_line)
            if match:
                bold_text, remainder = match.groups()
                enhanced_reflection.append(
                    f"<p><strong>{clean_text(bold_text)}:</strong> {clean_text(remainder)}</p>"
                )
            else:
                enhanced_reflection.append(f"<p>{clean_text(raw_line.replace('**', ''))}</p>")

        # Regular short label + content
        elif ":" in clean_line:
            flush_list()
            label, _, rest = clean_line.partition(":")
            enhanced_reflection.append(
                f"<p><strong>{clean_text(label)}:</strong> {clean_text(rest)}</p>"
            )

        # Just a paragraph
        else:
            flush_list()
            enhanced_reflection.append(f"<p>{clean_text(clean_line)}</p>")

    flush_list()
    reflection_html = "\n".join(enhanced_reflection)
    precautions_html = format_to_list(precautions)

    vitals = case.get("vital_signs", {})
    temperature = vitals.get("temperature", "N/A")
    bp = vitals.get("blood_pressure", "N/A")
    hr = vitals.get("heart_rate", "N/A")

    name = "Guest"
    if st.session_state.user:
        if "first_name" in st.session_state.user and "last_name" in st.session_state.user:
            name = f"{st.session_state.user['first_name']} {st.session_state.user['last_name']}".strip()
        elif "email" in st.session_state.user:
            name = st.session_state.user["email"]

    age = case.get("age", "N/A")
    sex = case.get("sex", "N/A")

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 40px;
                line-height: 1.6;
                color: #000;
            }}
            h1 {{
                font-size: 24px;
                margin-bottom: 4px;
            }}
            h2 {{
                font-size: 20px;
                margin-top: 24px;
                border-top: 1px solid #ccc;
                padding-top: 10px;
            }}
            h3 {{
                font-size: 18px;
                margin-top: 20px;
            }}
            p, li {{
                font-size: 14px;
            }}
            strong {{
                font-weight: bold;
            }}
            ul {{
                margin-top: 4px;
                margin-bottom: 10px;
                padding-left: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>MediMind Report</h1>
        <p><strong>Date:</strong> {timestamp.strftime('%B %d, %Y %I:%M %p')}</p>
        <p><strong>Patient Name:</strong> {name}</p>

        <h2>AI Clinical Report:</h2>

        <h3>Patient Summary</h3>
        <p><strong>Age:</strong> {age}</p>
        <p><strong>Sex:</strong> {sex}</p>
        <p><strong>Temperature:</strong> {temperature}°F</p>
        <p><strong>Blood Pressure:</strong> {bp}</p>
        <p><strong>Heart Rate:</strong> {hr}</p>

        <h3>Reflective Summary</h3>
        {reflection_html or "<p>No summary generated.</p>"}

        <h3>At-Home Precautions</h3>
        {precautions_html or "<p>No at-home precautions provided.</p>"}
    </body>
    </html>
    """

    pdf_bytes = pdfkit.from_string(
        html,
        False,
        options={
            "enable-local-file-access": "",
            "encoding": "UTF-8",
            "no-print-media-type": "",        # ← disables printer-specific styling
            "print-media-type": None,         # ← prevents triggering printer emulation
            "quiet": "",
            "disable-smart-shrinking": ""     # ← optional, but improves rendering consistency
        }
    )
    return pdf_bytes


def extract_specialties_from_symptoms(symptom_text):
    symptom_text = symptom_text.lower()
    mapping = {
        "cardiology": ["chest pain", "palpitations", "shortness of breath", "heart", "tachycardia"],
        "neurology": ["headache", "dizziness", "numbness", "seizure", "migraine", "lockjaw", "tremor", "confusion"],
        "gastroenterology": ["nausea", "vomiting", "abdominal pain", "diarrhea", "bloating", "indigestion"],
        "dermatology": ["rash", "itching", "acne", "eczema", "psoriasis", "lesion"],
        "pulmonology": ["cough", "wheezing", "shortness of breath", "asthma", "bronchitis"],
        "infectious disease": ["fever", "chills", "infection", "fatigue", "flu"],
        "orthopedics": ["joint pain", "back pain", "swelling", "fracture", "sprain"],
        "urology": ["urine", "bladder", "kidney", "painful urination"],
        "gynecology": ["menstrual", "vaginal", "pregnancy", "pelvic", "cramps"],
    }

    found_specialties = set()
    for specialty, keywords in mapping.items():
        if any(keyword in symptom_text for keyword in keywords):
            found_specialties.add(specialty)

    return list(found_specialties)

st.set_page_config(page_title="MediMind: Multi-Agent Clinical Review", page_icon="🧠", layout="wide")

# Firebase Initialization 
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firestore.client()

# Custom CSS for UI
st.markdown("""
    <style>
    summary {
        font-size: 1.4rem !important;
        font-weight: 600;
        padding: 8px 0;
    }
    .st-expanderHeader {
        font-size: 1.4rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
for key, default in {
    "results": None,
    "patient_case": None,
    "reflection_summary": None,
    "precautions_summary": None,
    "lat": None,
    "lon": None,
    "clinic_suggestions": [],
    "weight_kg": 70.0,
    "display_unit": "kg",
    "weight_display": 70.0,
    "user": None,
    "logged_in": False,
    "auth_stage": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------- AUTH BLOCK -------------------------
st.title("🧠 Welcome to MediMind")
st.markdown("Please choose how you’d like to continue:")
options = ["Log In", "Sign Up", "Continue as Guest"]

if "auth_choice" not in st.session_state or st.session_state.auth_choice not in options:
    st.session_state.auth_choice = "Log In"

# Render the radio button using session state for tracking
auth_choice = st.radio(
    "Choose an action:",
    options,
    index=options.index(st.session_state.auth_choice),
    key="auth_stage"
)
st.session_state.auth_choice = auth_choice


if auth_choice == "Log In":
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        col1, col2 = st.columns([2, 1])
        with col1:
            submitted_login = st.form_submit_button("Submit Log In")
        with col2:
            forgot_pw = st.form_submit_button("Forgot Password?")

        if submitted_login:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = user
                st.session_state.logged_in = True
                st.session_state.auth_choice = "Log In"
                st.success("✅ Logged in successfully!")
                st.rerun()
            except requests.exceptions.HTTPError as e:
                try:
                    error_json = e.response.json()
                    message = error_json["error"]["message"]

                    if message == "EMAIL_NOT_FOUND":
                        st.error("🚫 No account found with this email. Please sign up first.")
                    elif message == "INVALID_PASSWORD":
                        st.error("🚫 Incorrect password. Please try again or reset it.")
                    else:
                        st.error(f"❌ Login failed: {message}")
                except:
                    st.error("❌ Please log in, account already exists.")

        if forgot_pw:
            if email:
                try:
                    auth.send_password_reset_email(email)
                    st.success("📧 Password reset email sent. Check your inbox.")
                except Exception as e:
                    st.error(f"❌ Failed to send reset email: {e}")
            else:
                st.warning("Please enter your email above before clicking reset.")

elif auth_choice == "Sign Up":
    with st.form("signup_form"):
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password (min 6 characters)", type="password", key="signup_password")
        first_name = st.text_input("First Name", key="signup_first_name")
        last_name = st.text_input("Last Name", key="signup_last_name")
        submitted_signup = st.form_submit_button("Submit Sign Up")

        if submitted_signup:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.session_state.user = {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
                st.success("✅ Account created successfully! Please log in.")
                st.session_state.auth_choice = "Log In"
                st.rerun()

            except requests.exceptions.HTTPError as e:
                try:
                    error_json = e.response.json()
                    message = error_json["error"]["message"]

                    if message == "EMAIL_EXISTS":
                        st.error("🚫 This email is already registered. Please use the Log In tab instead.")
                    elif message == "INVALID_PASSWORD":
                        st.error("🚫 Password is too short. It must be at least 6 characters.")
                    else:
                        st.error(f"❌ Sign-up failed: {message}")
                except:
                    st.error("❌ An unknown error occurred during sign-up.")

elif auth_choice == "Continue as Guest":
    st.session_state.logged_in = False
    st.success("✅ Continuing as guest.")

# Prevent form access until logged in or guest
if auth_choice not in ["Continue as Guest"] and not st.session_state.logged_in:
    st.stop()

# Query parameter location fetch
location = st.query_params.get("location", None)
if location and (not st.session_state.lat or not st.session_state.lon):
    try:
        lat, lon = map(float, location.split(","))
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.success("📍 Location retrieved successfully!")
    except Exception:
        st.warning("❌ Failed to process geolocation data.")
# ------------------ LOCATION FETCH BLOCK (OUTSIDE FORM) ------------------
with st.container():
    st.markdown("**Optional:** Use current location")
    if st.button("📍 Use My Location"):
        streamlit_js_eval(
            js_expressions="navigator.geolocation.getCurrentPosition((pos) => [pos.coords.latitude, pos.coords.longitude])",
            key="get_location"
        )

    # On rerun, check if location was retrieved
location = get_geolocation()

if location:
    st.session_state.lat = location['coords']['latitude']
    st.session_state.lon = location['coords']['longitude']
    st.success("📍 Location detected!")
    st.session_state.user_location_used = True
    #st.experimental_rerun()
else:
    st.info("🔄 Waiting for location permission or data...")

# --------------------------- FORM SECTION --------------------------
st.markdown("<div id='form'></div>", unsafe_allow_html=True)
loc_col1, loc_col2 = st.columns([3, 1])
with loc_col1:
    user_location = st.text_input("Location (ZIP or City)", placeholder="e.g. 20052 or Washington, DC")


with st.form("patient_case_form"):
    st.header("📋 Patient Case Information")
    
    if not st.session_state.logged_in:
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        st.session_state.user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": "guest@medimind.app"
        }
    age = st.number_input("Age", min_value=0, max_value=120, value=45)
    sex = st.selectbox("Sex", ["M", "F", "Other"])
    #with loc_col1:
    #    user_location = st.text_input("Location (ZIP or City)", placeholder="e.g. 20052 or Washington, DC")
    col1, col2 = st.columns([2, 1])
    with col2:
        selected_unit = st.radio("Unit", ["kg", "lbs"], index=0 if st.session_state.display_unit == "kg" else 1)

    if selected_unit != st.session_state.display_unit:
        if selected_unit == "lbs":
            st.session_state.weight_display = round(st.session_state.weight_kg * 2.20462, 2)
        else:
            st.session_state.weight_kg = round(st.session_state.weight_display / 2.20462, 2)
            st.session_state.weight_display = st.session_state.weight_kg
        st.session_state.display_unit = selected_unit

    with col1:
        st.session_state.weight_display = st.number_input(
            f"Weight (kg or lbs)",
            min_value=1.0,
            max_value=1100.0,
            step=2.0,
            value=st.session_state.weight_display,
            key="weight_input"
        )

    weight = (
        st.session_state.weight_display
        if st.session_state.display_unit == "kg"
        else round(st.session_state.weight_display / 2.20462, 2)
    )
    st.session_state.weight_kg = weight

    medical_history = st.text_area("Medical History", placeholder="e.g. Hypertension, Diabetes")
    current_symptoms = st.text_area("Current Symptoms", placeholder="e.g. Fever, Fatigue")

    col1, col2, col3 = st.columns(3)
    with col1:
        heart_rate = st.text_input("❤️ Heart Rate (bpm)", placeholder="e.g. 95")
    with col2:
        temperature = st.text_input("🌡️ Temperature (°F)", placeholder="e.g. 101.2")
    with col3:
        blood_pressure = st.text_input("🩸 Blood Pressure", placeholder="e.g. 140/90")

    labs = st.text_area("Lab Results", placeholder="e.g. WBC:11.2, Glucose:140")
    medications = st.text_area("Medications", placeholder="e.g. Metformin, Lisinopril")




    submitted = st.form_submit_button("Run MediMind Review")
if "HTTP_COOKIE" in os.environ:
    cookies = http.cookies.SimpleCookie()
    cookies.load(os.environ["HTTP_COOKIE"])
    if "lat" in cookies and "lon" in cookies:
        st.session_state.lat = cookies["lat"].value
        st.session_state.lon = cookies["lon"].value
# Capture ?location=lat,lon from URL and store in session state
location = st.query_params.get("location", None)
if location and (not st.session_state.lat or not st.session_state.lon):
    try:
        lat, lon = map(float, location.split(","))
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.success("📍 Location retrieved successfully!")
        st.rerun()
    except Exception:
        st.warning("❌ Failed to process geolocation data.")

# Run Review


if submitted:
    vitals = {}
    if heart_rate.strip(): vitals["heart_rate"] = float(heart_rate)
    if temperature.strip(): vitals["temperature"] = float(temperature)
    if blood_pressure.strip(): vitals["blood_pressure"] = blood_pressure

    st.session_state.patient_case = {
        "age": age,
        "sex": sex,
        "weight": weight,
        "medical_history": [x.strip() for x in medical_history.split(",") if x.strip()],
        "current_symptoms": [x.strip() for x in current_symptoms.split(",") if x.strip()],
        "vital_signs": vitals,
        "medications": [x.strip() for x in medications.split(",") if x.strip()],
        "labs": {
            k.strip(): v.strip()
            for k, v in (pair.split(":") for pair in labs.split(",") if ":" in pair)
        },
    }
    if user_location and (not st.session_state.lat or not st.session_state.lon):
        geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geo_res = requests.get(geo_url, params={
            "address": user_location,
            "key": st.secrets["google_service_account"]["places_api_key"]
        }).json()
        if geo_res["status"] == "OK":
            loc = geo_res["results"][0]["geometry"]["location"]
            st.session_state.lat = loc["lat"]
            st.session_state.lon = loc["lng"]
            st.success("📍 Location geocoded successfully.")
        else:
            st.warning("❌ Could not determine location from the input.")


    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(st.session_state.patient_case, tmp)
        tmp.seek(0)
        st.session_state.results = run_all_agents(tmp.name)
    # Save report if logged in
    if st.session_state.logged_in and st.session_state.user:
        if not st.session_state.reflection_summary:
            full_text = "\n\n".join(st.session_state.results.values())
            st.session_state.reflection_summary = full_text
        if not st.session_state.precautions_summary:
            summary_text = json.dumps(st.session_state.patient_case, indent=2)
            st.session_state.precautions_summary = generate_precautions(summary_text, st.session_state.reflection_summary)
        try:
            user_email = st.session_state.user["email"]
            doc_ref = db.collection("users").document(user_email)
            doc_ref.collection("reports").add({
                "patient_case": st.session_state.patient_case,
                "results": st.session_state.results,
                "reflection": clean_text(st.session_state.reflection_summary or "No summary generated."),
                "precautions": clean_text(st.session_state.precautions_summary or "No at-home precautions provided."),
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            st.error(f"❌ Error saving report: {e}")

    st.success("✅ Review complete. See results below.")
    # Save to Firestore if logged in


# Display Results
if st.session_state.results:
    st.markdown("<div id='report'></div>", unsafe_allow_html=True)
    with st.expander("📄 Your Report"):
        for key, value in st.session_state.results.items():
            st.markdown(f"**{key.replace('_',' ').title()}**")
            st.markdown(value)
        full_text = "\n\n".join(st.session_state.results.values())
        st.session_state.reflection_summary = full_text

    st.subheader("➕ Add Missing Info")
    user_additions = st.text_area("Additional info or concerns (e.g. family history, exam findings):")
    if st.button("🔁 Update Reflection"):
        vertexai.init(project="vital-valor-462719-n9", location="us-central1")
        model = GenerativeModel("gemini-2.0-flash")
        summary_text = json.dumps(st.session_state.patient_case, indent=2)
        prompt = (
            "You're a clinical AI assistant. Analyze the updated case and user additions.\n\n"
            f"Patient Case:\n{summary_text}\n\nUser Additions:\n{user_additions.strip()}\n\n"
            "Provide a detailed reflective summary organized by clinical category."
        )
        response = model.generate_content(prompt)
        st.session_state.reflection_summary = response.text
        st.markdown("### 🆕 Updated Reflective Summary")
        filtered = response.text.split("Reflection by Category:")
        if len(filtered) > 1:
            st.markdown("### Reflection by Category:" + filtered[1], unsafe_allow_html=True)
        else:
            st.markdown(response.text)

    st.markdown("<div id='precautions'></div>", unsafe_allow_html=True)
    with st.expander("🏠 At-Home Precautions"):
        if not st.session_state.precautions_summary:
            summary_text = json.dumps(st.session_state.patient_case, indent=2)
            st.session_state.precautions_summary = generate_precautions(summary_text, st.session_state.reflection_summary)
        st.markdown(st.session_state.precautions_summary)

    st.markdown("<div id='clinics'></div>", unsafe_allow_html=True)
    with st.expander("🏥 Nearby Clinics"):
        if not st.session_state.lat and user_location:
            geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
            geo_res = requests.get(geo_url, params={
                "address": user_location,
                "key": st.secrets["google_service_account"]["places_api_key"]
            }).json()
            if geo_res["status"] == "OK":
                loc = geo_res["results"][0]["geometry"]["location"]
                st.session_state.lat = loc["lat"]
                st.session_state.lon = loc["lng"]
                st.success("📍 Location geocoded successfully.")
        elif st.session_state.lat and st.session_state.lon:
            st.success("📍 Using detected coordinates.")
        if st.session_state.lat and st.session_state.lon:
            

            symptom_text = ", ".join(st.session_state.patient_case.get("current_symptoms", []))
            keywords = extract_specialties_from_symptoms(symptom_text) or ["clinic"]  # fallback to generic if no match
            
            found_any = False
            for specialty in keywords:
                places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                nearby = requests.get(places_url, params={
                    "location": f"{st.session_state.lat},{st.session_state.lon}",
                    "radius": 10000,
                    "keyword": specialty,
                    "type": "hospital",
                    "key": st.secrets["google_service_account"]["places_api_key"]

                }).json()

                if nearby.get("results"):
                    st.markdown(f"### 🔍 Specialty match: `{specialty.title()}`")
                    for result in nearby["results"][:5]:
                        name = result.get("name")
                        address = result.get("vicinity")
                        place_id = result.get("place_id")
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={result['geometry']['location']['lat']},{result['geometry']['location']['lng']}"

                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_resp = requests.get(details_url, params={
                            "place_id": place_id,
                            "fields": "formatted_phone_number",
                            "key": st.secrets["google_service_account"]["places_api_key"]
                        }).json()
                        phone = details_resp.get("result", {}).get("formatted_phone_number", "Phone not listed")

                        st.markdown(f"- **{name}** — {address}<br>📞 {phone} [[Map]({maps_url})]", unsafe_allow_html=True)
                    break
            else:
                st.info("No specialty clinics found nearby for flagged concerns.")

# ---------------------- VIEW PAST REPORTS ----------------------
if st.session_state.logged_in:
    st.markdown("<div id='past-reports'></div>", unsafe_allow_html=True)
    st.subheader("📅 Past Reports")

    try:
        import tempfile

        user_email = st.session_state.user["email"]
        reports_ref = db.collection("users").document(user_email).collection("reports")
        reports = reports_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

        for report in reports:
            data = report.to_dict()
            timestamp = data.get("timestamp")
            input_data = data.get("patient_case", {})
            results = data.get("results", {})

            readable_time = timestamp.strftime('%B %d, %Y %I:%M %p') if timestamp else "Unknown"
            st.markdown(f"### 📂 Report from {readable_time}")
            col1, col2 = st.columns([1, 5])

            with col1:
                if st.button(f"🗑️ Delete", key=f"delete_{report.id}"):
                    try:
                        report.reference.delete()
                        st.success("Report deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to delete report: {e}")

            with col2:

                reflection = clean_text(data.get("reflection", "No summary generated."))
                precautions = clean_text(data.get("precautions", "No at-home precautions provided."))

                pdf_bytes = generate_clean_pdf(input_data, timestamp, reflection, precautions)
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"medimind_report_{timestamp.date()}.pdf",
                    mime="application/pdf",
                    key=f"download_{report.id}"
                )

    except Exception as e:
        st.error(f"❌ Error loading past reports: {e}")

# Also allow PDF download for guests

# This function should be called during PDF download block
# Example:
# reflection = clean_text(st.session_state.reflection_summary or "No summary generated.")
# precautions = clean_text(st.session_state.precautions_summary or "No at-home precautions provided.")
# pdf_bytes = generate_clean_pdf(case, timestamp, reflection, precautions)
# st.download_button("📄 Download PDF", data=pdf_bytes, file_name="medimind_report.pdf", mime="application/pdf")

if not st.session_state.logged_in and st.session_state.results:
    #import pdfkit
    st.markdown("### ⬇️ Download Your Report")

    





    timestamp = datetime.now(timezone.utc)
    case = st.session_state.patient_case

    reflection = clean_text(st.session_state.reflection_summary or "No summary generated.")
    precautions = clean_text(st.session_state.precautions_summary or "No at-home precautions provided.")
    

    

    

    pdf_bytes = generate_clean_pdf(case, timestamp, reflection, precautions)

    st.download_button(
        label="📄 Download PDF",
        data=pdf_bytes,
        file_name="medimind_guest_report.pdf",
        mime="application/pdf"
    )


# Feedback
st.markdown("""
---
### 💬 Your Opinion Matters
MediMind uses AI to generate health recommendations. Help us improve!  
👉 [Leave Feedback Here](https://docs.google.com/forms/d/e/1FAIpQLSfKA5PAfgQTAzdLX4ARXR50griLjKOi4RySCd7iLhoJSy1y1w/viewform?usp=header)
""")



