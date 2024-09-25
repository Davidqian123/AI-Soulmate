import streamlit as st
from PIL import Image
from streamlit_modal import Modal
from utils.gen_response import generate_and_play_response


def initialize_temp_customization():
    if "temp_customization" not in st.session_state:
        st.session_state.temp_customization = {
            "name": st.session_state.get("soulmate_name", "Claudia"),
            "gender": st.session_state.get("soulmate_gender", "Female"),
            "custom_instructions": st.session_state.get("custom_instructions", ""),
            "voice_id": st.session_state.get("voice_id", "v2/en_speaker_9"),
        }


def customize_avatar():
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.temp_custom_avatar = image
        st.image(image, caption="Preview", use_column_width=True)


def customize_voice():
    voices = {
        "Female voice 1": "v2/en_speaker_6",
        "Female voice 2": "v2/en_speaker_9",
        "Male voice 1": "v2/en_speaker_7",
        "Male voice 2": "v2/en_speaker_8",
    }
    selected_voice = st.selectbox(
        "Choose a voice:", list(voices.keys()), key="temp_voice"
    )
    return voices[selected_voice]


def customization_form():
    initialize_temp_customization()

    st.subheader("1. Change Avatar")
    customize_avatar()

    st.subheader("2. Customize Character")
    st.session_state.temp_customization["name"] = st.text_input(
        "Name:", value=st.session_state.temp_customization["name"]
    )
    st.session_state.temp_customization["gender"] = st.radio(
        "Gender:",
        ["Female", "Male"],
        index=0 if st.session_state.temp_customization["gender"] == "Female" else 1,
    )
    st.session_state.temp_customization["custom_instructions"] = st.text_area(
        "Custom Instructions:",
        value=st.session_state.temp_customization["custom_instructions"],
    )

    st.subheader("3. Choose a Voice")
    st.session_state.temp_customization["voice_id"] = customize_voice()

    if st.button("Submit Changes"):
        apply_changes()
        st.session_state.modal_open = False
        st.experimental_rerun()

    if st.button("Cancel"):
        st.session_state.modal_open = False
        if "temp_customization" in st.session_state:
            del st.session_state.temp_customization
        if "temp_custom_avatar" in st.session_state:
            del st.session_state.temp_custom_avatar
        st.experimental_rerun()


def apply_changes():
    if "temp_custom_avatar" in st.session_state:
        st.session_state.ai_avatar = st.session_state.temp_custom_avatar
        del st.session_state.temp_custom_avatar

    st.session_state.soulmate_name = st.session_state.temp_customization["name"]
    st.session_state.soulmate_gender = st.session_state.temp_customization["gender"]
    st.session_state.custom_instructions = st.session_state.temp_customization[
        "custom_instructions"
    ]
    st.session_state.voice_id = st.session_state.temp_customization["voice_id"]

    new_prompt = f"""
    You are {st.session_state.soulmate_name}, my perfect {st.session_state.soulmate_gender.lower()} soulmate. {st.session_state.custom_instructions}
    Start by introducing yourself briefly. You will say things in a concise way.
    """
    st.session_state.messages = [{"role": "system", "content": new_prompt}]

    st.session_state.customization_applied = True
    del st.session_state.temp_customization


def open_customization_modal():
    if "modal_open" not in st.session_state:
        st.session_state.modal_open = False

    if st.button("Customize Character"):
        st.session_state.modal_open = True
        initialize_temp_customization()

    if st.session_state.modal_open:
        modal = Modal("Customize Your Soulmate", key="customize_modal")
        with modal.container():
            customization_form()
