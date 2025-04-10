# 🌐🤖 Multi-Agent Cloud Architect

🌐 A multi-agent cloud architect

## 🛠️ Setup Instructions

### 1. 🐍 Create a Python Virtual Environment
To create a Python virtual environment, run the following command in the root of the project:

```bash
py -m venv .venv
```

Activate the virtual environment:
- On Windows:
  ```bash
  .venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

### 2. 📄 Create a `.env` File


Create a `.env` file at the root of the project and add the following environment variables:

```env
AZURE_OPENAI_ENDPOINT="https://models.inference.ai.azure.com"
GITHUB_TOKEN="<your_github_token>"

### Uncomment the lines below to enable OAuth authentication with Azure EntraID
#CHAINLIT_URL="http://localhost:8000"
#CHAINLIT_AUTH_SECRET="<your_chainlit_auth_secret>"

#OAUTH_AZURE_AD_CLIENT_ID="<your_oauth_azure_ad_client_id>"
#OAUTH_AZURE_AD_CLIENT_SECRET="<your_oauth_azure_ad_client_secret>"
#OAUTH_AZURE_AD_TENANT_ID="<your_oauth_azure_ad_tenant_id>"
#OAUTH_AZURE_AD_ENABLE_SINGLE_TENANT=True
```
⚠️**Notes:**
- Navigate to [GitHub Developer Settings](https://github.com/settings/tokens) and create a Personal Access Token (PAT). Use this token for the `GITHUB_TOKEN` variable. No specific scope is required.
- The `CHAINLIT_AUTH_SECRET` is a secret key used for authentication. You can generate it by running the following command:
  ```bash
  chainlit create-secret
  ```

### 3. 📦 Install Dependencies
After setting up the virtual environment and `.env` file, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. 🚀 Run Chainlit Apps
To run the Chainlit apps, use the following commands:

1. 🤖 **Autogen Multi-Agent App**
   ```bash
   chainlit run ag_multi_agent.py
   ```

2. 🤖 **Semantic Kernel Single-Agent App**
   ```bash
   chainlit run sk_single_agent.py
   ```

3. 🤖 **Semantic Kernel Multi-Agent App**
   ```bash
   chainlit run sk_multi_agent.py
   ```

