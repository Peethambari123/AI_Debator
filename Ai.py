import streamlit as st
import time

# --- Helper functions ---

def add_debate_turn(speaker, text):
    """Adds a new turn to the debate history."""
    st.session_state.debate_history.append({'speaker': speaker, 'text': text})

def simulate_ai_response():
    """Simulates an AI response."""
    with st.spinner("AI is thinking..."):
        time.sleep(2)  # Simulate a processing delay
        ai_response = "That's a valid concern. However, history shows that technological progress ultimately creates more opportunities than it eliminates. For instance, the industrial revolution initially displaced workers but eventually led to higher living standards."
        add_debate_turn('ai', ai_response)
        # Rerun to display the new message
        st.experimental_rerun()


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
            st.experimental_rerun()

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
        st.session_state.debate_history = [{'speaker': 'ai', 'text': "Thank you for initiating this debate. I'm looking forward to a thoughtful discussion on this topic. Let's begin."}]
        st.experimental_rerun()

# --- Debate Screen ---
elif st.session_state.app_state == 'debate':
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("Live Debate")
        st.markdown(f"**Topic:** {st.session_state.selected_topic}")
    
    with col2:
        # Calculate time remaining
        elapsed_time = time.time() - st.session_state.debate_start_time
        time_remaining = st.session_state.timer_duration - elapsed_time

        if time_remaining <= 0:
            st.session_state.app_state = 'summary'
            st.experimental_rerun()
            
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
        simulate_ai_response()

    if st.button("End Debate", use_container_width=True):
        st.session_state.app_state = 'summary'
        st.experimental_rerun()
