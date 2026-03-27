import codecs

with codecs.open('app.py', 'r', 'utf-8') as f:
    text = f.read()

# Strip all problematic raw HTML divs that Streamlit refuses to nest native elements inside
text = text.replace('<div class="login-container">', '')
text = text.replace('<div class="dashboard-card">', '')
text = text.replace("<div class='dashboard-card'>", '')
text = text.replace('st.markdown("</div>", unsafe_allow_html=True)', '')
text = text.replace("st.markdown('</div>', unsafe_allow_html=True)", "")
text = text.replace('''<div class="dashboard-card" style="padding: 1rem; border-left: 5px solid #107c41;">
                    <h4 style="margin:0;">{item.get('topic', 'N/A')}</h4>
                    <span style="color:#605e5c; font-size:0.85rem;">Status: Completed</span>
                </div>''', '''<div style="background: #ffffff; border-radius: 8px; border: 1px solid #edebe9; padding: 1rem; border-left: 5px solid #107c41; margin-bottom: 1rem;">
                    <h4 style="margin:0; color: #107c41;">{item.get('topic', 'N/A')}</h4>
                    <span style="color:#605e5c; font-size:0.85rem;">Status: Completed</span>
                </div>''')

text = text.replace('''<div class="dashboard-card" style="padding:1rem; text-align:center; height:150px; background:#f8f9fa;">
                        <h1 style="margin:0; font-size:2.5rem;">📄</h1>
                        <p style="font-weight:700; font-size:0.9rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-bottom:5px;">{f_doc['topic']}</p>
                        <p style="font-size:0.75rem; color:#64748b; margin-top:0;">{f_doc.get('username')}</p>
                    </div>''', '''<div style="background: #ffffff; border-radius: 8px; border: 1px solid #edebe9; padding:1rem; text-align:center; height:130px; margin-bottom: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <h1 style="margin:0; font-size:2.5rem;">📄</h1>
                        <p style="font-weight:700; font-size:0.9rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-bottom:5px; color:#107c41;">{f_doc['topic']}</p>
                        <p style="font-size:0.75rem; color:#64748b; margin-top:0;">{f_doc.get('username')}</p>
                    </div>''')

text = text.replace('<div class="dashboard-card" style="height: 600px; overflow-y: auto;">', '')

text = text.replace("""    /* Dashboard Cards */
    .dashboard-card {
        background: #ffffff; border-radius: 8px; border: 1px solid #edebe9; 
        padding: 1.8rem; margin-bottom: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }
    .login-container {
        background: #ffffff; padding: 3rem; border-radius: 12px; border-top: 6px solid #107c41;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06); text-align: center; max-width: 450px; margin: 40px auto;
    }""", 
"""    /* Excel Watermark Background */
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg');
        background-repeat: no-repeat; background-position: center;
        background-size: 50vh; opacity: 0.03; z-index: -1; pointer-events: none;
    }""")

with codecs.open('app.py', 'w', 'utf-8') as f:
    f.write(text)
