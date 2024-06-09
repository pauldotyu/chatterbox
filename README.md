# Chatter Box

Simple ChatGPT-like chatbot built with Streamlit and LangChain and uses Azure OpenAI as backend model.

To run the app, provision an Azure OpenAI resource and deploy a gpt-4o model.

Next, run the following commands to set up the environment variables:

```bash
export AZURE_OPENAI_ENDPOINT=https://<YOUR_RESOURCE_NAME>.openai.azure.com/
export AZURE_OPENAI_API_KEY=<YOUR_API_KEY>
export AZURE_OPENAI_API_VERSION=2024-02-15-preview
export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<YOUR_MODEL_DEPLOYMENT_NAME>
```

Next, run the following commands to run the app locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
streamlit run main.py
```