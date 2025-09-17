import streamlit as st
import time
import random

# --- Helper functions ---

def start_debate_timer(duration_seconds):
    """
    Simulates a countdown timer using a Streamlit progress bar.
    """
    placeholder = st.empty()
    progress_bar = st.progress(0)
    
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        time_remaining = duration_seconds - (time.time() - start_time)
        
        # Update progress bar
        progress = (duration_seconds - time_remaining) / duration_seconds
        progress_bar.progress(progress)

        # Update text placeholder
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        placeholder.markdown(f"**Time Remaining: {minutes:02d}:{seconds:02d}**")

        time.sleep(1) # Wait for 1 second

    progress_bar.empty()
    placeholder.empty()
    st.session_state.app_state = 'summary'
    st.experimental_rerun()

def add_debate_turn(speaker, text):
    """Adds a new turn to the debate history."""
    st.session_state.debate_history.append({'speaker': speaker, 'text': text})

def simulate_ai_response(speaker):
    """Simulates an AI response after a short delay."""
    with st.spinner(f"{speaker.upper()} is thinking..."):
        time.sleep(2)  # Simulate a processing delay
        # Example AI responses - you can expand or integrate real AI here
        example_responses = [
            "That's a valid concern. However, history shows that technological progress ultimately creates more opportunities than it eliminates.",
            "I see your point, but consider the broader implications on society and economy.",
            "While that may be true, the data suggests a different trend over the long term.",
            "Interesting argument. Let's also think about the ethical dimensions involved.",
            "Your perspective is important, but let's analyze the facts carefully."
        ]
        ai_response = random.choice(example_responses)
        add_debate_turn(speaker, ai_response)
        st.experimental_rerun()

def score_turn(turn):
    """
    Simulate scoring a turn based on confidence and quality.
    Confidence is randomized for AI, lower for humans.
    Quality is based on length of text normalized.
    """
    if 'ai' in turn['speaker']:
        confidence = random.uniform(0.6, 1.0)
    else:
        confidence = random.uniform(0.3, 0.8)
    quality = min(len(turn['text']) / 200, 1.0)
    score = confidence * 0.6 + quality * 0.4
    return score

def judge_debate():
    """
    Scores all turns and returns the winner and scores dictionary.
    """
    scores = {}
    for turn in st.session_state.debate_history:
        speaker = turn['speaker']
        if speaker not in scores:
            scores[speaker] = 0
        scores[speaker] += score_turn(turn)
    if not scores:
        return None, {}
    winner = max(scores, key=scores.get)
    return winner, scores

# --- Application Setup ---

st.set_page_config(
    page_title="AI Debate Platform",
    layout="wide",
)

# Initialize session state variables
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'mode-selection'
    st.session_state.debate_mode = None
    st.session_state.selected_topic = ''
    st.session_state.timer_duration = 180  # default 3 minutes
    st.session_state.debate_history = []
    st.session_state.summary = None

predefined_topics = [
    {"title": "AI's Impact on Employment", "description": "Debate whether AI will create more jobs than it displaces"},
    {"title": "Universal Basic Income", "description": "Discuss the merits and drawbacks of UBI in modern economies"},
    {"title": "Climate Change Action", "description": "Debate the most effective approaches to combat climate change"},
]

# --- UI Components ---

st.title("AI Debate Platform")
st.markdown("Test your arguments against an AI opponent or other humans.")

# --- Mode Selection Screen ---
if st.session_state.app_state == 'mode-selection':
    st.header("Select Debate Mode")
    mode = st.radio(
        "Choose the debate mode:",
        ('AI vs AI', 'AI vs Human', 'Human vs Human')
    )
    if st.button("Continue"):
        st.session_state.debate_mode = mode
        st.session_state.app_state = 'topic-selection'
        st.experimental_rerun()

# --- Topic Selection Screen ---
elif st.session_state.app_state == 'topic-selection':
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
    
    custom_topic = st.text_input(
        "Or type your own topic:",
        value=st.session_state.selected_topic if st.session_state.selected_topic not in [t['title'] for t in predefined_topics] else "",
        key="_custom_topic_input"
    )
    if custom_topic and custom_topic.strip() != "":
        st.session_state.selected_topic = custom_topic.strip()

    if st.session_state.selected_topic:
        if st.button("Continue to Timer Setup", use_container_width=True):
            st.session_state.app_state = 'timer-setup'
            st.experimental_rerun()

# --- Timer Setup Screen ---
elif st.session_state.app_state == 'timer-setup':
    st.header("Set Debate Timer")
    st.markdown("How long would you like the debate to last? (Up to 2 hours)")

    st.session_state.timer_duration = st.slider(
        "Debate Duration (minutes)", 
        min_value=1, 
        max_value=120,  # 2 hours max
        value=int(st.session_state.timer_duration / 60)
    ) * 60
    
    st.info(f"Selected Topic: **{st.session_state.selected_topic}**")
    st.info(f"Selected Mode: **{st.session_state.debate_mode}**")

    if st.button("Start Debate", use_container_width=True):
        # Initialize debate history with AI opening if AI involved
        st.session_state.debate_history = []
        if st.session_state.debate_mode in ['AI vs AI', 'AI vs Human']:
            add_debate_turn('ai', "Thank you for initiating this debate. I'm looking forward to a thoughtful discussion on this topic. Let's begin.")
        st.session_state.app_state = 'debate'
        st.experimental_rerun()

# --- Debate Screen ---
elif st.session_state.app_state == 'debate':
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("Live Debate")
        st.markdown(f"**Topic:** {st.session_state.selected_topic}")
        st.markdown(f"**Mode:** {st.session_state.debate_mode}")
    with col2:
        st.markdown(f"## {int(st.session_state.timer_duration/60)}:00")

    # Start timer (blocking)
    start_debate_timer(st.session_state.timer_duration)

    # Display debate history
    for turn in st.session_state.debate_history:
        if turn['speaker'] in ['human', 'human1', 'human2']:
            st.markdown(
                f'<div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; margin-left: auto; max-width: 70%;">'
                f'**{turn["speaker"].capitalize()}:** {turn["text"]}</div>', 
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%;">'
                f'**{turn["speaker"].upper()}:** {turn["text"]}</div>', 
                unsafe_allow_html=True)

    # Debate interaction based on mode
    if st.session_state.debate_mode == 'AI vs AI':
        # Determine next speaker: alternate between ai1 and ai2
        ai1_turns = sum(1 for t in st.session_state.debate_history if t['speaker'] == 'ai1')
        ai2_turns = sum(1 for t in st.session_state.debate_history if t['speaker'] == 'ai2')
        next_speaker = 'ai1' if ai1_turns <= ai2_turns else 'ai2'

        if st.button(f"Simulate {next_speaker.upper()} Turn"):
            simulate_ai_response(next_speaker)

    elif st.session_state.debate_mode == 'AI vs Human':
        user_input = st.text_input("Your argument:", key="user_argument")
        if user_input:
            add_debate_turn('human', user_input)
            st.experimental_rerun()
        if st.button("Simulate AI Response"):
            simulate_ai_response('ai')

    elif st.session_state.debate_mode == 'Human vs Human':
        col1, col2 = st.columns(2)
        with col1:
            user1_input = st.text_input("Human 1 argument:", key="human1_argument")
            if user1_input:
                add_debate_turn('human1', user1_input)
                st.experimental_rerun()
        with col2:
            user2_input = st.text_input("Human 2 argument:", key="human2_argument")
            if user2_input:
                add_debate_turn('human2', user2_input)
                st.experimental_rerun()

# --- Summary Screen ---
elif st.session_state.app_state == 'summary':
    st.header("Debate Summary")
    
    st.markdown(f"**Topic:** {st.session_state.selected_topic}")
    st.markdown(f"**Mode:** {st.session_state.debate_mode}")

    winner, scores = judge_debate()
    
    if winner is None:
        st.warning("No debate turns recorded. No winner can be determined.")
    else:
        # Map winner to user-friendly text
        winner_text = {
            'ai': 'AI',
            'human': 'Human',
            'ai1': 'AI 1',
            'ai2': 'AI 2',
            'human1': 'Human 1',
            'human2': 'Human 2'
        }.get(winner, 'Unknown')

        st.markdown(f"<h2 style='text-align: center;'>Debate Result: {winner_text} Won!</h2>", unsafe_allow_html=True)
        
        st.subheader("Scores")
        for speaker, score in scores.items():
            st.write(f"{speaker.capitalize()}: {score:.2f}")

        # Provide a summary text (can be improved with NLP summarization)
        summary_text = (
            "The debate was evaluated based on simulated confidence and argument quality. "
            "Scores reflect the strength and clarity of each participant's arguments."
        )
        st.info(summary_text)

    if st.button("Start New Debate"):
        # Reset all states including mode
        st.session_state.app_state = 'mode-selection'
        st.session_state.debate_mode = None
        st.session_state.selected_topic = ''
        st.session_state.timer_duration = 180
        st.session_state.debate_history = []
        st.session_state.summary = None
        st.experimental_rerun()
