import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Pyrebase config (client side)
firebase_config = {
    "apiKey": st.secrets["google_service_account"]["places_api_key"],
    "authDomain": "medimind-fc2a6.firebaseapp.com",
    "projectId": "medimind-fc2a6",
    "databaseURL": "https://medimind-fc2a6-default-rtdb.firebaseio.com",
    "storageBucket": "medimind-fc2a6.appspot.com",
    "messagingSenderId": "557894168058",
    "appId": "1:557894168058:web:068c294117bf6f5a7c0843",
    "measurementId": "G-XDFY5TF24J"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize Firebase Admin SDK (once)
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["google_service_account"]["type"],
        "project_id": st.secrets["google_service_account"]["project_id"],
        "private_key_id": st.secrets["google_service_account"]["private_key_id"],
        "private_key": st.secrets["google_service_account"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["google_service_account"]["client_email"],
        "client_id": st.secrets["google_service_account"]["client_id"],
        "auth_uri": st.secrets["google_service_account"]["auth_uri"],
        "token_uri": st.secrets["google_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["google_service_account"]["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()
print("firebase_config imported successfully.")
