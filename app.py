import streamlit as st
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from logic import run_comparison

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="TOON vs JSON Token Savings", layout="wide")

st.title("TOON vs JSON: Token & Cost Savings Showcase")
st.markdown("""
This app demonstrates the token usage and cost savings of using **TOON** (binary serialization) 
compared to standard **JSON** when interacting with OpenAI LLMs.
""")

# Sidebar Configuration
st.sidebar.header("Configuration")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
langsmith_api_key = st.sidebar.text_input("LangSmith API Key", type="password", value=os.environ.get("LANGSMITH_API_KEY", ""))

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
if langsmith_api_key:
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key

num_users = st.sidebar.slider("Number of Users in Payload", min_value=1, max_value=50, value=10)
model_name = st.sidebar.selectbox("OpenAI Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])

if st.button("Run Comparison"):
    with st.spinner("Generating data and calculating tokens..."):
        results = run_comparison(num_users=num_users, model=model_name)
        
        # Show data source
        if results.get("api_called"):
            st.success("✅ Using ACTUAL token counts from OpenAI API (logged in LangSmith)")
        else:
            st.warning("⚠️ Using ESTIMATED token counts (tiktoken). OpenAI API was not called.")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("JSON Tokens", f"{results['json']['tokens']:,}")
            st.metric("JSON Cost", f"${results['json']['cost']:.6f}")
            if results['json'].get('actual_usage'):
                with st.expander("JSON Token Details"):
                    st.write(f"**Input tokens:** {results['json']['actual_usage']['prompt_tokens']:,}")
                    st.write(f"**Output tokens:** {results['json']['actual_usage']['completion_tokens']:,}")
                    st.write(f"**Total tokens:** {results['json']['actual_usage']['total_tokens']:,}")
        with col2:
            st.metric("TOON Tokens", f"{results['toon']['tokens']:,}")
            st.metric("TOON Cost", f"${results['toon']['cost']:.6f}")
            if results['toon'].get('actual_usage'):
                with st.expander("TOON Token Details"):
                    st.write(f"**Input tokens:** {results['toon']['actual_usage']['prompt_tokens']:,}")
                    st.write(f"**Output tokens:** {results['toon']['actual_usage']['completion_tokens']:,}")
                    st.write(f"**Total tokens:** {results['toon']['actual_usage']['total_tokens']:,}")
        with col3:
            st.metric("Token Savings", f"{results['savings']['tokens']:,}", delta=f"{results['savings']['percentage']:.2f}%")
            st.metric("Cost Savings", f"${results['savings']['cost']:.6f}")

        # Charts
        st.subheader("Comparison Charts")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Token Comparison
        ax1.bar(["JSON", "TOON"], [results['json']['tokens'], results['toon']['tokens']], color=['#ff9999', '#66b3ff'])
        ax1.set_title("Token Usage")
        ax1.set_ylabel("Tokens")
        
        # Cost Comparison
        ax2.bar(["JSON", "TOON"], [results['json']['cost'], results['toon']['cost']], color=['#ff9999', '#66b3ff'])
        ax2.set_title("Cost ($)")
        ax2.set_ylabel("Cost ($)")
        
        st.pyplot(fig)
        
        # Detailed View
        st.subheader("Payload Preview")
        tab1, tab2 = st.tabs(["JSON Payload", "TOON Payload (Base64)"])
        
        with tab1:
            st.text_area("JSON", results['json']['full_content'], height=300)
        with tab2:
            st.text_area("TOON (Base64)", results['toon']['full_content'], height=300)

        if results.get("api_called"):
            st.success(f"✅ Requests sent to OpenAI! Check LangSmith project '{os.getenv('LANGSMITH_PROJECT')}' for traces.")
            st.info("💡 The token counts above match what you see in LangSmith because they're from the actual API response.")
        else:
            st.warning("⚠️ OpenAI API Key not provided. Token counts are ESTIMATES using tiktoken (not actual API usage).")

