import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from langdetect import detect
from gtts import gTTS
import os
import requests
from io import BytesIO
import time

# Google Gemini API Key (Replace with your actual API Key)
GENAI_API_KEY = ""
genai.configure(api_key=GENAI_API_KEY)

# Streamlit UI Setup
st.set_page_config(page_title="Tourist Guide App", page_icon="🌍", layout="wide")
st.title("🌍 AI-Powered Tourist Guide - Landmark Descriptions")

# Split the page into carousel (1/4) and chatbot (3/4) sections
carousel_section, chatbot_section = st.columns([1, 3])

# Image Carousel in the top 1/4th
with carousel_section:
    st.markdown("#### Explore Popular Destinations:")

    def image_carousel(image_paths, width=450, height=600, interval=3):
        if not image_paths:
            st.warning("No images provided.")
            return

        if 'carousel_index' not in st.session_state:
            st.session_state.carousel_index = 0

        image_placeholder = st.empty()  # Create an empty placeholder

        while True:
            try:
                response = requests.get(image_paths[st.session_state.carousel_index])
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                image = image.resize((width, height))
                image_placeholder.image(image, use_container_width=False)  # Display in placeholder

                time.sleep(interval)  # Wait for the specified interval

                st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(image_paths)
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching image: {e}")
                break  # Exit the loop on error
            except Exception as e:
                st.error(f"Error displaying image: {e}")
                break # Exit the loop on error

    image_paths = [
        "https://plus.unsplash.com/premium_photo-1661962754715-d081d9ec53a3?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "https://images.unsplash.com/photo-1553808991-e39e7611442c?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "https://images.unsplash.com/photo-1605368689763-cebf5db26f87?q=80&w=1964&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    ]

    image_carousel(image_paths)


# Chatbot input area in the bottom 3/4th
with chatbot_section:
    st.write("Upload an image of a landmark or ask a question to get AI-generated insights!")

    # File uploader for landmark image
    uploaded_file = st.file_uploader("Upload a landmark image 📸", type=["jpg", "jpeg", "png"])

    # Text input for user prompt
    user_prompt = st.text_input("Ask about a landmark (e.g., 'Tell me about the Eiffel Tower'):", "", key="user_prompt")

    # Language selection (Default: Auto-detect)
    language_options = {
        "Auto-detect": None,
        "English": "en",
        "Hindi": "hi",
        "Telugu": "te",
        "Spanish": "es",
        "French": "fr",
        "Russian": "ru",
        "Chinese": "zh",
        "Greek": "el",
        "Latin": "la",
        "Japanese": "ja",
        "Korean": "ko"
    }
    selected_language = st.selectbox("Choose response language:", list(language_options.keys()))

    # Generate Button
    generate_button = st.button("🔍 Generate Description")

    # Define system instruction
    system_prompt = (
        "You are a Landmark Expert AI. Your only job is to provide detailed historical, "
        "architectural, and cultural descriptions of landmarks.You should answer questions by the user about landmarks. If a user asks something irrelevant, "
        "kindly redirect them to landmark-related information."
    )

    # Convert image to bytes if uploaded
    img_bytes = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        # Display image in a smaller size
        st.image(image, caption="Uploaded Image", width=300)  # Adjust width as needed
        
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="JPEG")
        img_bytes = img_byte_array.getvalue()

    # Detect language if user entered a prompt
    detected_language = None
    if user_prompt:
        try:
            detected_language = detect(user_prompt)
        except:
            detected_language = "en"  # Default to English if detection fails

    # Override detected language if user selects a specific one
    if language_options[selected_language]:
        detected_language = language_options[selected_language]

    # AI Model Selection
    model = genai.GenerativeModel("gemini-1.5-flash")  

    # Generate response when either Enter is pressed OR Generate button is clicked
    if (uploaded_file or user_prompt) and (generate_button or user_prompt):  
        st.write("🔄 Generating description...")

        # Constructing the input payload dynamically
        input_data = [{"text": system_prompt}]
        
        if user_prompt:
            input_data.append({"text": user_prompt})  # Add user's text prompt

        if img_bytes:
            input_data.append({"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}})  # Add image

        # Append language instruction
        if detected_language:
            input_data.append({"text": f"Respond in {detected_language}."})

        # Get AI response
        response = model.generate_content(input_data)

        # Display AI-generated response
        if response and hasattr(response, "text"):
            st.subheader("📚Landmark Description:")
            st.write(response.text)

            # Text-to-Speech (TTS) Feature
            def text_to_speech(text, lang):
                tts = gTTS(text=text, lang=lang)  # Generate speech from text
                tts.save("description.mp3")  # Save as an MP3 file
                return "description.mp3"

            # Add a button to play audio
            if st.button("🔊 Listen to Description"):
                audio_file = text_to_speech(response.text, detected_language if detected_language else "en")
                st.audio(audio_file, format="audio/mp3")
        else:
            st.error("⚠️ Failed to generate a description. Try again.")

    st.write("ℹ️ Powered by Google Gemini AI 🤖")