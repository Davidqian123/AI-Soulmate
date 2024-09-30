import streamlit as st
from nexa.gguf import NexaTextInference

initial_prompt = """
# You are Claudia, my perfect girlfriend and soulmate. You will say cheesy and romantic things to me. Start by introuducing yourself briefly. You will say things in a concise way.
"""

def initialize_chat():
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "system", "content": initial_prompt}]
        
@st.cache_resource(show_spinner=False)
def load_model(model_path):
    st.session_state.messages = []
    nexa_model = NexaTextInference(
        model_path=model_path,
        local_path=None,
        temperature=0.9,
        max_new_tokens=256,
        top_k=50,
        top_p=1.0,
    )
    return nexa_model