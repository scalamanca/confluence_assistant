import streamlit as st
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import markdown
from bs4 import BeautifulSoup

# Initialize Pinecone (you'll need to add your API key to Streamlit secrets)
pc = Pinecone(api_key = st.secrets["PINECONE_API_KEY"])

# pc = Pinecone(api_key="11c075e7-0e09-4108-a570-24ba6889df28")
# Initialize the assistant
assistant = pc.assistant.describe_assistant("confluenceassistant")

def format_response(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    formatted_text = ''
    for element in soup.find_all(['p', 'ul', 'ol']):
        if element.name == 'p':
            formatted_text += f"{element.get_text()}\n\n"
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                formatted_text += f"• {li.get_text()}\n"
            formatted_text += "\n"
    return formatted_text.strip()

def chat(message: str):
    # create Message object
    msg = Message(content=message, role="user")
    # get response from assistant
    out = assistant.chat_completions(messages=[msg])
    assistant_msg = out.choices[0].message.to_dict()
    html_content = markdown.markdown(assistant_msg["content"])
    return format_response(html_content)

st.title("Confluence Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# React to user input
if prompt := st.chat_input("What is your question?"):
    # Display user message in chat message container
    st.chat_message("user").write(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = chat(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})