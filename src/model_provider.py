import os
from dotenv import load_dotenv
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv(override=True)

# Create a model client for Azure OpenAI


def create_model_client(
    model_name: str,
    json_output: bool = False,
    function_calling: bool = False,
    vision: bool = False,
    model_family: str = "Unknown"
) -> AzureAIChatCompletionClient:
    """
    Create a model client for Azure OpenAI.
    """
    return AzureAIChatCompletionClient(
        model=model_name,
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        # To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
        # Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
        credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN")),
        model_info={
            "model_name": model_name,
            "json_output": json_output,
            "function_calling": function_calling,
            "vision": vision,
            "family": model_family
        }
    )
