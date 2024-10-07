import streamlit as st
from utils.initialize import initialize_chat, load_model, load_local_model
from utils.gen_avatar import generate_ai_avatar
from utils.gen_response import generate_chat_response
from utils.customize import open_customization_modal
from PIL import Image

img = Image.open("./nexalogo.png")
st.set_page_config(page_title="AI Soulmate", page_icon=img)

with st.spinner("Hi, I'm your AI soulmate, I'm generating avatar now. You can check the progress in the terminal. I'll be with you in just a moment~"):
    ai_avatar = generate_ai_avatar()

default_model = "llama3-uncensored"
model_mapping = {
    "llama3-uncensored": "llama3-uncensored",
    "Llama-3SOME-8B-v2": "TheDrummer/Llama-3SOME-8B-v2:gguf-q4_K_M",
    "L3-8B-UGI-DontPlanToEnd-test": "mradermacher/L3-8B-UGI-DontPlanToEnd-test:gguf-q4_K_M",
    "Llama-3.1-8B-ArliAI-RPMax-v1.1": "ArliAI/Llama-3.1-8B-ArliAI-RPMax-v1.1:gguf-q4_K_M",
    "Llama-3.2-3B-Instruct-uncensored": "chuanli11/Llama-3.2-3B-Instruct-uncensored:gguf-q4_K_M"
}
model_options = list(model_mapping.keys()) + ["Use Model From Nexa Model Hub","Local Model"]

def main():
    col1, col2 = st.columns([5, 5], vertical_alignment="center")
    with col1:
        st.title("AI Soulmate")
    with col2:
        avatar_path = st.session_state.get("ai_avatar", "ai_avatar.png")
        if st.session_state.get("modal_open") and "uploaded_avatar" in st.session_state:
            avatar_path = st.session_state.uploaded_avatar
        st.image(avatar_path, width=150)
        open_customization_modal()
    st.caption("Powered by Nexa AI")

    st.sidebar.header("Model Configuration")
    model_path = st.sidebar.selectbox("Select a Model", model_options, index=model_options.index(default_model))
    
    if model_path == "Local Model":
        local_model_path = st.sidebar.text_input("Enter local model path")
        if not local_model_path:
            st.warning("Please enter a valid local model path to proceed.")
            st.stop()
        hub_model_name = None
    elif model_path == "Use Model From Nexa Model Hub":
        hub_model_name = st.sidebar.text_input("Enter model name from Nexa Model Hub")
        if hub_model_name:
            if hub_model_name.startswith("nexa run"):
                hub_model_name = hub_model_name.split("nexa run")[-1].strip()
            else:
                hub_model_name = hub_model_name.strip()
        if not hub_model_name:
            st.warning(f"""
                Please enter a valid model name from Nexa Model Hub.
                You can proceed by copying the full nexa run command or the model name in the nexa run command.
                Click [here](https://nexaai.com/models) to visit Nexa Model Hub.
            """)
            st.stop()
        local_model_path = None
    else:
        local_model_path = None
        hub_model_name = None
    
    if ("current_model_path" not in st.session_state or 
        st.session_state.current_model_path != model_path or
        (model_path == "Local Model" and local_model_path != st.session_state.current_local_model_path) or
        (model_path == "Use Model From Nexa Model Hub" and hub_model_name != st.session_state.current_hub_model_name)):
        st.session_state.current_model_path = model_path
        st.session_state.current_local_model_path = local_model_path
        st.session_state.current_hub_model_name = hub_model_name
        with st.spinner("Hang tight! Loading model, you can check the progress in the terminal. I'll be right back with you : )"):
            if model_path == "Local Model" and local_model_path:
                st.session_state.nexa_model = load_local_model(local_model_path)
            elif model_path == "Use Model From Nexa Model Hub" and hub_model_name:
                st.session_state.nexa_model = load_model(hub_model_name)
            else:
                st.session_state.nexa_model = load_model(model_mapping[model_path])
        st.session_state.messages = []
        
        if "intro_sent" in st.session_state:
            del st.session_state["intro_sent"]
        
    if not model_path:
        st.warning(
            "Please enter a valid path or identifier for the model in Nexa Model Hub to proceed."
        )
        st.stop()

    if "ai_avatar" not in st.session_state:
        st.session_state.ai_avatar = generate_ai_avatar()

    st.sidebar.header("Generation Parameters")
    temperature = st.sidebar.slider(
        "Temperature", 0.0, 1.0, st.session_state.nexa_model.params["temperature"]
    )
    max_new_tokens = st.sidebar.slider(
        "Max New Tokens", 1, 1000, st.session_state.nexa_model.params["max_new_tokens"]
    )
    top_k = st.sidebar.slider(
        "Top K", 1, 100, st.session_state.nexa_model.params["top_k"]
    )
    top_p = st.sidebar.slider(
        "Top P", 0.0, 1.0, st.session_state.nexa_model.params["top_p"]
    )

    st.session_state.nexa_model.params.update(
        {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "top_k": top_k,
            "top_p": top_p,
        }
    )

    initialize_chat()
    
    # check if customization was just applied:
    if st.session_state.get("customization_applied", False):
        st.session_state.customization_applied = False  # reset the flag

    for message in st.session_state.messages:
        if message["role"] != "system" and message.get("visible", True):
            if message["role"] == "user":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            else:
                with st.chat_message(
                    message["role"], avatar=st.session_state.ai_avatar
                ):
                    st.markdown(message["content"])
                    
    if "intro_sent" not in st.session_state:
        st.session_state.messages.append({"role": "user", "content": "hello, please intro your self in 30 words.", "visible": False})
        st.session_state.intro_sent = True
            
        with st.chat_message("assistant", avatar=ai_avatar):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in generate_chat_response(st.session_state.nexa_model):
                choice = chunk["choices"][0]
                if "delta" in choice:
                    delta = choice["delta"]
                    content = delta.get("content", "")
                elif "text" in choice:
                    delta = choice["text"]
                    content = delta

                full_response += content
                response_placeholder.markdown(full_response, unsafe_allow_html=True)
            response_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=ai_avatar):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in generate_chat_response(st.session_state.nexa_model):
                choice = chunk["choices"][0]
                if "delta" in choice:
                    delta = choice["delta"]
                    content = delta.get("content", "")
                elif "text" in choice:
                    delta = choice["text"]
                    content = delta

                full_response += content
                response_placeholder.markdown(full_response, unsafe_allow_html=True)
            response_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
