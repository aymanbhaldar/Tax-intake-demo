import streamlit as st
import requests
import json

# --- CONFIGURATION ---
# REPLACE THIS URL with your actual n8n Production Webhook URL
# Ensure your n8n Webhook node is set to 'POST'
N8N_WEBHOOK_URL = "https://aymanbhaldar.app.n8n.cloud/webhook-test/tax-intake-demo"

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="Tax Doc Processor", 
    page_icon="📄",
    layout="centered"
)

# --- HEADER SECTION ---
st.title("📄 AI Tax Document Extractor")
st.markdown("""
Upload **W-2** or **1099** forms (PDF/Images). 
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
            f.seek(0) # Reset pointer
            # Tuple format: ('form_field_name', (filename, file_bytes, content_type))
            # Note: We use 'data' because your n8n "Split Batch" node expects it
            files_payload.append(('data', (f.name, f.read(), f.type)))
        
        status_text.text("📤 Uploading and analyzing with AI...")
        progress_bar.progress(20)

        try:
            # 3. Send Request to n8n
            response = requests.post(N8N_WEBHOOK_URL, files=files_payload)
            progress_bar.progress(80)
            
            if response.status_code == 200:
                data = response.json()
                progress_bar.progress(100)
                status_text.success("✅ Analysis Complete!")
                
                # --- VITAL FIX: Handle List vs Object Response ---
                # Your n8n workflow returns a direct List [item1, item2]
                if isinstance(data, list):
                    results = data
                else:
                    # Fallback if n8n returns { "results": [...] }
                    results = data.get("results", [])
                
                # --- 4. Render Results ---
                if not results:
                    st.warning("No results returned. Check if the files were valid.")
                
                for res in results:
                    # Handle if the item is wrapped in a 'json' property or comes direct
                    item_data = res.get("json", res) if "json" in res else res
                    
                    # --- FIX: ADAPT TO YOUR ACTUAL API OUTPUT KEYS ---
                    # We check for BOTH the "Code Key" and the "Sheet Key"
                    file_name = item_data.get("File Name") or item_data.get("file_name") or "Unknown Doc"
                    status = item_data.get("Status") or item_data.get("status") or "processed"
                    doc_type = item_data.get("Doc Type") or item_data.get("document_type") or "N/A"
                    
                    # Extract Data (Handling flat structure from your screenshot)
                    employee = item_data.get("Employee Name") or \
                               item_data.get("extracted_fields", {}).get("employee_name") or "N/A"
                               
                    employer = item_data.get("Employer Name") or \
                               item_data.get("extracted_fields", {}).get("employer_name") or "N/A"
                    
                    wages = item_data.get("Wages (Box 1)") or \
                            item_data.get("extracted_fields", {}).get("wages_box_1") or 0
                            
                    # Audit Data
                    rate = item_data.get("Eff. Rate (%)") or \
                           item_data.get("extracted_fields", {}).get("tax_analysis", {}).get("effective_tax_rate_percent") or 0
                           
                    flags = item_data.get("Risk Flags") or \
                            item_data.get("extracted_fields", {}).get("tax_analysis", {}).get("risk_flags") or []
                    
                    summary = item_data.get("Reviewer Summary") or \
                              item_data.get("extracted_fields", {}).get("tax_analysis", {}).get("reviewer_summary") or "No summary."

                    # --- RENDER UI ---
                    with st.expander(f"📄 {file_name} ({status})", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        # Left Column: Raw Data
                        with col1:
                            st.subheader("Extraction")
                            st.caption(f"Doc Type: {doc_type}")
                            st.text(f"Employee: {employee}")
                            st.text(f"Employer: {employer}")
                            st.metric("Wages (Box 1)", f"${float(wages):,.2f}" if wages else "$0.00")
                        
                        # Right Column: Risk Analysis
                        with col2:
                            st.subheader("Compliance Audit")
                            st.metric("Effective Tax Rate", f"{float(rate):.2f}%")
                            
                            if flags:
                                st.error(f"🚩 Risks Detected: {len(flags)}")
                                # Handle if flags came back as a string (from Sheets) or list
                                if isinstance(flags, str):
                                    st.write(flags)
                                else:
                                    for flag in flags:
                                        st.write(f"- {flag}")
                            else:
                                st.success("✅ No Risks Detected")
                                
                        st.info(f"**Analyst Note:** {summary}")

            else:
                st.error(f"Server Error ({response.status_code}):")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")
