import os
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI

st.title('🦜🔗 Chatter Box')

# Store environment variables in constants
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

# Create the model once
model = AzureChatOpenAI(
  api_key=AZURE_OPENAI_API_KEY,
  azure_endpoint=AZURE_OPENAI_ENDPOINT,
  azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
  openai_api_version=AZURE_OPENAI_API_VERSION,
) if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_VERSION and AZURE_OPENAI_CHAT_DEPLOYMENT_NAME else None

# Set a default model deployment
if "openai_model_deployment" not in st.session_state:
  st.session_state["openai_model_deployment"] = AZURE_OPENAI_CHAT_DEPLOYMENT_NAME

# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])
  
if not model:
  st.warning('Azure OpenAI information not set!', icon='⚠')
else:
  # Accept user input
  if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user mesage in chat message container
    with st.chat_message("user"):
      st.markdown(prompt)
    # Display assistant response in chat message conatainer
    with st.chat_message("assistant"):
      # Create a list of all messages in the conversation history
      conversation_history = [HumanMessage(content=message["content"]) if message["role"] == "user" else SystemMessage(content=message["content"]) for message in st.session_state.messages]
      # Add the latest user message to the conversation history
      conversation_history.append(HumanMessage(content=prompt))
      # Generate the assistant response using the conversation history
      stream = model.stream(conversation_history)
      response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})