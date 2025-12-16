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
                    # Use 'json' key if n8n wraps items in { "json": ... } structure
                    # Otherwise use 'res' directly
                    item_data = res.get("json", res) if "json" in res else res
                    
                    file_name = item_data.get("file_name", "Unknown Document")
                    
                    with st.expander(f"📄 {file_name}", expanded=True):
                        # Get main data blocks
                        fields = item_data.get("extracted_fields", {})
                        analysis = fields.get("tax_analysis", {})
                        
                        # Layout: 2 Columns
                        col1, col2 = st.columns(2)
                        
                        # Left Column: Raw Data
                        with col1:
                            st.subheader("Extraction")
                            st.caption(f"Doc Type: {item_data.get('document_type', 'N/A')}")
                            st.text(f"Employee: {fields.get('employee_name', 'N/A')}")
                            st.text(f"Employer: {fields.get('employer_name', 'N/A')}")
                            st.metric("Wages (Box 1)", f"${fields.get('wages_box_1', 0):,}")
                        
                        # Right Column: Risk Analysis
                        with col2:
                            st.subheader("Compliance Audit")
                            rate = analysis.get('effective_tax_rate_percent', 0)
                            st.metric("Effective Tax Rate", f"{rate}%")
                            
                            flags = analysis.get("risk_flags", [])
                            if flags:
                                st.error(f"🚩 Risks Detected: {len(flags)}")
                                for flag in flags:
                                    st.write(f"- {flag}")
                            else:
                                st.success("✅ No Risks Detected")
                                
                        # Full Summary
                        st.info(f"**Analyst Note:** {analysis.get('reviewer_summary', 'No summary provided.')}")

            else:
                st.error(f"Server Error ({response.status_code}):")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")
