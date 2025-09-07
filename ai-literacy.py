import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import openai
from queue import Queue

# --- Configuration and Initialization ---

# Initialize pyttsx3 TTS engine and a thread-safe queue for voice commands
tts_engine = pyttsx3.init()
voice_queue = Queue()

# Voice worker thread
def voice_worker():
    while True:
        text = voice_queue.get()
        if text is None:
            break
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in voice worker: {e}")
        finally:
            voice_queue.task_done()

# Start the voice worker thread ONLY ONCE using Streamlit's session state.
if "voice_worker_started" not in st.session_state:
    threading.Thread(target=voice_worker, daemon=True).start()
    st.session_state["voice_worker_started"] = True

# Start the voice worker thread ONLY ONCE using Streamlit's session state.
# This is the key fix for the "run loop already started" error.
if "voice_worker_started" not in st.session_state:
    threading.Thread(target=voice_worker, daemon=True).start()
    st.session_state["voice_worker_started"] = True

def speak_text(text):
    voice_queue.put(text)

st.set_page_config(
    page_title="Shiksha Saathi 📚",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    openai.api_base = "https://openrouter.ai/api/v1"
except KeyError:
    st.error("API Key not found. Please add it to your secrets file.")
    st.stop()
except Exception as e:
    st.error(f"Error initializing API: {e}")
    st.stop()

# --- Session State Initialization ---
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "openai/gpt-3.5-turbo"
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are a helpful and simple Shiksha Saathi for rural learners. Give very short and simple answers in a friendly, conversational tone. Use analogies and simple words. Do not use any technical jargon. Always start your responses with a greeting like 'Hello friend,' or 'Namaste,'."}]
if "voice_search_enabled" not in st.session_state:
    st.session_state["voice_search_enabled"] = False
if "enable_voice_out" not in st.session_state:
    st.session_state["enable_voice_out"] = True
if "translate_to_hindi" not in st.session_state:
    st.session_state["translate_to_hindi"] = False
if "user_input_temp" not in st.session_state:
    st.session_state["user_input_temp"] = ""

# --- CSS Styles ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

body {
    background: url('https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1350&q=80') no-repeat center center fixed;
    background-size: cover;
    font-family: 'Nunito', sans-serif;
    color: #0a2540;
    margin: 0; padding: 0;
}

/* Navbar */
nav {
    background-color: rgba(255,255,255,0.95);
    padding: 1rem 2rem;
    box-shadow: 0 4px 7px rgba(0,0,0,0.2);
    position: sticky;
    top: 0;
    z-index: 1000;
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: 2px;
    text-align: center;
    color: #0a2540;
}

/* Main container */
.container {
    max-width: 1100px;
    margin: 3rem auto 5rem auto;
    background: rgba(255,255,255,0.95);
    padding: 40px 50px 60px 50px;
    border-radius: 25px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.3);
}

/* Header & Subheader */
.header {
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 10px;
    color: #0a2540;
    letter-spacing: 4px;
    text-shadow: 1px 1px 6px #8db1e1;
}
.subheader {
    font-size: 1.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 2rem;
    color: #1e3a8a;
    font-style: italic;
}

/* Compact hero image */
.intro-img {
    display: block;
    margin: 0 auto 3rem auto;
    max-width: 600px;
    width: 100%;
    height: 250px;
    object-fit: cover;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(30,58,138,0.3);
}

/* Cards Section - HORIZONTAL ALIGNMENT */
.card {
    background: #e4ecfe;
    border-radius: 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    padding: 30px 25px;
    flex-basis: 300px; 
    flex-grow: 1; 
    color: #0e2aad;
    font-weight: 700;
    transition: transform 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    height: 100%; /* Ensures cards have equal height */
}
.card:hover {
    transform: translateY(-10px);
}
.card img {
    max-width: 100%;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.card-title {
    font-size: 1.4rem;
    margin-bottom: 10px;
}
.card-desc {
    font-weight: 500;
    font-size: 1rem;
    line-height: 1.4;
}

/* Chat container */
.chat-container {
    max-width: 900px;
    margin: 0 auto 40px auto;
    border-radius: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    background: #f1f7ff;
    padding: 35px 45px 60px 45px;
    overflow-y: auto;
    max-height: 480px;
}

/* Chat bubbles */
.chat-user {
    background-color: #c4ebc7;
    color: #065f09;
    padding: 18px 26px;
    border-radius: 35px 35px 0 35px;
    margin-bottom: 18px;
    font-size: 19px;
    max-width: 75%;
    box-shadow: inset 1px 1px 6px #7caf7aaa;
    word-wrap: break-word;
    font-weight: 600;
    margin-left: auto;
}
.chat-ai {
    background-color: #c8ddf8;
    color: #0b3e91;
    padding: 18px 26px;
    border-radius: 35px 35px 35px 0;
    margin-bottom: 18px;
    font-size: 19px;
    max-width: 75%;
    box-shadow: inset 1px 1px 6px #7a8fafcc;
    word-wrap: break-word;
    font-weight: 600;
}

/* Input area with send button below textarea */
.input-section {
    max-width: 900px;
    margin: 0 auto 50px auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
textarea {
    padding: 15px 20px;
    font-size: 18px;
    font-family: 'Nunito', sans-serif;
    border: 2px solid #0a2540;
    border-radius: 20px;
    width: 100%;
    min-height: 90px;
    resize: none;
    transition: border-color 0.3s ease;
}
textarea:focus {
    outline: none;
    border-color: #1e40af;
    box-shadow: 0 0 12px #1e40af88;
}
button.btn-send {
    background-color: #1e40af;
    color: #fff;
    font-weight: 700;
    font-size: 20px;
    padding: 16px 0;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    box-shadow: 0 6px 15px #1e40af66;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
}
button.btn-send:hover {
    background-color: #2c3ab1;
    box-shadow: 0 8px 18px #2c3ab166;
}
button.btn-voice {
    background-color: #22c55e;
    color: white;
    font-weight: 700;
    font-size: 24px;
    border: none;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    cursor: pointer;
    box-shadow: 0 6px 15px #22c55e66;
    transition: background-color 0.3s ease;
    margin-left: auto;
}
button.btn-voice:hover {
    background-color: #2dd365;
    box-shadow: 0 8px 20px #2dd36577;
}

/* Sidebar */
.sidebar .sidebar-content {
    background: #e4ecfe;
    border-radius: 20px;
    padding: 30px 35px;
    font-weight: 700;
    color: #0e2aad;
    font-size: 18px;
}
.sidebar h3 {
    margin-bottom: 15px;
    font-weight: 900;
    color: #0a1f62;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px 10px;
    font-size: 16px;
    color: #375a9b;
    font-weight: 600;
    letter-spacing: 1.2px;
    background: #e4ecfe;
    border-top: 2px solid #0a1f62;
    margin-top: 80px;
}

/* Responsive */
@media (max-width: 900px) {
    .chat-container {
        padding: 25px 30px 40px 30px;
    }
    .header {
        font-size: 2.5rem;
    }
    .subheader {
        font-size: 1.2rem;
    }
    button.btn-voice {
        width: 48px;
        height: 48px;
        font-size: 18px;
    }
    button.btn-send {
        font-size: 18px;
        padding: 14px 0;
    }
    .cards {
        flex-direction: column;
        gap: 30px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Display Content and Chat History ---
st.markdown("""<nav>Shiksha Saathi</nav>""", unsafe_allow_html=True)
with st.container():
    
    st.markdown('<h1 class="header">Shiksha Saathi 📚</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Empowering Rural India through Voice-Activated Learning</p>', unsafe_allow_html=True)
    st.image(
        "https://www.powerschool.com/wp-content/uploads/2024/09/student-ai-literacy-blog-thumbnail-110424.jpg",
        caption="Learn anytime, anywhere",
        use_column_width=True,
        clamp=True,
        output_format="auto"
    )
    st.markdown('''
        <p style="font-size:1.25rem; text-align:center; color:#0a2540;">
        Welcome to <strong>Shiksha Saathi</strong>, your voice-based companion designed for rural learners with limited literacy. 
        Speak naturally and receive friendly, practical lessons and help—no typing necessary.
        </p>
    ''', unsafe_allow_html=True)
    st.markdown('<hr style="margin: 40px auto; max-width: 600px;">', unsafe_allow_html=True)

    # Use st.columns to ensure horizontal card layout
    cards_col1, cards_col2, cards_col3 = st.columns(3)
    
    card_data = [
        {"img": "https://images.unsplash.com/photo-1558261827-77136f565110?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8aGluZGl8ZW58MHx8MHx8fDA%3D", "title": "Local Language Support", "desc": "Interact in your native dialect. AI adapts to your language and cultural context."},
        {"img": "https://plus.unsplash.com/premium_photo-1678865184075-b635d6eeec78?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8U29sYXIlMjBSZWFkeXxlbnwwfHwwfHx8MA%3D%3D", "title": "Offline & Solar Ready", "desc": "Works with low connectivity and solar power to fit rural infrastructure."},
        {"img": "https://plus.unsplash.com/premium_photo-1682092805057-14abef3fdff7?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8TGlmZSUyMHNraWxscyUyMGluZGlhfGVufDB8fDB8fDA", "title": "Practical Life Skills", "desc": "Learn health, agriculture, finance and more integrated with literacy training."},
    ]

    with cards_col1:
        st.markdown(f'''
            <div class="card">
                <img src="{card_data[0]["img"]}" alt="{card_data[0]["title"]}">
                <div class="card-title">{card_data[0]["title"]}</div>
                <div class="card-desc">{card_data[0]["desc"]}</div>
            </div>
        ''', unsafe_allow_html=True)
    with cards_col2:
        st.markdown(f'''
            <div class="card">
                <img src="{card_data[1]["img"]}" alt="{card_data[1]["title"]}">
                <div class="card-title">{card_data[1]["title"]}</div>
                <div class="card-desc">{card_data[1]["desc"]}</div>
            </div>
        ''', unsafe_allow_html=True)
    with cards_col3:
        st.markdown(f'''
            <div class="card">
                <img src="{card_data[2]["img"]}" alt="{card_data[2]["title"]}">
                <div class="card-title">{card_data[2]["title"]}</div>
                <div class="card-desc">{card_data[2]["desc"]}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<hr style="margin: 40px auto; max-width: 600px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #0a2540;">📚 Study Notes</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #0a2540;">Download these free notes to learn more about important topics.</p>', unsafe_allow_html=True)

    notes_col1, notes_col2, notes_col3 = st.columns(3)
    

# Farming Techniques
with notes_col1:
    st.markdown("### Farming Techniques")
    st.download_button(
        label="Download Natural Farming Manual",
        data="https://naturalfarming.dac.gov.in/uploads/studymaterial/Technical-Manual-on-Natural_Farming_10.03.2025.pdf",
        file_name="natural-farming-manual.pdf",
        mime="application/pdf",
    )
    st.download_button(
        label="Download Organic Farming Training Manual",
        data="https://nconf.dac.gov.in/uploads/books_manual/Comprehensive_Training_manual_Organic_Farming.pdf",
        file_name="organic-farming-training-manual.pdf",
        mime="application/pdf",
    )

# Basic Healthcare
with notes_col2:
    st.markdown("### Basic Healthcare")
    st.download_button(
        label="Download Introduction to Public Health (CDC)",
        data="https://www.cdc.gov/training-publichealth101/media/pdfs/introduction-to-public-health.pdf",
        file_name="introduction-to-public-health.pdf",
        mime="application/pdf",
    )

# Financial Literacy
with notes_col3:
    st.markdown("### Financial Literacy")
    st.download_button(
        label="Download Financial Literacy Basics",
        data="https://www.metisnation.org/wp-content/uploads/2022/01/Financial-Literacy-Basics-for-Adults.pdf",
        file_name="financial-literacy-basics.pdf",
        mime="application/pdf",
    )
    st.download_button(
        label="Download Financial Literacy Manual",
        data="https://agra.org/wp-content/uploads/2020/03/CARI-EA-Financial-literacy-manual.pdf",
        file_name="financial-literacy-manual.pdf",
        mime="application/pdf",
    )
    st.markdown('</div>', unsafe_allow_html=True)


def display_chat(messages):
    for msg in [m for m in messages if m["role"] in ["user", "assistant"]]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

if len(st.session_state["messages"]) > 1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    display_chat(st.session_state["messages"])
    st.markdown('</div>', unsafe_allow_html=True)
    
with st.sidebar:
    st.markdown('<div class="sidebar"><h3>⚙️ Settings</h3></div>', unsafe_allow_html=True)
    voice_search = st.checkbox("Enable Voice Input 🎙️", value=st.session_state["voice_search_enabled"])
    st.session_state["voice_search_enabled"] = voice_search
    
    translate_to_hindi = st.checkbox("Translate to Hindi 🇮🇳", value=st.session_state["translate_to_hindi"])
    st.session_state["translate_to_hindi"] = translate_to_hindi

    st.markdown("### AI Voice Accent")
    voice_dialect = st.radio("Voice Dialect", ["American English", "British English"], index=0, label_visibility="hidden")
    st.markdown("### AI Voice Gender")
    voice_gender = st.radio("Voice Gender", ["Woman", "Man"], index=0, label_visibility="hidden")
    
def handle_voice_input():
    r = sr.Recognizer()
    with st.spinner("🎤 Listening... Please speak clearly."):
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=7, phrase_time_limit=7)
            st.success("🗣️ You spoke successfully! Processing your voice...")
            audio_text = r.recognize_google(audio)
            return audio_text
        except sr.WaitTimeoutError:
            st.error("⚠️ Listening timed out. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("⚠️ Sorry, couldn't understand. Please try again.")
            return None
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            return None

with st.form(key='chat_form', clear_on_submit=True):
    # Row for text input
    if st.session_state["voice_search_enabled"]:
        voice_input_clicked = st.form_submit_button(
            "🎙️ Tap to Speak",
            help="Click and speak your input",
            use_container_width=True
        )
        user_text = st.text_area(
            "Or type your message here:",
            value=st.session_state.get("user_input_temp", ""),
            height=110,
            key="chat_input_text"
        )
    else:
        user_text = st.text_area(
            "Type your message here:",
            value="",
            height=110,
            key="chat_input_text_normal"
        )
        voice_input_clicked = False

    # Row for centering the Send button
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        submit_clicked = st.form_submit_button(
            "➡️ Send",
            help="Send your message",
            use_container_width=True
        )


if submit_clicked or voice_input_clicked:
    final_prompt = ""
    if voice_input_clicked:
        voice_text = handle_voice_input()
        if voice_text:
            final_prompt = voice_text
            st.session_state["user_input_temp"] = voice_text
    else:
        final_prompt = user_text.strip()
        st.session_state["user_input_temp"] = ""

    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        full_response = ""
        
        with st.spinner("🤖 AI is thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                )
                full_response = response.choices[0].message.content
            except Exception as e:
                st.error(f"API error: {e}")
                full_response = "Sorry, an error occurred. Please try again."

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # This is the corrected voice output logic.
        # It's better to speak whenever voice_out is enabled, regardless of input method.
        if st.session_state["enable_voice_out"]:
            speak_text(full_response)
        
        if st.session_state["translate_to_hindi"]:
            with st.spinner("Translating..."):
                try:
                    translation_response = openai.ChatCompletion.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": "system", "content": "Translate the following English text to simple Hindi. Be direct and concise. Do not add any extra explanation or text. Just provide the translated text."},
                            {"role": "user", "content": full_response}
                        ],
                    )
                    hindi_translation = translation_response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": f"**Hindi Translation:** {hindi_translation}"})
                except Exception as e:
                    st.error(f"Translation error: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, an error occurred while translating."})
        
        st.rerun()

# --- New Section for Study Documents ---
st.markdown('<hr style="margin: 40px auto; max-width: 600px;">', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #0a2540;">📚 Download Free Study Documents</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #0a2540;">Get official and free study materials from NCERT, from Nursery to 10th grade.</p>', unsafe_allow_html=True)

notes_col1, notes_col2, notes_col3 = st.columns(3)
with notes_col1:
    st.markdown("### Primary (1-5)")
    st.link_button("NCERT Textbooks (official) — choose class & subject", "https://ncert.nic.in/textbook.php") 
    st.link_button("ePathshala eTextbooks (official)", "https://epathshala.nic.in/process.php?id=students&ln=en&type=eTextbooks") 

with notes_col2:
    st.markdown("### Middle (6-8)")
    st.link_button("NCERT Textbooks (official) — choose class & subject", "https://ncert.nic.in/textbook.php") 
    st.link_button("ePathshala eTextbooks (official)", "https://epathshala.nic.in/process.php?id=students&ln=en&type=eTextbooks")

with notes_col3:
    st.markdown("### Secondary (9-10)")
    st.link_button("NCERT Textbooks (official) — choose class & subject", "https://ncert.nic.in/textbook.php")
    st.link_button("ePathshala eTextbooks (official)", "https://epathshala.nic.in/process.php?id=students&ln=en&type=eTextbooks")

st.markdown("""
<div class="footer">
    © 2025 Shiksha Saathi — Powered by OpenAI API & pyttsx3 TTS — Designed for rural India
</div>""", unsafe_allow_html=True)