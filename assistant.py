import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import streamlit as st
import time
import base64

recognizer = sr.Recognizer()

def speak_and_wait(text):
    """Convert text to speech and wait for playback to finish"""
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio_file = fp.name

    # Create audio player with play button
    with open(audio_file, "rb") as audio:
        audio_bytes = audio.read()
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
        <audio autoplay="true" controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)

    # Wait for the audio to finish (~length of text / words per second)
    time.sleep(len(text.split()) / 2.5)  # ~2.5 words/sec

def listen(prompt=None, expected_keywords=None, max_retries=2):
    retries = 0
    if prompt:
        speak_and_wait(prompt)

    while retries < max_retries:
        try:
            with sr.Microphone() as source:
                st.info("🎤 Speak now...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                response = recognizer.recognize_google(audio).lower()
                st.success(f"✅ You said: {response}")

                if expected_keywords:
                    for keyword in expected_keywords:
                        if keyword in response:
                            return keyword
                    speak_and_wait("Didn't catch that properly. Please try again.")
                    retries += 1
                else:
                    return response
        except Exception as e:
            st.warning(f"Could not hear: {e}")
            speak_and_wait("Could not hear, please try again.")
            retries += 1

    return None

available_tags = [
    "Motivation", "Careers", "Technology", "Mental Health", "AI",
    "Machine Learning", "Entrepreneurship", "Startups", "Leadership",
    "Growth", "Productivity", "Life Lessons", "Networking", "GenAI"
]

def map_spoken_to_tag(spoken_text):
    spoken_words = spoken_text.lower().split()
    for tag in available_tags:
        tag_lower = tag.lower()
        if tag_lower in spoken_text or any(word in tag_lower for word in spoken_words):
            return tag
    return spoken_text.title()