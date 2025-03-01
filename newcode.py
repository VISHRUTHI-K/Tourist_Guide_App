import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from langdetect import detect
from gtts import gTTS
import os

# Google Gemini API Key (Replace with your actual API Key)
GENAI_API_KEY = "AIzaSyCftitEnpzYZMx_noILaYmMh3Amilv3LWk"
genai.configure(api_key=GENAI_API_KEY)

# Streamlit UI Setup
st.set_page_config(page_title="Pixella : An AI-Powered Tourist Guide", layout="wide")

# Load your logo image
logo_path = "logo.jpg"  # Replace with the path to your logo
try:
    logo = Image.open(logo_path)
except FileNotFoundError:
    st.error(f"Logo not found at: {logo_path}")
    st.stop()  # Stop execution if the logo is not found

# Display the logo and the title
st.image(logo, width=100)  # Adjust width as needed
st.title("Pixella : An AI-Powered Tourist Guide")

# Load image from local storage
image_path = "HOMEPAGE.png"  # Replace with the path to your image file
try:
    image = Image.open(image_path)
except FileNotFoundError:
    st.error(f"Image not found at: {image_path}")
    st.stop()  # Stop execution if the image is not found

# Display the image with a click event to scroll
if st.image(image, use_container_width=True, caption="Click to explore landmarks"):
    st.markdown(
        """
        <script>
            window.scrollTo(0, document.body.scrollHeight);
        </script>
        """,
        unsafe_allow_html=True,
    )

# Chatbot Section
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
    image.save(img_byte_array, format="PNG")
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

