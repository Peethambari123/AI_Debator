import streamlit as st
import time
import openai

# Set your OpenAI API key securely (recommended to put in secrets.toml)
openai.api_key = st.secrets.get("AIzaSyDXuDTH5QEicZOQnG5xA7e5qqAx_Vojfw0")

# --- Helper functions ---

def start_debate_timer(duration_seconds):
    placeholder = st.empty()
    progress_bar = st.progress(0)

    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        time_remaining = duration_seconds - (time.time() - start_time)
        progress = (duration_seconds - time_remaining) / duration_seconds
        progress_bar.progress(progress)

        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        placeholder.markdown(f"**Time Remaining: {minutes:02d}:{seconds:02d}**")

        time.sleep(1)

    progress_bar.empty()
    placeholder.empty()
    st.session_state.app_state = 'summary'
    st.experimental_rerun()

def add_debate_turn(speaker, text):
    st.session_state.debate_history.append({'speaker': speaker, 'text': text})

def get_ai_response(debate_history, topic):
    """
    Use OpenAI chat completion API to generate AI response based on debate history.
    Format the conversation as messages with roles 'user' and 'assistant'.
    """
    # Prepare messages for ChatCompletion
    messages = [
        {"role": "system", "content": f"You are an AI debating about the topic: {topic}. Respond thoughtfully and engage with the user's arguments."}
    ]

    for turn in debate_history:
        role = "user" if turn['speaker'] == 'user' else 'assistant'
        messages.append({"role": role, "content": turn['text']})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            temperature=0.7,
            max_tokens=200,
            n=1,
            stop=None,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {e}"

# --- App Setup ---

st.set_page_config(page_title="AI Debate Platform", layout="wide")

if 'app_state' not in st.session_state:
    st.session_state.app_state = 'topic-selection'
    st.session_state.selected_topic = ''
    st.session_state.timer_duration = 180
    st.session_state.debate_history = []
    st.session_state.summary = None
    st.session_state.user_argument = ""

predefined_topics = [
    {"title": "AI's Impact on Employment", "description": "Debate whether AI will create more jobs than it displaces"},
    {"title": "Universal Basic Income", "description": "Discuss the merits and drawbacks of UBI in modern economies"},
    {"title": "Climate Change Action", "description": "Debate the most effective approaches to combat climate change"},
]

st.title("AI Debate Platform")
st.markdown("Test your arguments against an AI opponent.")

# --- Topic Selection ---
if st.session_state.app_state == 'topic-selection':
    st.header("Choose a Debate Topic")
    st.markdown("Select from predefined topics or create your own.")

    col1, col2, col3 = st.columns(3)
    if col1.button(predefined_topics[0]['title']):
        st.session_state.selected_topic = predefined_topics[0]['title']
    if col2.button(predefined_topics[1]['title']):
        st.session_state.selected_topic = predefined_topics[1]['title']
    if col3.button(predefined_topics[2]['title']):
        st.session_state.selected_topic = predefined_topics[2]['title']

    def update_custom_topic():
        st.session_state.selected_topic = st.session_state._custom_topic_input.strip()

    st.text_input(
        "Or type your own topic:",
        value=st.session_state.selected_topic if st.session_state.selected_topic not in [t['title'] for t in predefined_topics] else "",
        on_change=update_custom_topic,
        key="_custom_topic_input"
    )

    if st.session_state.selected_topic:
        if st.button("Continue to Timer Setup"):
            st.session_state.app_state = 'timer-setup'
            st.experimental_rerun()

# --- Timer Setup ---
elif st.session_state.app_state == 'timer-setup':
    st.header("Set Debate Timer")
    st.session_state.timer_duration = st.slider("Debate Duration (minutes)", 1, 10, int(st.session_state.timer_duration / 60)) * 60
    st.info(f"Selected Topic: **{st.session_state.selected_topic}**")

    if st.button("Start Debate"):
        # Initial AI opening statement
        st.session_state.debate_history = [{'speaker': 'ai', 'text': f"Let's begin the debate on: {st.session_state.selected_topic}. I look forward to your arguments."}]
        st.session_state.app_state = 'debate'
        st.experimental_rerun()

# --- Debate ---
elif st.session_state.app_state == 'debate':
    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("Live Debate")
        st.markdown(f"**Topic:** {st.session_state.selected_topic}")
    with col2:
        st.markdown(f"## {int(st.session_state.timer_duration / 60)}:00")

    # Show debate history
    for turn in st.session_state.debate_history:
        if turn['speaker'] == 'user':
            st.markdown(
                f'<div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; margin-left: auto; max-width: 70%;">'
                f"**You:** {turn['text']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px; max-width: 70%;">'
                f"**AI:** {turn['text']}</div>",
                unsafe_allow_html=True
            )

    # Debate input box and submission
    def on_user_submit():
        user_input = st.session_state.user_argument.strip()
        if user_input:
            add_debate_turn('user', user_input)
            st.session_state.user_argument = ""

            # Generate AI response immediately
            ai_text = get_ai_response(st.session_state.debate_history, st.session_state.selected_topic)
            add_debate_turn('ai', ai_text)
            st.experimental_rerun()

    st.text_input("Your argument:", key="user_argument", on_change=on_user_submit)

    # Start the timer (runs blocking, so place after UI inputs)
    start_debate_timer(st.session_state.timer_duration)

# --- Summary ---
elif st.session_state.app_state == 'summary':
    st.header("Debate Summary")

    st.markdown(f"**Topic:** {st.session_state.selected_topic}")

    # You could dynamically generate a summary with AI here too, but for now:
    st.session_state.summary = {
        'summary': "The debate covered various points. The AI and user exchanged arguments thoughtfully.",
        'winner': 'ai'
    }

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
        st.session_state.user_argument = ""
        st.rerun()
