import streamlit as st
import requests
import json

# --- CONFIGURATION ---
# REPLACE THIS with your actual n8n Production Webhook URL
N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/your-uuid"

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="Tax Doc Processor", 
    page_icon="📄",
    layout="centered"
)

# --- HEADER SECTION ---
st.title("📄 AI Tax Document Extractor")
st.markdown("""
Upload **W-2** or **1099** forms. 
The AI will extract data and perform an **automatic compliance audit**.
""")

# --- FILE UPLOADER ---
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=['pdf', 'png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

# --- MAIN LOGIC ---
if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Document(s)", type="primary"):
        
        # 1. Setup Progress UI
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 2. Prepare Files for API
        files_payload = []
        for f in uploaded_files:
            f.seek(0)
            # Tuple format: ('data', (filename, file_bytes, content_type))
            files_payload.append(('data', (f.name, f.read(), f.type)))
        
        status_text.text("📤 Uploading and analyzing...")
        progress_bar.progress(20)

        try:
            # 3. Send Request to n8n
            response = requests.post(N8N_WEBHOOK_URL, files=files_payload)
            progress_bar.progress(80)
            
            if response.status_code == 200:
                data = response.json()
                progress_bar.progress(100)
                status_text.success("✅ Analysis Complete!")
                
                # Handle List vs Wrapper Object response
                if isinstance(data, list):
                    results = data
                else:
                    results = data.get("results", []) or data.get("data", [])
                
                if not results:
                    st.warning("No results returned.")

                # 4. Loop through results
                for res in results:
                    # Handle if item is wrapped in 'json'
                    item = res.get("json", res) if "json" in res else res
                    
                    # --- CRITICAL FIX: Match the exact keys from your Screenshot ---
                    file_name = item.get("File Name") or item.get("file_name") or "Unknown Doc"
                    status = item.get("Status") or item.get("status") or "processed"
                    doc_type = item.get("Doc Type") or item.get("document_type") or "N/A"
                    
                    # Extraction Data
                    employee = item.get("Employee Name", "N/A")
                    employer = item.get("Employer Name", "N/A")
                    
                    # Numeric Data (Handle potential $ symbols or strings)
                    raw_wages = item.get("Wages (Box 1)", 0)
                    try:
                        wages = float(str(raw_wages).replace(',', '').replace('$', '')) if raw_wages else 0.0
                    except:
                        wages = 0.0

                    # Audit Data
                    raw_rate = item.get("Eff. Rate (%)", 0)
                    try:
                        rate = float(raw_rate)
                    except:
                        rate = 0.0
                        
                    flags = item.get("Risk Flags", [])
                    summary = item.get("Reviewer Summary", "No summary provided.")

                    # --- RENDER UI ---
                    # Color code the expander based on status
                    icon = "⚠️" if "needs_review" in str(status) else "✅"
                    
                    with st.expander(f"{icon} {file_name}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        # Left Column: Raw Data
                        with col1:
                            st.subheader("Extraction")
                            st.caption(f"Doc Type: {doc_type}")
                            st.text(f"Employee: {employee}")
                            st.text(f"Employer: {employer}")
                            st.metric("Wages (Box 1)", f"${wages:,.2f}")
                        
                        # Right Column: Risk Analysis
                        with col2:
                            st.subheader("Compliance Audit")
                            
                            # Color code the metric
                            rate_color = "normal"
                            if rate > 35 or (rate < 5 and rate > 0):
                                rate_color = "inverse"
                                
                            st.metric("Effective Tax Rate", f"{rate:.2f}%")
                            
                            if flags:
                                st.error(f"Risks: {len(flags)} Issue(s) Found")
                                # Handle if flags is a list or a joined string
                                if isinstance(flags, list):
                                    for flag in flags:
                                        st.write(f"- {flag}")
                                else:
                                    st.write(flags)
                            else:
                                st.success("✅ No Risks Detected")
                                
                        st.info(f"**Analyst Note:** {summary}")

            else:
                st.error(f"Server Error ({response.status_code}):")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")
