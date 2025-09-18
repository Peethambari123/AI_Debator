import streamlit as st
import time
import google.generativeai as genai

# --- API Configuration ---
# Ensure you have your Google API key stored in Streamlit secrets
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except KeyError:
    st.error("API key not found. Please add your Google API key to Streamlit secrets.")
    st.stop()

# --- Helper functions ---

def add_debate_turn(speaker, text):
    """Adds a new turn to the debate history."""
    st.session_state.debate_history.append({'speaker': speaker, 'text': text})

def get_ai_response(conversation_history):
    """Generates an AI response using the Gemini API."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Build the prompt with the full conversation history
        prompt = f"You are a debate opponent. Your task is to provide a concise, single-paragraph counterargument or point. Topic: {st.session_state.selected_topic}\n\n"
        for turn in conversation_history:
            prompt += f"{turn['speaker']}: {turn['text']}\n"
        prompt += "AI:"
        
        # Generate the content
        response = model.generate_content(prompt)
        ai_response = response.text
        return ai_response
    except Exception as e:
        st.error(f"An error occurred while getting an AI response: {e}")
        return "Sorry, I am unable to respond at this time. Let's move on."


# --- Application Setup ---

st.set_page_config(
    page_title="AI Debate Platform",
    layout="wide",
)

# Initialize session state variables
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'topic-selection'
    st.session_state.selected_topic = ''
    st.session_state.timer_duration = 180
    st.session_state.debate_history = []
    st.session_state.summary = None
    st.session_state.debate_start_time = None

predefined_topics = [
    {"title": "AI's Impact on Employment", "description": "Debate whether AI will create more jobs than it displaces"},
    {"title": "Universal Basic Income", "description": "Discuss the merits and drawbacks of UBI in modern economies"},
    {"title": "Climate Change Action", "description": "Debate the most effective approaches to combat climate change"},
]

# --- UI Components ---

st.title("AI Debate Platform")
st.markdown("Test your arguments against an AI opponent.")

# --- Topic Selection Screen ---
if st.session_state.app_state == 'topic-selection':
    st.header("Choose a Debate Topic")
    st.markdown("Select from predefined topics or create your own.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"{predefined_topics[0]['title']}\n\n*{predefined_topics[0]['description']}*", use_container_width=True):
            st.session_state.selected_topic = predefined_topics[0]['title']
    with col2:
        if st.button(f"{predefined_topics[1]['title']}\n\n*{predefined_topics[1]['description']}*", use_container_width=True):
            st.session_state.selected_topic = predefined_topics[1]['title']
    with col3:
        if st.button(f"{predefined_topics[2]['title']}\n\n*{predefined_topics[2]['description']}*", use_container_width=True):
            st.session_state.selected_topic = predefined_topics[2]['title']
            
    st.markdown("---")
    
    st.text_input(
        "Or type your own topic:",
        value=st.session_state.selected_topic if st.session_state.selected_topic not in [t['title'] for t in predefined_topics] else "",
        on_change=lambda: st.session_state.update(selected_topic=st.session_state._custom_topic_input),
        key="_custom_topic_input"
    )

    if st.session_state.selected_topic:
        if st.button("Continue to Timer Setup", use_container_width=True):
            st.session_state.app_state = 'timer-setup'
            st.rerun()

# --- Timer Setup Screen ---
elif st.session_state.app_state == 'timer-setup':
    st.header("Set Debate Timer")
    st.markdown("How long would you like the debate to last?")

    st.session_state.timer_duration = st.slider(
        "Debate Duration (minutes)", 
        min_value=1, 
        max_value=10, 
        value=int(st.session_state.timer_duration / 60)
    ) * 60
    
    st.info(f"Selected Topic: **{st.session_state.selected_topic}**")

    if st.button("Start Debate", use_container_width=True):
        st.session_state.app_state = 'debate'
        st.session_state.debate_start_time = time.time()
        initial_ai_statement = "Thank you for initiating this debate. I'm looking forward to a thoughtful discussion on this topic. Let's begin."
        st.session_state.debate_history = [{'speaker': 'ai', 'text': initial_ai_statement}]
        st.experimental_rerun()

# --- Debate Screen ---
elif st.session_state.app_state == 'debate':
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("Live Debate")
        st.markdown(f"**Topic:** {st.session_state.selected_topic}")
    
    with col2:
        # Check and update timer
        elapsed_time = time.time() - st.session_state.debate_start_time
        time_remaining = st.session_state.timer_duration - elapsed_time

        if time_remaining <= 0:
            st.session_state.app_state = 'summary'
            st.rerun()
            
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        st.markdown(f"## {minutes:02d}:{seconds:02d}")
        
    st.markdown("---")

    # The debate container (chat-like interface)
    debate_container = st.container(height=400)
    with debate_container:
        # Display debate history
        for turn in st.session_state.debate_history:
            if turn['speaker'] == 'user':
                st.markdown(f'<div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; margin-left: auto; max-width: 70%;">**You:** {turn["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%;">**AI:** {turn["text"]}</div>', unsafe_allow_html=True)
                
    st.markdown("---")
    
    user_input = st.chat_input("Type your argument:")
    if user_input:
        add_debate_turn('user', user_input)
        
        with st.spinner("AI is thinking..."):
            ai_response = get_ai_response(st.session_state.debate_history)
            add_debate_turn('ai', ai_response)
        
        st.rerun()

    if st.button("End Debate", use_container_width=True):
        st.session_state.app_state = 'summary'
        st.rerun()
        
# --- Summary Screen ---
elif st.session_state.app_state == 'summary':
    st.header("Debate Summary")
    
    st.markdown(f"**Topic:** {st.session_state.selected_topic}")

    # Simulated summary data - In a real app, this would be generated by an LLM
    st.session_state.summary = {
        'summary': "The debate centered around the impact of technology on society. The user raised concerns about ethical implications, while the AI argued that technological progress ultimately benefits society. Both sides presented reasonable arguments, with the AI providing more historical evidence to support its claims.",
        'winner': 'ai'
    }

    # Display result
    result_text = "AI Won" if st.session_state.summary['winner'] == 'ai' else "You Won!"
    st.markdown(f"<h2 style='text-align: center;'>Debate Result: {result_text}</h2>", unsafe_allow_html=True)

    st.subheader("Debate Summary")
    st.info(st.session_state.summary['summary'])

    if st.button("Start New Debate"):
        st.session_state.app_state = 'topic-selection'
        st.session_state.selected_topic = ''
        st.session_state.timer_duration = 180
        st.session_state.debate_history = []
        st.session_state.summary = None
        st.rerun()
