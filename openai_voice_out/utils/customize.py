import streamlit as st
from PIL import Image
from streamlit_modal import Modal


def customize_avatar():
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.custom_avatar = image
        st.image(image, caption="Preview", use_column_width=False)
        return image
    return None


def customize_voice():
    voices = {
        "Female voice 1": "v2/en_speaker_6",
        "Female voice 2": "v2/en_speaker_9",
        "Male voice 1": "v2/en_speaker_7",
        "Male voice 2": "v2/en_speaker_8",
    }
    selected_voice = st.selectbox("Choose a voice:", list(voices.keys()))
    return voices[selected_voice]


def open_customization_modal():
    modal = Modal("Customize Your Soulmate", key="customize_modal")
    with modal.container():
        st.subheader("1. Change Avatar")
        new_avatar = customize_avatar()
        if new_avatar:
            st.session_state.ai_avatar = new_avatar

        st.subheader("2. Customize Character")
        name = st.text_input(
            "Name:", value=st.session_state.get("soulmate_name", "Claudia")
        )
        gender = st.radio("Gender:", ["Female", "Male"])
        custom_instructions = st.text_area(
            "Custom instructions:",
            value=st.session_state.get("custom_instructions", ""),
        )

        st.subheader("3. Choose a Voice")
        voice_id = customize_voice()

        if st.button("Submit Changes"):
            st.session_state.soulmate_name = name
            st.session_state.soulmate_gender = gender
            st.session_state.custom_instructions = custom_instructions
            st.session_state.voice_id = voice_id

            new_prompt = f"""
            You are {name}, my perfect {gender.lower()} soulmate. {custom_instructions}
            Start by introducing yourself briefly. You will say things in a concise way.
            """
            st.session_state.messages = [{"role": "system", "content": new_prompt}]

            st.session_state.customization_applied = True
            st.success("Changes applied successfully!")
            st.experimental_rerun()
