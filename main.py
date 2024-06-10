import os
import streamlit as st
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI

st.title('🦜🔗 ChatterBox')

system_message = {"role": "assistant", "content": "How can I help you today?"}

with st.sidebar:
  st.title('Azure OpenAI Settings')
  AZURE_OPENAI_API_VERSION = st.text_input('API Version', key='AZURE_OPENAI_API_VERSION', value=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'), help='The version of the Azure OpenAI API to use.')
  AZURE_OPENAI_ENDPOINT = st.text_input('Endpoint', key='AZURE_OPENAI_ENDPOINT', value=os.getenv('AZURE_OPENAI_ENDPOINT', ''), help='The endpoint of the Azure OpenAI service.')
  AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = st.text_input('Name', key='AZURE_OPENAI_MODEL_DEPLOYMENT_NAME', value=os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT_NAME', ''), help='The name of the model deployment to use for the chatbot.')

def clear_chat_history():
  st.session_state.messages = [system_message]
st.sidebar.button('New chat', on_click=clear_chat_history)

# Get the Azure Credential
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# Create the model once
model = AzureChatOpenAI(
  openai_api_version=AZURE_OPENAI_API_VERSION,
  azure_endpoint=AZURE_OPENAI_ENDPOINT,
  azure_deployment=AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
  azure_ad_token_provider=token_provider,
) if AZURE_OPENAI_API_VERSION and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_MODEL_DEPLOYMENT_NAME else None

# Set a default model deployment
if "openai_model_deployment" not in st.session_state:
  st.session_state["openai_model_deployment"] = AZURE_OPENAI_MODEL_DEPLOYMENT_NAME

# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = [system_message]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])
  
if not model:
  st.warning('Azure OpenAI information not set!', icon='⚠')
else:
  # Accept user input
  if prompt := st.chat_input("Type a message..."):
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