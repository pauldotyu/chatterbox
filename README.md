# ChatterBox

Simple ChatGPT-like chatbot built with Streamlit and LangChain and uses Azure OpenAI as backend model.

To run the app, provision an Azure OpenAI resource, deploy a **gpt-4o** model, and grant your user the **Cognitive Services OpenAI User** role.

Next, run the following commands to set up the environment variables to point to Azure OpenAI.

```bash
export AZURE_OPENAI_ENDPOINT=https://<YOUR_RESOURCE_NAME>.openai.azure.com/
export AZURE_OPENAI_API_VERSION=2024-02-15-preview
export AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=<YOUR_MODEL_DEPLOYMENT_NAME>
```

Or, if you are running this against local models hosted by Kaito in an AKS cluster, run these commands.

```bash
export SELECTED_MODEL=Kaito
export MODEL_ENDPOINT=http://<YOUR_SERVICE_PUBLIC_IP>/chat
```

Create a virtual environment and install the dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Run the app.
 
```bash
streamlit run main.py
```

Or, you can run the app in a Docker container:

```bash
docker run -p 8501:8501 -e SELECTED_MODEL="${SELECTED_MODEL}" -e MODEL_ENDPOINT="${MODEL_ENDPOINT}" ghcr.io/pauldotyu/chatterbox:latest
```