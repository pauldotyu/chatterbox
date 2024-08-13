import json
import os
import streamlit as st
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from kaito_llama import KaitoLlamaLLM
from kaito import KaitoLLM

SYSTEM_MESSAGE = {"role": "assistant", "content": "How can I help you today?"}
if "messages" not in st.session_state:
    st.session_state['messages'] = [SYSTEM_MESSAGE]

# Function to clear chat history
def clear_chat_history():
    st.session_state['messages'] = [SYSTEM_MESSAGE]

# Main title
st.title('🦜🔗 KAITO Chatbot')

with st.sidebar:
  st.title('Settings')
  
  model_endpoint = st.text_input('Endpoint', value=os.getenv('MODEL_ENDPOINT', ''), help='The endpoint of the model to use for the chatbot.')
  response_temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=1.0, value=0.7, step=0.01, help='The temperature to use when generating text. The higher the temperature, the more creative the response.')
  response_top_k = st.sidebar.slider('Top K', min_value=1, max_value=100, value=50, step=1, help='The number of highest probability vocabulary tokens to consider.')
  response_top_p = st.sidebar.slider('Top P', min_value=0.01, max_value=1.0, value=0.9, step=0.01, help='The cumulative probability threshold for nucleus sampling.')
  response_diversity_penalty = st.sidebar.slider('Diversity Penalty', min_value=0.0, max_value=1.0, value=0.0, step=0.01, help='The diversity penalty to use when generating text.')
  response_max_length = st.sidebar.slider('Max Length', min_value=200, max_value=1000, value=200, step=100, help='The maximum length of the response.')
  response_max_new_tokens = st.sidebar.slider('Max New Tokens', min_value=200, max_value=1000, value=200, step=100, help='The maximum number of tokens to generate in the response.')

  # Button to start a new chat
  st.button('New chat', on_click=clear_chat_history)

if model_endpoint:
  model = KaitoLLM(endpoint=model_endpoint,max_length=response_max_length,max_new_tokens=response_max_new_tokens,temperature=response_temperature)

  # Display chat messages from history on app rerun
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Set a default model deployment
  if "model_endpoint" not in st.session_state:
    st.session_state["model_endpoint"] = model_endpoint
  
  # Accept user input
  if prompt := st.chat_input("Type a message..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
      st.markdown(prompt)

    # Invoke the call to KAITO's inferencing endpoint
    try:
      # Get session_state.messages from 1 index to the last index minus 1
      messages = st.session_state.messages[1:-1]
      # Build a chat history string from the messages
      chat_history = "".join([f"<|{message['role']}|>{message['content']}<|end|>" for message in messages])
      # Get the user's prompt
      prompt = st.session_state.messages[-1]["content"]
      # Invoke the model with the user's prompt and chat history
      result = model.invoke(chat_history + "<|user|> " + prompt + "<|end|><|assistant|>")
      # Add the model's response to the chat history
      st.session_state.messages.append({"role": "assistant", "content": result})
      # Display the response in the chat message container    
      with st.chat_message("assistant"):
        response = st.write(result)
    except Exception as e:
      st.error(e)
else:
  st.warning('Please enter the model inference endpoint to use for the chatbot.')