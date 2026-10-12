import os
import requests

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

def run_dashboard():
    if not STREAMLIT_AVAILABLE:
        print("Streamlit is not installed in current environment. Install via: pip install streamlit")
        return

    st.set_page_config(page_title="Sabha AI — Ops & Qualcomm Telemetry", layout="wide")
    st.title("Sabha AI: Internal AI Operations & Qualcomm Benchmark Viewer")
    st.caption("Every conversation. A smarter decision. | Exclusive Provider: Qualcomm Cloud AI Playground")

    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    try:
        health_resp = requests.get(f"{api_url}/api/health", timeout=3).json()
        st.success(f"Backend API Connected: {health_resp.get('product')} (v{health_resp.get('version')})")
        
        qualcomm_info = health_resp.get("qualcomm_cloud_ai", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Qualcomm Cloud AI Status", qualcomm_info.get("status", "unknown").upper())
        with col2:
            st.metric("Base Endpoint", qualcomm_info.get("endpoint", "N/A"))
        with col3:
            st.metric("Models Ready", len(qualcomm_info.get("models_ready", [])))

        st.subheader("Configured Qualcomm Cloud AI Models")
        for m in qualcomm_info.get("models_ready", []):
            st.write(f"- `{m}`")

    except Exception as e:
        st.warning(f"Could not reach backend health endpoint: {e}")

if __name__ == "__main__":
    run_dashboard()
