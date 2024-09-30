import streamlit as st
from utils.initialize import initialize_chat, load_model
from utils.gen_avatar import generate_ai_avatar
from utils.transcribe import record_and_transcribe
from utils.gen_response import generate_chat_response, generate_and_play_response
from utils.customize import open_customization_modal
from PIL import Image

img = Image.open("./nexalogo.png")
st.set_page_config(page_title="AI Soulmate", page_icon=img)

with st.spinner("Hi, I'm your AI soulmate, I'm generating avatar now. I'll be with you in just a moment~"):
    ai_avatar = generate_ai_avatar()

default_model = "llama3-uncensored"
model_options = ["llama3-uncensored", "llama2", "llama3.1", "tinyllama"]



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
    
    if "current_model_path" not in st.session_state or st.session_state.current_model_path != model_path:
        st.session_state.current_model_path = model_path
        with st.spinner("Hang tight! Loading model, I'll be right back with you : )"):
            st.session_state.nexa_model = load_model(model_path)
        st.session_state.messages = []
        
        if "intro_sent" in st.session_state:
            del st.session_state["intro_sent"]

    if not model_path:
        st.warning(
            "Please enter a valid path or identifier for the model in Nexa Model Hub to proceed."
        )
        st.stop()

    if (
        "current_model_path" not in st.session_state
        or st.session_state.current_model_path != model_path
    ):
        st.session_state.current_model_path = model_path
        with st.spinner("Hang tight! Loading model, I'll be right back with you :)"):
            st.session_state.nexa_model = load_model(model_path)
        if st.session_state.nexa_model is None:
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
        name = st.session_state.soulmate_name
        gender = st.session_state.soulmate_gender
        custom_instructions = st.session_state.custom_instructions
        voice = st.session_state.voice

        # introduction = f"Hi, I'm {name}, your perfect {gender.lower()} soulmate. {custom_instructions}"
        # st.session_state.messages.append({"role": "assistant", "content": introduction})

        # with st.chat_message(
        #     "assistant", avatar=st.session_state.get("ai_avatar", ai_avatar)
        # ):
        #     st.write(introduction)

        # generate_and_play_response(introduction, voice_id)

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
            
        generate_and_play_response(full_response)
        
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

    if st.button("🎙️ Start Voice Chat"):
        transcribed_text = record_and_transcribe()
        if transcribed_text:
            st.session_state.messages.append(
                {"role": "user", "content": transcribed_text}
            )
            with st.chat_message("user"):
                st.markdown(transcribed_text)

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

            generate_and_play_response(full_response)

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

        generate_and_play_response(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
