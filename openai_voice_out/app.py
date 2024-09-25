import streamlit as st
import base64
from utils.initialize import initialize_chat, load_model
from utils.gen_avatar import generate_ai_avatar
from utils.transcribe import record_and_transcribe
from utils.gen_response import generate_chat_response, generate_and_play_response
from utils.customize import open_customization_modal
from PIL import Image

img = Image.open("./nexalogo.png")
st.set_page_config(page_title="AI Soulmate", page_icon=img)

ai_avatar = generate_ai_avatar()
default_model = "llama3-uncensored"


def main():
    col1, col2 = st.columns([5, 5], vertical_alignment="center")
    with col1:
        st.title("AI Soulmate")
    with col2:
        st.image(st.session_state.get("ai_avatar", ai_avatar), width=150)
        open_customization_modal()
    st.caption("Powered by Nexa AI")

    st.sidebar.header("Model Configuration")
    model_path = st.sidebar.text_input("Model path", default_model)

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
        st.session_state.nexa_model = load_model(model_path)
        if st.session_state.nexa_model is None:
            st.stop()

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

        introduction = f"Hi, I'm {name}, your perfect {gender.lower()} soulmate. {custom_instructions}"
        st.session_state.messages.append({"role": "assistant", "content": introduction})

        with st.chat_message(
            "assistant", avatar=st.session_state.get("ai_avatar", ai_avatar)
        ):
            st.write(introduction)

        generate_and_play_response(introduction, voice)

        st.session_state.customization_applied = False  # reset the flag

    for message in st.session_state.messages:
        if message["role"] != "system":
            if message["role"] == "user":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            else:
                with st.chat_message(message["role"], avatar=ai_avatar):
                    st.markdown(message["content"])

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

            audio_path = generate_and_play_response(
                full_response, st.session_state.voice
            )

            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            st.markdown(
                f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """,
                unsafe_allow_html=True,
            )

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

        audio_path = generate_and_play_response(full_response, st.session_state.voice)

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        st.markdown(
            f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """,
            unsafe_allow_html=True,
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
