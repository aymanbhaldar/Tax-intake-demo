import streamlit as st
import requests
import json

# --- CONFIGURATION ---
N8N_WEBHOOK_URL = "https://aymanbhaldar.app.n8n.cloud/webhook/tax-intake-demo"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Tax Doc Processor", 
    page_icon="📄",
    layout="centered"
)

# --- SESSION STATE INITIALIZATION ---
# This variable tracks if we are in "Upload Mode" or "Result Mode"
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

# --- HEADER ---
st.title("📄 AI Tax Document Extractor")

# ==========================================
# MODE A: UPLOAD & PROCESS (The Input Screen)
# ==========================================
if not st.session_state.processing_complete:
    st.markdown("""
    Upload **W-2** or **1099** forms. 
    The AI will extract data and perform an **automatic compliance audit**.
    """)

    # 1. File Uploader
    uploaded_files = st.file_uploader(
        "Drag and drop files here", 
        type=['pdf', 'png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )

    # 2. Process Button
    if uploaded_files:
        if st.button(f"Process {len(uploaded_files)} Document(s)", type="primary"):
            
            # Progress UI
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare Files
            files_payload = []
            for f in uploaded_files:
                f.seek(0)
                files_payload.append(('data', (f.name, f.read(), f.type)))
            
            status_text.text("📤 Sending to AI Agent...")
            progress_bar.progress(20)

            try:
                # API Request
                response = requests.post(N8N_WEBHOOK_URL, files=files_payload)
                progress_bar.progress(80)
                
                if response.status_code == 200:
                    data = response.json()
                    progress_bar.progress(100)
                    
                    # --- UNWRAP DATA LOGIC ---
                    results = []
                    # Scenario 1: Nested [ { "data": [...] } ]
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "data" in data[0] and isinstance(data[0]["data"], list):
                        results = data[0]["data"]
                    # Scenario 2: Object { "data": [...] }
                    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                        results = data["data"]
                    # Scenario 3: List [ ... ]
                    elif isinstance(data, list):
                        results = data
                    
                    # SAVE TO SESSION STATE & SWITCH MODES
                    st.session_state.analysis_results = results
                    st.session_state.processing_complete = True
                    st.rerun() # <--- This forces the page to reload immediately into Mode B
                    
                else:
                    st.error(f"Server Error ({response.status_code}):")
                    st.code(response.text)
                    
            except Exception as e:
                st.error(f"Connection Failed: {str(e)}")

# ==========================================
# MODE B: RESULTS DISPLAY (The Output Screen)
# ==========================================
else:
    # 1. "Start Over" Button (Top of page for easy access)
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.success("✅ Analysis Complete")
    with col_btn:
        if st.button("🔄 Start New Analysis"):
            # Clear all state to reset the app completely
            st.session_state.clear()
            st.rerun()

    # 2. Display Results (From Memory)
    results = st.session_state.analysis_results
    
    if not results:
        st.warning("No results returned from API.")
    
    for res in results:
        # Standardize Item
        item = res.get("json", res) if "json" in res else res
        
        # Get Vars
        file_name = item.get("File Name") or item.get("file_name") or "Unknown Doc"
        status = item.get("Status") or item.get("status") or "processed"
        doc_type = item.get("Doc Type") or item.get("document_type") or "N/A"
        
        employee = item.get("Employee Name", "N/A")
        employer = item.get("Employer Name", "N/A")
        
        # Wages
        raw_wages = item.get("Wages (Box 1)", 0)
        try: wages = float(str(raw_wages).replace(',', '').replace('$', '')) if raw_wages else 0.0
        except: wages = 0.0

        # Rate
        raw_rate = item.get("Eff. Rate (%)", 0)
        try: rate = float(raw_rate)
        except: rate = 0.0
            
        flags = item.get("Risk Flags", [])
        summary = item.get("Reviewer Summary", "No summary provided.")
        confidence = item.get("Confidence", 0)

        # Render UI
        icon = "⚠️" if "needs_review" in str(status) else "✅"
        
        with st.expander(f"{icon} {file_name} (Conf: {confidence}%)", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Extraction")
                st.caption(f"Doc Type: {doc_type}")
                st.text(f"Employee: {employee}")
                st.text(f"Employer: {employer}")
                st.metric("Wages (Box 1)", f"${wages:,.2f}")
            with c2:
                st.subheader("Compliance Audit")
                st.metric("Effective Tax Rate", f"{rate:.2f}%")
                if flags:
                    st.error(f"Risks: {len(flags)} Found")
                    if isinstance(flags, list):
                        for f in flags: st.write(f"- {f}")
                    else: st.write(flags)
                else:
                    st.success("✅ No Risks Detected")
            st.info(f"**Analyst Note:** {summary}")
