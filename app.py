import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import datetime
import hashlib
import collections
import pandas as pd
import plotly.express as px
import os

# Create local storage drive for binary files
DRIVE_DIR = "community_drive"
if not os.path.exists(DRIVE_DIR):
    os.makedirs(DRIVE_DIR)

# --- 1. Page Configuration ---
st.set_page_config(page_title="Excel AI Tutor", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR MICROSOFT EXCEL THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"]  { font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stApp { background-color: #f3f2f1; color: #323130; }
    
    /* Elegant Pill Tabs (Excel Green Theme) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; background-color: transparent; border: none !important; margin-bottom: 2rem;
    }
    .stTabs button[data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.7); backdrop-filter: blur(10px); border-radius: 20px; padding: 12px 28px;
        color: #605e5c !important; border: 1px solid rgba(255,255,255,0.6); font-weight: 600; font-size: 1.05rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .stTabs button[aria-selected="true"] { 
        background-color: transparent !important; background-image: linear-gradient(135deg, #107c41 0%, #185c37 100%) !important; border: none !important;
        box-shadow: 0 6px 16px rgba(16, 124, 65, 0.4) !important; transform: translateY(-2px);
    }
    .stTabs button[aria-selected="true"] *, .stTabs button[aria-selected="true"] p, .stTabs button[aria-selected="true"] span { 
        color: #ffffff !important; font-weight: 700 !important; 
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    
    /* Typography & Sidebar */
    [data-testid="stSidebar"] { background-color: rgba(255,255,255,0.85) !important; backdrop-filter: blur(12px) !important; border-right: 1px solid #edebe9; }
    [data-testid="stHeader"] { background: transparent !important; }
    h1, h2, h3, h4 { color: #107c41 !important; font-weight: 800 !important; letter-spacing: -0.5px; margin-bottom: 0.5rem; }
    p, li, span, div.stMarkdown p { font-size: 1.05rem !important; line-height: 1.6 !important; color: #323130 !important; }
      /* Glassmorphism Forms */
    [data-testid="stForm"] {
        background: #ffffff !important;
        border-radius: 20px !important;
        border: 1px solid #e1dfdd !important;
        box-shadow: 0 15px 50px rgba(16, 124, 65, 0.15) !important;
        padding: 2.5rem !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stForm"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 60px rgba(16, 124, 65, 0.2) !important;
    }
    
    /* Buttons */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #107c41 !important; color: #ffffff !important; border-radius: 8px !important; 
        border: none !important; padding: 0.8rem 1.5rem !important; font-weight: 700 !important; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; width: 100%; box-shadow: 0 4px 10px rgba(16, 124, 65, 0.3) !important;
    }
    .stButton > button *, [data-testid="stFormSubmitButton"] > button *, .stButton > button p, [data-testid="stFormSubmitButton"] > button p {
        color: #ffffff !important; font-weight: 800 !important; font-size: 1.1rem;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { 
        background-image: linear-gradient(135deg, #185c37 0%, #107c41 100%) !important; transform: translateY(-3px) !important;
        box-shadow: 0 8px 15px rgba(16, 124, 65, 0.4) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: #f8f9fa !important; border-radius: 8px !important; border: 1px solid #c8c6c4 !important; color: #323130 !important; padding: 0.8rem 1rem !important; font-size: 1.05rem !important; transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #107c41 !important; background: #ffffff !important; box-shadow: 0 0 0 3px rgba(16, 124, 65, 0.2) !important; transform: translateY(-1px);
    }
    
    /* Background Floating Keyframes */
    @keyframes float1 { 0% { transform: translateY(0px); } 50% { transform: translateY(-25px); } 100% { transform: translateY(0px); } }
    @keyframes float2 { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    @keyframes float3 { 0% { transform: translateY(0px); } 50% { transform: translateY(20px); } 100% { transform: translateY(0px); } }
    
    .bg-anim-1 { animation: float1 8s ease-in-out infinite; position:fixed; z-index:0; pointer-events:none; }
    .bg-anim-2 { animation: float2 6s ease-in-out infinite; position:fixed; z-index:0; pointer-events:none; }
    .bg-anim-3 { animation: float3 9s ease-in-out infinite; position:fixed; z-index:0; pointer-events:none; }
    
</style>

<!-- SCATTERED PERIMETER ANIMATED ELEMENTS -->
<div class="bg-anim-1" style="top:5%; left:5%;"><div style="font-size:120px; opacity:0.15; transform:rotate(-15deg); filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));">📊</div></div>
<div class="bg-anim-2" style="bottom:10%; right:5%;"><div style="font-size:160px; opacity:0.15; transform:rotate(15deg); filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));">📉</div></div>
<div class="bg-anim-3" style="top:15%; right:10%;"><div style="font-size:90px; color:#107c41; opacity:0.20; transform:rotate(25deg); font-family:serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.4);">∑</div></div>
<div class="bg-anim-1" style="bottom:10%; left:10%;"><div style="font-size:110px; color:#107c41; opacity:0.25; transform:rotate(-10deg); font-family:serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.4);">ƒx</div></div>
<div class="bg-anim-2" style="top:40%; left:3%;"><div style="font-size:100px; color:#217346; opacity:0.15; transform:rotate(40deg); font-family:sans-serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.3);">+</div></div>
<div class="bg-anim-3" style="top:35%; right:3%;"><div style="font-size:100px; color:#217346; opacity:0.15; transform:rotate(-20deg); font-family:sans-serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.3);">%</div></div>

<!-- NEW EDGES ICONS -->
<div class="bg-anim-1" style="top:25%; left:10%;"><div style="font-size:80px; opacity:0.12; transform:rotate(10deg); filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));">🧮</div></div>
<div class="bg-anim-2" style="bottom:25%; right:15%;"><div style="font-size:90px; color:#107c41; opacity:0.15; transform:rotate(-15deg); font-family:serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.4);">➗</div></div>
<div class="bg-anim-3" style="top:5%; right:30%;"><div style="font-size:100px; color:#107c41; opacity:0.12; transform:rotate(5deg); font-family:sans-serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.4);">$$</div></div>
<div class="bg-anim-1" style="bottom:30%; left:5%;"><div style="font-size:110px; opacity:0.15; transform:rotate(-25deg); filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));">💡</div></div>
<div class="bg-anim-2" style="top:70%; right:2%;"><div style="font-size:100px; color:#107c41; opacity:0.15; transform:rotate(30deg); font-family:sans-serif; text-shadow: 2px 2px 8px rgba(16,124,65,0.4);">✖</div></div>
<div class="bg-anim-3" style="top:10%; left:35%;"><div style="font-size:80px; opacity:0.12; transform:rotate(-5deg); filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));">📁</div></div>

<!-- CORNER ANCHORED EXCEL LOGO -->
<div class="bg-anim-2" style="bottom:-5%; right:-5%; position:fixed; z-index:0; pointer-events:none;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg" style="width:55vh; opacity:0.06; filter: drop-shadow(0px 8px 30px rgba(16,124,65,0.7)); transform:rotate(-10deg);">
</div>

<div class="bg-anim-1" style="bottom:5%; left:35%;"><div style="font-size:100px; opacity:0.15; transform:rotate(17deg); filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1));">📈</div></div>
""", unsafe_allow_html=True)

# --- 2. Backend Setup ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets:
                # Streamlit Cloud Deployment Mode (Strict TOML Array)
                cred_dict = dict(st.secrets["firebase"])
                # Fallback handler if Streamlit stripped backslash-n format into raw substrings
                if "\\n" in cred_dict.get("private_key", ""):
                    cred_dict["private_key"] = cred_dict["private_key"].replace('\\n', '\n')
                cred = credentials.Certificate(cred_dict)
            elif "type" in st.secrets and "project_id" in st.secrets:
                # Alternative Array: Streamlit Cloud Fallback Deployment Mode (Flat TOML)
                cred_dict = {
                    "type": st.secrets.get("type"),
                    "project_id": st.secrets.get("project_id"),
                    "private_key_id": st.secrets.get("private_key_id"),
                    "private_key": st.secrets.get("private_key", "").replace('\\n', '\n'),
                    "client_email": st.secrets.get("client_email"),
                    "client_id": st.secrets.get("client_id"),
                    "auth_uri": st.secrets.get("auth_uri"),
                    "token_uri": st.secrets.get("token_uri"),
                    "auth_provider_x509_cert_url": st.secrets.get("auth_provider_x509_cert_url"),
                    "client_x509_cert_url": st.secrets.get("client_x509_cert_url")
                }
                cred = credentials.Certificate(cred_dict)
            else:
                # Local Windows Desktop Mode
                st.error(f"CRUISING DEBUG: Streamlit parsed Secrets keys are: {list(st.secrets.keys())}")
                cred = credentials.Certificate("excel-quiz-ai-firebase-adminsdk-fbsvc-5d59f8e602.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"FIREBASE DB CRASH TRACE: {e}")
            raise e
    return firestore.client()

try:
    db = init_firebase()
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("DEBUG: GEMINI_API_KEY MISSING FROM SECRETS!")
except Exception:
    db = None
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_gemini_content(prompt):
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    last_error = None
    for m in models_to_try:
        try:
            return genai.GenerativeModel(m).generate_content(prompt).text
        except Exception as e:
            last_error = e
            if "404" in str(e) or "429" in str(e): continue
            else: continue
    raise Exception(f"Failed to generate content: {last_error}")

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 3. EXCEL THEMED LOGIN PAGE ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 5px; height: 85px;'>
                <div style='width: 48px; height: 65px; background-color: #107c41; border-radius: 4px; display: flex; align-items: center; justify-content: center; box-shadow: 2px 4px 10px rgba(16,124,65,0.4); z-index: 2;'>
                    <span style='color: white; font-size: 32px; font-family: "Segoe UI", sans-serif; font-weight: 900;'>X</span>
                </div>
                <div style='width: 35px; height: 55px; background-color: #185c37; border-radius: 0 4px 4px 0; margin-left: -4px; z-index: 1; display:flex; flex-direction:column; padding: 6px 5px; box-sizing: border-box; justify-content: space-between;'>
                    <div style='height:4px; background:rgba(255,255,255,0.9); width:100%; border-radius:1px;'></div>
                    <div style='height:4px; background:rgba(255,255,255,0.9); width:100%; border-radius:1px;'></div>
                    <div style='height:4px; background:rgba(255,255,255,0.9); width:100%; border-radius:1px;'></div>
                    <div style='height:4px; background:rgba(255,255,255,0.9); width:100%; border-radius:1px;'></div>
                </div>
            </div>
            <h1 style='text-align:center; color:#107c41; margin-top:0px; margin-bottom:0px; font-weight:800; font-size:3rem;'>Excel AI Hub</h1>
            <p style='text-align:center; color:#605e5c; font-size:1.15rem; margin-bottom:30px;'>Please securely identify yourself to proceed.</p>
        """, unsafe_allow_html=True)
        
        auth_mode = st.radio("Auth Mode", ["Sign In", "Sign Up"], horizontal=True, label_visibility="collapsed")
        
        with st.form("auth_form"):
            username = st.text_input("Username / Email", placeholder="Username", label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            
            btn_text = "🚪 Sign In" if auth_mode == "Sign In" else "➕ Create Account"
            if st.form_submit_button(btn_text, use_container_width=True):
                if username and password:
                    if auth_mode == "Sign In":
                        user_doc = db.collection("users").document(username).get()
                        if user_doc.exists and user_doc.to_dict().get("password") == make_hash(password):
                            st.session_state.user = username
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                    else:
                        if db.collection("users").document(username).get().exists:
                            st.error("Username already exists.")
                        else:
                            db.collection("users").document(username).set({"username": username, "password": make_hash(password), "created_at": firestore.SERVER_TIMESTAMP})
                            st.success("Account created successfully! Please Sign In.")
                else:
                    st.warning("Please fill out both fields.")
        
    st.stop()

# --- 4. DATA FETCHING (LEADERBOARD & HISTORY) ---
@st.cache_data(ttl=60)
def get_global_leaderboard():
    try:
        logs = db.collection("learning_logs").get()
        scores = {}
        for doc in logs:
            uname = doc.to_dict().get("username", "Unknown")
            scores[uname] = scores.get(uname, 0) + 10
        return sorted([{"name": k, "score": v} for k,v in scores.items()], key=lambda x: x["score"], reverse=True)
    except: return []

@st.cache_data(ttl=5)
def get_user_history(user):
    try:
        logs_ref = db.collection("learning_logs").where("username", "==", user).get()
        history = [doc.to_dict() | {"id": doc.id} for doc in logs_ref]
        def get_time(item):
            t = item.get("timestamp")
            if not t: return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
            return t
        history.sort(key=get_time, reverse=True)
        return history
    except: return []

history = get_user_history(st.session_state.user)

# --- 5. SESSION STATE CONFIG ---
for key in ["lesson", "quiz", "current_topic", "quiz_fallback", "current_doc_id", "custom_notes", "trigger_generate_topic"]:
    if key not in st.session_state: st.session_state[key] = ""

# --- 6. SIDEBAR MENU ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg", width=50)
    st.markdown(f"<h3 style='margin-bottom:0;'>Hi, {st.session_state.user}!</h3>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.user = None
        st.rerun()
    st.markdown("<hr style='border: 1px solid #edebe9; margin: 1rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("### 🎓 Quick Topics")
    topics = ["Basic Interface", "VLOOKUP", "Pivot Tables", "Macros & VBA", "Financial Formulas"]
    for topic in topics:
        if st.button(f"📘 {topic}", key=f"btn_{topic}"):
            st.session_state.trigger_generate_topic = topic

    st.markdown("<hr style='border: 1px solid #edebe9; margin: 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Custom Topic Request")
    user_custom_topic = st.text_input("Ask a specific question:", placeholder="e.g., Index Match")
    if st.button("🚀 Generate AI Lesson"):
        if user_custom_topic: st.session_state.trigger_generate_topic = user_custom_topic

# --- 7. TOP NAVIGATION TABS ---
tab_dash, tab_study, tab_quiz, tab_upload = st.tabs(["📊 My Dashboard", "📖 Study Material", "📝 Interactive Quizzes", "🌐 Community & Upload"])

# --- 8. AI GENERATION LOGIC ---
if st.session_state.trigger_generate_topic:
    current_request = st.session_state.trigger_generate_topic
    st.session_state.trigger_generate_topic = None
    
    with st.spinner(f"✨ Building specialized MS Excel module on '{current_request}'..."):
        try:
            data_context = ""
            # Access uploaded file silently from session_state if available from the Community tab!
            shared_file = st.session_state.get('global_uploader')
            if shared_file is not None:
                try:
                    df = pd.read_csv(shared_file) if shared_file.name.endswith('.csv') else pd.read_excel(shared_file)
                    df_preview = df.head(20).to_markdown()
                    data_context = f"\n\n**CRITICAL**: Analyze this user-uploaded dataset:\n{df_preview}\nYou MUST use this data to provide practical examples for '{current_request}'."
                except Exception as e: st.warning(f"Could not read the uploaded data file: {e}")

            lesson_prompt = f"Explain the Microsoft Excel topic '{current_request}' in simple English. Explain it step by step. Use markdown formatting with clear headers, bullet points, and provide one real-world business example.{data_context}"
            res_lesson = generate_gemini_content(lesson_prompt)
            st.session_state.lesson = res_lesson
            
            gen_seed = datetime.datetime.now().timestamp()
            quiz_prompt = f"Create a 10-question MCQ for Excel topic: '{current_request}'. Random seed: {gen_seed}. Return ONLY valid JSON array with dicts: {{question, options[], answer}}."
            res_quiz = generate_gemini_content(quiz_prompt)
            st.session_state.current_topic = current_request
            
            try:
                cleaned_quiz = res_quiz.replace("```json", "").replace("```", "").strip()
                st.session_state.quiz = json.loads(cleaned_quiz)
                st.session_state.quiz_fallback = ""
            except:
                st.session_state.quiz_fallback = res_quiz; st.session_state.quiz = None

            update_time, doc_ref = db.collection("learning_logs").add({
                "username": st.session_state.user, "topic": current_request, "lesson_payload": res_lesson,
                "quiz_payload": st.session_state.quiz if st.session_state.quiz else res_quiz,
                "user_notes": "", "timestamp": firestore.SERVER_TIMESTAMP, "shared": False, "status": "Completed"
            })
            st.session_state.current_doc_id = doc_ref.id
            st.session_state.custom_notes = ""
            
            get_user_history.clear()
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ **Processing Error:** {e}")

# --- 9. TAB IMPLEMENTATIONS ---

# 9.A. [DASHBOARD] - Pie and Bar Charts
with tab_dash:
    st.markdown("## 📈 My Learning Analytics")
    st.caption("Track your personal progress through rich, interactive visual graphs.")
    
    if history:
        colChart1, colChart2 = st.columns(2)
        with colChart1:
            st.markdown("", unsafe_allow_html=True)
            st.markdown("### Modules Timeline (Bar)")
            # Generate dummy dates or real dates for timeline
            dates = []
            for h in history:
                t = h.get("timestamp")
                if t: dates.append(str(t).split()[0])
                else: dates.append("Unknown")
            df_dates = pd.DataFrame({"Date": dates}).groupby("Date").size().reset_index(name="Modules")
            fig_bar = px.bar(df_dates, x="Date", y="Modules", color_discrete_sequence=["#107c41"], template="plotly_white", text_auto=True)
            fig_bar.update_traces(marker_line_width=1.5, marker_line_color="#185c37", opacity=0.9, textfont_size=12, textposition="outside", cliponaxis=False)
            fig_bar.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title="<b>Daily Completion Timeline</b>")
            st.plotly_chart(fig_bar, use_container_width=True)
            
            
        with colChart2:
            st.markdown("", unsafe_allow_html=True)
            st.markdown("### Learning Distribution (Pie)")
            cats = {}
            for h in history:
                name = h.get("topic", "").lower()
                if "vlookup" in name or "match" in name or "lookup" in name: 
                    cats["Lookup Functions"] = cats.get("Lookup Functions", 0) + 1
                elif "pivot" in name: 
                    cats["Pivot Tables"] = cats.get("Pivot Tables", 0) + 1
                elif "macro" in name or "vba" in name: 
                    cats["Macros & VBA"] = cats.get("Macros & VBA", 0) + 1
                elif "chart" in name or "graph" in name: 
                    cats["Charting"] = cats.get("Charting", 0) + 1
                else: 
                    cats["General Excel"] = cats.get("General Excel", 0) + 1
            
            df_pie = pd.DataFrame(list(cats.items()), columns=["Category", "Count"])
            fig_pie = px.pie(df_pie, values="Count", names="Category", color_discrete_sequence=px.colors.sequential.Greens[::-1], hole=0.4, template="plotly_white")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
            fig_pie.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300, paper_bgcolor='rgba(0,0,0,0)', title="<b>Skill Distribution</b>", showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        
        st.markdown("### 📋 Recent History Logs")
        colLog1, colLog2 = st.columns(2)
        for idx, item in enumerate(history[:4]):
            col = colLog1 if idx % 2 == 0 else colLog2
            with col:
                st.markdown(f"""
                <div style="background: #ffffff; border-radius: 8px; border: 1px solid #edebe9; padding: 1rem; border-left: 5px solid #107c41; margin-bottom: 1rem;">
                    <h4 style="margin:0; color: #107c41;">{item.get('topic', 'N/A')}</h4>
                    <span style="color:#605e5c; font-size:0.85rem;">Status: Completed</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Start generating modules from the sidebar to populate your analytics dashboard with Pie and Bar charts!")

# 9.B. [STUDY MATERIAL] - Includes Search!
with tab_study:
    st.markdown("## 📖 Study Material & Personal Vault")
    
    colSearch1, colSearch2 = st.columns([3, 1])
    with colSearch2:
        st.markdown("", unsafe_allow_html=True)
        st.markdown("### 🔍 Search Library")
        study_search = st.text_input("Find past lessons", placeholder="e.g., VLOOKUP", label_visibility="collapsed").strip().lower()
        if study_search and history:
            results = [h for h in history if study_search in h.get("topic", "").lower()]
            if results:
                st.success(f"Found {len(results)} module(s)!")
                for r in results:
                    if st.button(f"Load: {r['topic'][:15]}...", key=f"res_{r['id']}"):
                        st.session_state.current_topic = r['topic']
                        st.session_state.lesson = r['lesson_payload']
                        st.session_state.custom_notes = r.get('user_notes', "")
                        if isinstance(r['quiz_payload'], str):
                            st.session_state.quiz_fallback = r['quiz_payload']; st.session_state.quiz = None
                        else:
                            st.session_state.quiz = r['quiz_payload']; st.session_state.quiz_fallback = ""
                        st.session_state.current_doc_id = r['id']
                        st.rerun()
            else:
                st.warning("No matches found in your history.")
        

    with colSearch1:
        if st.session_state.lesson:
            st.markdown('', unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#107c41 !important;'>📘 {st.session_state.current_topic}</h2>", unsafe_allow_html=True)
            st.markdown(st.session_state.lesson)
            
        else:
            st.info("👈 Generate a topic from the sidebar or search your vault to view materials.")

# 9.C. [QUIZ DASHBOARD]
with tab_quiz:
    if st.session_state.lesson:
        st.markdown('', unsafe_allow_html=True)
        if isinstance(st.session_state.quiz, list):
            st.markdown("## 📝 Interactive Assessment")
            st.caption(f"10 Questions on {st.session_state.current_topic}")
            st.markdown("<hr style='border: 1px solid #edebe9; margin: 1.5rem 0;'>", unsafe_allow_html=True)
            
            with st.form("quiz_form"):
                user_answers = []
                for i, q in enumerate(st.session_state.quiz):
                    st.markdown(f"**Q{i+1}. {q.get('question', '')}**")
                    ans = st.radio(f"For Q{i+1}:", q.get("options", []), key=f"q_{i}", index=None, label_visibility="collapsed")
                    user_answers.append(ans)
                    st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("✅ Grade My Assessment", use_container_width=True):
                    score = 0
                    for i, q in enumerate(st.session_state.quiz):
                        if user_answers[i] == q.get("answer"): score += 1
                        else: st.error(f"**Q{i+1} Incorrect.** Answer was: {q.get('answer')}")
                    
                    st.success(f"🏆 **Your Final Score:** {score} out of {len(st.session_state.quiz)}")
                    if score == len(st.session_state.quiz): st.balloons()
        else:
            st.markdown(st.session_state.get("quiz_fallback", "Could not load interactive quiz."))
        
    else:
        st.info("No active module selected.")

# 9.D. [UPLOAD & COMMUNITY HUB]
with tab_upload:
    st.markdown("## ☁️ Community Drive & Resources")
    comm_search = st.text_input("🔍 Search Drive files, authors, or topics...", placeholder="Search Google Drive...").strip().lower()
    
    st.markdown("<hr style='border: 1px solid #edebe9;'>", unsafe_allow_html=True)
    
    st.markdown("### 📂 Upload to Cloud Drive")
    uploaded_files = st.file_uploader("Upload PPTs, PDFs, Word, Excel, Images", accept_multiple_files=True)
    if uploaded_files:
        for f in uploaded_files:
            file_path = os.path.join(DRIVE_DIR, f.name)
            with open(file_path, "wb") as f_out: f_out.write(f.getbuffer())
            # Save file metadata to firestore
            db.collection("learning_logs").add({
                "username": st.session_state.user, "topic": f.name, "lesson_payload": "FILE_UPLOAD",
                "file_path": file_path, "timestamp": firestore.SERVER_TIMESTAMP, "shared": True, "status": "FILE"
            })
        st.success(f"{len(uploaded_files)} file(s) safely uploaded to the Cloud Drive!")
        st.rerun()

    st.markdown("<br>### 📁 Suggested Drive Files", unsafe_allow_html=True)
    
    try:
        shared_logs = db.collection("learning_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).get()
        all_shared = [doc.to_dict() | {"id": doc.id} for doc in shared_logs if doc.to_dict().get("shared", False)]
        
        # Filter logic
        if comm_search:
            all_shared = [h for h in all_shared if comm_search in h.get("topic", "").lower() or comm_search in h.get("username", "").lower()]
            
        # Separate files vs text notes
        files_data = [h for h in all_shared if h.get("status") == "FILE"]
        text_data = [h for h in all_shared if h.get("status") != "FILE"]
        
        if files_data:
            # Build Google Drive Card Grid
            grid_cols = st.columns(4)
            for i, f_doc in enumerate(files_data):
                with grid_cols[i % 4]:
                    st.markdown(f"""
                    <div style="background: #ffffff; border-radius: 8px; border: 1px solid #edebe9; padding:1rem; text-align:center; height:130px; margin-bottom: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <h1 style="margin:0; font-size:2.5rem;">📄</h1>
                        <p style="font-weight:700; font-size:0.9rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-bottom:5px; color:#107c41;">{f_doc['topic']}</p>
                        <p style="font-size:0.75rem; color:#64748b; margin-top:0;">{f_doc.get('username')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    try:
                        if os.path.exists(f_doc['file_path']):
                            with open(f_doc['file_path'], "rb") as physical_file:
                                st.download_button("⬇️ Download", data=physical_file.read(), file_name=f_doc['topic'], key=f"dl_{f_doc['id']}", use_container_width=True)
                        else: st.error("Unavailable")
                    except Exception as e: st.caption("Error")
            st.markdown("<hr style='border: 1px solid #edebe9;'>", unsafe_allow_html=True)
        else:
            st.info("Drive is empty! Be the first to upload.")

        st.markdown("### 📝 Shared Learning Notes")
        if text_data:
            for i, item in enumerate(text_data):
                author = item.get("username", "Anonymous")
                topic = item.get("topic", "Unknown")
                with st.expander(f"📚 {topic} (by {author})"):
                    st.markdown(item.get("lesson_payload", ""))
                    user_added_notes = item.get("user_notes", "")
                    if user_added_notes.strip():
                        st.info(f"**Community Notes:**\\n\\n{user_added_notes}")
        else:
            st.info("No text notes available.")
            
    except Exception as e: st.error(f"Error loading drive: {e}")

st.markdown("---")
st.markdown('<div style="text-align: center; color: #605e5c; margin-top: 20px;">Excel AI Hub | Powered by Native Microsoft Excel Aesthetics 🟢</div>', unsafe_allow_html=True)