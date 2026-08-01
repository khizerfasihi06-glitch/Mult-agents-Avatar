import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
import io
from pypdf import PdfReader

# --- Page Configuration ---
st.set_page_config(page_title="Multi-persona AI Chatbot", layout="centered")

# --- API Key Setup ---
# Best practice: Set MISTRAL_API_KEY in your environment or Streamlit Secrets
if "MISTRAL_API_KEY" in st.secrets:
    os.environ["MISTRAL_API_KEY"] = GsoCCPZTCzSgOxV3Jx7pCN94g9hVxdJh
else:
    # Replace with environment variable loading or fallback
    os.environ["MISTRAL_API_KEY"] = "GsoCCPZTCzSgOxV3Jx7pCN94g9hVxdJh"

# --- Optional Image Header ---
try:
    st.image("Image.png", width=150)
except Exception:
    pass

# --- Model Initialization ---
@st.cache_resource
def get_model():
    return ChatMistralAI(model="mistral-small-2506", temperature=0.9)

model = get_model()

# --- Sidebar: Persona Selection ---
st.sidebar.title("Chat Settings")

persona_list = [
    "Motivation", "Cooking", "Coding", "Civil Engineer", "Amazon",
    "Facebook and Instagram post", "BS in Cloud Computing, AI, Robotic, Cybersecurity and Data Science",
    "Petroleum", "Chemical Engineering", "Physics", "Calculus", "Maths",
    "English", "Ethics", "Statistics", "Linear Algebra", "Electrical Engineering",
    "Electronics Engineering", "Criminology", "Hardware", "Software Engineering",
    "Medical Patient", "Research", "News & World Affairs", "Project Management",
    "Digital Marketing & SEO", "Data Analytics & BI", "UI/UX Product Design",
    "Creative Writing", "Music Theory & Production", "Photography & Videography",
    "Financial Planning", "Fitness & Exercise Science", "Nutrition & Dietetics",
    "Mental Health & Mindfulness", "World History & Archaeology",
    "Entrepreneurship & Startups", "Game Design & Development",
    "Public Speaking & Presenting", "Astronomy & Space Exploration"
]

persona = st.sidebar.selectbox("Choose Which AI you want:", persona_list)

# --- Hide Streamlit Branding ---
hide_streamlit_badge = """ 
<style> 
#MainMenu {visibility: hidden;}
footer {visibility: hidden;} 
header {visibility: hidden;}
.stDeployButton {display:none;}
div[data-testid="stStatusWidget"] {visibility: hidden;} 
</style> """ 
st.markdown(hide_streamlit_badge, unsafe_allow_html=True)

# --- Sidebar: Document Upload ---
st.sidebar.markdown("---")
st.sidebar.title("Paper / Document")

uploaded_file = st.sidebar.file_uploader(
    "Upload a text document or paper context:",
    type=["txt", "pdf", "py", "csv", "json"]
)

document_context = ""
if uploaded_file is not None:
    try:
        document_context = uploaded_file.getvalue().decode("utf-8")
        st.sidebar.success(f"Loaded: {uploaded_file.name} ({len(document_context)} characters)")
    except Exception:
        st.sidebar.error("Error reading file. Ensure it is UTF-8 text.")

# --- Persona Configuration Mapping ---
PERSONA_CONFIGS = {
    "Motivation": {
        "title": "Mindset Master AI",
        "subtitle": "Your 24/7 personal pocket cheerleader.",
        "input_placeholder": "What goal are you tackling today?",
        "system_prompt": "You are an enthusiastic, high-energy Motivational AI agent. Boost user confidence, combat self-doubt, and give actionable productivity advice.",
        "spinner": "Channeling pure motivation..."
    },
    "Cooking": {
        "title": "Chef de Partie AI",
        "subtitle": "Your culinary guide, recipe creator, and kitchen assistant.",
        "input_placeholder": "What ingredients do you have, or what do you want to cook?",
        "system_prompt": "You are an expert culinary chef AI. Provide clear recipes, cooking techniques, ingredient substitutions, and kitchen tips.",
        "spinner": "Sharpening the knives..."
    },
    "Coding": {
        "title": "StackOverflow Companion",
        "subtitle": "Your expert software engineer and debugger.",
        "input_placeholder": "Paste your code error or ask a programming question...",
        "system_prompt": "You are an expert senior software engineer AI. Provide clean, secure, optimized code snippets with explanations.",
        "spinner": "Compiling thoughts..."
    }
    # Add other persona dictionary mappings here as needed...
}

# Fallback default configuration if selected persona isn't explicitly defined in PERSONA_CONFIGS
default_config = {
    "title": f"{persona} AI Assistant",
    "subtitle": f"Specialized expert in {persona}.",
    "input_placeholder": "Ask a question...",
    "system_prompt": f"You are an expert AI assistant specialized in {persona}. Provide clear, professional, and detailed assistance.",
    "spinner": "Processing response..."
}

current_config = PERSONA_CONFIGS.get(persona, default_config)

# --- Construct System Prompt ---
final_system_prompt = current_config["system_prompt"]
if document_context:
    final_system_prompt += (
        f"\n\n[Context Document]\n"
        f"The user has provided the following reference document to help you answer questions:\n"
        f"{document_context}\n"
        f"[END OF CONTEXT DOCUMENT]\n\n"
        f"Refer to this document content directly if the user asks you to explain, summarize, or extract details from it."
    )

# --- Initialize or Reset Session Messages ---
doc_name = uploaded_file.name if uploaded_file else None

if (
    "current_persona" not in st.session_state
    or st.session_state.current_persona != persona
    or "last_doc_name" not in st.session_state
    or st.session_state.last_doc_name != doc_name
):
    st.session_state.current_persona = persona
    st.session_state.last_doc_name = doc_name
    st.session_state.messages = [SystemMessage(content=final_system_prompt)]

# Display Title and Subtitle
st.title(current_config["title"])
st.subheader(current_config["subtitle"])

if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = [SystemMessage(content=final_system_prompt)]
    st.rerun()

# --- Render Chat History ---
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# --- Handle User Input ---
user_input = st.chat_input(current_config["input_placeholder"])

if user_input:
    # Display user message
    st.chat_message("user").write(user_input)
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner(current_config["spinner"]):
            response = model.invoke(st.session_state.messages)
            st.write(response.content)
            st.session_state.messages.append(AIMessage(content=response.content))
