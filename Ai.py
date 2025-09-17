import streamlit as st
import google.generativeai as genai
import time
import os
import json
from google.cloud import texttospeech_v1 as texttospeech

# Load Google Cloud credentials from environment variables
# For production, use environment variables. For local testing, you can use a file path.
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize APIs
tts_client = texttospeech.TextToSpeechClient()
gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- Helper Functions ---

def generate_tts_audio(text: str) -> bytes:
    """Generates speech from text and returns the audio content as bytes."""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    return response.audio_content

def generate_summary_and_analysis(history):
    """Generates a summary and analysis of the debate."""
    full_transcript = "\n".join([f"{turn['speaker'].upper()}: {turn['text']}" for turn in history])
    summary_prompt = f"""
    Analyze the following debate transcript on the topic: '{st.session_state.topic}'.
    ---
    {full_transcript}
    ---
    Provide a concise "summary" of the key points from both the human and AI.
    Determine the "winner" of the debate based on the quality of arguments. The value should be 'user', 'ai', or 'draw'.
    Rate the argument "strengths" for both the user and AI on a scale of 1 to 10 for clarity, quality, and persuasiveness.
    Your response must be a valid JSON object with the keys 'summary', 'winner', and 'strengths'.
    """
    try:
        response = gemini_model.generate_content(summary_prompt)
        summary_data_raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(summary_data_raw)
    except Exception as e:
        st.error(f"Failed to generate summary: {e}")
        return None

# --- Streamlit UI Components ---

st.set_page_config(page_title="AI Debate Platform", layout="wide")

st.title("AI Debate Platform 🎙️")
st.markdown("---")

# Initialize session state
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'topic-selection'
    st.session_state.topic = ""
    st.session_state.debate_history = []
    st.session_state.debate_start_time = None
    st.session_state.debate_duration = 3 * 60  # 3 minutes in seconds
    st.session_state.summary = None
    st.session_state.is_listening = False

def start_debate():
    if not st.session_state.topic:
        st.warning("Please enter a debate topic.")
        return
    st.session_state.app_state = 'debate'
    st.session_state.debate_history = []
    st.session_state.debate_start_time = time.time()
    
    initial_ai_statement = "Let's begin the debate on: " + st.session_state.topic + ". I look forward to your arguments."
    st.session_state.debate_history.append({"speaker": "ai", "text": initial_ai_statement})
    audio_content = generate_tts_audio(initial_ai_statement)
    st.audio(audio_content, format="audio/mp3", autoplay=True, loop=False)
    st.rerun()

def end_debate():
    st.session_state.summary = generate_summary_and_analysis(st.session_state.debate_history)
    st.session_state.app_state = 'summary'
    st.rerun()

def handle_user_input(user_argument):
    if not user_argument:
        return
    st.session_state.debate_history.append({"speaker": "user", "text": user_argument})
    
    full_transcript = "\n".join([f"{turn['speaker'].upper()}: {turn['text']}" for turn in st.session_state.debate_history])
    
    debate_prompt = f"""
    You are an AI debating a human. The debate topic is: '{st.session_state.topic}'.
    Here is the debate history so far:
    ---
    {full_transcript}
    ---
    Your turn. Provide a concise counter-argument to the last statement. Do not exceed 50 words.
    """
    
    try:
        response = gemini_model.generate_content(debate_prompt)
        ai_response = response.text.strip()
        st.session_state.debate_history.append({"speaker": "ai", "text": ai_response})
        audio_content = generate_tts_audio(ai_response)
        st.audio(audio_content, format="audio/mp3", autoplay=True, loop=False)
        st.rerun()
    except Exception as e:
        st.error(f"Failed to get AI response: {e}")
        st.session_state.debate_history.append({"speaker": "ai", "text": "I'm sorry, I couldn't process that. Please try again."})
        st.rerun()

# --- Page Rendering Logic ---

if st.session_state.app_state == 'topic-selection':
    st.header("Select a Debate Topic")
    topic_options = [
        "AI's Impact on Employment",
        "Universal Basic Income",
        "The Role of Social Media in Society",
        "Climate Change Action"
    ]
    selected_topic = st.selectbox("Choose a topic:", [""] + topic_options, index=0)
    
    custom_topic = st.text_input("Or, enter your own topic:", value=st.session_state.topic if st.session_state.topic not in topic_options else "")
    
    if custom_topic:
        st.session_state.topic = custom_topic
    elif selected_topic:
        st.session_state.topic = selected_topic

    if st.button("Start Debate", disabled=not st.session_state.topic):
        start_debate()

elif st.session_state.app_state == 'debate':
    st.subheader(f"Debate on: {st.session_state.topic}")
    
    placeholder = st.empty()
    if st.session_state.debate_start_time:
        with placeholder.container():
            current_time = int(st.session_state.debate_duration - (time.time() - st.session_state.debate_start_time))
            if current_time <= 0:
                end_debate()
            st.metric("Time Remaining", f"{current_time // 60}:{current_time % 60:02d}")
            st.markdown("---")
            
    # Chat display area with scrolling
    with st.container(height=400, border=True):
        for turn in st.session_state.debate_history:
            if turn["speaker"] == "user":
                st.markdown(f'<div style="background-color:#E0F7FA; border-radius:10px; padding:10px; margin:5px; text-align:right;">{turn["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background-color:#F5F5F5; border-radius:10px; padding:10px; margin:5px;">{turn["text"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    user_input = st.text_input("Your argument:", key="user_input")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send Argument"):
            handle_user_input(user_input)
    with col2:
        if st.button("End Debate"):
            end_debate()
    
    if st.session_state.is_listening:
        st.info("Listening...")

elif st.session_state.app_state == 'summary':
    st.header("Debate Summary & Analysis")
    
    if st.session_state.summary:
        summary_data = st.session_state.summary
        
        # Display the winner
        if summary_data['winner'] == 'user':
            st.balloons()
            st.success("🎉 You Won the Debate!")
        elif summary_data['winner'] == 'ai':
            st.error("🤖 The AI Won the Debate.")
        else:
            st.info("🤝 The Debate was a Draw.")
        
        # Display the summary
        st.subheader("Summary")
        st.markdown(summary_data['summary'])
        
        # Display the strengths analysis
        st.subheader("Argument Strengths")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Your Performance")
            st.metric("Clarity", f"{summary_data['strengths']['user']['clarity']}/10")
            st.metric("Quality", f"{summary_data['strengths']['user']['quality']}/10")
            st.metric("Persuasiveness", f"{summary_data['strengths']['user']['persuasiveness']}/10")
            
        with col2:
            st.markdown("### AI Performance")
            st.metric("Clarity", f"{summary_data['strengths']['ai']['clarity']}/10")
            st.metric("Quality", f"{summary_data['strengths']['ai']['quality']}/10")
            st.metric("Persuasiveness", f"{summary_data['strengths']['ai']['persuasiveness']}/10")
            
    if st.button("Start New Debate"):
        st.session_state.clear()
        st.rerun()
