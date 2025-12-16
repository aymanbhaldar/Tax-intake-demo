import streamlit as st
import requests
import json

# --- CONFIGURATION ---
# Replace this with your actual n8n Webhook URL
N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/your-uuid"

# --- UI LAYOUT ---
st.set_page_config(page_title="Tax Doc Processor", page_icon="📄")
st.title("📄 AI Tax Document Extractor")
st.markdown("Upload W-2 or 1099 forms to automatically extract data and audit for compliance risks.")

# --- FILE UPLOADER ---
uploaded_files = st.file_uploader(
    "Drag and drop PDFs or Images here", 
    type=['pdf', 'png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Document(s)"):
        
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Prepare the files for the API request
        files_payload = []
        for f in uploaded_files:
            # Re-read file pointer to start
            f.seek(0)
            # Tuple format: ('files', (filename, file_bytes, content_type))
            files_payload.append(('data', (f.name, f.read(), f.type)))
        
        status_text.text("Sending to AI Agent... please wait...")
        progress_bar.progress(20)

        try:
            # Send to n8n
            response = requests.post(N8N_WEBHOOK_URL, files=files_payload)
            progress_bar.progress(80)
            
            if response.status_code == 200:
                data = response.json()
                progress_bar.progress(100)
                status_text.success("Processing Complete!")
                
                # --- DISPLAY RESULTS ---
                # Assuming your n8n returns: { "results": [ ... ] }
                results = data.get("results", [])
                
                for res in results:
                    with st.expander(f"📄 {res.get('file_name', 'Document')}", expanded=True):
                        # Layout columns
                        col1, col2 = st.columns(2)
                        
                        fields = res.get("extracted_fields", {})
                        analysis = fields.get("tax_analysis", {})
                        
                        # Left Column: Key Details
                        with col1:
                            st.metric("Doc Type", res.get("document_type", "Unknown"))
                            st.metric("Employee", fields.get("employee_name", "N/A"))
                            st.metric("Effective Rate", f"{analysis.get('effective_tax_rate_percent', 0)}%")
                        
                        # Right Column: Risk Analysis
                        with col2:
                            flags = analysis.get("risk_flags", [])
                            if flags:
                                st.error(f"⚠️ Risks Found: {len(flags)}")
                                for flag in flags:
                                    st.write(f"- {flag}")
                            else:
                                st.success("✅ No Compliance Risks Found")
                                
                        # Show full summary
                        st.info(f"**Analyst Note:** {analysis.get('reviewer_summary', 'No summary available.')}")

            else:
                st.error(f"Error: Server returned status {response.status_code}")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")
