## NexaAI SDK Demo: AI Soulmate

### Introduction:

This project is an AI chatbot that interacts with users via text and voice. The project offers two options for voice output: using the **Bark** model for on-device text-to-speech or the **OpenAI TTS API** for cloud-based text-to-speech. **Bark** will be slow to generate speech without using GPU, but it's on device. The **OpenAI TTS API** has the advantage in terms of speed, but it is cloud-based and requires you to have an OPENAI API KEY. Each option is designed to provide flexibility based on the user's resources and preferences.You can also choose other options according to your preference.

- Key features:

  - On-device Character AI
  - No privacy concerns

- File structure:

  - `bark_voice_out/app.py`: main Streamlit app using Bark for voice output
  - `bark_voice_out/utils/initialize.py`: initializes chat and load model
  - `bark_voice_out/utils/gen_avatar.py`: generates avatar for AI Soulmate
  - `bark_voice_out/utils/transcribe.py`: handles voice input to text transcription
  - `bark_voice_out/utils/gen_response.py`: handles text and voice output

  - `openai_voice_out/app.py`: main Streamlit app using OpenAI TTS API for voice output
  - `openai_voice_out/utils/initialize.py`: initializes chat and load model
  - `openai_voice_out/utils/gen_avatar.py`: generates avatar for AI Soulmate
  - `openai_voice_out/utils/transcribe.py`: handles voice input to text transcription
  - `openai_voice_out/utils/gen_response.py`: handles text and voice output

### Technical Architecture

<p align="center">
  <img src="https://public-storage.nexa4ai.com/ai_soulmate.png" alt="Technical Architecture" width="50%">
</p>

### Setup:

#### Bark Voice Output

1. Install required packages:

```
pip install -r bark_requirements.txt
```

2. Usage:

- Run the Streamlit app: `streamlit run bark_voice_out/app.py`
- Start a chat with text or voice as you like

#### OpenAI Voice Output

1. Install required packages:

```
pip install -r openai_requirements.txt
```

2. Usage:

- Add your openai key in utils/gen_response.py line 8
- Run the Streamlit app: `streamlit run openai_voice_out/app.py`
- Start a chat with text or voice as you like

### Roadmap

More new features and improvements will follow:

1. More flexible customization for:
  - Name: Ability to set a custom name for the AI character.
  - Gender: Define the gender of the AI character.
  - Avatar & Image Upload: Allow users to upload a custom avatar or image representing the AI character.
  - Description: Set a background or description for the AI character.
  - Voice: Provide options to customize the voice of the AI character.
  - Greetings: Configure initial greetings or introduction phrases.
  - NSFW/Violence Switch: Implement a switch to toggle between safe-for-work and NSFW/violence modes.

2. Long-term Memory with mem0:
  - Integrate a memory system allowing the AI to retain and recall information over multiple sessions.

3. Multimodal Input & Output:
  - Support for various input and output modes, including text, image, and voice.

4. Image & Avatar Generation:
  - Enhance AI capabilities to generate images and avatars based on user inputs.

5. Voice Training & Upload:
  - Allow users to train the AI's voice model or upload custom voice data to create a personalized AI experience.

### Resources:

- [NexaAI | Model Hub](https://nexaai.com/models)
- [NexaAI | Inference with GGUF models](https://docs.nexaai.com/sdk/inference/gguf)
- [GitHub | BARK](https://github.com/suno-ai/bark)
- [Text to speech - OpenAI API](https://platform.openai.com/docs/guides/text-to-speech)
