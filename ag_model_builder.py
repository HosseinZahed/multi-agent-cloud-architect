import os
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import EmbeddingsClient

# Create a model client for Azure OpenAI
def create_model_client(
    model_name: str,
    json_output: bool = False,
    function_calling: bool = False,
    structured_output: bool = False,
    vision: bool = False,
    model_family: str = "text"
) -> AzureAIChatCompletionClient:
    """
    Create a model client for Azure OpenAI.
    """
    return AzureAIChatCompletionClient(
        model=model_name,
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN")),
        model_info={
            "model_name": model_name,
            "json_output": json_output,
            "function_calling": function_calling,
            "structured_output": structured_output,
            "vision": vision,
            "family": model_family
        }
    )

def create_embeddings_client(
    model_name: str = "text-embedding-3-small" 
    ) -> AzureAIChatCompletionClient:
    """
    Create an embeddings client for Azure OpenAI.
    """
    return EmbeddingsClient(
        model=model_name,
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN"))
)