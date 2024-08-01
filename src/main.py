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
st.title('🦜🔗 ChatterBox')

with st.sidebar:
  st.title('Settings')
  
  modelIndex=0
  if os.getenv('SELECTED_MODEL') == 'Kaito - Phi-3-mini-128k-instruct':
    modelIndex=1
  # Model selection
  selected_model = st.selectbox('Model source', ['Azure OpenAI', 'Kaito - Llama2Chat', 'Kaito - Phi-3-mini-128k-instruct'], key='selected_model', index=modelIndex, placeholder="Choose an option", help='The source of the model to use for the chatbot.')
    
  # Display warnings for unavailable models
  if selected_model in ['Kaito - Llama2Chat', 'Kaito - Phi-3-mini-128k-instruct']:
      model_endpoint = st.text_input('Endpoint', value=os.getenv('MODEL_ENDPOINT', ''), help='The endpoint of the model to use for the chatbot.')
      request_system_message = st.text_area('System Message', value=os.getenv('SYSTEM_MESSAGE', 'Answer using very few words'))
      response_temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=1.0, value=0.0, step=0.01, help='The temperature to use when generating text. The higher the temperature, the more creative the response.')
  else:
      # Azure OpenAI settings
      azure_openai_api_version = st.text_input('API Version', value=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'), help='The version of the Azure OpenAI API to use.')
      azure_openai_endpoint = st.text_input('Endpoint', value=os.getenv('AZURE_OPENAI_ENDPOINT', ''), help='The endpoint of the Azure OpenAI service.')
      azure_openai_model_deployment_name = st.text_input('Name', value=os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT_NAME', ''), help='The name of the model deployment to use for the chatbot.')

  # Button to start a new chat
  st.button('New chat', on_click=clear_chat_history)

if selected_model in ['Kaito - Llama2Chat']:
  model = None 
  if model_endpoint:
    model = KaitoLlamaLLM(endpoint=model_endpoint,temperature=response_temperature)
    if not model:
      st.warning('Model endpoint not set!', icon='⚠')
    else:
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

        # Display user mesage in chat message container
        with st.chat_message("user"):
          st.markdown(prompt)
        
        # Display assistant response in chat message conatainer
        with st.chat_message("assistant"):
          # Create a list of all messages in the conversation history
          conversation_json = json.dumps(st.session_state.messages)
          # Convert the conversation history to a list
          conversation_list = json.loads(conversation_json)
          # Modify the conversation list to replace streamlit's system message with the user's system message
          conversation_list = [{"role": "system", "content": request_system_message}] + conversation_list[1:]
          # Convert the conversation list back to JSON
          conversation_json = json.dumps(conversation_list)
          
          try:
            # Generate the assistant response using the conversation history
            result = model.invoke(conversation_json)
            # Display the assistant response
            response = st.write(result)
            # Add the assistant response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": result})
          except Exception as e:
            st.error(f"Sorry, we've reached my chat limit. Click the **New chat** button to start over.")
elif selected_model in ['Kaito - Phi-3-mini-128k-instruct']:
  model = None 
  if model_endpoint:
    model = KaitoLLM(endpoint=model_endpoint,temperature=response_temperature)
    if not model:
      st.warning('Model endpoint not set!', icon='⚠')
    else:
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

        # Display user mesage in chat message container
        with st.chat_message("user"):
          st.markdown(prompt)

        # Display assistant response in chat message conatainer
        with st.chat_message("assistant"):
          try:
            # Get the user's prompt
            prompt = st.session_state.messages[-1]["content"]
            # Invoke the model with the user's prompt
            result = model.invoke("<|user|> " + prompt + "<|end|><|assistant|>")            
            # Display the user's prompt
            response = st.write(result)
            # Add the assistant response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": result})
          except Exception as e:
            st.error(e)
else:
  model = None
  if azure_openai_api_version and azure_openai_endpoint and azure_openai_model_deployment_name:
    # Get the Azure Credential
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    # Create the model once
    model = AzureChatOpenAI(
      openai_api_version=azure_openai_api_version,
      azure_endpoint=azure_openai_endpoint,
      azure_deployment=azure_openai_model_deployment_name,
      azure_ad_token_provider=token_provider,
    )

  if not model:
    st.warning('Azure OpenAI information not set!', icon='⚠')
  else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
    # Set a default model deployment
    if "openai_model_deployment" not in st.session_state:
      st.session_state["openai_model_deployment"] = azure_openai_model_deployment_name
    
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