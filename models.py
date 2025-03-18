import os
from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient

# Load environment variables from .env file
load_dotenv(override=True)

# Create the Azure OpenAI client using key-based authentication
def create_azure_openai_client() -> AzureOpenAIChatCompletionClient:
    """Create an Azure OpenAI client using key-based authentication."""
    if not all([
        os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        os.getenv("AZURE_OPENAI_MODEL"),
        os.getenv("AZURE_OPENAI_API_VERSION"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_KEY")
    ]):
        raise ValueError("Please set all required environment variables for Azure OpenAI.")

    model_client = AzureOpenAIChatCompletionClient(
        api_type="azure",
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        model=os.getenv("AZURE_OPENAI_MODEL"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
        temperature=0.7,
        timeout=600
    )

    return model_client

# Create the Phi4 Mini client using Ollama
def create_phi4_mini_client() -> OllamaChatCompletionClient:
    """Create an Ollama client for Phi4 Mini."""
    model_client = OllamaChatCompletionClient(
        model="phi4-mini", 
        temperature=0.7, 
        timeout=600)
    
    return model_client


def get_model_client(model_name: str) -> AzureOpenAIChatCompletionClient | OllamaChatCompletionClient:
    """Get the appropriate model client based on the model name."""
    """Accepts: azure_openai, phi4_mini"""
    if model_name == "azure_openai":
        return create_azure_openai_client()
    elif model_name == "phi4_mini":
        return create_phi4_mini_client()
    else:
        raise ValueError(f"Unsupported model name: {model_name}")