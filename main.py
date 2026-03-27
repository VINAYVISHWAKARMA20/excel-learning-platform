import firebase_admin
from firebase_admin import credentials, firestore

try:
    # 1. अपनी JSON फाइल का सही नाम यहाँ लिखें
    cred = credentials.Certificate("excel-quiz-ai-firebase-adminsdk-fbsvc-5d59f8e602.json") 
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("--- Connecting to Firebase ---")

    # 2. डेटा भेजने की कोशिश
    data = {
        "topic": "Excel Basics",
        "status": "Learning",
        "user": "Vinay"
    }
    db.collection("users").document("vinay_test").set(data)
    
    print("✅ Success! Data sent to Firebase.")

except Exception as e:
    print(f"❌ Error occurred: {e}")